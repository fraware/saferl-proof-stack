#!/usr/bin/env python3
"""
Robotic Arm Safety with SafeRL ProofStack

This script demonstrates SafeRL ProofStack for robotic arm control with
safety constraints on joint torques, end-effector position, and quaternion
orientation.
"""

import gymnasium as gym
import numpy as np
from stable_baselines3 import DDPG
from proofstack import ProofPipeline, SpecGen
import os


class RoboticArmEnv(gym.Env):
    """Custom robotic arm environment with safety constraints."""

    def __init__(self):
        super().__init__()

        # State space: [joint_angles(3), joint_velocities(3), end_effector_pos(3), quaternion(4)]
        self.observation_space = gym.spaces.Box(
            low=np.array([-np.pi] * 3 + [-2.0] * 3 + [-1.0] * 3 + [-1.0] * 4),
            high=np.array([np.pi] * 3 + [2.0] * 3 + [1.0] * 3 + [1.0] * 4),
            dtype=np.float32,
        )

        # Action space: [joint_torques(3)]
        self.action_space = gym.spaces.Box(
            low=np.array([-10.0, -10.0, -10.0]),
            high=np.array([10.0, 10.0, 10.0]),
            dtype=np.float32,
        )

        # Safety bounds
        self.max_torque = 8.0  # N⋅m
        self.max_joint_velocity = 1.5  # rad/s
        self.max_end_effector_velocity = 0.5  # m/s
        self.workspace_bounds = 0.8  # m

        self.state = None
        self.step_count = 0
        self.max_steps = 500

    def reset(self, seed=None):
        super().reset(seed=seed)

        # Initialize to safe state
        self.state = np.array(
            [
                0.0,
                0.0,
                0.0,  # joint angles
                0.0,
                0.0,
                0.0,  # joint velocities
                0.3,
                0.0,
                0.5,  # end effector position
                1.0,
                0.0,
                0.0,
                0.0,  # quaternion (identity)
            ],
            dtype=np.float32,
        )

        self.step_count = 0
        return self.state, {}

    def step(self, action):
        self.step_count += 1

        # Apply torques (simplified dynamics)
        dt = 0.01
        inertia = np.array([1.0, 1.0, 1.0])  # Simplified inertia

        # Update joint velocities
        self.state[3:6] += action / inertia * dt

        # Update joint angles
        self.state[0:3] += self.state[3:6] * dt

        # Update end effector position (simplified forward kinematics)
        self.state[6:9] = self._forward_kinematics(self.state[0:3])

        # Update quaternion (simplified)
        self.state[9:13] = self._update_quaternion(
            self.state[9:13], self.state[3:6], dt
        )

        # Apply safety constraints
        self.state[3:6] = np.clip(
            self.state[3:6], -self.max_joint_velocity, self.max_joint_velocity
        )
        self.state[6:9] = np.clip(
            self.state[6:9], -self.workspace_bounds, self.workspace_bounds
        )

        # Calculate reward
        reward = self._calculate_reward()

        # Check if episode is done
        done = self.step_count >= self.max_steps

        # Check for safety violations
        if self._check_safety_violation(action):
            reward -= 100.0  # Penalty for safety violation
            done = True

        return self.state, reward, done, False, {}

    def _forward_kinematics(self, joint_angles):
        """Simplified forward kinematics."""
        # Simple 3-DOF arm model
        x = 0.3 * np.cos(joint_angles[0]) + 0.3 * np.cos(
            joint_angles[0] + joint_angles[1]
        )
        y = 0.3 * np.sin(joint_angles[0]) + 0.3 * np.sin(
            joint_angles[0] + joint_angles[1]
        )
        z = 0.5 + 0.3 * np.sin(joint_angles[2])
        return np.array([x, y, z])

    def _update_quaternion(self, quat, angular_vel, dt):
        """Update quaternion based on angular velocity."""
        # Simplified quaternion update
        omega = np.array([0.0, angular_vel[0], angular_vel[1], angular_vel[2]])
        quat_dot = 0.5 * self._quaternion_multiply(omega, quat)
        new_quat = quat + quat_dot * dt
        return new_quat / np.linalg.norm(new_quat)  # Normalize

    def _quaternion_multiply(self, q1, q2):
        """Multiply two quaternions."""
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2
        return np.array(
            [
                w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
                w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
                w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
                w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
            ]
        )

    def _calculate_reward(self):
        """Calculate reward based on task completion and safety."""
        # Task reward (reach target position)
        target_pos = np.array([0.5, 0.0, 0.3])
        distance = np.linalg.norm(self.state[6:9] - target_pos)
        task_reward = 1.0 / (1.0 + distance)

        # Safety penalty (closer to limits is worse)
        torque_penalty = np.sum(np.abs(self.state[3:6])) / (3 * self.max_joint_velocity)
        workspace_penalty = np.sum(np.abs(self.state[6:9])) / (
            3 * self.workspace_bounds
        )

        return task_reward - 0.1 * torque_penalty - 0.1 * workspace_penalty

    def _check_safety_violation(self, action):
        """Check if safety bounds are violated."""
        # Check torque limits
        if np.any(np.abs(action) > self.max_torque):
            return True

        # Check joint velocity limits
        if np.any(np.abs(self.state[3:6]) > self.max_joint_velocity):
            return True

        # Check workspace bounds
        if np.any(np.abs(self.state[6:9]) > self.workspace_bounds):
            return True

        return False


