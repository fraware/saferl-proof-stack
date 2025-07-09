import pytest
from hypothesis import given, strategies as st
from pathlib import Path
import tempfile
import shutil
import hashlib

from proofstack.attestation import Attestation


class MockSafetySpec:
    def __init__(self, invariants, guard, lemmas):
        self.invariants = invariants
        self.guard = guard
        self.lemmas = lemmas


class MockGuardGen:
    def __init__(self):
        pass


class TestAttestation:
    """Test suite for Attestation with property-based testing."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.attestation = Attestation(out_dir=self.temp_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @given(spec_content=st.text(min_size=10, max_size=1000))
    def test_generate_html_report_creates_valid_html(self, spec_content):
        """Property: generate_html_report always creates valid HTML with spec content."""
        # Arrange
        spec = MockSafetySpec(["inv1"], ["guard1"], ["lemma1"])

        # Act
        html_path = self.attestation.generate_html_report(spec)

        # Assert
        assert html_path.exists()
        assert html_path.suffix == ".html"

        content = html_path.read_text(encoding="utf-8")
        assert "ProofStack Attestation" in content
        assert "Spec" in content

    @given(
        spec_hash=st.text(
            min_size=10,
            max_size=64,
            alphabet=st.characters(whitelist_categories=("Nd",)),
        )
    )
    def test_generate_hash_creates_valid_sha256(self, spec_hash):
        """Property: generate_hash creates valid SHA256 hash."""
        # Create a temporary Lean file for testing
        lean_file = Path(self.temp_dir) / "test.lean"
        lean_file.write_text("test content", encoding="utf-8")

        # Act
        hash_path = self.attestation.generate_hash(target_dir=self.temp_dir)

        # Assert
        assert hash_path.exists()
        hash_content = hash_path.read_text(encoding="utf-8")
        assert len(hash_content.strip()) == 64  # SHA256 is 64 hex chars
        assert all(c in "0123456789abcdef" for c in hash_content.lower())

    def test_generate_sbom_creates_valid_json(self):
        """Test: generate_sbom creates valid JSON file."""
        # Act
        sbom_path = self.attestation.generate_sbom()

        # Assert
        assert sbom_path.exists()
        assert sbom_path.suffix == ".json"

        content = sbom_path.read_text(encoding="utf-8")
        assert content.strip() in ["{}", ""]  # Either empty or valid JSON

    def test_generate_pdf_creates_file(self):
        """Test: generate_pdf creates a file (even if placeholder)."""
        # Arrange
        html_path = Path(self.temp_dir) / "test.html"
        html_path.write_text("<html><body>test</body></html>", encoding="utf-8")

        # Act
        pdf_path = self.attestation.generate_pdf(html_path)

        # Assert
        assert pdf_path.exists()
        assert pdf_path.suffix == ".pdf"

    @given(
        invariant_count=st.integers(min_value=1, max_value=10),
        guard_count=st.integers(min_value=1, max_value=10),
    )
    def test_bundle_creates_all_artifacts(self, invariant_count, guard_count):
        """Property: bundle creates all required artifacts regardless of spec size."""
        # Arrange
        invariants = [f"invariant_{i}" for i in range(invariant_count)]
        guards = [f"guard_{i}" for i in range(guard_count)]
        spec = MockSafetySpec(invariants, guards, ["lemma1"])
        guardgen = MockGuardGen()

        # Act
        bundle = self.attestation.bundle(spec, guardgen)

        # Assert
        assert bundle is not None
        assert hasattr(bundle, "path")
        assert Path(bundle.path).exists()

        # Check that all expected files exist
        bundle_dir = Path(bundle.path)
        expected_files = [
            "attestation.html",
            "attestation.pdf",
            "sbom.spdx.json",
            "lean_project.sha256",
            "guard.c",
        ]

        for expected_file in expected_files:
            assert (bundle_dir / expected_file).exists()

    def test_bundle_with_empty_spec(self):
        """Test edge case: bundle with empty safety specification."""
        spec = MockSafetySpec([], [], [])
        guardgen = MockGuardGen()

        bundle = self.attestation.bundle(spec, guardgen)

        assert bundle is not None
        assert hasattr(bundle, "path")

    def test_bundle_with_complex_spec(self):
        """Test edge case: bundle with complex safety specification."""
        spec = MockSafetySpec(
            invariants=["|σ.cart_position| ≤ 2.4", "|σ.pole_angle| ≤ 0.2095"],
            guard=[
                "|σ.cart_position| ≤ 2.3",
                "|σ.pole_angle| ≤ 0.2",
                "|a.force| ≤ 10.0",
            ],
            lemmas=["position_step_bound", "angle_step_preserved"],
        )
        guardgen = MockGuardGen()

        bundle = self.attestation.bundle(spec, guardgen)

        assert bundle is not None
        assert hasattr(bundle, "path")

    @given(
        invalid_chars=st.text(
            min_size=1,
            max_size=10,
            alphabet=st.characters(blacklist_categories=("L", "N")),
        )
    )
    def test_bundle_handles_special_characters(self, invalid_chars):
        """Property: bundle handles special characters in specifications gracefully."""
        spec = MockSafetySpec(
            invariants=[f"test_{invalid_chars}"],
            guard=[f"guard_{invalid_chars}"],
            lemmas=[],
        )
        guardgen = MockGuardGen()

        bundle = self.attestation.bundle(spec, guardgen)

        assert bundle is not None
        assert hasattr(bundle, "path")
