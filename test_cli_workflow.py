#!/usr/bin/env python3
"""
Test script for SafeRL ProofStack CLI workflow.
Tests the complete one-command UX from init to bundle generation.
"""

import sys
import os
import shutil
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from proofstack.cli import app


def test_cli_workflow():
    """Test the complete CLI workflow."""
    print("🚀 Testing SafeRL ProofStack CLI Workflow")
    print("=" * 50)

    # Clean up any existing test directories
    test_dirs = ["test_cartpole", "test_lunarlander"]
    for test_dir in test_dirs:
        if Path(test_dir).exists():
            shutil.rmtree(test_dir)

    # Test 1: CLI help
    print("\n📋 Test 1: CLI Help")
    print("-" * 30)
    sys.argv = ["proofstack", "--help"]
    try:
        app()
        print("✅ CLI help works")
    except SystemExit:
        print("✅ CLI help works (exited as expected)")

    # Test 2: Version
    print("\n📋 Test 2: Version")
    print("-" * 30)
    sys.argv = ["proofstack", "version"]
    try:
        app()
        print("✅ Version command works")
    except SystemExit:
        print("✅ Version command works (exited as expected)")

    # Test 3: Project initialization
    print("\n📋 Test 3: Project Initialization")
    print("-" * 30)
    sys.argv = ["proofstack", "init", "cartpole", "--output", "./test_cartpole"]
    try:
        app()
        print("✅ Project initialization works")

        # Verify files were created
        test_dir = Path("test_cartpole")
        expected_files = ["env.py", "safety_spec.yaml", "README.md"]
        for file in expected_files:
            if (test_dir / file).exists():
                print(f"  ✅ {file} created")
            else:
                print(f"  ❌ {file} missing")
                return False

    except Exception as e:
        print(f"❌ Project initialization failed: {e}")
        return False

    # Test 4: Bundle generation with mock
    print("\n📋 Test 4: Bundle Generation (Mock)")
    print("-" * 30)
    sys.argv = [
        "proofstack",
        "bundle",
        "--mock",
        "--spec",
        "test_cartpole/safety_spec.yaml",
    ]
    try:
        app()
        print("✅ Bundle generation works")

        # Verify artifacts were created
        bundle_dir = Path("attestation_bundle")
        if bundle_dir.exists():
            expected_artifacts = [
                "attestation.html",
                "attestation.pdf",
                "sbom.spdx.json",
                "lean_project.sha256",
                "guard.c",
            ]
            for artifact in expected_artifacts:
                if (bundle_dir / artifact).exists():
                    print(f"  ✅ {artifact} created")
                else:
                    print(f"  ❌ {artifact} missing")
                    return False
        else:
            print("  ❌ Bundle directory not created")
            return False

    except Exception as e:
        print(f"❌ Bundle generation failed: {e}")
        return False

    # Test 5: Multiple environment initialization
    print("\n📋 Test 5: Multiple Environments")
    print("-" * 30)
    environments = ["lunarlander", "acrobot", "pendulum"]

    for env in environments:
        sys.argv = ["proofstack", "init", env, "--output", f"./test_{env}"]
        try:
            app()
            print(f"  ✅ {env} project initialized")
        except Exception as e:
            print(f"  ❌ {env} project failed: {e}")
            return False

    print("\n🎉 All CLI tests passed!")
    print("=" * 50)
    print("✅ CLI workflow is working correctly")
    print("✅ One-command UX is functional")
    print("✅ Mock mode works for offline testing")

    return True


if __name__ == "__main__":
    success = test_cli_workflow()
    if not success:
        sys.exit(1)
