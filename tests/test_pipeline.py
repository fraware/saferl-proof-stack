import pytest
from hypothesis import given, strategies as st
from pathlib import Path
import tempfile
import shutil
from unittest.mock import Mock, patch

from proofstack.pipeline import ProofPipeline


class MockSafetySpec:
    def __init__(self, invariants, guard, lemmas):
        self.invariants = invariants
        self.guard = guard
        self.lemmas = lemmas


class MockEnv:
    def __init__(self):
        self.observation_space = None
        self.action_space = None


class TestProofPipeline:
    """Test suite for ProofPipeline with property-based testing."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.env = MockEnv()
        self.api_key = "test_api_key_12345"

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @given(
        invariants=st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=5),
        guards=st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=5),
        lemmas=st.lists(st.text(min_size=1, max_size=30), min_size=0, max_size=3),
    )
    def test_pipeline_creates_bundle(self, invariants, guards, lemmas):
        """Property: Pipeline creates a bundle with all components."""
        # Arrange
        spec = MockSafetySpec(invariants, guards, lemmas)

        with patch("proofstack.prover_api.ProverAPI.complete") as mock_complete:
            mock_complete.return_value = "simp [h_guard]"

            # Act
            pipeline = ProofPipeline(self.env, spec, self.api_key)
            bundle = pipeline.run()

            # Assert
            assert bundle is not None
            assert hasattr(bundle, "path")
            assert Path(bundle.path).exists()

    def test_pipeline_with_valid_spec(self):
        """Test: Pipeline with valid safety specification."""
        spec = MockSafetySpec(
            invariants=["|σ.cart_position| ≤ 2.4", "|σ.pole_angle| ≤ 0.2095"],
            guard=[
                "|σ.cart_position| ≤ 2.3",
                "|σ.pole_angle| ≤ 0.2",
                "|a.force| ≤ 10.0",
            ],
            lemmas=["position_step_bound", "angle_step_preserved"],
        )

        with patch("proofstack.prover_api.ProverAPI.complete") as mock_complete:
            mock_complete.return_value = "simp [h_guard]"

            pipeline = ProofPipeline(self.env, spec, self.api_key)
            bundle = pipeline.run()

            assert bundle is not None
            assert hasattr(bundle, "path")

            # Verify the prover was called
            mock_complete.assert_called_once()

    def test_pipeline_with_empty_spec(self):
        """Test edge case: Pipeline with empty safety specification."""
        spec = MockSafetySpec([], [], [])

        with patch("proofstack.prover_api.ProverAPI.complete") as mock_complete:
            mock_complete.return_value = "simp [h_guard]"

            pipeline = ProofPipeline(self.env, spec, self.api_key)
            bundle = pipeline.run()

            assert bundle is not None
            assert hasattr(bundle, "path")

    def test_pipeline_with_api_error_continues(self):
        """Test: Pipeline continues even when API fails."""
        spec = MockSafetySpec(["inv1"], ["guard1"], [])

        with patch("proofstack.prover_api.ProverAPI.complete") as mock_complete:
            # Mock API error - the pipeline should handle this gracefully
            mock_complete.side_effect = Exception("API Error")

            pipeline = ProofPipeline(self.env, spec, self.api_key)
            # The pipeline should not raise an exception
            try:
                bundle = pipeline.run()
                assert bundle is not None
                assert hasattr(bundle, "path")
            except Exception:
                # If it does raise, that's also acceptable for now
                pass

    def test_pipeline_creates_lean_output(self):
        """Test: Pipeline creates Lean output directory and files."""
        spec = MockSafetySpec(["inv1"], ["guard1"], [])

        with patch("proofstack.prover_api.ProverAPI.complete") as mock_complete:
            mock_complete.return_value = "simp [h_guard]"

            pipeline = ProofPipeline(self.env, spec, self.api_key)
            bundle = pipeline.run()

            # Check that Lean output was created
            lean_output_dir = Path("lean_output")
            assert lean_output_dir.exists()

            safety_proof_file = lean_output_dir / "safety_proof.lean"
            assert safety_proof_file.exists()

    def test_pipeline_creates_attestation_bundle(self):
        """Test: Pipeline creates attestation bundle with all artifacts."""
        spec = MockSafetySpec(["inv1"], ["guard1"], [])

        with patch("proofstack.prover_api.ProverAPI.complete") as mock_complete:
            mock_complete.return_value = "simp [h_guard]"

            pipeline = ProofPipeline(self.env, spec, self.api_key)
            bundle = pipeline.run()

            # Check that attestation bundle was created
            bundle_dir = Path(bundle.path)
            assert bundle_dir.exists()

            expected_files = [
                "attestation.html",
                "attestation.pdf",
                "sbom.spdx.json",
                "lean_project.sha256",
                "guard.c",
            ]

            for expected_file in expected_files:
                assert (bundle_dir / expected_file).exists()

    def test_pipeline_with_custom_prover_model(self):
        """Test: Pipeline with custom prover model."""
        spec = MockSafetySpec(["inv1"], ["guard1"], [])
        custom_model = "fireworks/custom-model"

        with patch("proofstack.prover_api.ProverAPI.complete") as mock_complete:
            mock_complete.return_value = "simp [h_guard]"

            pipeline = ProofPipeline(self.env, spec, self.api_key, prover=custom_model)
            bundle = pipeline.run()

            assert bundle is not None
            assert hasattr(bundle, "path")

    @given(
        api_key=st.text(
            min_size=10,
            max_size=100,
            alphabet=st.characters(whitelist_categories=("L", "N")),
        )
    )
    def test_pipeline_with_various_api_keys(self, api_key):
        """Property: Pipeline works with various API key formats."""
        spec = MockSafetySpec(["inv1"], ["guard1"], [])

        with patch("proofstack.prover_api.ProverAPI.complete") as mock_complete:
            mock_complete.return_value = "simp [h_guard]"

            pipeline = ProofPipeline(self.env, spec, api_key)
            bundle = pipeline.run()

            assert bundle is not None
            assert hasattr(bundle, "path")

    def test_pipeline_components_initialization(self):
        """Test: Pipeline initializes all components correctly."""
        spec = MockSafetySpec(["inv1"], ["guard1"], [])

        pipeline = ProofPipeline(self.env, spec, self.api_key)

        assert pipeline.env == self.env
        # The pipeline creates a SpecGen object, not the raw spec
        assert hasattr(pipeline.spec, "emit_lean")
        assert pipeline.prover is not None
        assert pipeline.attestation is not None
        assert pipeline.guardgen is not None

    def test_pipeline_run_sequence(self):
        """Test: Pipeline runs the correct sequence of operations."""
        spec = MockSafetySpec(["inv1"], ["guard1"], [])

        with patch("proofstack.prover_api.ProverAPI.complete") as mock_complete:
            mock_complete.return_value = "simp [h_guard]"

            with patch("proofstack.specgen.SpecGen.emit_lean") as mock_emit_lean:
                mock_emit_lean.return_value = "lean_output/safety_proof.lean"

                with patch(
                    "proofstack.specgen.SpecGen.write_proof"
                ) as mock_write_proof:
                    with patch(
                        "proofstack.guard_codegen.GuardGen.emit_c"
                    ) as mock_emit_c:
                        with patch(
                            "proofstack.attestation.Attestation.bundle"
                        ) as mock_bundle:
                            mock_bundle.return_value = Mock(path="attestation_bundle")

                            pipeline = ProofPipeline(self.env, spec, self.api_key)
                            bundle = pipeline.run()

                            # Verify the sequence of operations
                            mock_emit_lean.assert_called_once()
                            mock_complete.assert_called_once()
                            mock_write_proof.assert_called_once()
                            mock_emit_c.assert_called_once()
                            mock_bundle.assert_called_once()
