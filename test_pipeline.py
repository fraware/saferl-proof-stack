#!/usr/bin/env python3
import sys

sys.path.append(".")

print("Testing ProofPipeline step by step...")

# Test 1: Import
try:
    from proofstack import ProofPipeline, SpecGen, ProverAPI, Attestation, GuardGen

    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Create components
try:

    class SafetySpec:
        def __init__(self, invariants, guard, lemmas):
            self.invariants = invariants
            self.guard = guard
            self.lemmas = lemmas

    class CartPoleEnv:
        def __init__(self):
            self.observation_space = None
            self.action_space = None

        def safety_invariant(self, state):
            cart_pos, cart_vel, pole_ang, pole_vel = state
            return abs(cart_pos) <= 2.4 and abs(pole_ang) <= 0.2095

    spec = SafetySpec(
        invariants=["|σ.cart_position| ≤ 2.4", "|σ.pole_angle| ≤ 0.2095"],
        guard=["|σ.cart_position| ≤ 2.3", "|σ.pole_angle| ≤ 0.2", "|a.force| ≤ 10.0"],
        lemmas=["position_step_bound", "angle_step_preserved"],
    )
    env = CartPoleEnv()
    print("✅ Components created successfully")
except Exception as e:
    print(f"❌ Component creation failed: {e}")
    sys.exit(1)

# Test 3: Create ProofPipeline
try:
    api_key = "fw_3ZWuySSrYa944mmbG756d6fc"
    pipeline = ProofPipeline(env, spec, api_key=api_key)
    print("✅ ProofPipeline created successfully")
except Exception as e:
    print(f"❌ ProofPipeline creation failed: {e}")
    sys.exit(1)

# Test 4: Run pipeline
try:
    print("🚀 Running pipeline...")
    bundle = pipeline.run()
    print("✅ Pipeline completed successfully!")
    print(f"📦 Bundle location: {getattr(bundle, 'path', 'output/')}")
except Exception as e:
    print(f"❌ Pipeline execution failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("🎉 All tests passed!")
