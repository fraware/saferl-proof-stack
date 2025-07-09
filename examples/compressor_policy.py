# Example: Compressor Policy RL Script
# Placeholder for training and evaluating a safe RL policy on CompressorEnv

import gymnasium as gym
from stable_baselines3 import PPO

if __name__ == "__main__":
    # Create the environment
    env = gym.make("CartPole-v1")

    # Instantiate the agent
    model = PPO("MlpPolicy", env, verbose=1)

    # Train the agent
    model.learn(total_timesteps=10_000)

    # Save the trained model
    model.save("ppo_cartpole.zip")
    print("Trained PPO agent saved as 'ppo_cartpole.zip'")
