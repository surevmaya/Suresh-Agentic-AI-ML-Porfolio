#!/usr/bin/env python3

import json
from datetime import datetime
import os

# Mock assessment data for testing without API calls
MOCK_ASSESSMENT = """
GMP COMPLIANCE ASSESSMENT REPORT
================================

FACILITY: PharmaCorp Manufacturing Plant
ASSESSMENT DATE: 2025-06-27
AUDITOR: GMP Compliance Agent

1. COMPLIANCE STATUS: PARTIAL COMPLIANCE
   - Overall Rating: 72% Compliant
   - Compliance Grade: B (Acceptable with Deficiencies)

2. CRITICAL ISSUES:
   ⚠ MAJOR - Training Records Incomplete
     * 2 operators missing recent training documentation
     * Urgency: HIGH - Must be addressed within 30 days
     * Impact: Personnel qualification - Critical for product safety

   ⚠ MAJOR - Environmental Monitoring Data Gap
     * Q2 2025 monitoring records missing
     * Urgency: HIGH - Affects batch release decisions
     * Impact: Cannot verify controlled environment conditions

3. OBSERVATIONS AND FINDINGS:
   ✓ Documentation Control: Well-established with electronic system
   ✓ Change Management: Implemented with proper approval workflows
   ⚠ Validation Documentation: Pending validation report for new production line
   ✓ Equipment Maintenance: Preventive maintenance program in place
   ⚠ Deviation Management: Process exists but trending analysis incomplete

4. CORRECTIVE ACTIONS REQUIRED:
   1. Complete operator training records (Priority: CRITICAL)
      - Action: Update training completion records within 1 week
      - Owner: HR Department
      - Evidence Required: Training certificates and competency assessments

   2. Recover/Reconstruct Q2 Environmental Monitoring Data (Priority: CRITICAL)
      - Action: Retrieve data from monitoring equipment logs within 2 weeks
      - Owner: Quality Assurance
      - Evidence Required: Documented investigation report and recovered data

   3. Complete Validation Report for New Production Line (Priority: HIGH)
      - Action: Finalize and approve validation documentation within 30 days
      - Owner: Engineering Department
      - Evidence Required: Signed validation report with IQ/OQ/PQ protocols

   4. Implement Deviation Trending Analysis (Priority: MEDIUM)
      - Action: Establish quarterly trending review process
      - Owner: Quality Management
      - Evidence Required: Trending analysis spreadsheet with corrective action linkage

5. TIMELINE FOR REMEDIATION:
   - Immediate (0-7 days): Critical training records and initial investigation plan
   - Short-term (1-4 weeks): Recovery of environmental data, completion of missing docs
   - Medium-term (1-2 months): Validation report completion, process improvements
   - Follow-up: 60-day verification of all corrective actions

6. DOCUMENTATION GAPS:
   - Training records for 2 operators
   - Environmental monitoring data for Q2 2025
   - Completed validation report for new production line
   - Deviation trending analysis spreadsheet
   - SOPs update history (last review: 18 months ago)

7. RISK ASSESSMENT: MEDIUM RISK
   - Product Safety Risk: MEDIUM - Training gaps could impact quality decisions
   - Regulatory Risk: HIGH - Missing documentation could trigger regulatory action
   - Operational Risk: LOW - Processes are documented and followed
   - Overall: MEDIUM - Manageable with prompt corrective action

8. NEXT AUDIT RECOMMENDATION:
   - Full Facility Audit: 6 months (Q1 2026)
   - Focus Areas: Training program effectiveness, data integrity, new line performance
   - 30-day Verification Audit: Recommended to verify critical corrective actions
   - Mock Audit: Recommended to prepare staff for regulatory inspection

AUDITOR NOTES:
This facility demonstrates a strong quality culture with established systems.
The identified issues are administrative and procedural in nature, not indicating
systemic quality problems. With prompt corrective action, full compliance can be
achieved within 60 days.
"""

def get_mock_assessment(facility_data: dict) -> str:
    """Return mock GMP compliance assessment."""
    return MOCK_ASSESSMENT

def check_gmp_compliance(facility_data: dict, use_api: bool = False) -> dict:
    """
    Analyze facility data for GMP (Good Manufacturing Practice) compliance.

    Args:
        facility_data: Dictionary containing facility information
        use_api: Whether to use real API (requires ANTHROPIC_API_KEY) or mock data

    Returns:
        Dictionary with compliance assessment and recommendations
    """

    if use_api and os.getenv("ANTHROPIC_API_KEY"):
        # Real API call
        import anthropic
        client = anthropic.Anthropic()

        prompt = f"""
        You are a GMP (Good Manufacturing Practice) compliance expert auditor.
        Analyze the following facility data and provide a comprehensive compliance assessment.

        Facility Data:
        {json.dumps(facility_data, indent=2)}

        Please provide:
        1. Compliance Status (Compliant/Non-Compliant/Partial)
        2. Critical Issues (if any)
        3. Observations and Findings
        4. Corrective Actions Required
        5. Timeline for Remediation
        6. Documentation Gaps
        7. Risk Assessment (High/Medium/Low)
        8. Next Audit Recommendation

        Format your response as a structured report.
        """

        message = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        assessment = message.content[0].text
    else:
        # Mock data for testing
        assessment = get_mock_assessment(facility_data)

    return {
        "timestamp": datetime.now().isoformat(),
        "facility_id": facility_data.get("facility_id", "Unknown"),
        "compliance_assessment": assessment,
        "model_used": "mock-data" if not (use_api and os.getenv("ANTHROPIC_API_KEY")) else "claude-opus-4-8"
    }


def generate_compliance_report(assessments: list) -> str:
    """
    Generate a comprehensive compliance report from multiple facility assessments.

    Args:
        assessments: List of compliance assessment results

    Returns:
        Formatted compliance report
    """

    summary = f"""
    GMP COMPLIANCE REPORT
    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

    Total Facilities Assessed: {len(assessments)}

    INDIVIDUAL ASSESSMENTS:
    {json.dumps(assessments, indent=2)}
    """

    return summary


def main():
    """Main function to demonstrate GMP compliance agent."""

    # Example facility data for testing
    test_facility = {
        "facility_id": "FAC-001",
        "name": "PharmaCorp Manufacturing Plant",
        "location": "New Jersey, USA",
        "products": ["Tablets", "Capsules", "Injectable Solutions"],
        "last_audit_date": "2025-06-15",
        "quality_system": {
            "documentation_control": "Implemented",
            "change_management": "Implemented",
            "training_program": "In Progress",
            "equipment_maintenance": "Implemented"
        },
        "issues": [
            "Training records incomplete for 2 operators",
            "Environmental monitoring data missing for Q2",
            "Validation report pending for new line"
        ],
        "recent_deviations": [
            {
                "date": "2025-06-20",
                "severity": "Major",
                "description": "Out-of-specification batch detected"
            }
        ]
    }

    print("\n" + "=" * 70)
    print("GMP COMPLIANCE AGENT - TESTING WITH MOCK DATA")
    print("=" * 70)

    # Run compliance check (using mock data)
    assessment = check_gmp_compliance(test_facility, use_api=False)
    print(f"\nFacility: {assessment['facility_id']}")
    print(f"Model Used: {assessment['model_used']}")
    print(f"Assessment Time: {assessment['timestamp']}")
    print("\n" + "-" * 70)
    print("COMPLIANCE ASSESSMENT:")
    print("-" * 70)
    print(assessment["compliance_assessment"])

    # Generate summary report
    report = generate_compliance_report([assessment])
    print("\n" + "=" * 70)
    print(report)

    return assessment


if __name__ == "__main__":
    main()
