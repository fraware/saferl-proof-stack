# SafeRL ProofStack - Cache Implementation

## Overview

The SafeRL ProofStack includes a sophisticated proof caching system that reduces LLM API calls and improves development iteration speed by intelligently detecting specification changes and reusing cached proofs when appropriate.

## Key Features

### 1. SHA256-Based Mutation Detection

- **Purpose**: Detect when safety specifications have changed
- **Implementation**: Uses SHA256 hashing of the complete specification
- **Benefits**:
  - Avoids cache hits for modified specs
  - Ensures new proofs are generated when needed
  - Maintains proof correctness

### 2. Multi-Dimensional Cache Keys

- **Components**: `(spec_sha256, algorithm, mathlib_commit)`
- **Isolation**: Different algorithms (PPO, SAC, DDPG) have separate caches
- **Version Safety**: Different mathlib commits are isolated
- **Benefits**: Prevents cross-contamination between different configurations

### 3. Lazy Proof-Sketch Caching

- **Storage**: JSON files in `.proofstack_cache/` directory
- **Format**: Structured proof sketches with tactics and metadata
- **Persistence**: Survives across development sessions
- **Benefits**: Reduces expensive LLM API calls

## Implementation Details

### Cache Class (`proofstack/cache.py`)

```python
class ProofCache:
    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir

    def get(self, spec_sha256: str, algo: str, mathlib_commit: str) -> Optional[Dict[str, Any]]:
        """Return cached proof sketch if present, else None."""

    def set(self, spec_sha256: str, algo: str, mathlib_commit: str, proof_sketch: Dict[str, Any]) -> None:
        """Store proof sketch in cache."""

    @staticmethod
    def compute_spec_sha256(spec: str) -> str:
        """Compute SHA256 hash of the spec string."""
```

### Pipeline Integration (`proofstack/pipeline.py`)

The cache is seamlessly integrated into the proof pipeline:

```python
def run(self, reuse_cache: bool = True, mathlib_commit: str = "latest", algo: str = "ppo"):
    lean_file = self.spec.emit_lean(algorithm_name=algo)
    spec_sha256 = ProofCache.compute_spec_sha256(lean_file)

    # Check cache first
    if reuse_cache:
        cached = self.cache.get(spec_sha256, algo, mathlib_commit)
        if cached and "proof" in cached:
            proof = cached["proof"]
            cache_hit = True

    # Generate new proof if needed
    if not proof:
        proof = self.prover.complete(lean_file)
        if reuse_cache:
            self.cache.set(spec_sha256, algo, mathlib_commit, {"proof": proof})
```

### CLI Integration (`proofstack/cli.py`)

Cache control is available via CLI:

```bash
proofstack bundle --reuse-cache  # Default: enabled
proofstack bundle --no-reuse-cache  # Disable cache
```

## Usage Examples

### Basic Usage

```python
from proofstack import ProofPipeline

# First run - generates and caches proof
pipeline = ProofPipeline(env, spec, api_key)
bundle1 = pipeline.run(reuse_cache=True, algo="ppo")

# Second run with same spec - cache hit!
bundle2 = pipeline.run(reuse_cache=True, algo="ppo")
# Output: [ProofCache] Cache hit: reused proof sketch.
```

### Mutation Detection

```python
# Original spec
spec1 = {"invariants": ["|σ.cart_position| ≤ 2.4"]}
bundle1 = pipeline.run(reuse_cache=True, algo="ppo")

# Modified spec - cache miss!
spec2 = {"invariants": ["|σ.cart_position| ≤ 2.5"]}
bundle2 = pipeline.run(reuse_cache=True, algo="ppo")
# Output: [ProofCache] Cache miss: generated new proof.
```

### Algorithm Isolation

```python
# PPO algorithm
bundle_ppo = pipeline.run(reuse_cache=True, algo="ppo")

# SAC algorithm - separate cache
bundle_sac = pipeline.run(reuse_cache=True, algo="sac")
```

## Testing

### Comprehensive Test Suite (`tests/test_cache.py`)

The cache implementation includes extensive testing:

- **Basic Functionality**: Set/get operations
- **Mutation Detection**: SHA256-based change detection
- **Algorithm Isolation**: PPO vs SAC vs DDPG isolation
- **Mathlib Commit Isolation**: Version-specific caching
- **Edge Cases**: Unicode, empty specs, malformed files
- **Performance**: Large data structures, concurrent access

### Basic Test Script (`test_cache_basic.py`)

A standalone test script that can be run without complex dependencies:

```bash
python test_cache_basic.py
```

### Demonstration Script (`demo_cache_mutation.py`)

Interactive demonstration of cache features:

```bash
python demo_cache_mutation.py
```

## Performance Benefits

### Cost Reduction

- **LLM API Calls**: Significantly reduced for repeated specs
- **Development Speed**: Faster iteration during development
- **Resource Usage**: Lower computational overhead

### Example Performance Metrics

```
Cache Performance Summary:
   Total requests: 6
   Cache hits: 3
   Cache misses: 3
   Hit rate: 50.0%
   LLM calls saved: 3
```

## Configuration

### Cache Directory

- **Default**: `.proofstack_cache/` in project root
- **Custom**: Can be specified during ProofCache initialization
- **Cleanup**: Use `cache.clear()` to remove all cached files

### Cache Control

- **Enable**: `--reuse-cache` (default)
- **Disable**: `--no-reuse-cache`
- **Runtime**: Can be controlled programmatically

## Best Practices

### 1. Cache Management

- Clear cache when switching between major spec versions
- Monitor cache size for large projects
- Use different cache directories for different environments

### 2. Development Workflow

- Enable cache during development for faster iteration
- Disable cache for final verification runs
- Use cache to experiment with different spec variations

### 3. Debugging

- Check cache hits/misses in pipeline output
- Verify cache isolation between algorithms
- Monitor cache file contents for debugging

## Troubleshooting

### Common Issues

1. **Unexpected Cache Misses**

   - Check if spec content has changed
   - Verify algorithm and mathlib commit match
   - Ensure cache directory is writable

2. **Cache Corruption**

   - Clear cache directory: `cache.clear()`
   - Check for malformed JSON files
   - Verify file permissions

3. **Performance Issues**
   - Monitor cache directory size
   - Check for excessive cache misses
   - Verify cache key generation

### Debug Commands

```python
# Check cache contents
cache_dir = Path(".proofstack_cache")
for file in cache_dir.glob("*.json"):
    print(f"Cache file: {file.name}")

# Verify hash computation
spec = "your_spec_here"
hash = ProofCache.compute_spec_sha256(spec)
print(f"Spec hash: {hash}")
```

## Future Enhancements

### Planned Features

1. **Cache Compression**: Reduce storage requirements
2. **Cache Expiration**: Automatic cleanup of old entries
3. **Distributed Caching**: Share cache across team members
4. **Cache Analytics**: Detailed usage statistics
5. **Smart Invalidation**: Partial cache invalidation

### Integration Opportunities

1. **CI/CD Integration**: Cache sharing across builds
2. **Cloud Storage**: Remote cache storage
3. **Cache Warming**: Pre-populate cache with common specs
4. **Cache Validation**: Verify cached proofs are still valid

## Conclusion

The SafeRL ProofStack cache implementation provides significant performance benefits while maintaining proof correctness through intelligent mutation detection. The multi-dimensional cache keys ensure proper isolation between different algorithms and mathlib versions, while the SHA256-based hashing guarantees that specification changes trigger new proof generation.

This caching system is essential for efficient development workflows and cost-effective deployment of safety-critical RL systems.
