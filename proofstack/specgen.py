"""Lean4 specification generation for SafeRL ProofStack."""

from pathlib import Path
from typing import Optional

from .errors import ValidationError


class SpecGen:
    """Generate Lean4 specifications from Python safety constraints."""

    def __init__(self):
        """Initialize the specification generator."""
        self.invariants: list[str] = []
        self.guard: list[str] = []
        self.lemmas: list[str] = []
        self.lean_file_path: Optional[Path] = None
        self.algorithm_name: str = "ppo"  # Default algorithm
        self._proof_placeholder = "__PROOF_PLACEHOLDER__"

    def set_algorithm(self, algorithm_name: str) -> None:
        """Set the algorithm name for template generation.

        Args:
            algorithm_name: Name of the algorithm ('ppo', 'sac', 'ddpg')
        """
        self.algorithm_name = algorithm_name

    def emit_lean(self, algorithm_name: Optional[str] = None) -> str:
        """Generate Lean4 specification file.

        Args:
            algorithm_name: Optional algorithm name override

        Returns:
            Path to the generated Lean file
        """
        if algorithm_name:
            self.algorithm_name = algorithm_name

        # Create lean_output directory
        lean_dir = Path("lean_output")
        lean_dir.mkdir(exist_ok=True)

        # Generate Lean content
        lean_content = self._generate_lean_content()

        # Write to file
        self.lean_file_path = lean_dir / "safety_proof.lean"
        with open(self.lean_file_path, "w", encoding="utf-8") as f:
            f.write(lean_content)

        return str(self.lean_file_path)

    def write_proof(self, proof: str) -> None:
        """Write proof to the Lean file.

        Args:
            proof: Proof content to write
        """
        if not self.lean_file_path or not self.lean_file_path.exists():
            raise ValueError("Lean file not generated. Call emit_lean() first.")

        # Read current content
        with open(self.lean_file_path, encoding="utf-8") as f:
            content = f.read()

        # Replace explicit proof placeholder token with generated proof.
        if self._proof_placeholder in content:
            content = content.replace(self._proof_placeholder, proof)
        else:
            raise ValidationError("Proof placeholder token missing from generated Lean file.")

        # Write back
        with open(self.lean_file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _generate_lean_content(self) -> str:
        """Generate the complete Lean4 specification content."""

        # Algorithm-specific template
        algorithm_template = self._get_algorithm_template()

        # Generate invariants
        invariants_text = self._generate_invariants()

        # Generate guards
        guards_text = self._generate_guards()

        # Generate lemmas
        lemmas_text = self._generate_lemmas()

        # Complete Lean file
        lean_content = f"""-- SafeRL ProofStack: {self.algorithm_name.upper()} Safety Specification
-- Generated automatically from Python safety constraints

import Mathlib.Data.Real.Basic
import Mathlib.Analysis.NormedSpace.Basic

-- State representation
structure State where
  cart_position : ℝ
  cart_velocity : ℝ
  pole_angle : ℝ
  pole_angular_velocity : ℝ

-- Action representation
structure Action where
  force : ℝ

-- Policy function type
def Policy := State → Action

-- Safety invariants (must always hold)
{invariants_text}

-- Guard conditions (checked before actions)
{guards_text}

-- Safety lemmas for proof generation
{lemmas_text}

-- Main safety theorem for {self.algorithm_name.upper()}
{algorithm_template}

-- Helper definitions
def safe_action (a : Action) : Prop :=
  |a.force| ≤ 10.0

def invariant (σ : State) : Prop :=
  |σ.cart_position| ≤ 2.4 ∧
  |σ.pole_angle| ≤ 0.2095

-- Proof placeholder
theorem safety_proof : ∀ σ, invariant σ → safe_action (safe_{self.algorithm_name}_policy σ) := by
  by
    exact {self._proof_placeholder}
"""

        return lean_content

    def _get_algorithm_template(self) -> str:
        """Get algorithm-specific Lean template."""
        templates = {
            "ppo": """-- PPO-specific safety theorem
axiom ppo_policy : Policy
theorem safe_ppo_policy : ∀ σ, invariant σ → safe_action (ppo_policy σ) := by
  intro σ h_invariant
  exact __PROOF_PLACEHOLDER__""",
            "sac": """-- SAC-specific safety theorem
axiom sac_policy : Policy
theorem safe_sac_policy : ∀ σ, invariant σ → safe_action (sac_policy σ) := by
  intro σ h_invariant
  exact __PROOF_PLACEHOLDER__""",
            "ddpg": """-- DDPG-specific safety theorem
axiom ddpg_policy : Policy
theorem safe_ddpg_policy : ∀ σ, invariant σ → safe_action (ddpg_policy σ) := by
  intro σ h_invariant
  exact __PROOF_PLACEHOLDER__""",
        }

        return templates.get(self.algorithm_name, templates["ppo"])

    def _generate_invariants(self) -> str:
        """Generate Lean invariants from Python constraints."""
        if not self.invariants:
            return """-- Default invariants
def default_invariant (σ : State) : Prop :=
  |σ.cart_position| ≤ 2.4 ∧
  |σ.pole_angle| ≤ 0.2095"""

        invariant_lines = []
        for inv in self.invariants:
            # Convert Python notation to Lean
            lean_inv = self._convert_to_lean(inv)
            invariant_lines.append(f"  {lean_inv}")

        return "\n".join(invariant_lines)

    def _generate_guards(self) -> str:
        """Generate Lean guards from Python constraints."""
        if not self.guard:
            return """-- Default guards
def default_guard (σ : State) (a : Action) : Prop :=
  |σ.cart_position| ≤ 2.3 ∧
  |σ.pole_angle| ≤ 0.2 ∧
  |a.force| ≤ 10.0"""

        guard_lines = []
        for guard in self.guard:
            # Convert Python notation to Lean
            lean_guard = self._convert_to_lean(guard)
            guard_lines.append(f"  {lean_guard}")

        return "\n".join(guard_lines)

    def _generate_lemmas(self) -> str:
        """Generate Lean lemmas from Python constraints."""
        if not self.lemmas:
            return """-- Default lemmas
lemma position_step_bound : ∀ σ, invariant σ → |σ.cart_position| ≤ 2.4 := by
  intro σ h_inv
  exact h_inv.left

lemma angle_step_preserved : ∀ σ, invariant σ → |σ.pole_angle| ≤ 0.2095 := by
  intro σ h_inv
  exact h_inv.right"""

        lemma_lines = []
        for lemma in self.lemmas:
            lemma_lines.append(
                f"""lemma {lemma} : ∀ σ σ', step σ σ' → {lemma}_property σ σ' := by
  intro σ σ' h_step
  exact {self._proof_placeholder}"""
            )

        return "\n".join(lemma_lines)

    def _convert_to_lean(self, constraint: str) -> str:
        """Convert Python constraint notation to Lean syntax."""
        # Replace common patterns
        lean_constraint = constraint

        # Replace sigma notation
        lean_constraint = lean_constraint.replace("σ.", "σ.")
        lean_constraint = lean_constraint.replace("a.", "a.")

        # Replace mathematical symbols
        lean_constraint = lean_constraint.replace("≤", "≤")
        lean_constraint = lean_constraint.replace("≥", "≥")
        lean_constraint = lean_constraint.replace("∈", "∈")
        lean_constraint = lean_constraint.replace("|", "|")

        # Replace variable names
        lean_constraint = lean_constraint.replace("cart_position", "cart_position")
        lean_constraint = lean_constraint.replace("pole_angle", "pole_angle")
        lean_constraint = lean_constraint.replace("force", "force")

        return lean_constraint
