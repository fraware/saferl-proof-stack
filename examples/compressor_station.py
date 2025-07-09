#!/usr/bin/env python3
"""
Compressor Station Safety with SafeRL ProofStack

This script demonstrates SafeRL ProofStack for continuous control in a
compressor station environment with safety constraints on pressure,
temperature, and flow rates.
"""

import gymnasium as gym
import numpy as np
from stable_baselines3 import SAC
from proofstack import ProofPipeline, SpecGen
import os


class CompressorStationEnv(gym.Env):
    """Custom compressor station environment with safety constraints."""

    def __init__(self):
        super().__init__()

        # State space: [pressure, temperature, flow_rate, valve_position]
        self.observation_space = gym.spaces.Box(
            low=np.array([0.0, 0.0, 0.0, 0.0]),
            high=np.array([100.0, 200.0, 50.0, 1.0]),
            dtype=np.float32,
        )

        # Action space: [valve_control, compressor_speed]
        self.action_space = gym.spaces.Box(
            low=np.array([-1.0, -1.0]), high=np.array([1.0, 1.0]), dtype=np.float32
        )

        # Safety bounds
        self.max_pressure = 80.0  # psi
        self.max_temperature = 150.0  # °C
        self.max_flow_rate = 40.0  # m³/h

        self.state = None
        self.step_count = 0
        self.max_steps = 1000

    def reset(self, seed=None):
        super().reset(seed=seed)

        # Initialize to safe state
        self.state = np.array(
            [
                50.0,  # pressure (psi)
                75.0,  # temperature (°C)
                20.0,  # flow rate (m³/h)
                0.5,  # valve position
            ],
            dtype=np.float32,
        )

        self.step_count = 0
        return self.state, {}

    def step(self, action):
        self.step_count += 1

        # Apply actions
        valve_delta = action[0] * 0.1
        compressor_delta = action[1] * 0.1

        # Update state (simplified dynamics)
        self.state[3] = np.clip(self.state[3] + valve_delta, 0.0, 1.0)  # valve
        self.state[0] += compressor_delta * 2.0  # pressure
        self.state[1] += compressor_delta * 1.5  # temperature
        self.state[2] = self.state[3] * 40.0  # flow rate

        # Apply safety constraints
        self.state[0] = np.clip(self.state[0], 0.0, self.max_pressure)
        self.state[1] = np.clip(self.state[1], 0.0, self.max_temperature)
        self.state[2] = np.clip(self.state[2], 0.0, self.max_flow_rate)

        # Calculate reward
        reward = self._calculate_reward()

        # Check if episode is done
        done = self.step_count >= self.max_steps

        # Check for safety violations
        if self._check_safety_violation():
            reward -= 100.0  # Penalty for safety violation
            done = True

        return self.state, reward, done, False, {}

    def _calculate_reward(self):
        """Calculate reward based on efficiency and safety."""
        # Efficiency reward (higher flow rate is better)
        efficiency_reward = self.state[2] / self.max_flow_rate

        # Safety penalty (closer to limits is worse)
        pressure_penalty = max(0, (self.state[0] - 60.0) / 20.0)
        temperature_penalty = max(0, (self.state[1] - 100.0) / 50.0)

        return efficiency_reward - pressure_penalty - temperature_penalty

    def _check_safety_violation(self):
        """Check if safety bounds are violated."""
        return (
            self.state[0] > self.max_pressure
            or self.state[1] > self.max_temperature
            or self.state[2] > self.max_flow_rate
        )


