#!/usr/bin/env python3
"""
Demonstration of ProofCache mutation detection functionality.
This script shows how the cache correctly detects spec changes and avoids cache hits.
"""

import sys
import tempfile
import shutil
from pathlib import Path

# Add current directory to path
sys.path.insert(0, ".")

from proofstack.cache import ProofCache


def demo_cache_mutation_detection():
    """Demonstrate cache mutation detection with real examples."""
    print("🚀 SafeRL ProofStack - Cache Mutation Detection Demo")
    print("=" * 60)

    # Create temporary directory for demo
    temp_dir = tempfile.mkdtemp()
    cache_dir = Path(temp_dir) / ".proofstack_cache"
    cache = ProofCache(cache_dir)

    try:
        print("📋 Step 1: Initial Cache Setup")
        print("-" * 40)

        # Original safety specification
        original_spec = """
        invariants:
          - "|σ.cart_position| ≤ 2.4"
          - "|σ.pole_angle| ≤ 0.2095"
        guards:
          - "|σ.cart_position| ≤ 2.3"
          - "|σ.pole_angle| ≤ 0.2"
        lemmas:
          - "position_step_bound"
          - "angle_step_preserved"
        """

        # Compute hash for original spec
        original_hash = ProofCache.compute_spec_sha256(original_spec)
        print(f"Original spec hash: {original_hash[:16]}...")

        # Cache the original proof
        original_proof = {
            "tactic": "simp [h_guard]",
            "lemmas": ["position_step_bound", "angle_step_preserved"],
            "spec": original_spec,
            "timestamp": "2024-01-01T00:00:00Z",
        }

        cache.set(original_hash, "ppo", "def456", original_proof)
        print("✅ Original proof cached successfully")

        print("\n📋 Step 2: Cache Hit Test")
        print("-" * 40)

        # Try to get the same spec - should hit
        result = cache.get(original_hash, "ppo", "def456")
        if result:
            print("✅ Cache HIT: Found existing proof for original spec")
            print(f"   Tactic: {result['tactic']}")
            print(f"   Lemmas: {result['lemmas']}")
        else:
            print("❌ Cache MISS: Unexpected miss for original spec")

        print("\n📋 Step 3: Mutation Detection Test")
        print("-" * 40)

        # Mutated safety specification (changed cart position limit)
        mutated_spec = """
        invariants:
          - "|σ.cart_position| ≤ 2.5"  # Changed from 2.4 to 2.5
          - "|σ.pole_angle| ≤ 0.2095"
        guards:
          - "|σ.cart_position| ≤ 2.4"  # Changed from 2.3 to 2.4
          - "|σ.pole_angle| ≤ 0.2"
        lemmas:
          - "position_step_bound"
          - "angle_step_preserved"
        """

        # Compute hash for mutated spec
        mutated_hash = ProofCache.compute_spec_sha256(mutated_spec)
        print(f"Mutated spec hash: {mutated_hash[:16]}...")

        # Verify hashes are different
        if original_hash != mutated_hash:
            print("✅ Hash verification: Specs have different hashes")
        else:
            print("❌ Hash verification: Specs have same hash (unexpected)")

        # Try to get with mutated spec - should miss
        result = cache.get(mutated_hash, "ppo", "def456")
        if result is None:
            print("✅ Cache MISS: Correctly detected spec mutation")
            print("   → New proof generation required")
        else:
            print("❌ Cache HIT: Unexpected hit for mutated spec")

        print("\n📋 Step 4: Algorithm Isolation Test")
        print("-" * 40)

        # Test that different algorithms are isolated
        sac_proof = {
            "tactic": "rw [h_guard]",
            "lemmas": ["sac_specific_lemma"],
            "algo": "sac",
        }

        cache.set(original_hash, "sac", "def456", sac_proof)

        # Should get different proofs for different algorithms
        ppo_result = cache.get(original_hash, "ppo", "def456")
        sac_result = cache.get(original_hash, "sac", "def456")

        if ppo_result and sac_result and ppo_result != sac_result:
            print("✅ Algorithm isolation: Different proofs for PPO vs SAC")
            print(f"   PPO tactic: {ppo_result['tactic']}")
            print(f"   SAC tactic: {sac_result['tactic']}")
        else:
            print("❌ Algorithm isolation: Proofs not properly isolated")

        print("\n📋 Step 5: Mathlib Commit Isolation Test")
        print("-" * 40)

        # Test that different mathlib commits are isolated
        commit1_proof = {
            "tactic": "simp [h_guard]",
            "commit": "def456",
            "mathlib_version": "4.7.0",
        }

        commit2_proof = {
            "tactic": "simp [h_guard, new_lemma]",
            "commit": "ghi789",
            "mathlib_version": "4.8.0",
        }

        cache.set(original_hash, "ppo", "def456", commit1_proof)
        cache.set(original_hash, "ppo", "ghi789", commit2_proof)

        # Should get different proofs for different commits
        result1 = cache.get(original_hash, "ppo", "def456")
        result2 = cache.get(original_hash, "ppo", "ghi789")

        if result1 and result2 and result1 != result2:
            print("✅ Commit isolation: Different proofs for different mathlib commits")
            print(f"   Commit def456: {result1['tactic']}")
            print(f"   Commit ghi789: {result2['tactic']}")
        else:
            print("❌ Commit isolation: Proofs not properly isolated by commit")

        print("\n📋 Step 6: Edge Case Testing")
        print("-" * 40)

        # Test Unicode handling
        unicode_spec = "ℝ → ℝ function with α, β, γ, ≤, ≥, ≠"
        unicode_hash = ProofCache.compute_spec_sha256(unicode_spec)
        unicode_proof = {
            "tactic": "simp",
            "description": "Unicode mathematical symbols",
            "symbols": ["α", "β", "γ", "≤", "≥", "≠"],
        }

        cache.set(unicode_hash, "ppo", "def456", unicode_proof)
        result = cache.get(unicode_hash, "ppo", "def456")

        if result and result == unicode_proof:
            print("✅ Unicode handling: Unicode characters handled correctly")
        else:
            print("❌ Unicode handling: Unicode characters not handled correctly")

        # Test empty spec
        empty_spec = ""
        empty_hash = ProofCache.compute_spec_sha256(empty_spec)
        empty_proof = {}

        cache.set(empty_hash, "ppo", "def456", empty_proof)
        result = cache.get(empty_hash, "ppo", "def456")

        if result == empty_proof:
            print("✅ Empty spec handling: Empty specifications handled correctly")
        else:
            print("❌ Empty spec handling: Empty specifications not handled correctly")

        print("\n🎉 Cache Mutation Detection Demo Complete!")
        print("=" * 60)
        print("Key Features Demonstrated:")
        print("• SHA256-based spec hashing for mutation detection")
        print("• Cache hits for identical specs")
        print("• Cache misses for mutated specs")
        print("• Algorithm isolation (PPO vs SAC)")
        print("• Mathlib commit isolation")
        print("• Unicode and edge case handling")
        print("\nThis ensures that:")
        print("• Spec changes trigger new proof generation")
        print("• Identical specs reuse cached proofs")
        print("• Different algorithms/commits are properly isolated")
        print("• Cache is robust against edge cases")

    finally:
        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)


