import pytest
from hypothesis import given, strategies as st
from pathlib import Path
import tempfile
import shutil
import json
import hashlib
from unittest.mock import patch, mock_open

from proofstack.cache import ProofCache


class TestProofCache:
    """Test suite for ProofCache with comprehensive mutation detection."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = Path(self.temp_dir) / ".proofstack_cache"
        self.cache = ProofCache(self.cache_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cache_initialization(self):
        """Test: Cache initializes correctly with custom directory."""
        assert self.cache.cache_dir == self.cache_dir
        assert self.cache.cache_dir.exists()

    def test_cache_key_generation(self):
        """Test: Cache key generation is deterministic and unique."""
        spec_sha256 = "abc123"
        algo = "ppo"
        mathlib_commit = "def456"

        key1 = self.cache._cache_key(spec_sha256, algo, mathlib_commit)
        key2 = self.cache._cache_key(spec_sha256, algo, mathlib_commit)

        assert key1 == key2
        assert key1 == "abc123_ppo_def456"

    def test_cache_path_generation(self):
        """Test: Cache path generation creates correct file paths."""
        key = "test_key"
        expected_path = self.cache_dir / "test_key.json"

        assert self.cache._cache_path(key) == expected_path

    def test_cache_set_and_get(self):
        """Test: Basic cache set and get functionality."""
        spec_sha256 = "abc123"
        algo = "ppo"
        mathlib_commit = "def456"
        proof_sketch = {"tactic": "simp", "lemmas": ["h1", "h2"]}

        # Set cache
        self.cache.set(spec_sha256, algo, mathlib_commit, proof_sketch)

        # Get cache
        result = self.cache.get(spec_sha256, algo, mathlib_commit)

        assert result == proof_sketch

    def test_cache_miss_returns_none(self):
        """Test: Cache miss returns None."""
        result = self.cache.get("nonexistent", "ppo", "def456")
        assert result is None

    def test_cache_clear(self):
        """Test: Cache clear removes all cached files."""
        # Add some test data
        self.cache.set("abc123", "ppo", "def456", {"test": "data"})
        self.cache.set("xyz789", "sac", "ghi012", {"test2": "data2"})

        # Verify files exist
        assert len(list(self.cache.cache_dir.glob("*.json"))) == 2

        # Clear cache
        self.cache.clear()

        # Verify files are gone
        assert len(list(self.cache.cache_dir.glob("*.json"))) == 0

    def test_compute_spec_sha256(self):
        """Test: SHA256 computation is deterministic."""
        spec1 = "test specification"
        spec2 = "test specification"
        spec3 = "different specification"

        hash1 = ProofCache.compute_spec_sha256(spec1)
        hash2 = ProofCache.compute_spec_sha256(spec2)
        hash3 = ProofCache.compute_spec_sha256(spec3)

        assert hash1 == hash2
        assert hash1 != hash3
        assert len(hash1) == 64  # SHA256 hex length

    @given(
        spec=st.text(min_size=1, max_size=100),
        algo=st.text(min_size=1, max_size=20),
        mathlib_commit=st.text(min_size=1, max_size=40),
    )
    def test_cache_with_various_inputs(self, spec, algo, mathlib_commit):
        """Property: Cache works with various input combinations."""
        spec_sha256 = ProofCache.compute_spec_sha256(spec)
        proof_sketch = {"tactic": "simp", "spec": spec}

        # Set and get
        self.cache.set(spec_sha256, algo, mathlib_commit, proof_sketch)
        result = self.cache.get(spec_sha256, algo, mathlib_commit)

        assert result == proof_sketch

    def test_cache_mutation_detection(self):
        """Test: Cache correctly detects spec mutations."""
        # Original spec
        original_spec = "cart_position <= 2.4"
        original_hash = ProofCache.compute_spec_sha256(original_spec)

        # Mutated spec
        mutated_spec = "cart_position <= 2.5"
        mutated_hash = ProofCache.compute_spec_sha256(mutated_spec)

        # Verify hashes are different
        assert original_hash != mutated_hash

        # Cache original
        original_proof = {"tactic": "simp", "spec": original_spec}
        self.cache.set(original_hash, "ppo", "def456", original_proof)

        # Try to get with mutated spec - should miss
        result = self.cache.get(mutated_hash, "ppo", "def456")
        assert result is None

        # Original should still be cached
        result = self.cache.get(original_hash, "ppo", "def456")
        assert result == original_proof

    def test_cache_algorithm_isolation(self):
        """Test: Cache isolates different algorithms."""
        spec_sha256 = "abc123"
        mathlib_commit = "def456"

        ppo_proof = {"tactic": "simp", "algo": "ppo"}
        sac_proof = {"tactic": "rw", "algo": "sac"}

        # Cache both algorithms
        self.cache.set(spec_sha256, "ppo", mathlib_commit, ppo_proof)
        self.cache.set(spec_sha256, "sac", mathlib_commit, sac_proof)

        # Verify isolation
        assert self.cache.get(spec_sha256, "ppo", mathlib_commit) == ppo_proof
        assert self.cache.get(spec_sha256, "sac", mathlib_commit) == sac_proof

    def test_cache_mathlib_commit_isolation(self):
        """Test: Cache isolates different mathlib commits."""
        spec_sha256 = "abc123"
        algo = "ppo"

        commit1_proof = {"tactic": "simp", "commit": "def456"}
        commit2_proof = {"tactic": "rw", "commit": "ghi789"}

        # Cache both commits
        self.cache.set(spec_sha256, algo, "def456", commit1_proof)
        self.cache.set(spec_sha256, algo, "ghi789", commit2_proof)

        # Verify isolation
        assert self.cache.get(spec_sha256, algo, "def456") == commit1_proof
        assert self.cache.get(spec_sha256, algo, "ghi789") == commit2_proof

    def test_cache_file_persistence(self):
        """Test: Cache files persist correctly on disk."""
        spec_sha256 = "abc123"
        algo = "ppo"
        mathlib_commit = "def456"
        proof_sketch = {"tactic": "simp", "data": "test"}

        # Set cache
        self.cache.set(spec_sha256, algo, mathlib_commit, proof_sketch)

        # Verify file exists
        cache_file = self.cache._cache_path(
            self.cache._cache_key(spec_sha256, algo, mathlib_commit)
        )
        assert cache_file.exists()

        # Read file directly
        with open(cache_file, "r", encoding="utf-8") as f:
            stored_data = json.load(f)

        assert stored_data == proof_sketch

    def test_cache_json_serialization(self):
        """Test: Cache handles complex JSON data correctly."""
        spec_sha256 = "abc123"
        algo = "ppo"
        mathlib_commit = "def456"

        complex_proof = {
            "tactic": "simp",
            "lemmas": ["h1", "h2", "h3"],
            "nested": {"key": "value", "array": [1, 2, 3]},
            "boolean": True,
            "null": None,
        }

        # Set and get complex data
        self.cache.set(spec_sha256, algo, mathlib_commit, complex_proof)
        result = self.cache.get(spec_sha256, algo, mathlib_commit)

        assert result == complex_proof

    def test_cache_unicode_handling(self):
        """Test: Cache handles Unicode characters correctly."""
        spec_sha256 = "abc123"
        algo = "ppo"
        mathlib_commit = "def456"

        unicode_proof = {
            "tactic": "simp",
            "description": "ℝ → ℝ function",
            "symbols": ["α", "β", "γ", "≤", "≥", "≠"],
        }

        # Set and get Unicode data
        self.cache.set(spec_sha256, algo, mathlib_commit, unicode_proof)
        result = self.cache.get(spec_sha256, algo, mathlib_commit)

        assert result == unicode_proof

    def test_cache_malformed_file_handling(self):
        """Test: Cache handles malformed JSON files gracefully."""
        spec_sha256 = "abc123"
        algo = "ppo"
        mathlib_commit = "def456"

        # Create a malformed cache file
        cache_file = self.cache._cache_path(
            self.cache._cache_key(spec_sha256, algo, mathlib_commit)
        )
        with open(cache_file, "w", encoding="utf-8") as f:
            f.write('{"malformed": json}')

        # Should return None for malformed files
        result = self.cache.get(spec_sha256, algo, mathlib_commit)
        assert result is None

    def test_cache_directory_creation(self):
        """Test: Cache creates directory if it doesn't exist."""
        new_cache_dir = Path(self.temp_dir) / "new_cache"
        new_cache = ProofCache(new_cache_dir)

        assert new_cache_dir.exists()
        assert new_cache.cache_dir == new_cache_dir

    def test_cache_overwrite_behavior(self):
        """Test: Cache overwrites existing entries correctly."""
        spec_sha256 = "abc123"
        algo = "ppo"
        mathlib_commit = "def456"

        # Set initial proof
        initial_proof = {"tactic": "simp", "version": 1}
        self.cache.set(spec_sha256, algo, mathlib_commit, initial_proof)

        # Overwrite with new proof
        updated_proof = {"tactic": "rw", "version": 2}
        self.cache.set(spec_sha256, algo, mathlib_commit, updated_proof)

        # Should get updated proof
        result = self.cache.get(spec_sha256, algo, mathlib_commit)
        assert result == updated_proof

    def test_cache_empty_values(self):
        """Test: Cache handles empty values correctly."""
        spec_sha256 = "abc123"
        algo = "ppo"
        mathlib_commit = "def456"

        empty_proof = {}
        self.cache.set(spec_sha256, algo, mathlib_commit, empty_proof)

        result = self.cache.get(spec_sha256, algo, mathlib_commit)
        assert result == empty_proof

    def test_cache_large_data(self):
        """Test: Cache handles large data structures."""
        spec_sha256 = "abc123"
        algo = "ppo"
        mathlib_commit = "def456"

        # Create large proof with many lemmas
        large_proof = {
            "tactic": "simp",
            "lemmas": [f"lemma_{i}" for i in range(1000)],
            "metadata": {
                "timestamp": "2024-01-01T00:00:00Z",
                "version": "1.0.0",
                "tags": ["safety", "verification", "rl"],
            },
        }

        self.cache.set(spec_sha256, algo, mathlib_commit, large_proof)
        result = self.cache.get(spec_sha256, algo, mathlib_commit)

        assert result == large_proof
        assert len(result["lemmas"]) == 1000

    def test_cache_concurrent_access_simulation(self):
        """Test: Cache handles simulated concurrent access patterns."""
        spec_sha256 = "abc123"
        algo = "ppo"
        mathlib_commit = "def456"

        # Simulate multiple rapid set/get operations
        for i in range(10):
            proof = {"tactic": "simp", "iteration": i}
            self.cache.set(spec_sha256, algo, mathlib_commit, proof)
            result = self.cache.get(spec_sha256, algo, mathlib_commit)
            assert result == proof

        # Final result should be the last set
        final_result = self.cache.get(spec_sha256, algo, mathlib_commit)
        assert final_result["iteration"] == 9
