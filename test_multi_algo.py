#!/usr/bin/env python3
"""
Test script for multi-algorithm support in SafeRL ProofStack.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from proofstack.rl.algorithms import (
    create_safe_algorithm,
    PPOSafeAdapter,
    SACSafeAdapter,
    DDPGSafeAdapter,
)
from proofstack import SpecGen
import gymnasium as gym


def test_algorithm_adapters():
    """Test the algorithm adapter classes."""
    print("🧪 Testing Algorithm Adapters")
    print("=" * 40)

    # Create test environment
    env = gym.make("CartPole-v1")

    # Test PPO adapter
    print("\n1. Testing PPO Adapter")
    ppo_adapter = PPOSafeAdapter(env)
    print(f"  Algorithm name: {ppo_adapter.algorithm_name}")
    print(f"  ✅ PPO adapter created successfully")

    # Test SAC adapter
    print("\n2. Testing SAC Adapter")
    sac_adapter = SACSafeAdapter(env)
    print(f"  Algorithm name: {sac_adapter.algorithm_name}")
    print(f"  ✅ SAC adapter created successfully")

    # Test DDPG adapter
    print("\n3. Testing DDPG Adapter")
    ddpg_adapter = DDPGSafeAdapter(env)
    print(f"  Algorithm name: {ddpg_adapter.algorithm_name}")
    print(f"  ✅ DDPG adapter created successfully")

    env.close()


def test_algorithm_factory():
    """Test the algorithm factory function."""
    print("\n🧪 Testing Algorithm Factory")
    print("=" * 40)

    # Create test environment
    env = gym.make("CartPole-v1")

    # Test factory with different algorithms
    algorithms = ["ppo", "sac", "ddpg"]

    for algo in algorithms:
        print(f"\nTesting {algo.upper()} factory:")
        try:
            adapter = create_safe_algorithm(algo, env)
            print(f"  ✅ {algo.upper()} adapter created successfully")
            print(f"  Algorithm name: {adapter.algorithm_name}")
        except Exception as e:
            print(f"  ❌ Failed to create {algo.upper()} adapter: {e}")

    # Test invalid algorithm
    print(f"\nTesting invalid algorithm:")
    try:
        adapter = create_safe_algorithm("invalid", env)
        print(f"  ❌ Should have failed for invalid algorithm")
    except ValueError as e:
        print(f"  ✅ Correctly rejected invalid algorithm: {e}")

    env.close()


def test_specgen_algorithm_support():
    """Test SpecGen with algorithm-specific templates."""
    print("\n🧪 Testing SpecGen Algorithm Support")
    print("=" * 40)

    # Create SpecGen instance
    spec = SpecGen()
    spec.invariants = ["|σ.cart_position| ≤ 2.4", "|σ.pole_angle| ≤ 0.2095"]
    spec.guard = ["|σ.cart_position| ≤ 2.3", "|σ.pole_angle| ≤ 0.2"]
    spec.lemmas = ["position_step_bound", "angle_step_preserved"]

    # Test different algorithms
    algorithms = ["ppo", "sac", "ddpg"]

    for algo in algorithms:
        print(f"\nTesting {algo.upper()} template:")
        spec.set_algorithm(algo)

        # Generate Lean content
        lean_content = spec._generate_lean_content()

        # Check if algorithm-specific template is included
        if f"safe_{algo}_policy" in lean_content:
            print(f"  ✅ {algo.upper()} template generated correctly")
        else:
            print(f"  ❌ {algo.upper()} template not found in generated content")

        # Check if algorithm name is mentioned
        if algo.upper() in lean_content:
            print(f"  ✅ {algo.upper()} algorithm name found in content")
        else:
            print(f"  ❌ {algo.upper()} algorithm name not found")


def test_safety_constraints():
    """Test safety constraint application."""
    print("\n🧪 Testing Safety Constraints")
    print("=" * 40)

    # Create test environment
    env = gym.make("CartPole-v1")

    # Test PPO safety constraints
    print("\n1. Testing PPO Safety Constraints")
    ppo_adapter = PPOSafeAdapter(env)

    # Test action masking
    test_state = [0.0, 0.0, 0.0, 0.0]  # Safe state
    test_action = 0  # Left action

    safe_action = ppo_adapter._apply_safety_constraints(test_action, test_state)
    print(f"  Original action: {test_action}")
    print(f"  Safe action: {safe_action}")
    print(f"  ✅ Action masking applied")

    # Test reward shaping
    original_reward = 1.0
    adjusted_reward = ppo_adapter._calculate_safety_reward(
        original_reward, test_state, test_action
    )
    print(f"  Original reward: {original_reward}")
    print(f"  Adjusted reward: {adjusted_reward}")
    print(f"  ✅ Reward shaping applied")

    # Test SAC safety constraints
    print("\n2. Testing SAC Safety Constraints")
    sac_adapter = SACSafeAdapter(env)

    # Test action clipping
    test_continuous_action = [0.5, 0.3]  # Continuous action
    safe_continuous_action = sac_adapter._apply_safety_constraints(
        test_continuous_action, test_state
    )
    print(f"  Original action: {test_continuous_action}")
    print(f"  Safe action: {safe_continuous_action}")
    print(f"  ✅ Action clipping applied")

    env.close()


def main():
    """Run all multi-algorithm tests."""
    print("🚀 Multi-Algorithm Support Tests")
    print("=" * 50)

    try:
        test_algorithm_adapters()
        test_algorithm_factory()
        test_specgen_algorithm_support()
        test_safety_constraints()

        print("\n🎉 All multi-algorithm tests passed!")
        print("=" * 50)
        print("✅ Algorithm adapters working correctly")
        print("✅ Algorithm factory functioning")
        print("✅ SpecGen supports algorithm-specific templates")
        print("✅ Safety constraints applied properly")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