def demo_cache_performance():
    """Demonstrate cache performance benefits."""
    print("\n🚀 Cache Performance Benefits Demo")
    print("=" * 50)

    temp_dir = tempfile.mkdtemp()
    cache_dir = Path(temp_dir) / ".proofstack_cache"
    cache = ProofCache(cache_dir)

    try:
        # Simulate multiple proof generations
        specs = [
            "cart_position <= 2.4",
            "cart_position <= 2.4",  # Duplicate
            "cart_position <= 2.5",  # Mutation
            "cart_position <= 2.4",  # Back to original
            "pole_angle <= 0.2",
            "pole_angle <= 0.2",  # Duplicate
        ]

        cache_hits = 0
        cache_misses = 0

        for i, spec in enumerate(specs, 1):
            spec_hash = ProofCache.compute_spec_sha256(spec)
            proof = {"tactic": "simp", "spec": spec, "iteration": i}

            # Check cache first
            cached_proof = cache.get(spec_hash, "ppo", "def456")

            if cached_proof:
                cache_hits += 1
                print(f"  {i}. Cache HIT: Reusing proof for '{spec}'")
            else:
                cache_misses += 1
                print(f"  {i}. Cache MISS: Generating new proof for '{spec}'")
                # Simulate expensive proof generation
                cache.set(spec_hash, "ppo", "def456", proof)

        print(f"\n📊 Cache Performance Summary:")
        print(f"   Total requests: {len(specs)}")
        print(f"   Cache hits: {cache_hits}")
        print(f"   Cache misses: {cache_misses}")
        print(f"   Hit rate: {cache_hits/len(specs)*100:.1f}%")
        print(f"   LLM calls saved: {cache_hits}")

        if cache_hits > 0:
            print(f"\n💰 Cost Savings:")
            print(f"   • Reduced LLM API calls: {cache_hits}")
            print(f"   • Faster proof generation: {cache_hits} cached proofs")
            print(f"   • Improved development iteration speed")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    try:
        demo_cache_mutation_detection()
        demo_cache_performance()
        print("\n✅ All cache demonstrations completed successfully!")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
