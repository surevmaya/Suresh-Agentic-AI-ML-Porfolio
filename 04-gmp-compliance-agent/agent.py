#!/usr/bin/env python3

import json
from datetime import datetime
from tools import (
    get_process_order_data,
    verify_equipment_calibration,
    scan_qm_deviations,
    get_batch_quality_status,
    audit_sap_order,
)


def generate_compliance_report(audit_findings: dict) -> str:
    """
    Generate a structured GMP compliance report from SAP audit findings.

    Args:
        audit_findings: Dictionary from audit_sap_order()

    Returns:
        Formatted compliance report string
    """

    if "error" in audit_findings:
        return f"Error: {audit_findings['error']}"

    report = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║           GMP COMPLIANCE AUDIT REPORT - SAP S/4HANA INTEGRATION          ║
╚══════════════════════════════════════════════════════════════════════════╝

AUDIT DETAILS
─────────────────────────────────────────────────────────────────────────
Audit Date/Time:        {audit_findings['audit_timestamp']}
Process Order ID:       {audit_findings['order_id']}
Overall Status:         {audit_findings['compliance_summary']['overall_status']}
Critical Findings:      {audit_findings['compliance_summary']['critical_findings']}
Major Findings:         {audit_findings['compliance_summary']['major_findings']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. PROCESS TIME ANALYSIS
─────────────────────────────────────────────────────────────────────────
"""

    proc_analysis = audit_findings.get("process_time_analysis", {})
    if "time_analysis" in proc_analysis:
        for time_check in proc_analysis["time_analysis"]:
            status_icon = "✗ CRITICAL" if time_check["status"] == "CRITICAL" else "✓ OK"
            report += f"""
   Operation {time_check['operation']}: {time_check['description']}
   ├─ Standard Duration:     {time_check['standard_duration_min']} minutes (SOP requirement)
   ├─ Actual Duration:       {time_check['actual_duration_min']} minutes
   ├─ Deviation:             {time_check['deviation_min']} minutes ({time_check['deviation_percent']}%)
   └─ Status:                {status_icon}
"""
    else:
        report += "   No process time data available\n"

    report += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. EQUIPMENT CALIBRATION COMPLIANCE
─────────────────────────────────────────────────────────────────────────
"""

    for equip in audit_findings.get("equipment_compliance", []):
        status_icon = "✗ EXPIRED" if equip["compliance_status"] == "EXPIRED" else "✓ VALID"
        report += f"""
   Equipment: {equip['equipment_id']}
   ├─ Description:          {equip['equipment_description']}
   ├─ Cert Number:          {equip['calibration'].get('CERT_NUM', 'N/A')}
   ├─ Cert Type:            {equip['calibration'].get('CERT_TYPE', 'N/A')}
   ├─ Issued Date:          {equip['calibration'].get('ISSUED_DATE', 'N/A')}
   ├─ Expiry Date:          {equip['calibration'].get('EXPIRY_DATE', 'N/A')}
   ├─ Days Expired:         {equip['days_expired']} days
   └─ Status:               {status_icon}
"""

    report += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. QUALITY DEVIATIONS & NOTIFICATIONS
─────────────────────────────────────────────────────────────────────────
"""

    qm_data = audit_findings.get("quality_deviations", {})
    report += f"   Total Deviations:       {qm_data.get('total_deviations', 0)}\n"
    report += f"   Open Deviations:        {len(qm_data.get('open_deviations', []))}\n"
    report += f"   Critical Issues:        {len(qm_data.get('critical_issues', []))}\n"

    if qm_data.get("open_deviations"):
        report += "\n   OPEN DEVIATIONS:\n"
        for dev in qm_data["open_deviations"]:
            report += f"""
   ├─ QM Number:            {dev['qm_number']}
   ├─ Description:          {dev['description']}
   ├─ Severity:             {dev['severity']}
   ├─ Created:              {dev['created_date']}
   └─ Details:              {dev['details']}
"""

    report += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. BATCH QUALITY STATUS
─────────────────────────────────────────────────────────────────────────
"""

    batch = audit_findings.get("batch_quality")
    if batch:
        report += f"""
   Batch ID:                {batch['batch_id']}
   ├─ Batch Status:         {batch['batch_status']}
   ├─ QA Status:            {batch['qa_status']}
   ├─ MFG Date:             {batch['mfg_date']}
   ├─ Exp Date:             {batch['exp_date']}
   ├─ Overall Status:       {batch['overall_status']}
   ├─ Failed Tests:         {batch['failed_tests']}
   └─ Hold Reason:          {batch.get('hold_reason', 'N/A')}

   TEST RESULTS:
"""
        for test in batch.get("test_results", []):
            test_icon = "✗ FAILED" if test["status"] == "FAILED" else "✓ PASSED"
            report += f"""
   ├─ {test['test_name']}
   │  ├─ Result:            {test['result']} {test['unit']}
   │  ├─ Spec Range:        {test['specification_lower']}-{test['specification_upper']}
   │  ├─ Status:            {test_icon}
   │  └─ Remarks:           {test.get('remarks', 'N/A')}
"""
    else:
        report += "   No batch quality data available\n"

    report += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. COMPLIANCE FINDINGS & CORRECTIVE ACTIONS
─────────────────────────────────────────────────────────────────────────
"""

    summary = audit_findings["compliance_summary"]

    if summary["overall_status"] == "NON-COMPLIANT":
        report += f"""
   ⚠ OVERALL STATUS: NON-COMPLIANT

   CRITICAL FINDINGS: {summary['critical_findings']}

   IDENTIFIED ISSUES:
"""

        # Add specific findings based on audit data
        proc_analysis = audit_findings.get("process_time_analysis", {})
        if "time_analysis" in proc_analysis:
            for time_check in proc_analysis["time_analysis"]:
                if time_check["status"] == "CRITICAL":
                    report += f"""
   • PROCESS TIME DEVIATION
     Process Operation: {time_check['operation']} - {time_check['description']}
     - Actual duration: {time_check['actual_duration_min']} minutes
     - SOP requirement: {time_check['standard_duration_min']} minutes
     - Deviation: {time_check['deviation_min']} minutes ({time_check['deviation_percent']}%)
     - Impact: Potential impact on product homogeneity and API dissolution
     - Required Action: Investigate root cause and implement corrective action
     - Timeline: Within 14 days
     - Evidence: Batch hold, rework evaluation, or disposition decision required
"""

        for equip in audit_findings.get("equipment_compliance", []):
            if equip["compliance_status"] == "EXPIRED":
                report += f"""
   • EXPIRED EQUIPMENT CALIBRATION
     Equipment: {equip['equipment_id']} - {equip['equipment_description']}
     - Expiry Date: {equip['calibration'].get('EXPIRY_DATE', 'N/A')}
     - Days Expired: {equip['days_expired']}
     - Compliance Status: EXPIRED
     - Impact: Equipment used in batch production with invalid calibration
     - Required Action:
       1. Immediate quarantine of affected batches
       2. Re-calibration of equipment with certification
       3. Impact assessment on all batches produced during expiration period
     - Timeline: Calibration within 7 days; Impact assessment within 14 days
     - Evidence: Calibration certificate, batch investigation report
"""

    else:
        report += f"""
   ✓ OVERALL STATUS: COMPLIANT

   All processes meet GMP requirements.
   Continue routine monitoring and maintenance schedules.
"""

    report += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. RECOMMENDATIONS & NEXT STEPS
─────────────────────────────────────────────────────────────────────────

   Immediate Actions (0-7 days):
   ├─ Escalate findings to Quality Assurance and Production Management
   ├─ Place affected batch(es) on quality hold pending investigation
   ├─ Schedule equipment re-calibration
   └─ Initiate root cause analysis (5-Why or equivalent)

   Short-term Actions (1-4 weeks):
   ├─ Complete corrective and preventive actions (CAPA)
   ├─ Re-test affected batches if rework is approved
   ├─ Update SOPs if process parameter changes are made
   ├─ Conduct training on updated procedures
   └─ Submit completion report to Quality Assurance

   Follow-up Verification:
   ├─ 30-day verification of corrective actions
   ├─ Enhanced monitoring for next 3 batches
   └─ Next audit scheduled: 30 days

╚══════════════════════════════════════════════════════════════════════════╝
"""

    return report


def audit_process_order(order_id: str) -> dict:
    """
    Execute comprehensive SAP compliance audit for a process order.

    Args:
        order_id: SAP process order ID

    Returns:
        Dictionary with complete audit findings
    """
    print(f"\nAuditing Process Order: {order_id}")
    print("Retrieving data from SAP S/4HANA mock environment...")

    # Step 1: Get process order and time analysis
    print("  ✓ Analyzing process times...")
    proc_data = get_process_order_data(order_id)

    if "error" in proc_data:
        return {"error": f"Failed to retrieve process order: {proc_data['error']}"}

    # Step 2: Check equipment calibration
    print("  ✓ Verifying equipment calibration...")
    equipment_checks = []
    if proc_data["header"].get("ARBPL") == "MIXING-ZONE-01":
        equip_check = verify_equipment_calibration("MIXER-001")
        equipment_checks.append(equip_check)

    # Step 3: Scan quality deviations
    print("  ✓ Scanning quality notifications...")
    qm_deviations = scan_qm_deviations(order_id=order_id)

    # Step 4: Get batch quality status
    print("  ✓ Retrieving batch quality data...")
    batch_quality = None
    if qm_deviations.get("open_deviations"):
        batch_id = qm_deviations["open_deviations"][0].get("batch_id")
        if batch_id:
            batch_quality = get_batch_quality_status(batch_id)

    # Step 5: Run comprehensive audit
    print("  ✓ Generating compliance assessment...")
    audit_findings = audit_sap_order(order_id)

    return audit_findings


def main():
    """Main agent entry point."""

    print("\n" + "=" * 78)
    print("GMP COMPLIANCE AGENT - SAP S/4HANA INTEGRATION")
    print("=" * 78)

    # Audit the process order
    audit_findings = audit_process_order("4500012345")

    if "error" in audit_findings:
        print(f"\n❌ Audit Error: {audit_findings['error']}")
        return

    # Generate and display compliance report
    report = generate_compliance_report(audit_findings)
    print(report)

    # Save report to file
    report_filename = f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_filename, "w") as f:
        f.write(report)
    print(f"\n📄 Report saved to: {report_filename}")

    return audit_findings


if __name__ == "__main__":
    main()
