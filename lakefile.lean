import Lake
open Lake DSL

/-- Reservoir-oriented metadata (description, homepage, SPDX license) is documented in README.md and pyproject.toml.
    The Lake build bundled with Lean v4.7.0 rejects `description` / `homepage` / etc. on `package` (not in `Lake.PackageConfig`). -/
package proofstack

@[default_target]
lean_lib Proofstack

require mathlib from git "https://github.com/leanprover-community/mathlib4.git" @ "v4.7.0"
