#!/usr/bin/env python3
"""
Compliance Mapping Demo
Demonstrates regulator-grade evidence generation with artifact lineage.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from proofstack.compliance_mapper import ComplianceMapper, ComplianceReport
from proofstack.attestation import Attestation


def demo_compliance_mapping():
    """Demonstrate compliance mapping functionality."""
    print("🔐 SafeRL ProofStack - Compliance Mapping Demo")
    print("=" * 60)

    # Initialize compliance mapper
    mapper = ComplianceMapper()

    print("\n📋 Step 1: Loading Compliance Standards")
    print("-" * 40)
    print(f"✅ Loaded {len(mapper.standards)} standards:")
    for standard_name in mapper.standards.keys():
        print(f"   • {standard_name}")

    # Mock test results
    test_results = {
        "safety_verification_tests": {
            "status": "passed",
            "coverage": 100,
            "test_cases": 25,
            "execution_time": "2.3s",
        },
        "security_tests": {
            "status": "passed",
            "coverage": 95,
            "test_cases": 18,
            "execution_time": "1.8s",
        },
        "integration_tests": {
            "status": "passed",
            "coverage": 88,
            "test_cases": 12,
            "execution_time": "5.2s",
        },
    }

    print("\n🔍 Step 2: Mapping Artifacts to Controls")
    print("-" * 40)

    # Generate compliance report
    compliance_report = mapper.map_artifacts_to_controls(
        lean_file_path="lean_output/safety_proof.lean",
        guard_file_path="attestation_bundle/guard.c",
        sbom_file_path="attestation_bundle/sbom.spdx.json",
        test_results=test_results,
        algorithm="ppo",
    )

    print(
        f"✅ Generated compliance report for {len(compliance_report.control_mappings)} controls"
    )
    print(f"✅ Standards covered: {', '.join(compliance_report.standards)}")
    print(f"✅ Compliance level: {compliance_report.compliance_level}")

    # Display compliance summary
    print("\n📊 Step 3: Compliance Summary")
    print("-" * 40)
    summary = compliance_report.summary
    print(f"Total Controls: {summary['total_controls']}")
    print(f"Compliant: {summary['compliant']}")
    print(f"Partially Compliant: {summary['partially_compliant']}")
    print(f"Non-Compliant: {summary['non_compliant']}")
    print(f"Compliance Rate: {summary['compliance_rate']:.1f}%")

    # Show detailed control mappings
    print("\n🎯 Step 4: Control Mappings")
    print("-" * 40)

    for mapping in compliance_report.control_mappings[:3]:  # Show first 3
        print(f"\n🔸 {mapping.control_id}: {mapping.control_name}")
        print(f"   Status: {mapping.status.upper()}")
        print(f"   Standard: {mapping.standard}")
        print(f"   Evidence: {mapping.evidence_description}")
        print(f"   Verification: {mapping.verification_method}")
        print(f"   Artifacts: {len(mapping.artifacts)} linked")

        for i, artifact in enumerate(mapping.artifacts, 1):
            print(f"     {i}. {artifact.artifact_type}: {artifact.artifact_path}")
            if artifact.line_numbers:
                print(f"        Lines: {artifact.line_numbers}")
            if artifact.description:
                print(f"        Description: {artifact.description}")

    # Generate compliance.json
    print("\n📄 Step 5: Generating compliance.json")
    print("-" * 40)

    compliance_json = mapper.generate_compliance_json(compliance_report)
    compliance_path = Path("attestation_bundle/compliance.json")
    compliance_path.parent.mkdir(exist_ok=True)
    compliance_path.write_text(compliance_json)

    print(f"✅ Generated: {compliance_path}")
    print(f"📏 File size: {compliance_path.stat().st_size} bytes")

    # Show sample of compliance.json
    print("\n📋 Sample compliance.json structure:")
    print("-" * 40)
    compliance_data = json.loads(compliance_json)
    print(
        json.dumps(
            {
                "system_name": compliance_data["system_name"],
                "standards": compliance_data["standards"],
                "compliance_level": compliance_data["compliance_level"],
                "summary": compliance_data["summary"],
                "control_mappings_count": len(compliance_data["control_mappings"]),
            },
            indent=2,
        )
    )

    # Demonstrate attestation bundle with compliance
    print("\n📦 Step 6: Generating Complete Attestation Bundle")
    print("-" * 40)

    attestation = Attestation()

    # Mock spec and guardgen for demo
    class MockSpec:
        def __repr__(self):
            return "SafetySpec(invariants=['safety_constraint'], guards=['action_validation'])"

    class MockGuardGen:
        pass

    bundle = attestation.bundle(MockSpec(), MockGuardGen(), algorithm="ppo")

    print(f"✅ Generated attestation bundle: {bundle.path}")

    # List generated files
    bundle_path = Path(bundle.path)
    if bundle_path.exists():
        print("\n📁 Generated files:")
        for file_path in bundle_path.glob("*"):
            if file_path.is_file():
                size = file_path.stat().st_size
                print(f"   • {file_path.name} ({size} bytes)")

    print("\n🎉 Compliance Mapping Demo Complete!")
    print("=" * 60)
    print("\n📋 Next Steps:")
    print("1. View compliance.json for complete artifact lineage")
    print("2. Open attestation.html for interactive compliance report")
    print("3. Review attestation.pdf for regulatory submission")
    print("4. Use compliance mapping for audit preparation")

    return compliance_report


def demo_artifact_lineage():
    """Demonstrate specific artifact lineage examples."""
    print("\n🔗 Artifact Lineage Examples")
    print("=" * 60)

    # Example 1: Safety Requirements
    print("\n📋 Example 1: Safety Requirements (SW-1)")
    print("-" * 40)
    print("Control: Software Safety Requirements Specification")
    print("Status: ✅ Compliant")
    print("Evidence: Formal specification in Lean4 with mathematical proofs")
    print("\nLinked Artifacts:")
    print("1. Lean Theorem (lean_output/safety_proof.lean:15)")
    print("   ```lean")
    print("   theorem safety_requirement_1 :")
    print("     ∀ (s : State), invariant s → safe_action s")
    print("   ```")
    print("2. SBOM Component (attestation_bundle/sbom.spdx.json)")
    print("   ```json")
    print('   {"SPDXID": "SPDXRef-safety-specification",')
    print('    "name": "Safety Specification",')
    print('    "versionInfo": "1.0.0"}')
    print("   ```")

    # Example 2: System Integrity
    print("\n📋 Example 2: System Integrity (SR-3)")
    print("-" * 40)
    print("Control: System Integrity")
    print("Status: ✅ Compliant")
    print("Evidence: Formal integrity proofs and runtime validation")
    print("\nLinked Artifacts:")
    print("1. Integrity Proof (lean_output/safety_proof.lean:45)")
    print("   ```lean")
    print("   theorem system_integrity :")
    print("     ∀ (s s' : State), transition s s' → integrity_preserved s s'")
    print("   ```")
    print("2. Guard Code (attestation_bundle/guard.c:23)")
    print("   ```c")
    print("   bool validate_integrity(state_t* state) {")
    print("       return check_state_integrity(state) &&")
    print("              verify_safety_constraints(state);")
    print("   }")
    print("   ```")


def main():
    """Run the complete compliance mapping demo."""
    try:
        # Run main compliance mapping demo
        compliance_report = demo_compliance_mapping()

        # Show artifact lineage examples
        demo_artifact_lineage()

        print("\n✅ Demo completed successfully!")
        print("\n🎯 Key Benefits Demonstrated:")
        print("• Complete artifact lineage tracking")
        print("• Regulator-grade evidence generation")
        print("• Automated compliance mapping")
        print("• Interactive compliance reporting")
        print("• Audit-ready documentation")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
