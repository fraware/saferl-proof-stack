from proofstack.attestation import Attestation
from proofstack.cache import ProofCache
from proofstack.guard_codegen import GuardGen
from proofstack.observability import get_logger, log_event
from proofstack.prover_api import ProverAPI
from proofstack.specgen import SpecGen

LOGGER = get_logger(__name__)


class ProofPipeline:
    """
    Orchestrates the end-to-end proof and attestation pipeline.
    Converts environment and safety spec into Lean, calls prover, generates guard code, and bundles compliance artifacts.
    """

    def __init__(
        self, env, safety_spec, api_key, prover="fireworks/deepseek-prover-v2"
    ):
        self.env = env
        self.spec = SpecGen()
        # Populate spec fields from safety_spec dict if provided
        if safety_spec:
            if hasattr(safety_spec, "invariants"):
                self.spec.invariants = list(safety_spec.invariants)
            elif isinstance(safety_spec, dict):
                self.spec.invariants = safety_spec.get("invariants", [])
            if hasattr(safety_spec, "guard"):
                self.spec.guard = list(safety_spec.guard)
            elif isinstance(safety_spec, dict):
                self.spec.guard = safety_spec.get("guard", [])
            if hasattr(safety_spec, "lemmas"):
                self.spec.lemmas = list(safety_spec.lemmas)
            elif isinstance(safety_spec, dict):
                self.spec.lemmas = safety_spec.get("lemmas", [])
        self.prover = ProverAPI(api_key=api_key, model=prover)
        self.attestation = Attestation()
        self.guardgen = GuardGen()
        self.cache = ProofCache()

    def run(
        self,
        reuse_cache: bool = True,
        mathlib_commit: str = "latest",
        algo: str = "ppo",
    ):
        """
        Runs the full pipeline: emits Lean, proves (with cache), writes proof, emits guard, bundles attestation.
        Returns the attestation bundle object.
        """
        lean_file = self.spec.emit_lean(algorithm_name=algo)
        spec_sha256 = ProofCache.compute_spec_sha256(lean_file)
        cache_hit = False
        proof = None
        if reuse_cache:
            cached = self.cache.get(spec_sha256, algo, mathlib_commit)
            if cached and "proof" in cached:
                proof = cached["proof"]
                cache_hit = True
        if not proof:
            proof = self.prover.complete(lean_file)
            if reuse_cache:
                self.cache.set(spec_sha256, algo, mathlib_commit, {"proof": proof})
        self.spec.write_proof(proof)
        self.guardgen.emit_c(self.spec)
        bundle = self.attestation.bundle(self.spec, self.guardgen, algorithm=algo)
        log_event(
            LOGGER,
            "pipeline_run_completed",
            cache_hit=cache_hit,
            algorithm=algo,
            bundle_path=bundle.path,
        )
        return bundle
