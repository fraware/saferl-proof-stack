import gymnasium as gym
from proofstack.rl.algorithms import create_safe_algorithm


def train_compressor_policy(total_timesteps: int = 10_000) -> str:
    """Train a safety-constrained policy and return saved model path."""
    env = gym.make("CartPole-v1")
    safe_algo = create_safe_algorithm("ppo", env)
    safe_algo.train(total_timesteps=total_timesteps)
    output_path = "ppo_cartpole_safe.zip"
    safe_algo.save(output_path)
    return output_path


if __name__ == "__main__":
    artifact = train_compressor_policy()
    print(f"Trained safe PPO agent saved as '{artifact}'")
