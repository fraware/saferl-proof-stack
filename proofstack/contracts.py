"""Strongly typed input contracts for ProofStack runtime."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .errors import ValidationError

SUPPORTED_ALGORITHMS = {"ppo", "sac", "ddpg"}


@dataclass(frozen=True)
class SafetySpecInput:
    """Validated safety specification contract."""

    environment: str
    invariants: list[str]
    guard: list[str]
    lemmas: list[str]

    def set_algorithm(self, algorithm_name: str) -> None:
        """Compatibility method for existing callers."""
        if algorithm_name not in SUPPORTED_ALGORITHMS:
            raise ValidationError(f"Unsupported algorithm: {algorithm_name}")


def _ensure_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValidationError(f"Field '{field_name}' must be a list of strings.")
    return value


def load_safety_spec(path: Path) -> SafetySpecInput:
    """Load and validate safety spec YAML from path."""
    if not path.exists():
        raise ValidationError(f"Specification file not found: {path}")

    with path.open("r", encoding="utf-8") as spec_file:
        payload = yaml.safe_load(spec_file) or {}

    if not isinstance(payload, dict):
        raise ValidationError("Specification payload must be a mapping.")

    environment = payload.get("environment", "unknown")
    if not isinstance(environment, str) or not environment.strip():
        raise ValidationError("Field 'environment' must be a non-empty string.")

    return SafetySpecInput(
        environment=environment,
        invariants=_ensure_string_list(payload.get("invariants", []), "invariants"),
        guard=_ensure_string_list(payload.get("guard", []), "guard"),
        lemmas=_ensure_string_list(payload.get("lemmas", []), "lemmas"),
    )
