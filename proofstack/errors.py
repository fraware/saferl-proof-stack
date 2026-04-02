"""Typed exception hierarchy for ProofStack runtime."""


class ProofStackError(Exception):
    """Base exception for ProofStack failures."""


class ConfigurationError(ProofStackError):
    """Raised when configuration is missing or invalid."""


class ValidationError(ProofStackError):
    """Raised when input payloads are invalid."""


class ProverAPIError(ProofStackError):
    """Raised when the remote prover API returns invalid output."""


class ProverNetworkError(ProofStackError):
    """Raised when prover calls fail due to transport/network errors."""


class ArtifactGenerationError(ProofStackError):
    """Raised when a required artifact cannot be generated."""


class BundleNotFoundError(ProofStackError):
    """Raised when a requested bundle does not exist."""