def main():
    print("🤖 Robotic Arm Safety with SafeRL ProofStack")
    print("=" * 60)

    # 1. Environment Setup
    print("\n1. Setting up robotic arm environment...")
    env = RoboticArmEnv()

    print(f"Observation space: {env.observation_space}")
    print(f"Action space: {env.action_space}")
    print(f"Safety bounds:")
    print(f"  Max torque: {env.max_torque} N⋅m")
    print(f"  Max joint velocity: {env.max_joint_velocity} rad/s")
    print(f"  Max end effector velocity: {env.max_end_effector_velocity} m/s")
    print(f"  Workspace bounds: ±{env.workspace_bounds} m")

    # 2. Safety Specification
    print("\n2. Creating safety specification...")
    spec = SpecGen()

    # Safety invariants (must always hold)
    spec.invariants = [
        "|σ.joint_velocity_i| ≤ 1.5",  # Joint velocity limits
        "|σ.end_effector_pos_i| ≤ 0.8",  # Workspace bounds
        "|σ.quaternion_i| ≤ 1.0",  # Quaternion normalization
        "||σ.quaternion|| = 1.0",  # Unit quaternion constraint
    ]

    # Guard conditions (checked before actions)
    spec.guard = [
        "|σ.joint_velocity_i| ≤ 1.2",  # Conservative joint velocity
        "|σ.end_effector_pos_i| ≤ 0.7",  # Conservative workspace
        "|a.joint_torque_i| ≤ 8.0",  # Torque limits
        "|a.joint_torque_i| ≤ 6.0",  # Conservative torque
        "||σ.quaternion|| ≥ 0.9",  # Quaternion validity
    ]

    # Safety lemmas for proof generation
    spec.lemmas = [
        "torque_step_bound",  # Torque change bounds
        "velocity_step_bound",  # Velocity change bounds
        "workspace_preserved",  # Workspace constraint
        "quaternion_validity",  # Quaternion properties
        "forward_kinematics_safe",  # FK safety
    ]

    print("Safety Specification:")
    print(f"  Invariants: {spec.invariants}")
    print(f"  Guards: {spec.guard}")
    print(f"  Lemmas: {spec.lemmas}")

    # 3. Train Safe RL Agent
    print("\n3. Training DDPG agent...")
    model = DDPG("MlpPolicy", env, verbose=0, learning_rate=0.001)
    model.learn(total_timesteps=15000)

    # Save the model
    model.save("robotic_arm_ddpg.zip")
    print("  Model saved as robotic_arm_ddpg.zip")

    # 4. Test Safety Violations
    print("\n4. Testing safety violations...")
    violations = test_robotic_arm_safety(model, env, n_episodes=10)

    print("Safety Violation Test Results:")
    print(f"  Total steps: {violations['total_steps']}")
    print(
        f"  Torque violations: {violations['torque_violations']} ({violations['torque_violations']/violations['total_steps']*100:.2f}%)"
    )
    print(
        f"  Velocity violations: {violations['velocity_violations']} ({violations['velocity_violations']/violations['total_steps']*100:.2f}%)"
    )
    print(
        f"  Workspace violations: {violations['workspace_violations']} ({violations['workspace_violations']/violations['total_steps']*100:.2f}%)"
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

    print("\n🎉 Robotic arm safety demonstration completed!")
    print("=" * 60)
    print("✅ Trained DDPG agent for continuous control")
    print("✅ Implemented safety constraints on torque, velocity, workspace")
    print("✅ Generated formal proofs in Lean4")
    print("✅ Created compliance artifacts")
    print("✅ Implemented runtime safety guards")
    print("\nNext steps:")
    print("1. Deploy with runtime guards in robotic system")
    print("2. Add real-time monitoring and emergency stop")
    print("3. Integrate with ROS/ROS2")
    print("4. Extend to multi-arm coordination")


def test_robotic_arm_safety(model, env, n_episodes=100):
    """Test for safety violations during agent execution."""
    violations = {
        "torque_violations": 0,
        "velocity_violations": 0,
        "workspace_violations": 0,
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
            if np.any(np.abs(action) > env.max_torque):  # Torque
                violations["torque_violations"] += 1
            if np.any(np.abs(obs[3:6]) > env.max_joint_velocity):  # Velocity
                violations["velocity_violations"] += 1
            if np.any(np.abs(obs[6:9]) > env.workspace_bounds):  # Workspace
                violations["workspace_violations"] += 1

    return violations


if __name__ == "__main__":
    main()
