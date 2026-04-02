from pathlib import Path

import pytest

from proofstack.errors import ValidationError
from proofstack.specgen import SpecGen


def test_emit_lean_contains_proof_placeholder_token():
    spec = SpecGen()
    spec.invariants = ["|σ.cart_position| ≤ 2.4"]
    spec.guard = ["|a.force| ≤ 10.0"]
    spec.lemmas = ["position_step_bound"]
    lean_file_path = spec.emit_lean()
    content = Path(lean_file_path).read_text(encoding="utf-8")
    assert "__PROOF_PLACEHOLDER__" in content
    assert "sorry" not in content


def test_write_proof_replaces_placeholder():
    spec = SpecGen()
    lean_file_path = spec.emit_lean()
    spec.write_proof("by simp")
    content = Path(lean_file_path).read_text(encoding="utf-8")
    assert "__PROOF_PLACEHOLDER__" not in content
    assert "by simp" in content


def test_write_proof_requires_placeholder():
    spec = SpecGen()
    lean_file_path = spec.emit_lean()
    Path(lean_file_path).write_text("theorem x : True := by trivial", encoding="utf-8")
    with pytest.raises(ValidationError):
        spec.write_proof("by trivial")
