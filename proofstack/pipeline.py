from proofstack.specgen import SpecGen
from proofstack.prover_api import ProverAPI
from proofstack.attestation import Attestation
from proofstack.guard_codegen import GuardGen
from proofstack.cache import ProofCache


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
            if hasattr(self.spec, "invariants") and "invariants" in safety_spec:
                self.spec.invariants = safety_spec["invariants"]
            if hasattr(self.spec, "guard") and "guard" in safety_spec:
                self.spec.guard = safety_spec["guard"]
            if hasattr(self.spec, "lemmas") and "lemmas" in safety_spec:
                self.spec.lemmas = safety_spec["lemmas"]
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
        if cache_hit:
            print("[ProofCache] Cache hit: reused proof sketch.")
        else:
            print("[ProofCache] Cache miss: generated new proof.")
        return bundle
