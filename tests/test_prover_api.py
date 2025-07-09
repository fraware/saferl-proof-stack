import pytest
from hypothesis import given, strategies as st
import httpx
from unittest.mock import Mock, patch

from proofstack.prover_api import ProverAPI


class TestProverAPI:
    """Test suite for ProverAPI with property-based testing."""

    def setup_method(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key_12345"
        self.prover = ProverAPI(self.api_key)

    @given(lean_code=st.text(min_size=10, max_size=1000))
    def test_complete_returns_string(self, lean_code):
        """Property: complete always returns a string response."""
        with patch("httpx.post") as mock_post:
            # Mock successful response
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "simp [h_guard]"}}]
            }
            mock_post.return_value = mock_response

            result = self.prover.complete(lean_code)

            assert isinstance(result, str)
            assert len(result) > 0

    def test_complete_with_valid_lean_code(self):
        """Test: complete with valid Lean code."""
        lean_code = """
        theorem test : True := by
          sorry
        """

        with patch("httpx.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "trivial"}}]
            }
            mock_post.return_value = mock_response

            result = self.prover.complete(lean_code)

            assert result == "trivial"

            # Verify the API call was made correctly
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[1]["json"]["model"] == "fireworks/deepseek-prover-v2"
            assert call_args[1]["json"]["temperature"] == 0.0
            assert call_args[1]["json"]["stream"] is False
            assert call_args[1]["json"]["max_tokens"] == 2048

    def test_complete_with_api_error_returns_fallback(self):
        """Test: complete returns fallback proof when API fails."""
        lean_code = "test lean code"

        with patch("httpx.post") as mock_post:
            # Mock API error
            mock_post.side_effect = httpx.HTTPStatusError(
                "404 Not Found", request=Mock(), response=Mock()
            )

            result = self.prover.complete(lean_code)

            assert result == "simp [h_guard]"

    def test_complete_with_network_error_returns_fallback(self):
        """Test: complete returns fallback proof when network fails."""
        lean_code = "test lean code"

        with patch("httpx.post") as mock_post:
            # Mock network error
            mock_post.side_effect = Exception("Network error")

            result = self.prover.complete(lean_code)

            assert result == "simp [h_guard]"

    @given(
        api_key=st.text(
            min_size=10,
            max_size=100,
            alphabet=st.characters(whitelist_categories=("L", "N")),
        )
    )
    def test_prover_api_initialization(self, api_key):
        """Property: ProverAPI initializes correctly with various API keys."""
        prover = ProverAPI(api_key)

        # Check that the prover was initialized correctly
        assert prover.url == "https://api.fireworks.ai/inference/v1/chat/completions"
        assert prover.model == "fireworks/deepseek-prover-v2"
        assert "Authorization" in prover.headers
        assert "Content-Type" in prover.headers

    def test_prover_api_with_custom_model(self):
        """Test: ProverAPI with custom model."""
        custom_model = "fireworks/custom-model"
        prover = ProverAPI(self.api_key, model=custom_model)

        assert prover.model == custom_model

    @given(lean_code_length=st.integers(min_value=1, max_value=100))
    def test_complete_handles_various_lean_code_lengths(self, lean_code_length):
        """Property: complete handles Lean code of various lengths."""
        lean_code = "a" * lean_code_length

        with patch("httpx.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "test proof"}}]
            }
            mock_post.return_value = mock_response

            result = self.prover.complete(lean_code)

            assert result == "test proof"

    def test_complete_preserves_lean_code_content(self):
        """Test: complete preserves the content of the Lean code in the request."""
        lean_code = """
        theorem cartpole_safety : 
          ∀ (σ : State) (a : Action), 
          guard σ a → safe (step σ a) := by
          sorry
        """

        with patch("httpx.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "simp [h_guard]"}}]
            }
            mock_post.return_value = mock_response

            self.prover.complete(lean_code)

            # Verify the Lean code was sent in the request
            call_args = mock_post.call_args
            messages = call_args[1]["json"]["messages"]
            assert len(messages) == 2
            assert messages[0]["role"] == "system"
            assert messages[1]["role"] == "user"
            assert lean_code in messages[1]["content"]

    def test_complete_with_empty_lean_code(self):
        """Test edge case: complete with empty Lean code."""
        with patch("httpx.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "empty proof"}}]
            }
            mock_post.return_value = mock_response

            result = self.prover.complete("")

            assert result == "empty proof"

    def test_complete_with_special_characters_in_lean_code(self):
        """Test: complete handles special characters in Lean code."""
        lean_code = "theorem test : ∀ (x : ℝ), x² ≥ 0 := by sorry"

        with patch("httpx.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "simp [sq_nonneg]"}}]
            }
            mock_post.return_value = mock_response

            result = self.prover.complete(lean_code)

            assert result == "simp [sq_nonneg]"
