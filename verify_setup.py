#!/usr/bin/env python3
"""
SafeRL ProofStack Setup Verification Script
Tests all components to ensure the environment is properly configured.
"""

import sys
import importlib
from pathlib import Path


def test_import(module_name, description):
    """Test if a module can be imported successfully."""
    try:
        importlib.import_module(module_name)
        print(f"✅ {description}: {module_name}")
        return True
    except ImportError as e:
        print(f"❌ {description}: {module_name} - {e}")
        return False


def test_poetry_environment():
    """Test Poetry environment and dependencies."""
    print("🔧 Testing Poetry Environment...")

    # Test core dependencies
    core_deps = [
        ("gymnasium", "RL Environment"),
        ("stable_baselines3", "RL Algorithms"),
        ("torch", "PyTorch"),
        ("httpx", "HTTP Client"),
        ("weasyprint", "PDF Generation"),
        ("pytest", "Testing Framework"),
        ("black", "Code Formatter"),
        ("ruff", "Linter"),
        ("mypy", "Type Checker"),
    ]

    success_count = 0
    for module, desc in core_deps:
        if test_import(module, desc):
            success_count += 1

    # Test documentation dependencies
    print("\n📚 Testing Documentation Dependencies...")
    doc_deps = [
        ("mkdocs", "MkDocs"),
        ("mkdocs_material", "Material Theme"),
        ("mkdocs_mermaid2_plugin", "Mermaid Diagrams"),
        ("mkdocs_click", "CLI Documentation"),
    ]

    for module, desc in doc_deps:
        if test_import(module, desc):
            success_count += 1

    return success_count, len(core_deps) + len(doc_deps)


def test_proofstack_modules():
    """Test ProofStack internal modules."""
    print("\n🧠 Testing ProofStack Modules...")

    # Add current directory to path
    sys.path.insert(0, str(Path(__file__).parent))

    proofstack_modules = [
        ("proofstack", "Main Package"),
        ("proofstack.pipeline", "Pipeline"),
        ("proofstack.specgen", "Specification Generator"),
        ("proofstack.prover_api", "Prover API"),
        ("proofstack.attestation", "Attestation"),
        ("proofstack.guard_codegen", "Guard Code Generator"),
        ("proofstack.rl.algorithms", "RL Algorithms"),
    ]

    success_count = 0
    for module, desc in proofstack_modules:
        if test_import(module, desc):
            success_count += 1

    return success_count, len(proofstack_modules)


def test_cli_functionality():
    """Test CLI functionality."""
    print("\n🖥️  Testing CLI Functionality...")

    try:
        from proofstack.cli import app

        print("✅ CLI App: proofstack.cli.app")
        return True
    except Exception as e:
        print(f"❌ CLI App: proofstack.cli.app - {e}")
        return False


def test_example_scripts():
    """Test example scripts exist and are valid."""
    print("\n📝 Testing Example Scripts...")

    examples_dir = Path(__file__).parent / "examples"
    if not examples_dir.exists():
        print("❌ Examples directory not found")
        return False

    example_files = [
        "compressor_policy.py",
        "cartpole_policy.py",
        "robotic_arm_policy.py",
        "generate_bundle.py",
    ]

    success_count = 0
    for example in example_files:
        example_path = examples_dir / example
        if example_path.exists():
            print(f"✅ Example: {example}")
            success_count += 1
        else:
            print(f"❌ Example: {example} - not found")

    return success_count, len(example_files)


def test_documentation_setup():
    """Test documentation setup."""
    print("\n📖 Testing Documentation Setup...")

    docs_dir = Path(__file__).parent / "docs"
    mkdocs_config = Path(__file__).parent / "mkdocs.yml"

    success_count = 0

    if docs_dir.exists():
        print("✅ Documentation directory: docs/")
        success_count += 1
    else:
        print("❌ Documentation directory: docs/ - not found")

    if mkdocs_config.exists():
        print("✅ MkDocs configuration: mkdocs.yml")
        success_count += 1
    else:
        print("❌ MkDocs configuration: mkdocs.yml - not found")

    return success_count, 2


def main():
    """Run all verification tests."""
    print("🚀 SafeRL ProofStack Setup Verification")
    print("=" * 50)

    total_success = 0
    total_tests = 0

    # Test Poetry environment
    success, count = test_poetry_environment()
    total_success += success
    total_tests += count

    # Test ProofStack modules
    success, count = test_proofstack_modules()
    total_success += success
    total_tests += count

    # Test CLI
    if test_cli_functionality():
        total_success += 1
    total_tests += 1

    # Test examples
    success, count = test_example_scripts()
    total_success += success
    total_tests += count

    # Test documentation
    success, count = test_documentation_setup()
    total_success += success
    total_tests += count

    # Summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    print(f"✅ Passed: {total_success}/{total_tests}")
    print(f"📈 Success Rate: {(total_success/total_tests)*100:.1f}%")

    if total_success == total_tests:
        print("\n🎉 All tests passed! SafeRL ProofStack is ready to use.")
        print("\n📋 Next steps:")
        print("  1. Run: poetry run proofstack init cartpole")
        print("  2. Run: poetry run proofstack train --algo ppo --timesteps 1000")
        print("  3. Run: poetry run proofstack bundle")
        print("  4. Build docs: poetry run mkdocs build")
    else:
        print(
            f"\n⚠️  {total_tests - total_success} test(s) failed. Please check the errors above."
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
