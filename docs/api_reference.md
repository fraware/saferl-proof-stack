# SafeRL ProofStack API Reference

This document provides comprehensive API documentation for the SafeRL ProofStack library, based on the actual implementation.

## Table of Contents

- [Core Classes](#core-classes)
- [Pipeline](#pipeline)
- [Specification Generation](#specification-generation)
- [Proof Generation](#proof-generation)
- [Attestation](#attestation)
- [Guard Code Generation](#guard-code-generation)
- [Caching](#caching)
- [Compliance Mapping](#compliance-mapping)
- [RL Algorithms](#rl-algorithms)
- [CLI Interface](#cli-interface)

## Core Classes

### ProofPipeline

The main orchestrator for the end-to-end proof and attestation pipeline.

```python
class ProofPipeline:
    def __init__(self, env, safety_spec, api_key, prover="fireworks/deepseek-prover-v2"):
        """
        Initialize the proof pipeline.

        Args:
            env: Gymnasium environment
            safety_spec: Dictionary containing safety specifications
            api_key: Fireworks API key for proof generation
            prover: Prover model to use (default: "fireworks/deepseek-prover-v2")
        """

    def run(self, reuse_cache=True, mathlib_commit="latest", algo="ppo"):
        """
        Run the complete pipeline.

        Args:
            reuse_cache: Whether to reuse cached proofs (default: True)
            mathlib_commit: Mathlib commit hash (default: "latest")
            algo: Algorithm name for template generation (default: "ppo")

        Returns:
            Attestation bundle object
        """
```

## Specification Generation

### SpecGen

Generates Lean4 specifications from Python safety constraints.

```python
class SpecGen:
    def __init__(self):
        """
        Initialize the specification generator.

        Attributes:
            invariants: List of safety invariants
            guard: List of guard conditions
            lemmas: List of safety lemmas
            lean_file_path: Path to generated Lean file
            algorithm_name: Algorithm name for template generation
        """

    def set_algorithm(self, algorithm_name: str) -> None:
        """
        Set the algorithm name for template generation.

        Args:
            algorithm_name: Name of the algorithm ('ppo', 'sac', 'ddpg')
        """

    def emit_lean(self, algorithm_name: Optional[str] = None) -> str:
        """
        Generate Lean4 specification file.

        Args:
            algorithm_name: Optional algorithm name override

        Returns:
            Path to the generated Lean file
        """

    def write_proof(self, proof: str) -> None:
        """
        Write proof to the Lean file.

        Args:
            proof: Proof content to write
        """
```

## Proof Generation

### ProverAPI

Client for Fireworks DeepSeek-Prover API for Lean proof completion.

```python
class ProverAPI:
    def __init__(self, api_key, model="fireworks/deepseek-prover-v2"):
        """
        Initialize the prover API client.

        Args:
            api_key: Fireworks API key
            model: Model to use for proof generation
        """

    def complete(self, lean_code):
        """
        Send Lean code to the prover and return the completed proof.

        Args:
            lean_code: Lean4 code to prove

        Returns:
            Completed proof as string
        """

    async def stream(self, lean_file: str) -> AsyncIterator[str]:
        """
        Stream proof generation updates in real-time.

        Args:
            lean_file: Path to the Lean file to prove

        Yields:
            Status updates as strings
        """
```

## Attestation

### Attestation

Generates compliance artifacts and bundles them.

```python
class Attestation:
    def __init__(self, out_dir="attestation_bundle"):
        """
        Initialize the attestation generator.

        Args:
            out_dir: Output directory for artifacts
        """

    def generate_html_report(self, spec):
        """
        Generate HTML attestation report.

        Args:
            spec: Specification object

        Returns:
            Path to generated HTML file
        """

    def generate_sbom(self):
        """
        Generate Software Bill of Materials (SBOM).

        Returns:
            Path to generated SBOM file
        """

    def generate_pdf(self, html_path):
        """
        Generate PDF attestation report.

        Args:
            html_path: Path to HTML report

        Returns:
            Path to generated PDF file
        """

    def generate_hash(self, target_dir="."):
        """
        Generate cryptographic hash of Lean project.

        Args:
            target_dir: Directory to hash

        Returns:
            Path to hash file
        """

    def generate_compliance_mapping(self, spec, guardgen, algorithm: str = "ppo") -> Path:
        """
        Generate compliance mapping linking control objectives to artifacts.

        Args:
            spec: Specification object
            guardgen: Guard code generator
            algorithm: Algorithm name

        Returns:
            Path to compliance.json file
        """

    def bundle(self, spec, guardgen, algorithm: str = "ppo"):
        """
        Bundle all artifacts into a single package.

        Args:
            spec: Specification object
            guardgen: Guard code generator
            algorithm: Algorithm name

        Returns:
            Bundle object with .path attribute
        """
```

## Guard Code Generation

### GuardGen

Generates runtime guard code from safety specifications.

```python
class GuardGen:
    def __init__(self):
        """Initialize the guard code generator."""

    def emit_c(self, spec) -> str:
        """
        Generate C99 runtime guard code from safety specification.

        Args:
            spec: Safety specification object with invariants, guard, and lemmas

        Returns:
            Path to the generated C file
        """
```

## Caching

### ProofCache

Lazy proof-sketch cache for Lean proofs.

```python
class ProofCache:
    def __init__(self, cache_dir: Path = CACHE_DIR):
        """
        Initialize the proof cache.

        Args:
            cache_dir: Cache directory path
        """

    def get(self, spec_sha256: str, algo: str, mathlib_commit: str) -> Optional[Dict[str, Any]]:
        """
        Get cached proof sketch if present.

        Args:
            spec_sha256: SHA256 hash of specification
            algo: Algorithm name
            mathlib_commit: Mathlib commit hash

        Returns:
            Cached proof sketch or None
        """

    def set(self, spec_sha256: str, algo: str, mathlib_commit: str, proof_sketch: Dict[str, Any]) -> None:
        """
        Store proof sketch in cache.

        Args:
            spec_sha256: SHA256 hash of specification
            algo: Algorithm name
            mathlib_commit: Mathlib commit hash
            proof_sketch: Proof sketch to cache
        """

    def clear(self) -> None:
        """Clear the entire cache."""

    @staticmethod
    def compute_spec_sha256(spec: str) -> str:
        """
        Compute SHA256 hash of the spec string.

        Args:
            spec: Specification string

        Returns:
            SHA256 hash as hex string
        """
```

## Compliance Mapping

### ComplianceMapper

Maps control objectives to specific artifacts for compliance evidence.

```python
class ComplianceMapper:
    def __init__(self, standards_dir: str = "opencontrol"):
        """
        Initialize the compliance mapper.

        Args:
            standards_dir: Directory containing compliance standards
        """

    def map_artifacts_to_controls(self, lean_file_path: str, guard_file_path: str,
                                 sbom_file_path: str, test_results: Dict[str, Any],
                                 algorithm: str = "ppo") -> ComplianceReport:
        """
        Map artifacts to control objectives for compliance evidence.

        Args:
            lean_file_path: Path to Lean proof file
            guard_file_path: Path to guard code file
            sbom_file_path: Path to SBOM file
            test_results: Test results dictionary
            algorithm: Algorithm name

        Returns:
            ComplianceReport object
        """

    def generate_compliance_json(self, compliance_report: ComplianceReport) -> str:
        """
        Generate compliance JSON from report.

        Args:
            compliance_report: Compliance report object

        Returns:
            JSON string representation
        """
```

### Data Classes

```python
@dataclass
class ArtifactReference:
    """Reference to a specific artifact with line numbers or identifiers."""
    artifact_type: str  # "lean_theorem", "guard_code", "sbom_component", "test_case"
    artifact_path: str
    line_numbers: Optional[List[int]] = None
    identifiers: Optional[List[str]] = None
    description: Optional[str] = None

@dataclass
class ControlMapping:
    """Mapping of a control objective to specific artifacts."""
    control_id: str
    control_name: str
    control_description: str
    standard: str
    compliance_level: str
    status: str  # "compliant", "partially_compliant", "non_compliant", "not_applicable"
    artifacts: List[ArtifactReference]
    evidence_description: str
    verification_method: str
    last_verified: datetime
    verified_by: str

@dataclass
class ComplianceReport:
    """Complete compliance report for a system."""
    system_name: str
    system_version: str
    standards: List[str]
    compliance_level: str
    report_date: datetime
    generated_by: str
    control_mappings: List[ControlMapping]
    summary: Dict[str, Any]
```

## RL Algorithms

### SafeAlgorithmAdapter

Abstract base class for safe RL algorithm adapters.

```python
class SafeAlgorithmAdapter(ABC):
    def __init__(self, env: gym.Env, **kwargs):
        """
        Initialize the algorithm adapter.

        Args:
            env: Gymnasium environment
            **kwargs: Algorithm-specific parameters
        """

    def create_model(self) -> BaseAlgorithm:
        """Create and return the RL model."""

    def train(self, total_timesteps: int, **kwargs) -> None:
        """
        Train the model with safety considerations.

        Args:
            total_timesteps: Number of training timesteps
            **kwargs: Additional training parameters
        """

    def predict(self, observation: np.ndarray, deterministic: bool = True) -> tuple:
        """
        Predict action with safety constraints.

        Args:
            observation: Current observation
            deterministic: Whether to use deterministic policy

        Returns:
            Tuple of (action, state)
        """

    def save(self, path: str) -> None:
        """
        Save the trained model.

        Args:
            path: Path to save the model
        """
```

### Algorithm Adapters

```python
class PPOSafeAdapter(SafeAlgorithmAdapter):
    """Safe PPO algorithm adapter."""

class SACSafeAdapter(SafeAlgorithmAdapter):
    """Safe SAC algorithm adapter."""

class DDPGSafeAdapter(SafeAlgorithmAdapter):
    """Safe DDPG algorithm adapter."""
```

### Factory Function

```python
def create_safe_algorithm(algorithm: str, env: gym.Env, **kwargs) -> SafeAlgorithmAdapter:
    """
    Create a safe algorithm adapter.

    Args:
        algorithm: Algorithm name ('ppo', 'sac', 'ddpg')
        env: Gymnasium environment
        **kwargs: Algorithm-specific parameters

    Returns:
        SafeAlgorithmAdapter instance

    Raises:
        ValueError: If algorithm is not supported
    """
```

## CLI Interface

The CLI provides a command-line interface for SafeRL ProofStack operations.

### Commands

#### init

Initialize a new SafeRL ProofStack project.

```bash
proofstack init <env_name> [--output <output_dir>]
```

**Arguments:**

- `env_name`: Environment name (e.g., cartpole, lunarlander)

**Options:**

- `--output, -o`: Output directory (default: "./my_env")

#### train

Train an RL agent using SafeRL ProofStack algorithms.

```bash
proofstack train [--algo <algorithm>] [--timesteps <timesteps>] [--env <environment>] [--wandb] [--output <output_dir>]
```

**Options:**

- `--algo, -a`: RL algorithm (ppo, sac, ddpg) (default: "ppo")
- `--timesteps, -t`: Training timesteps (default: 10000)
- `--env, -e`: Environment name (default: "CartPole-v1")
- `--wandb`: Enable Weights & Biases logging
- `--output, -o`: Output directory (default: "./rl")

#### bundle

Generate safety bundle with proofs and compliance artifacts.

```bash
proofstack bundle [--spec <spec_file>] [--output <output_dir>] [--watch] [--mock] [--algo <algorithm>] [--reuse-cache/--no-reuse-cache]
```

**Options:**

- `--spec, -s`: Safety specification file (default: "safety_spec.yaml")
- `--output, -o`: Output directory (default: "./dist")
- `--watch, -w`: Watch proof generation in real-time
- `--mock`: Use mock proofs (no API calls)
- `--algo, -a`: Algorithm for Lean template (ppo, sac, ddpg) (default: "ppo")
- `--reuse-cache/--no-reuse-cache`: Reuse cached proof sketches (default: on)

#### version

Display version information.

```bash
proofstack version
```

## Environment Variables

- `FIREWORKS_API_KEY`: Fireworks API key for proof generation

## Error Handling

The library provides comprehensive error handling:

- **API Errors**: Network and API errors are caught and logged
- **File Errors**: File operations include proper error handling
- **Validation**: Input validation for all public methods
- **Fallbacks**: Mock implementations for testing without API access

## Examples

### Basic Usage

```python
from proofstack import ProofPipeline
import gymnasium as gym

# Create environment
env = gym.make("CartPole-v1")

# Define safety specifications
safety_spec = {
    "invariants": ["|σ.cart_position| ≤ 2.4", "|σ.pole_angle| ≤ 0.2095"],
    "guard": ["|σ.cart_position| ≤ 2.3", "|σ.pole_angle| ≤ 0.2", "|a.force| ≤ 10.0"],
    "lemmas": ["position_step_bound", "angle_step_preserved"]
}

# Create pipeline
pipeline = ProofPipeline(env, safety_spec, api_key="your-api-key")

# Run pipeline
bundle = pipeline.run(reuse_cache=True, algo="ppo")
print(f"Bundle generated at: {bundle.path}")
```

### Using Safe RL Algorithms

```python
from proofstack.rl.algorithms import create_safe_algorithm
import gymnasium as gym

# Create environment
env = gym.make("CartPole-v1")

# Create safe algorithm
safe_algo = create_safe_algorithm("ppo", env)

# Train with safety constraints
safe_algo.train(total_timesteps=10000)

# Save model
safe_algo.save("safe_ppo_cartpole.zip")
```

### Compliance Mapping

```python
from proofstack import ComplianceMapper

# Create compliance mapper
mapper = ComplianceMapper()

# Map artifacts to controls
report = mapper.map_artifacts_to_controls(
    lean_file_path="lean_output/safety_proof.lean",
    guard_file_path="attestation_bundle/guard.c",
    sbom_file_path="attestation_bundle/sbom.spdx.json",
    test_results={"safety_tests": {"status": "passed"}},
    algorithm="ppo"
)

# Generate compliance JSON
compliance_json = mapper.generate_compliance_json(report)
```

## Notes

- All file paths are handled using `pathlib.Path` for cross-platform compatibility
- The library supports both synchronous and asynchronous operations
- Caching is enabled by default to reduce API calls and improve performance
- Mock implementations are available for testing without external dependencies
- The CLI provides a user-friendly interface for common operations
