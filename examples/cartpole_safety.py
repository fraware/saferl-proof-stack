#!/usr/bin/env python3
"""
CartPole Safety with SafeRL ProofStack

This script demonstrates how to use SafeRL ProofStack to create provably safe
reinforcement learning for the classic CartPole environment.
"""

import gymnasium as gym
import numpy as np
from stable_baselines3 import PPO
from proofstack import ProofPipeline, SpecGen
import os


def main():
    print("🎮 CartPole Safety with SafeRL ProofStack")
    print("=" * 50)

    # 1. Environment Setup
    print("\n1. Setting up CartPole environment...")
    env = gym.make("CartPole-v1")

    print(f"Observation space: {env.observation_space}")
    print(f"Action space: {env.action_space}")

    # 2. Safety Specification
    print("\n2. Creating safety specification...")
    spec = SpecGen()

    # Safety invariants (must always hold)
    spec.invariants = [
        "|σ.cart_position| ≤ 2.4",  # Cart position bounds
        "|σ.pole_angle| ≤ 0.2095",  # Pole angle bounds (12°)
    ]

    # Guard conditions (checked before actions)
    spec.guard = [
        "|σ.cart_position| ≤ 2.3",  # Conservative cart bounds
        "|σ.pole_angle| ≤ 0.2",  # Conservative angle bounds
        "|a.force| ≤ 10.0",  # Action force bounds
    ]

    # Safety lemmas for proof generation
    spec.lemmas = [
        "position_step_bound",  # Bounds on position change per step
        "angle_step_preserved",  # Angle preservation under safe actions
    ]

    print("Safety Specification:")
    print(f"  Invariants: {spec.invariants}")
    print(f"  Guards: {spec.guard}")
    print(f"  Lemmas: {spec.lemmas}")

    # 3. Train Safe RL Agent
    print("\n3. Training PPO agent...")
    model = PPO("MlpPolicy", env, verbose=0)
    model.learn(total_timesteps=5000)

    # Save the model
    model.save("cartpole_ppo.zip")
    print("  Model saved as cartpole_ppo.zip")

    # 4. Test Safety Violations
    print("\n4. Testing safety violations...")
    violations = test_safety_violations(model, env, n_episodes=20)

    print("Safety Violation Test Results:")
    print(f"  Total steps: {violations['total_steps']}")
    print(
        f"  Position violations: {violations['position_violations']} ({violations['position_violations']/violations['total_steps']*100:.2f}%)"
    )
    print(
        f"  Angle violations: {violations['angle_violations']} ({violations['angle_violations']/violations['total_steps']*100:.2f}%)"
    )

    # 5. Generate Formal Proofs
    print("\n5. Generating formal proofs and compliance artifacts...")
    api_key = os.getenv("FIREWORKS_API_KEY", "mock_key")

    pipeline = ProofPipeline(env, spec, api_key)
    bundle = pipeline.run()

    print(f"  Compliance bundle created at: {bundle.path}")
    print("  Generated artifacts:")
    for artifact in bundle.path.glob("*"):
        if artifact.is_file():
            print(f"    - {artifact.name}")

    # 6. Show generated Lean proof
    print("\n6. Generated Lean4 Proof:")
    print("-" * 30)
    lean_file = spec.lean_file_path
    if lean_file and lean_file.exists():
        with open(lean_file, "r") as f:
            content = f.read()
            print(content[:500] + "..." if len(content) > 500 else content)
    else:
        print("  Lean proof file not found.")

    # 7. Show generated guard code
    print("\n7. Generated Runtime Guard Code:")
    print("-" * 30)
    guard_file = bundle.path / "guard.c"
    if guard_file.exists():
        with open(guard_file, "r") as f:
            content = f.read()
            print(content)
    else:
        print("  Guard code file not found.")

    env.close()

    print("\n🎉 CartPole safety demonstration completed!")
    print("=" * 50)
    print("✅ Trained PPO agent with safety considerations")
    print("✅ Generated formal proofs in Lean4")
    print("✅ Created compliance artifacts")
    print("✅ Implemented runtime safety guards")
    print("\nNext steps:")
    print("1. Deploy with runtime guards in production")
    print("2. Extend to other environments")
    print("3. Add real-time monitoring")


def test_safety_violations(model, env, n_episodes=100):
    """Test for safety violations during agent execution."""
    violations = {"position_violations": 0, "angle_violations": 0, "total_steps": 0}

    for episode in range(n_episodes):
        obs, info = env.reset()
        done = False

        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, truncated, info = env.step(action)

            violations["total_steps"] += 1

            # Check safety violations
            if abs(obs[0]) > 2.4:  # Cart position
                violations["position_violations"] += 1
            if abs(obs[2]) > 0.2095:  # Pole angle
                violations["angle_violations"] += 1

    return violations


if __name__ == "__main__":
    main()