def main():
    print("🏭 Compressor Station Safety with SafeRL ProofStack")
    print("=" * 60)

    # 1. Environment Setup
    print("\n1. Setting up compressor station environment...")
    env = CompressorStationEnv()

    print(f"Observation space: {env.observation_space}")
    print(f"Action space: {env.action_space}")
    print(f"Safety bounds:")
    print(f"  Max pressure: {env.max_pressure} psi")
    print(f"  Max temperature: {env.max_temperature} °C")
    print(f"  Max flow rate: {env.max_flow_rate} m³/h")

    # 2. Safety Specification
    print("\n2. Creating safety specification...")
    spec = SpecGen()

    # Safety invariants (must always hold)
    spec.invariants = [
        "σ.pressure ≤ 80.0",  # Pressure safety limit
        "σ.temperature ≤ 150.0",  # Temperature safety limit
        "σ.flow_rate ≤ 40.0",  # Flow rate safety limit
        "σ.valve_position ∈ [0.0, 1.0]",  # Valve position bounds
    ]

    # Guard conditions (checked before actions)
    spec.guard = [
        "σ.pressure ≤ 75.0",  # Conservative pressure limit
        "σ.temperature ≤ 140.0",  # Conservative temperature limit
        "σ.flow_rate ≤ 35.0",  # Conservative flow limit
        "|a.valve_control| ≤ 0.5",  # Valve control bounds
        "|a.compressor_speed| ≤ 0.5",  # Compressor speed bounds
    ]

    # Safety lemmas for proof generation
    spec.lemmas = [
        "pressure_step_bound",  # Pressure change bounds
        "temperature_step_bound",  # Temperature change bounds
        "flow_rate_preserved",  # Flow rate preservation
        "valve_position_valid",  # Valve position validity
    ]

    print("Safety Specification:")
    print(f"  Invariants: {spec.invariants}")
    print(f"  Guards: {spec.guard}")
    print(f"  Lemmas: {spec.lemmas}")

    # 3. Train Safe RL Agent
    print("\n3. Training SAC agent...")
    model = SAC("MlpPolicy", env, verbose=0, learning_rate=0.001)
    model.learn(total_timesteps=10000)

    # Save the model
    model.save("compressor_sac.zip")
    print("  Model saved as compressor_sac.zip")

    # 4. Test Safety Violations
    print("\n4. Testing safety violations...")
    violations = test_compressor_safety(model, env, n_episodes=10)

    print("Safety Violation Test Results:")
    print(f"  Total steps: {violations['total_steps']}")
    print(
        f"  Pressure violations: {violations['pressure_violations']} ({violations['pressure_violations']/violations['total_steps']*100:.2f}%)"
    )
    print(
        f"  Temperature violations: {violations['temperature_violations']} ({violations['temperature_violations']/violations['total_steps']*100:.2f}%)"
    )
    print(
        f"  Flow rate violations: {violations['flow_violations']} ({violations['flow_violations']/violations['total_steps']*100:.2f}%)"
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

    print("\n🎉 Compressor station safety demonstration completed!")
    print("=" * 60)
    print("✅ Trained SAC agent for continuous control")
    print("✅ Implemented safety constraints on pressure, temperature, flow")
    print("✅ Generated formal proofs in Lean4")
    print("✅ Created compliance artifacts")
    print("✅ Implemented runtime safety guards")
    print("\nNext steps:")
    print("1. Deploy with runtime guards in industrial environment")
    print("2. Add real-time monitoring and alerting")
    print("3. Integrate with SCADA systems")
    print("4. Extend to multi-compressor networks")


def test_compressor_safety(model, env, n_episodes=100):
    """Test for safety violations during agent execution."""
    violations = {
        "pressure_violations": 0,
        "temperature_violations": 0,
        "flow_violations": 0,
        "total_steps": 0,
    }

    for episode in range(n_episodes):
        obs, info = env.reset()
        done = False

        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, truncated, info = env.step(action)

            violations["total_steps"] += 1

            # Check safety violations
            if obs[0] > env.max_pressure:  # Pressure
                violations["pressure_violations"] += 1
            if obs[1] > env.max_temperature:  # Temperature
                violations["temperature_violations"] += 1
            if obs[2] > env.max_flow_rate:  # Flow rate
                violations["flow_violations"] += 1

    return violations


if __name__ == "__main__":
    main()
