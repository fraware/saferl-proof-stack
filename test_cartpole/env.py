"""Environment wrapper for cartpole."""
import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

def make_env():
    """Create the environment."""
    return gym.make("cartpole-v1")

def train_agent(env, total_timesteps=10000):
    """Train an agent using PPO."""
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=total_timesteps)
    return model

if __name__ == "__main__":
    env = make_env()
    model = train_agent(env)
    model.save("ppo_cartpole.zip")
