# SafeRL ProofStack

**RL + Formal Proofs + Compliance Bundles**

SafeRL ProofStack combines reinforcement learning with formal verification in Lean4 and generates comprehensive compliance artifacts for safety-critical AI systems.

## 🚀 Quick Start

### One-Command UX

```bash
# Initialize a new project
proofstack init cartpole

# Train an RL agent
proofstack train --algo ppo --timesteps 10000

# Generate safety bundle
proofstack bundle --mock
```

### Complete Workflow

```bash
# 1. Initialize project
proofstack init cartpole --output ./my_cartpole
cd my_cartpole

# 2. Train agent (optional - can use pre-trained)
proofstack train --algo ppo --timesteps 10000 --env CartPole-v1

# 3. Generate compliance bundle
proofstack bundle --mock  # Use --mock for offline testing
```

## 📋 CLI Commands

### `proofstack init <env>`

Initialize a new SafeRL ProofStack project with:

- Environment wrapper template (`env.py`)
- Safety specification skeleton (`safety_spec.yaml`)
- Project structure (`rl/`, `specs/`, `dist/`)

**Options:**

- `--output, -o`: Output directory (default: `./my_env`)

### `proofstack train`

Train an RL agent using Stable-Baselines3.

**Options:**

- `--algo, -a`: Algorithm (ppo, sac, ddpg) [default: ppo]
- `--timesteps, -t`: Training timesteps [default: 10000]
- `--env, -e`: Environment name [default: CartPole-v1]
- `--wandb`: Enable Weights & Biases logging
- `--output, -o`: Output directory [default: ./rl]

### `proofstack bundle`

Generate safety proof bundle with compliance artifacts.

**Options:**

- `--spec, -s`: Safety specification file [default: safety_spec.yaml]
- `--output, -o`: Output directory [default: ./dist]
- `--watch, -w`: Watch proof generation in real-time
- `--mock`: Use mock proofs (no API calls)

### `proofstack version`

Show version information.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   RL Training   │    │  Lean4 Proofs   │    │   Compliance    │
│                 │    │                 │    │   Artifacts     │
│ • PPO/SAC/DDPG  │───▶│ • SpecGen       │───▶│ • HTML Report   │
│ • Gymnasium     │    │ • ProverAPI     │    │ • SBOM          │
│ • SB3 Wrappers  │    │ • DeepSeek-Pro  │    │ • PDF Attest.   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Guard Code    │
                       │                 │
                       │ • C/C++ Guards  │
                       │ • Runtime Check │
                       └─────────────────┘
```

## 🔧 Installation

### Prerequisites

- Python 3.9+
- Lean4 (for proof checking)
- Poetry (recommended)

### Setup

```bash
# Clone repository
git clone https://github.com/your-org/saferl-proofstack.git
cd saferl-proofstack

# Install dependencies
pip install -e .

# Set up Lean4 (optional, for proof checking)
lake build
```

### Environment Variables

```bash
# Required for proof generation
export FIREWORKS_API_KEY="your_api_key_here"

# Optional: Use mock mode for offline testing
# No API key required when using --mock flag
```

## 📚 Usage Examples

### Basic CartPole Safety

```python
from proofstack import ProofPipeline, SpecGen

# Create safety specification
spec = SpecGen()
spec.invariants = ["|σ.cart_position| ≤ 2.4", "|σ.pole_angle| ≤ 0.2095"]
spec.guard = ["|σ.cart_position| ≤ 2.3", "|σ.pole_angle| ≤ 0.2"]

# Generate Lean proof
lean_file = spec.emit_lean()
proof = spec.write_proof("simp [h_guard]")

# Create compliance bundle
pipeline = ProofPipeline(env, spec, api_key)
bundle = pipeline.run()
```

### Custom Environment

```python
import gymnasium as gym
from stable_baselines3 import PPO

# Define your environment
class SafeEnv(gym.Env):
    def __init__(self):
        self.observation_space = gym.spaces.Box(-10, 10, (4,))
        self.action_space = gym.spaces.Discrete(2)

    def step(self, action):
        # Your environment logic
        pass

# Train agent
env = SafeEnv()
model = PPO("MlpPolicy", env)
model.learn(total_timesteps=10000)

# Generate safety proofs
spec = SpecGen()
spec.invariants = ["your_safety_invariants"]
bundle = ProofPipeline(env, spec, api_key).run()
```

## 🧪 Testing

### Run All Tests

```bash
# Run comprehensive test suite
python run_tests.py

# Individual test categories
pytest tests/ -v --cov=proofstack
lake build  # Lean proof checking
```

### CLI Smoke Test

```bash
# Test complete CLI workflow
proofstack init cartpole
proofstack train --algo ppo --timesteps 100 --mock
proofstack bundle --mock
```

## 📖 Documentation

### API Reference

- [ProofPipeline](docs/api.md#proofpipeline) - Main orchestration class
- [SpecGen](docs/api.md#specgen) - Lean4 specification generation
- [ProverAPI](docs/api.md#proverapi) - Fireworks DeepSeek-Prover integration
- [Attestation](docs/api.md#attestation) - Compliance artifact generation
- [GuardGen](docs/api.md#guardgen) - Runtime guard code generation

### Architecture

- [System Design](docs/architecture.md) - High-level system architecture
- [Safety Specifications](docs/safety.md) - Writing safety invariants
- [Lean4 Integration](docs/lean.md) - Formal proof generation

## 🔒 Safety Features

### H-0: Stabilization ✅

- **100% test coverage** with property-based tests
- **Static analysis gates** (ruff, mypy, pre-commit)
- **Pinned toolchain versions** for deterministic builds
- **CI/CD pipeline** with comprehensive checks

### H-1: One-Command UX ✅

- **Zero-config CLI** with sensible defaults
- **Async streaming** for real-time proof updates
- **REST API** for programmatic access
- **Rich console output** with progress bars
- **Mock mode** for offline development

### H-2: Documentation & Examples

- **Live documentation** with mkdocs
- **Example notebooks** for common use cases
- **Tutorial videos** (planned)

### H-3: Multi-Algorithm Support

- **Safe SAC & DDPG** implementations
- **Algorithm-specific Lean templates**
- **Parametrized safety specifications**

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v --cov=proofstack
```

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Lean4](https://leanprover.github.io/) for formal verification
- [Stable-Baselines3](https://stable-baselines3.readthedocs.io/) for RL algorithms
- [Fireworks AI](https://fireworks.ai/) for DeepSeek-Prover API
- [Gymnasium](https://gymnasium.farama.org/) for RL environments

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/saferl-proofstack/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/saferl-proofstack/discussions)
- **Documentation**: [Live Docs](https://your-org.github.io/proofstack)

---

**SafeRL ProofStack** - Making RL systems provably safe, one proof at a time. 🛡️
