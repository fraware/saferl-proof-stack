"""Multi-algorithm support for SafeRL ProofStack."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import gymnasium as gym
import numpy as np

from stable_baselines3 import PPO, SAC, DDPG
from stable_baselines3.common.base_class import BaseAlgorithm


class SafeAlgorithmAdapter(ABC):
    """Abstract base class for safe RL algorithm adapters."""

    def __init__(self, env: gym.Env, **kwargs):
        """Initialize the algorithm adapter.

        Args:
            env: Gymnasium environment
            **kwargs: Algorithm-specific parameters
        """
        self.env = env
        self.kwargs = kwargs
        self.model: Optional[BaseAlgorithm] = None
        self.algorithm_name = self._get_algorithm_name()

    @abstractmethod
    def _get_algorithm_name(self) -> str:
        """Get the algorithm name for Lean template generation."""
        pass

    @abstractmethod
    def _create_model(self) -> BaseAlgorithm:
        """Create the underlying RL model."""
        pass

    @abstractmethod
    def _apply_safety_constraints(
        self, action: np.ndarray, state: np.ndarray
    ) -> np.ndarray:
        """Apply safety constraints to actions.

        Args:
            action: Raw action from the model
            state: Current state

        Returns:
            Safe action
        """
        pass

    @abstractmethod
    def _calculate_safety_reward(
        self, reward: float, state: np.ndarray, action: np.ndarray
    ) -> float:
        """Calculate safety-adjusted reward.

        Args:
            reward: Original reward
            state: Current state
            action: Applied action

        Returns:
            Safety-adjusted reward
        """
        pass

    def create_model(self) -> BaseAlgorithm:
        """Create and return the RL model."""
        self.model = self._create_model()
        return self.model

    def train(self, total_timesteps: int, **kwargs) -> None:
        """Train the model with safety considerations."""
        if self.model is None:
            self.create_model()

        # Create a safety wrapper for training
        safe_env = SafeEnvWrapper(self.env, self)
        self.model.set_env(safe_env)
        self.model.learn(total_timesteps=total_timesteps, **kwargs)

    def predict(self, observation: np.ndarray, deterministic: bool = True) -> tuple:
        """Predict action with safety constraints."""
        if self.model is None:
            raise ValueError("Model not created. Call create_model() first.")

        action, state = self.model.predict(observation, deterministic=deterministic)
        safe_action = self._apply_safety_constraints(action, observation)
        return safe_action, state

    def save(self, path: str) -> None:
        """Save the trained model."""
        if self.model is None:
            raise ValueError("No model to save. Train first.")
        self.model.save(path)


class PPOSafeAdapter(SafeAlgorithmAdapter):
    """Safe PPO algorithm adapter."""

    def _get_algorithm_name(self) -> str:
        return "ppo"

    def _create_model(self) -> BaseAlgorithm:
        return PPO("MlpPolicy", self.env, verbose=0, **self.kwargs)

    def _apply_safety_constraints(
        self, action: np.ndarray, state: np.ndarray
    ) -> np.ndarray:
        """Apply action masking for discrete actions."""
        # For discrete actions, mask unsafe actions
        if hasattr(self.env.action_space, "n"):
            # Discrete action space
            safe_actions = self._get_safe_actions(state)
            if len(safe_actions) == 0:
                # No safe actions, return the original action
                return action

            # If current action is unsafe, choose a safe alternative
            if action not in safe_actions:
                action = np.random.choice(safe_actions)

        return action

    def _calculate_safety_reward(
        self, reward: float, state: np.ndarray, action: np.ndarray
    ) -> float:
        """Calculate safety-adjusted reward for PPO."""
        # Add safety penalty based on state proximity to unsafe regions
        safety_penalty = self._calculate_safety_penalty(state)
        return reward - safety_penalty

    def _get_safe_actions(self, state: np.ndarray) -> list:
        """Get list of safe actions for current state."""
        # This would be implemented based on the specific environment
        # For now, return all actions as safe
        return list(range(self.env.action_space.n))

    def _calculate_safety_penalty(self, state: np.ndarray) -> float:
        """Calculate safety penalty based on state."""
        # Example: penalty for being close to unsafe regions
        penalty = 0.0

        # CartPole-specific safety penalty
        if hasattr(self.env, "observation_space") and len(state) >= 4:
            cart_pos, cart_vel, pole_ang, pole_vel = state[:4]

            # Penalty for being close to position limits
            if abs(cart_pos) > 2.0:
                penalty += (abs(cart_pos) - 2.0) * 10.0

            # Penalty for being close to angle limits
            if abs(pole_ang) > 0.15:
                penalty += (abs(pole_ang) - 0.15) * 50.0

        return penalty


class SACSafeAdapter(SafeAlgorithmAdapter):
    """Safe SAC algorithm adapter."""

    def _get_algorithm_name(self) -> str:
        return "sac"

    def _create_model(self) -> BaseAlgorithm:
        return SAC("MlpPolicy", self.env, verbose=0, **self.kwargs)

    def _apply_safety_constraints(
        self, action: np.ndarray, state: np.ndarray
    ) -> np.ndarray:
        """Apply action clipping for continuous actions."""
        # For continuous actions, clip to safe bounds
        if hasattr(self.env.action_space, "low") and hasattr(
            self.env.action_space, "high"
        ):
            # Continuous action space
            safe_low = self.env.action_space.low * 0.8  # Conservative bounds
            safe_high = self.env.action_space.high * 0.8
            action = np.clip(action, safe_low, safe_high)

        return action

    def _calculate_safety_reward(
        self, reward: float, state: np.ndarray, action: np.ndarray
    ) -> float:
        """Calculate safety-adjusted reward for SAC."""
        # Add safety penalty based on action magnitude and state
        action_penalty = np.sum(np.square(action)) * 0.01  # Penalize large actions
        state_penalty = self._calculate_safety_penalty(state)
        return reward - action_penalty - state_penalty

    def _calculate_safety_penalty(self, state: np.ndarray) -> float:
        """Calculate safety penalty based on state."""
        penalty = 0.0

        # Continuous control safety penalty
        if len(state) >= 4:
            # Example: penalty for extreme values
            for i, val in enumerate(state):
                if abs(val) > 0.8:
                    penalty += (abs(val) - 0.8) * 5.0

        return penalty


class DDPGSafeAdapter(SafeAlgorithmAdapter):
    """Safe DDPG algorithm adapter."""

    def _get_algorithm_name(self) -> str:
        return "ddpg"

    def _create_model(self) -> BaseAlgorithm:
        return DDPG("MlpPolicy", self.env, verbose=0, **self.kwargs)

    def _apply_safety_constraints(
        self, action: np.ndarray, state: np.ndarray
    ) -> np.ndarray:
        """Apply action clipping and velocity limits for DDPG."""
        # For continuous actions, apply conservative clipping
        if hasattr(self.env.action_space, "low") and hasattr(
            self.env.action_space, "high"
        ):
            # More conservative bounds for DDPG
            safe_low = self.env.action_space.low * 0.7
            safe_high = self.env.action_space.high * 0.7
            action = np.clip(action, safe_low, safe_high)

        return action

    def _calculate_safety_reward(
        self, reward: float, state: np.ndarray, action: np.ndarray
    ) -> float:
        """Calculate safety-adjusted reward for DDPG."""
        # Add safety penalty with higher weight for DDPG
        action_penalty = np.sum(np.square(action)) * 0.02  # Higher penalty
        state_penalty = self._calculate_safety_penalty(state)
        return reward - action_penalty - state_penalty

    def _calculate_safety_penalty(self, state: np.ndarray) -> float:
        """Calculate safety penalty based on state."""
        penalty = 0.0

        # DDPG-specific safety penalty (more conservative)
        if len(state) >= 4:
            for i, val in enumerate(state):
                if abs(val) > 0.7:  # More conservative threshold
                    penalty += (abs(val) - 0.7) * 8.0  # Higher penalty

        return penalty


class SafeEnvWrapper(gym.Wrapper):
    """Environment wrapper that applies safety constraints during training."""

    def __init__(self, env: gym.Env, adapter: SafeAlgorithmAdapter):
        super().__init__(env)
        self.adapter = adapter

    def step(self, action):
        # Apply safety constraints
        safe_action = self.adapter._apply_safety_constraints(action, self.state)

        # Take step in environment
        observation, reward, done, truncated, info = self.env.step(safe_action)

        # Calculate safety-adjusted reward
        adjusted_reward = self.adapter._calculate_safety_reward(
            reward, observation, safe_action
        )

        return observation, adjusted_reward, done, truncated, info

    def reset(self, **kwargs):
        observation, info = self.env.reset(**kwargs)
        self.state = observation
        return observation, info


# Algorithm factory
def create_safe_algorithm(
    algorithm: str, env: gym.Env, **kwargs
) -> SafeAlgorithmAdapter:
    """Create a safe algorithm adapter.

    Args:
        algorithm: Algorithm name ('ppo', 'sac', 'ddpg')
        env: Gymnasium environment
        **kwargs: Algorithm-specific parameters

    Returns:
        SafeAlgorithmAdapter instance
    """
    algorithm_map = {
        "ppo": PPOSafeAdapter,
        "sac": SACSafeAdapter,
        "ddpg": DDPGSafeAdapter,
    }

    if algorithm not in algorithm_map:
        raise ValueError(
            f"Unsupported algorithm: {algorithm}. Supported: {list(algorithm_map.keys())}"
        )

    return algorithm_map[algorithm](env, **kwargs)


# Export main classes
__all__ = [
    "SafeAlgorithmAdapter",
    "PPOSafeAdapter",
    "SACSafeAdapter",
    "DDPGSafeAdapter",
    "SafeEnvWrapper",
    "create_safe_algorithm",
]
