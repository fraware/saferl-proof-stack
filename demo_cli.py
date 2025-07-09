#!/usr/bin/env python3
"""
Demo script showcasing SafeRL ProofStack CLI functionality.
This demonstrates the one-command UX for RL safety proofs.
"""

import sys
import os
import shutil
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from proofstack.cli import app


def demo_cli_workflow():
    """Demonstrate the complete CLI workflow."""
    print("🎬 SafeRL ProofStack CLI Demo")
    print("=" * 50)
    print("This demo showcases the one-command UX for RL safety proofs.")
    print()

    # Clean up any existing demo directories
    demo_dir = Path("demo_cartpole")
    if demo_dir.exists():
        shutil.rmtree(demo_dir)

    print("🚀 Step 1: Initialize a new project")
    print("-" * 40)
    print("Command: proofstack init cartpole --output demo_cartpole")
    sys.argv = ["proofstack", "init", "cartpole", "--output", "demo_cartpole"]
    try:
        app()
        print("✅ Project initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize project: {e}")
        return False

    print("\n📁 Project structure created:")
    for item in demo_dir.rglob("*"):
        if item.is_file():
            print(f"  📄 {item.relative_to(demo_dir)}")

    print("\n🚀 Step 2: Generate safety bundle (mock mode)")
    print("-" * 40)
    print("Command: proofstack bundle --mock --spec demo_cartpole/safety_spec.yaml")
    sys.argv = [
        "proofstack",
        "bundle",
        "--mock",
        "--spec",
        "demo_cartpole/safety_spec.yaml",
    ]
    try:
        app()
        print("✅ Safety bundle generated successfully!")
    except Exception as e:
        print(f"❌ Failed to generate bundle: {e}")
        return False

    print("\n📦 Generated artifacts:")
    bundle_dir = Path("attestation_bundle")
    if bundle_dir.exists():
        for artifact in bundle_dir.glob("*"):
            if artifact.is_file():
                size = artifact.stat().st_size
                print(f"  📄 {artifact.name} ({size} bytes)")

    print("\n🎉 Demo completed successfully!")
    print("=" * 50)
    print("✅ CLI workflow is working correctly")
    print("✅ One-command UX is functional")
    print("✅ Mock mode works for offline development")
    print()
    print("Next steps:")
    print("1. Set FIREWORKS_API_KEY for real proof generation")
    print("2. Try: proofstack train --algo ppo --timesteps 1000")
    print("3. Try: proofstack bundle --watch (for real-time updates)")
    print("4. Check out the generated attestation.html")

    return True


def demo_cli_help():
    """Show CLI help information."""
    print("\n📋 CLI Help Information")
    print("-" * 40)
    sys.argv = ["proofstack", "--help"]
    try:
        app()
    except SystemExit:
        pass  # Expected behavior


def demo_version():
    """Show version information."""
    print("\n📋 Version Information")
    print("-" * 40)
    sys.argv = ["proofstack", "version"]
    try:
        app()
    except SystemExit:
        pass  # Expected behavior


if __name__ == "__main__":
    print("🎬 SafeRL ProofStack CLI Demo")
    print("=" * 50)

    # Show help and version
    demo_cli_help()
    demo_version()

    # Run the main demo
    success = demo_cli_workflow()

    if not success:
        print("\n❌ Demo failed!")
        sys.exit(1)

    print("\n🎬 Demo completed! Check out the generated files:")
    print("  📁 demo_cartpole/ - Project structure")
    print("  📁 attestation_bundle/ - Compliance artifacts")
    print("  📄 demo_cartpole/safety_spec.yaml - Safety specification")
    print("  📄 attestation_bundle/attestation.html - Compliance report")
