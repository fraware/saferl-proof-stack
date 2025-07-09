# System Architecture

## Overview

SafeRL ProofStack is designed as a modular system that transforms RL environments into formally verified safety proofs and compliance artifacts. The architecture follows a pipeline pattern with clear separation of concerns.

## High-Level Architecture

```mermaid
graph TB
    subgraph "Input Layer"
        A[RL Environment] --> B[Safety Specification]
        C[API Key] --> D[ProverAPI]
    end

    subgraph "Processing Pipeline"
        B --> E[SpecGen]
        E --> F[Lean4 Code]
        F --> D
        D --> G[Proof]
        G --> H[GuardGen]
        H --> I[Runtime Guards]
    end

    subgraph "Output Layer"
        I --> J[Attestation]
        J --> K[Compliance Bundle]
        K --> L[HTML Report]
        K --> M[SBOM]
        K --> N[PDF]
        K --> O[Guard Code]
    end

    style A fill:#e1f5fe
    style F fill:#f3e5f5
    style K fill:#e8f5e8
```

## Component Architecture

### Core Components

```mermaid
graph LR
    subgraph "ProofPipeline"
        A[Orchestrator] --> B[SpecGen]
        A --> C[ProverAPI]
        A --> D[GuardGen]
        A --> E[Attestation]
    end

    subgraph "External Services"
        F[Fireworks API] --> C
        G[Lean4] --> B
    end

    style A fill:#fff3e0
    style F fill:#fce4ec
```

### Data Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Pipeline
    participant SpecGen
    participant ProverAPI
    participant GuardGen
    participant Attestation

    User->>CLI: proofstack bundle
    CLI->>Pipeline: run()
    Pipeline->>SpecGen: emit_lean()
    SpecGen-->>Pipeline: lean_file_path
    Pipeline->>ProverAPI: complete(lean_code)
    ProverAPI-->>Pipeline: proof
    Pipeline->>SpecGen: write_proof(proof)
    Pipeline->>GuardGen: emit_c(spec)
    GuardGen-->>Pipeline: guard_file
    Pipeline->>Attestation: bundle(spec, guardgen)
    Attestation-->>Pipeline: bundle
    Pipeline-->>CLI: bundle
    CLI-->>User: Success message
```

## Detailed Component Design

### ProofPipeline

The main orchestrator that coordinates all components:

```python
class ProofPipeline:
    def __init__(self, env, spec, api_key):
        self.env = env
        self.spec = spec
        self.prover = ProverAPI(api_key)
        self.guardgen = GuardGen()
        self.attestation = Attestation()

    def run(self) -> Bundle:
        # 1. Generate Lean specification
        lean_file = self.spec.emit_lean()

        # 2. Generate proof
        proof = self.prover.complete(lean_file)
        self.spec.write_proof(proof)

        # 3. Generate guard code
        guard_file = self.guardgen.emit_c(self.spec)

        # 4. Create compliance bundle
        bundle = self.attestation.bundle(self.spec, self.guardgen)
        return bundle
```

### SpecGen

Converts Python safety specifications to Lean4 code:

```mermaid
graph TD
    A[Safety Spec] --> B[Template Engine]
    B --> C[Lean4 Code]
    C --> D[File Output]

    subgraph "Templates"
        E[Invariant Template]
        F[Guard Template]
        G[Lemma Template]
    end

    B --> E
    B --> F
    B --> G

    style A fill:#e3f2fd
    style C fill:#f1f8e9
```

### ProverAPI

Integrates with Fireworks DeepSeek-Prover for proof completion:

```mermaid
graph LR
    A[Lean Code] --> B[API Client]
    B --> C[Fireworks API]
    C --> D[DeepSeek-Prover]
    D --> E[Proof]
    E --> F[File Write]

    style C fill:#fff8e1
    style D fill:#fce4ec
```

### GuardGen

Generates runtime safety guards in C/C++:

```mermaid
graph TD
    A[Safety Spec] --> B[Guard Generator]
    B --> C[C Code]
    C --> D[Compilation]
    D --> E[Binary]

    subgraph "Guard Types"
        F[State Guards]
        G[Action Guards]
        H[Transition Guards]
    end

    B --> F
    B --> G
    B --> H

    style C fill:#e8f5e8
    style E fill:#f3e5f5
```

### Attestation

Creates comprehensive compliance artifacts:

```mermaid
graph LR
    A[Spec + Guards] --> B[HTML Generator]
    A --> C[SBOM Generator]
    A --> D[PDF Generator]
    A --> E[Hash Generator]

    B --> F[attestation.html]
    C --> G[sbom.spdx.json]
    D --> H[attestation.pdf]
    E --> I[lean_project.sha256]

    style F fill:#e8f5e8
    style G fill:#fff3e0
    style H fill:#f3e5f5
    style I fill:#fce4ec
```

## Multi-Algorithm Support

### Algorithm Adapter Pattern

```mermaid
graph TB
    subgraph "Algorithm Layer"
        A[PPO Adapter]
        B[SAC Adapter]
        C[DDPG Adapter]
    end

    subgraph "Safety Layer"
        D[Action Masking]
        E[Reward Shaping]
        F[State Validation]
    end

    subgraph "Specification Layer"
        G[PPO Spec Template]
        H[SAC Spec Template]
        I[DDPG Spec Template]
    end

    A --> D
    B --> E
    C --> F

    A --> G
    B --> H
    C --> I

    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
