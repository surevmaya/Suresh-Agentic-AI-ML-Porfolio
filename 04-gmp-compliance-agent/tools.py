"""
Tools for querying SAP S/4HANA data from mock database.
These functions replace live API calls and read from mock_sap_db.py.
"""

from mock_sap_db import (
    get_process_order,
    get_equipment_data,
    get_quality_deviations,
    get_batch_record,
    get_quality_test_results,
    get_maintenance_orders,
    audit_process_order,
)
from datetime import datetime


def get_process_order_data(order_id: str) -> dict:
    """
    Retrieve process order data from mock SAP database.
    Analyzes actual vs. standard process times.

    Args:
        order_id: SAP process order number (e.g., "4500012345")

    Returns:
        Dictionary with order header, operations, and time analysis
    """
    order_data = get_process_order(order_id)

    if "error" in order_data:
        return order_data

    # Analyze time deviations for each operation
    order_data["time_analysis"] = []

    for operation in order_data["operations"]:
        dzeit = int(operation.get("DZEIT", 0))  # Standard duration
        ismnw = int(operation.get("ISMNW", 0))  # Actual duration

        deviation = dzeit - ismnw  # Positive = less time than standard
        deviation_pct = (deviation / dzeit * 100) if dzeit > 0 else 0

        time_analysis = {
            "operation": operation.get("VORNR"),
            "description": operation.get("LTXA4", ""),
            "standard_duration_min": dzeit,
            "actual_duration_min": ismnw,
            "deviation_min": deviation,
            "deviation_percent": round(deviation_pct, 2),
            "status": "CRITICAL" if deviation > 10 else "OK",
        }

        order_data["time_analysis"].append(time_analysis)

    return order_data


def verify_equipment_calibration(equipment_id: str) -> dict:
    """
    Verify equipment calibration status from mock SAP database.
    Checks if calibration certificates are valid and current.

    Args:
        equipment_id: SAP equipment number (e.g., "MIXER-001")

    Returns:
        Dictionary with calibration status and compliance assessment
    """
    equipment_data = get_equipment_data(equipment_id)

    if "error" in equipment_data:
        return equipment_data

    result = {
        "equipment_id": equipment_id,
        "equipment_description": equipment_data["master"].get("EQTXT", ""),
        "equipment_status": equipment_data["master"].get("STATUS", ""),
        "calibration": equipment_data.get("calibration", {}),
        "compliance_status": "UNKNOWN",
        "days_expired": 0,
    }

    if equipment_data.get("calibration"):
        calib = equipment_data["calibration"]
        expiry_date = calib.get("EXPIRY_DATE")

        if expiry_date:
            today = datetime.now().date()
            days_since_expiry = (today - expiry_date).days

            result["compliance_status"] = "EXPIRED" if days_since_expiry > 0 else "VALID"
            result["days_expired"] = days_since_expiry
            result["expiry_status"] = (
                f"EXPIRED {days_since_expiry} days ago"
                if days_since_expiry > 0
                else f"Valid for {-days_since_expiry} more days"
            )

    return result


def scan_qm_deviations(
    batch_id: str = None, order_id: str = None
) -> dict:
    """
    Scan quality notifications/deviations from mock SAP database.
    Retrieves open quality issues linked to batch or process order.

    Args:
        batch_id: SAP batch/lot ID
        order_id: SAP process order ID

    Returns:
        Dictionary with open deviations and impact assessment
    """
    if not batch_id and not order_id:
        return {"error": "Either batch_id or order_id must be provided"}

    deviations = get_quality_deviations(batch_id=batch_id, order_id=order_id)

    result = {
        "search_criteria": {"batch_id": batch_id, "order_id": order_id},
        "total_deviations": len(deviations),
        "open_deviations": [],
        "closed_deviations": [],
        "critical_issues": [],
    }

    for deviation in deviations:
        deviation_summary = {
            "qm_number": deviation.get("QMNUM"),
            "description": deviation.get("QMTXT", ""),
            "status": deviation.get("QMSTAT", ""),
            "severity": deviation.get("SEVERITY", "MEDIUM"),
            "created_date": str(deviation.get("ERDAT", "")),
            "details": deviation.get("BESKR", ""),
        }

        if deviation.get("QMSTAT") == "CRTE":
            result["open_deviations"].append(deviation_summary)
            if deviation.get("SEVERITY") == "HIGH":
                result["critical_issues"].append(deviation_summary)
        else:
            result["closed_deviations"].append(deviation_summary)

    return result


