import hashlib
import json
from pathlib import Path
from typing import Any, Optional

CACHE_DIR = Path(".proofstack_cache")
CACHE_DIR.mkdir(exist_ok=True)


class ProofCache:
    """
    Lazy proof-sketch cache for Lean proofs.
    Keyed by (spec_sha256, algo, mathlib_commit).
    Stores proof sketches as JSON files in .proofstack_cache/.
    """

    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_key(self, spec_sha256: str, algo: str, mathlib_commit: str) -> str:
        return f"{spec_sha256}_{algo}_{mathlib_commit}"

    def _cache_path(self, key: str) -> Path:
        # Hash keys so algo/mathlib segments cannot inject path separators or reserved names.
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{digest}.json"

    def get(
        self, spec_sha256: str, algo: str, mathlib_commit: str
    ) -> Optional[dict[str, Any]]:
        """Return cached proof sketch if present, else None."""
        key = self._cache_key(spec_sha256, algo, mathlib_commit)
        path = self._cache_path(key)
        if path.exists():
            try:
                with open(path, encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return None
        return None

    def set(
        self,
        spec_sha256: str,
        algo: str,
        mathlib_commit: str,
        proof_sketch: dict[str, Any],
    ) -> None:
        """Store proof sketch in cache."""
        key = self._cache_key(spec_sha256, algo, mathlib_commit)
        path = self._cache_path(key)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(proof_sketch, f, indent=2)

    def clear(self) -> None:
        """Clear the entire cache."""
        for file in self.cache_dir.glob("*.json"):
            file.unlink()

    @staticmethod
    def compute_spec_sha256(spec: str) -> str:
        """Compute SHA256 hash of the spec string."""
        return hashlib.sha256(spec.encode("utf-8")).hexdigest()