```

### Algorithm-Specific Lean Templates

Each algorithm has its own Lean4 template that references the appropriate policy:

```lean
-- PPO Template
theorem safe_ppo_policy : ∀ σ, invariant σ → safe_action (ppo_policy σ)

-- SAC Template
theorem safe_sac_policy : ∀ σ, invariant σ → safe_action (sac_policy σ)

-- DDPG Template
theorem safe_ddpg_policy : ∀ σ, invariant σ → safe_action (ddpg_policy σ)
```

## CLI Architecture

### Command Structure

```mermaid
graph TD
    A[proofstack] --> B[init]
    A --> C[train]
    A --> D[bundle]
    A --> E[version]

    B --> F[Project Template]
    C --> G[RL Training]
    D --> H[Proof Pipeline]

    F --> I[env.py]
    F --> J[safety_spec.yaml]
    F --> K[README.md]

    G --> L[Stable-Baselines3]
    G --> M[Algorithm Selection]

    H --> N[SpecGen]
    H --> O[ProverAPI]
    H --> P[GuardGen]
    H --> Q[Attestation]

    style A fill:#fff3e0
    style H fill:#e8f5e8
```

### Async Streaming Architecture

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant ProverAPI
    participant Fireworks

    User->>CLI: proofstack bundle --watch
    CLI->>ProverAPI: stream(lean_file)
    ProverAPI->>Fireworks: POST /chat/completions
    Fireworks-->>ProverAPI: SSE stream
    loop Stream Processing
        ProverAPI-->>CLI: "🤖 Analyzing..."
        CLI-->>User: Progress update
    end
    ProverAPI-->>CLI: "✅ Complete"
    CLI-->>User: Success
```

## REST API Architecture

### API Endpoints

```mermaid
graph LR
    A[FastAPI Server] --> B[/init]
    A --> C[/train]
    A --> D[/bundle]
    A --> E[/spec]
    A --> F[/bundle/{id}]

    B --> G[Project Creation]
    C --> H[RL Training]
    D --> I[Proof Generation]
    E --> J[Spec Management]
    F --> K[Artifact Download]

    style A fill:#e3f2fd
    style I fill:#e8f5e8
```

### Request/Response Flow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant CLI
    participant Pipeline

    Client->>FastAPI: POST /bundle
    FastAPI->>CLI: bundle(spec_file, mock)
    CLI->>Pipeline: run()
    Pipeline-->>CLI: bundle
    CLI-->>FastAPI: response
    FastAPI-->>Client: JSON response
```

## Security Architecture

### API Key Management

```mermaid
graph TD
    A[Environment Variable] --> B[CLI Validation]
    B --> C[ProverAPI Client]
    C --> D[Fireworks API]

    E[Mock Mode] --> F[Offline Testing]

    style A fill:#fff3e0
    style E fill:#e8f5e8
```

### Artifact Integrity

```mermaid
graph LR
    A[Lean Project] --> B[SHA256 Hash]
    B --> C[Attestation]
    C --> D[Compliance Bundle]

    E[Guard Code] --> F[Compiled Hash]
    F --> C

    style B fill:#fce4ec
    style D fill:#e8f5e8
```

## Deployment Architecture

### CI/CD Pipeline

```mermaid
graph TB
    A[Git Push] --> B[GitHub Actions]
    B --> C[Static Analysis]
    B --> D[Unit Tests]
    B --> E[Integration Tests]
    B --> F[Docker Build]
    B --> G[Documentation Build]

    C --> H[ruff]
    C --> I[mypy]
    D --> J[pytest]
    E --> K[CLI Smoke Test]
    F --> L[Container Image]
    G --> M[mkdocs]

    style B fill:#e3f2fd
    style L fill:#e8f5e8
```

### Docker Architecture

```mermaid
graph TD
    A[Base Image] --> B[Python Runtime]
    B --> C[SafeRL ProofStack]
    C --> D[Lean4]
    D --> E[Proof Environment]

    F[CI Image] --> G[Testing Tools]
    G --> H[Coverage]
    H --> I[Quality Gates]

    style E fill:#e8f5e8
    style I fill:#fff3e0
```

## Performance Considerations

### Caching Strategy

```mermaid
graph LR
    A[Lean Proofs] --> B[Local Cache]
    B --> C[Reuse Valid Proofs]

    D[API Calls] --> E[Rate Limiting]
    E --> F[Fallback Proofs]

    style B fill:#e8f5e8
    style F fill:#fff3e0
```

### Scalability

- **Horizontal scaling** via REST API
- **Async processing** for proof generation
- **Caching** for repeated specifications
- **Mock mode** for offline development

## Future Architecture

### Planned Enhancements

```mermaid
graph TB
    A[Current] --> B[H-4: Lean Tactics]
    B --> C[H-5: Compliance Mapping]
    C --> D[H-6: Runtime Hardening]
    D --> E[H-7: Observability]
    E --> F[H-8: Release Engineering]
    F --> G[H-9: Ecosystem]

    style A fill:#e8f5e8
    style G fill:#f3e5f5
```

This architecture provides a solid foundation for safe, scalable, and maintainable RL safety proofs with formal verification.