def get_batch_quality_status(batch_id: str) -> dict:
    """
    Get comprehensive quality status for a batch.

    Args:
        batch_id: SAP batch ID

    Returns:
        Dictionary with batch status and test results
    """
    batch = get_batch_record(batch_id)

    if "error" in batch:
        return batch

    tests = get_quality_test_results(batch_id)

    result = {
        "batch_id": batch_id,
        "batch_status": batch.get("STATUS", ""),
        "qa_status": batch.get("QA_STATUS", ""),
        "mfg_date": str(batch.get("MFG_DATE", "")),
        "exp_date": str(batch.get("EXP_DATE", "")),
        "hold_reason": batch.get("HOLD_REASON", ""),
        "test_results": [],
        "overall_status": "PASS" if not tests else "UNKNOWN",
    }

    failed_count = 0
    for test in tests:
        test_summary = {
            "test_name": test.get("TEST_NAME", ""),
            "result": test.get("RESULT", ""),
            "specification_lower": test.get("SPEC_LOWER", ""),
            "specification_upper": test.get("SPEC_UPPER", ""),
            "unit": test.get("UNIT", ""),
            "status": test.get("STATUS", ""),
            "remarks": test.get("REMARKS", ""),
        }
        result["test_results"].append(test_summary)

        if test.get("STATUS") == "FAILED":
            failed_count += 1

    result["overall_status"] = "FAILED" if failed_count > 0 else "PASSED"
    result["failed_tests"] = failed_count

    return result


def audit_sap_order(order_id: str) -> dict:
    """
    Comprehensive audit of SAP process order.
    Integrates all compliance checks: process time, equipment calibration, quality deviations.

    Args:
        order_id: SAP process order ID

    Returns:
        Dictionary with complete audit findings
    """
    audit_record = audit_process_order(order_id)

    if "error" in audit_record:
        return audit_record

    # Extract batch ID from quality deviations or generate default
    batch_id = None
    if audit_record["quality_deviations"]:
        batch_id = audit_record["quality_deviations"][0].get("BATCH")

    # Build comprehensive audit
    audit_findings = {
        "audit_timestamp": datetime.now().isoformat(),
        "order_id": order_id,
        "process_time_analysis": get_process_order_data(order_id),
        "equipment_compliance": [],
        "quality_deviations": scan_qm_deviations(order_id=order_id),
        "batch_quality": None,
        "compliance_summary": {
            "critical_findings": 0,
            "major_findings": 0,
            "minor_findings": 0,
            "overall_status": "COMPLIANT",
        },
    }

    # Check equipment
    for equip in audit_record["equipment_used"]:
        equip_id = equip["master"].get("EQUNR")
        calib_check = verify_equipment_calibration(equip_id)
        audit_findings["equipment_compliance"].append(calib_check)

        if calib_check.get("compliance_status") == "EXPIRED":
            audit_findings["compliance_summary"]["critical_findings"] += 1
            audit_findings["compliance_summary"]["overall_status"] = "NON-COMPLIANT"

    # Check batch quality
    if batch_id:
        batch_quality = get_batch_quality_status(batch_id)
        audit_findings["batch_quality"] = batch_quality

        if batch_quality.get("overall_status") == "FAILED":
            audit_findings["compliance_summary"]["critical_findings"] += 1

    # Count process time deviations
    proc_analysis = audit_findings["process_time_analysis"]
    if "time_analysis" in proc_analysis:
        for time_check in proc_analysis["time_analysis"]:
            if time_check["status"] == "CRITICAL":
                audit_findings["compliance_summary"]["major_findings"] += 1
                audit_findings["compliance_summary"]["overall_status"] = "NON-COMPLIANT"

    return audit_findings


if __name__ == "__main__":
    # Test the tools
    print("Testing SAP Data Tools")
    print("=" * 70)

    # Test process order analysis
    print("\n1. Process Order Time Analysis:")
    proc_data = get_process_order_data("4500012345")
    for time_check in proc_data.get("time_analysis", []):
        print(
            f"   Operation {time_check['operation']}: "
            f"{time_check['actual_duration_min']}min "
            f"(std: {time_check['standard_duration_min']}min) "
            f"- {time_check['status']}"
        )

    # Test equipment calibration
    print("\n2. Equipment Calibration Check:")
    equip = verify_equipment_calibration("MIXER-001")
    print(f"   Equipment: {equip['equipment_description']}")
    print(f"   Status: {equip['compliance_status']} - {equip['expiry_status']}")

    # Test quality deviations
    print("\n3. Quality Deviations:")
    qm = scan_qm_deviations(order_id="4500012345")
    print(f"   Total: {qm['total_deviations']}")
    print(f"   Open: {len(qm['open_deviations'])}")
    print(f"   Critical: {len(qm['critical_issues'])}")

    # Full audit
    print("\n4. Complete Order Audit:")
    audit = audit_sap_order("4500012345")
    print(f"   Compliance Status: {audit['compliance_summary']['overall_status']}")
    print(f"   Critical Findings: {audit['compliance_summary']['critical_findings']}")
