import time
from unittest.mock import patch

from proofstack.pipeline import ProofPipeline


class _Spec:
    invariants = ["|σ.cart_position| ≤ 2.4"]
    guard = ["|a.force| ≤ 10.0"]
    lemmas = []


def test_pipeline_latency_budget_seconds():
    budget_seconds = 2.0
    pipeline = ProofPipeline(env=None, safety_spec=_Spec(), api_key="test-key")
    with patch("proofstack.prover_api.ProverAPI.complete", return_value="by trivial"):
        start = time.perf_counter()
        pipeline.run(reuse_cache=False)
        elapsed = time.perf_counter() - start
    assert elapsed < budget_seconds, f"Pipeline exceeded latency budget: {elapsed:.3f}s"
