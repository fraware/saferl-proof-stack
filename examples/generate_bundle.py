# Example: Generate proof bundle using ProofPipeline
import os
import sys

sys.path.append(".")

from proofstack import ProofPipeline


# Real SafetySpec class for CartPole environment
class SafetySpec:
    def __init__(self, invariants, guard, lemmas):
        self.invariants = invariants
        self.guard = guard
        self.lemmas = lemmas


# Real CartPole environment wrapper
class CartPoleEnv:
    def __init__(self):
        self.observation_space = None  # Will be set by gym
        self.action_space = None  # Will be set by gym

    def safety_invariant(self, state):
        # CartPole safety: cart position and pole angle within bounds
        cart_pos, cart_vel, pole_ang, pole_vel = state
        return abs(cart_pos) <= 2.4 and abs(pole_ang) <= 0.2095


if __name__ == "__main__":
    # Real safety specs for CartPole
    spec = SafetySpec(
        invariants=["|σ.cart_position| ≤ 2.4", "|σ.pole_angle| ≤ 0.2095"],
        guard=[
            "|σ.cart_position| ≤ 2.3",  # Conservative bound
            "|σ.pole_angle| ≤ 0.2",  # Conservative bound
            "|a.force| ≤ 10.0",  # Action bound
        ],
        lemmas=["position_step_bound", "angle_step_preserved"],
    )

    env = CartPoleEnv()

    # Use the provided Fireworks API key
    api_key = "fw_3ZWuySSrYa944mmbG756d6fc"

    print("🚀 Starting SafeRL ProofStack pipeline...")
    print("📝 Environment: CartPole-v1")
    print("🔒 Safety specs loaded")
    print("🔑 Using Fireworks API for proof generation")

    try:
        bundle = ProofPipeline(env, spec, api_key=api_key).run()
        print("✅ Proof bundle generated successfully!")
        print(f"📦 Bundle location: {getattr(bundle, 'path', 'output/')}")
        print("🎉 End-to-end workflow completed!")

    except Exception as e:
        print(f"❌ Error during proof generation: {e}")
        print("💡 Check your API key and network connection")
