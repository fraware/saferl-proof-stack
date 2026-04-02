"""FastAPI server for SafeRL ProofStack REST API."""

import tempfile
from pathlib import Path
from typing import Any, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .cli import check_fireworks_key, init, train
from .contracts import SUPPORTED_ALGORITHMS, load_safety_spec
from .errors import BundleNotFoundError, ValidationError
from .observability import configure_logging, get_logger, log_event
from .pipeline import ProofPipeline

configure_logging()
LOGGER = get_logger(__name__)
BUNDLE_REGISTRY: dict[str, Path] = {}

app = FastAPI(
    title="SafeRL ProofStack API",
    description="REST API for RL safety proofs and compliance bundles",
    version="0.1.0",
)


class InitRequest(BaseModel):
    env_name: str = Field(..., min_length=1, max_length=128)
    output_dir: Optional[str] = "./my_env"


class TrainRequest(BaseModel):
    algo: str = Field(default="ppo")
    timesteps: int = Field(default=10000, ge=1, le=10_000_000)
    env: str = Field(default="CartPole-v1", min_length=1, max_length=128)
    wandb: bool = False
    output_dir: str = "./rl"


class BundleRequest(BaseModel):
    spec_file: str = Field(default="safety_spec.yaml", min_length=1)
    output_dir: str = "./dist"
    algorithm: str = Field(default="ppo")


class SafetySpec(BaseModel):
    environment: str
    invariants: list[str]
    guard: list[str]
    lemmas: list[str]


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "SafeRL ProofStack API",
        "version": "0.1.0",
        "endpoints": {
            "POST /init": "Initialize a new project",
            "POST /train": "Train an RL agent",
            "POST /bundle": "Generate safety bundle",
            "GET /bundle/{bundle_id}": "Download bundle artifacts",
        },
    }


@app.post("/init")
async def init_project(request: InitRequest):
    """Initialize a new SafeRL ProofStack project."""
    try:
        # Create temporary directory for the project
        temp_dir = tempfile.mkdtemp(prefix="proofstack_")
        project_dir = Path(temp_dir) / request.env_name

        # Call the CLI init function
        init(request.env_name, str(project_dir))

        return {
            "status": "success",
            "message": "Project initialized successfully",
            "project_dir": str(project_dir),
            "temp_dir": temp_dir,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/train")
async def train_agent(request: TrainRequest):
    """Train an RL agent."""
    try:
        if request.algo not in SUPPORTED_ALGORITHMS:
            raise HTTPException(status_code=422, detail="Unsupported algorithm")
        # Create output directory
        output_path = Path(request.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Call the CLI train function
        train(
            algo=request.algo,
            timesteps=request.timesteps,
            env=request.env,
            wandb=request.wandb,
            output_dir=request.output_dir,
        )

        # Find the generated model file
        model_pattern = f"{request.algo}_{request.env.lower().replace('-', '_')}.zip"
        model_files = list(output_path.glob(model_pattern))

        if not model_files:
            raise HTTPException(
                status_code=500, detail="Model file not found after training"
            )

        return {
            "status": "success",
            "message": "Agent trained successfully",
            "model_file": str(model_files[0]),
            "algorithm": request.algo,
            "environment": request.env,
            "timesteps": request.timesteps,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/bundle")
async def generate_bundle(request: BundleRequest):
    """Generate safety proof bundle."""
    try:
        api_key = check_fireworks_key()
        if not api_key:
            raise HTTPException(
                status_code=400,
                detail="FIREWORKS_API_KEY environment variable not set",
            )
        if request.algorithm not in SUPPORTED_ALGORITHMS:
            raise HTTPException(status_code=422, detail="Unsupported algorithm")
        spec = load_safety_spec(Path(request.spec_file))

        # Create pipeline and run
        pipeline = ProofPipeline(None, spec, api_key)
        bundle = pipeline.run(algo=request.algorithm)
        bundle_id = f"bundle-{len(BUNDLE_REGISTRY) + 1}"
        BUNDLE_REGISTRY[bundle_id] = Path(bundle.path)
        log_event(LOGGER, "bundle_generated", bundle_id=bundle_id, bundle_path=bundle.path)

        return {
            "status": "success",
            "message": "Bundle generated successfully",
            "bundle_id": bundle_id,
            "bundle_path": bundle.path,
            "artifacts": list_artifacts(bundle.path),
        }
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/bundle/{bundle_id}")
async def download_bundle(bundle_id: str, artifact: Optional[str] = None):
    """Download bundle artifacts."""
    try:
        bundle_path = BUNDLE_REGISTRY.get(bundle_id)
        if bundle_path is None:
            raise BundleNotFoundError(f"Unknown bundle id: {bundle_id}")

        if not bundle_path.exists():
            raise HTTPException(status_code=404, detail="Bundle not found")

        if artifact:
            # Download specific artifact
            artifact_path = bundle_path / artifact
            if not artifact_path.exists():
                raise HTTPException(
                    status_code=404, detail=f"Artifact {artifact} not found"
                )

            return FileResponse(
                artifact_path, filename=artifact, media_type="application/octet-stream"
            )
        else:
            # List all artifacts
            return {"bundle_id": bundle_id, "artifacts": list_artifacts(bundle_path)}
    except BundleNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/spec")
async def create_spec(spec: SafetySpec):
    """Create a safety specification file."""
    try:
        # Create specs directory
        specs_dir = Path("specs")
        specs_dir.mkdir(exist_ok=True)

        # Generate spec file
        spec_file = specs_dir / f"{spec.environment}_spec.yaml"

        spec_file.write_text(spec.model_dump_json(indent=2), encoding="utf-8")

        return {
            "status": "success",
            "message": "Safety specification created",
            "spec_file": str(spec_file),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


def list_artifacts(bundle_path: str) -> dict[str, Any]:
    """List artifacts in a bundle."""
    bundle_dir = Path(bundle_path)
    if not bundle_dir.exists():
        return {}

    artifacts = {}
    for file_path in bundle_dir.glob("*"):
        if file_path.is_file():
            artifacts[file_path.name] = {
                "size": file_path.stat().st_size,
                "type": file_path.suffix,
            }

    return artifacts


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
