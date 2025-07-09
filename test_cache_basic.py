#!/usr/bin/env python3
"""
Basic test script for ProofCache functionality.
This can be run directly without pytest or other test frameworks.
"""

import sys
import tempfile
import shutil
from pathlib import Path

# Add current directory to path
sys.path.insert(0, ".")

from proofstack.cache import ProofCache


def test_basic_functionality():
    """Test basic cache functionality."""
    print("🧪 Testing basic cache functionality...")

    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    cache_dir = Path(temp_dir) / ".proofstack_cache"
    cache = ProofCache(cache_dir)

    try:
        # Test initialization
        assert cache.cache_dir == cache_dir
        assert cache.cache_dir.exists()
        print("✅ Cache initialization successful")

        # Test basic set/get
        spec_sha256 = "abc123"
        algo = "ppo"
        mathlib_commit = "def456"
        proof_sketch = {"tactic": "simp", "lemmas": ["h1", "h2"]}

        cache.set(spec_sha256, algo, mathlib_commit, proof_sketch)
        result = cache.get(spec_sha256, algo, mathlib_commit)

        assert result == proof_sketch
        print("✅ Basic set/get functionality works")

        # Test cache miss
        result = cache.get("nonexistent", algo, mathlib_commit)
        assert result is None
        print("✅ Cache miss returns None")

        return True

    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False
    finally:
        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_mutation_detection():
    """Test cache mutation detection."""
    print("\n🧪 Testing mutation detection...")

    temp_dir = tempfile.mkdtemp()
    cache_dir = Path(temp_dir) / ".proofstack_cache"
    cache = ProofCache(cache_dir)

    try:
        # Original spec
        original_spec = "cart_position <= 2.4"
        mutated_spec = "cart_position <= 2.5"

        original_hash = ProofCache.compute_spec_sha256(original_spec)
        mutated_hash = ProofCache.compute_spec_sha256(mutated_spec)

        # Verify hashes are different
        assert original_hash != mutated_hash
        print("✅ SHA256 computation works correctly")

        # Cache original
        original_proof = {"tactic": "simp", "spec": original_spec}
        cache.set(original_hash, "ppo", "def456", original_proof)

        # Try to get with mutated spec - should miss
        result = cache.get(mutated_hash, "ppo", "def456")
        assert result is None
        print("✅ Mutation detection works correctly")

        # Original should still be cached
        result = cache.get(original_hash, "ppo", "def456")
        assert result == original_proof
        print("✅ Original spec still cached correctly")

        return True

    except Exception as e:
        print(f"❌ Mutation detection test failed: {e}")
        return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_algorithm_isolation():
    """Test algorithm isolation."""
    print("\n🧪 Testing algorithm isolation...")

    temp_dir = tempfile.mkdtemp()
    cache_dir = Path(temp_dir) / ".proofstack_cache"
    cache = ProofCache(cache_dir)

    try:
        spec_sha256 = "abc123"
        mathlib_commit = "def456"

        ppo_proof = {"tactic": "simp", "algo": "ppo"}
        sac_proof = {"tactic": "rw", "algo": "sac"}

        # Cache both algorithms
        cache.set(spec_sha256, "ppo", mathlib_commit, ppo_proof)
        cache.set(spec_sha256, "sac", mathlib_commit, sac_proof)

        # Verify isolation
        assert cache.get(spec_sha256, "ppo", mathlib_commit) == ppo_proof
        assert cache.get(spec_sha256, "sac", mathlib_commit) == sac_proof
        print("✅ Algorithm isolation works correctly")

        return True

    except Exception as e:
        print(f"❌ Algorithm isolation test failed: {e}")
        return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_edge_cases():
    """Test edge cases."""
    print("\n🧪 Testing edge cases...")

    temp_dir = tempfile.mkdtemp()
    cache_dir = Path(temp_dir) / ".proofstack_cache"
    cache = ProofCache(cache_dir)

    try:
        spec_sha256 = "abc123"
        algo = "ppo"
        mathlib_commit = "def456"

        # Test empty values
        empty_proof = {}
        cache.set(spec_sha256, algo, mathlib_commit, empty_proof)
        result = cache.get(spec_sha256, algo, mathlib_commit)
        assert result == empty_proof
        print("✅ Empty values handled correctly")

        # Test Unicode handling
        unicode_proof = {
            "tactic": "simp",
            "description": "ℝ → ℝ function",
            "symbols": ["α", "β", "γ", "≤", "≥", "≠"],
        }

        cache.set(spec_sha256, algo, mathlib_commit, unicode_proof)
        result = cache.get(spec_sha256, algo, mathlib_commit)
        assert result == unicode_proof
        print("✅ Unicode handling works correctly")

        return True

    except Exception as e:
        print(f"❌ Edge cases test failed: {e}")
        return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    """Run all tests."""
    print("🚀 SafeRL ProofStack - Basic Cache Test Suite")
    print("=" * 50)

    tests = [
        test_basic_functionality,
        test_mutation_detection,
        test_algorithm_isolation,
        test_edge_cases,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")

    print(f"\n📊 Test Results:")
    print(f"   Passed: {passed}/{total}")
    print(f"   Failed: {total - passed}/{total}")

    if passed == total:
        print("🎉 All tests passed! Cache functionality is working correctly.")
        print("\nKey Features Verified:")
        print("• Basic cache operations (set/get)")
        print("• SHA256-based mutation detection")
        print("• Algorithm isolation")
        print("• Edge case handling")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
