"""Pytest and Hypothesis configuration for stable CI across platforms."""

from hypothesis import settings

# Property-based tests touch disk and coverage; default 200ms deadline flakes on Windows/CI.
settings.register_profile("proofstack", deadline=None)
settings.load_profile("proofstack")
