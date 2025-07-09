"""FastAPI server for SafeRL ProofStack REST API."""

import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import yaml

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

from .cli import init, train, bundle, check_fireworks_key
from .pipeline import ProofPipeline


app = FastAPI(
    title="SafeRL ProofStack API",
    description="REST API for RL safety proofs and compliance bundles",
    version="0.1.0",
)


class InitRequest(BaseModel):
    env_name: str
    output_dir: Optional[str] = "./my_env"


class TrainRequest(BaseModel):
    algo: str = "ppo"
    timesteps: int = 10000
    env: str = "CartPole-v1"
    wandb: bool = False
    output_dir: str = "./rl"


class BundleRequest(BaseModel):
    spec_file: str = "safety_spec.yaml"
    output_dir: str = "./dist"
    mock: bool = False


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
            "message": f"Project initialized successfully",
            "project_dir": str(project_dir),
            "temp_dir": temp_dir,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/train")
async def train_agent(request: TrainRequest, background_tasks: BackgroundTasks):
    """Train an RL agent."""
    try:
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
            "message": f"Agent trained successfully",
            "model_file": str(model_files[0]),
            "algorithm": request.algo,
            "environment": request.env,
            "timesteps": request.timesteps,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/bundle")
async def generate_bundle(request: BundleRequest):
    """Generate safety proof bundle."""
    try:
        # Check API key if not using mock
        if not request.mock:
            api_key = check_fireworks_key()
            if not api_key:
                raise HTTPException(
                    status_code=400,
                    detail="FIREWORKS_API_KEY environment variable not set",
                )
        else:
            api_key = "mock_key"

        # Load safety specification
        spec_path = Path(request.spec_file)
        if not spec_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Specification file not found: {request.spec_file}",
            )

        with open(spec_path) as f:
            spec_data = yaml.safe_load(f)

        # Create mock environment and spec objects
        class MockEnv:
            def __init__(self):
                self.observation_space = None
                self.action_space = None

        class MockSafetySpec:
            def __init__(self, data):
                self.invariants = data.get("invariants", [])
                self.guard = data.get("guard", [])
                self.lemmas = data.get("lemmas", [])

        env = MockEnv()
        spec = MockSafetySpec(spec_data)

        # Create pipeline and run
        pipeline = ProofPipeline(env, spec, api_key)
        bundle = pipeline.run()

        return {
            "status": "success",
            "message": "Bundle generated successfully",
            "bundle_path": bundle.path,
            "artifacts": list_artifacts(bundle.path),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/bundle/{bundle_id}")
async def download_bundle(bundle_id: str, artifact: Optional[str] = None):
    """Download bundle artifacts."""
    try:
        # In a real implementation, you'd look up the bundle by ID
        # For now, we'll assume bundle_id is a path
        bundle_path = Path(bundle_id)

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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/spec")
async def create_spec(spec: SafetySpec):
    """Create a safety specification file."""
    try:
        # Create specs directory
        specs_dir = Path("specs")
        specs_dir.mkdir(exist_ok=True)

        # Generate spec file
        spec_file = specs_dir / f"{spec.environment}_spec.yaml"

        with open(spec_file, "w") as f:
            yaml.dump(spec.dict(), f, default_flow_style=False)

        return {
            "status": "success",
            "message": "Safety specification created",
            "spec_file": str(spec_file),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def list_artifacts(bundle_path: str) -> Dict[str, Any]:
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
