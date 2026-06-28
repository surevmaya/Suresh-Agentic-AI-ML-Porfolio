"""
Mock SAP S/4HANA ERP database for GMP compliance testing.
Simulates critical SAP tables: AFKO, AFVC, EQUI, AUFK, QMEL.
"""

from datetime import datetime, timedelta
import random

# Process Order Header (AFKO) - Generate 100 orders
def _generate_afko_orders():
    """Generate 100 mock process orders for bulk testing."""
    orders = {}
    base_date = datetime(2025, 6, 1)

    for i in range(1, 101):
        order_id = f"450001{i:04d}"

        # Stagger the dates across June
        order_date = base_date + timedelta(days=i % 30)

        orders[order_id] = {
            "AUFNR": order_id,
            "AUART": "PP01",
            "MATNR": f"MAT-PHARMA-{(i % 10) + 1:03d}",
            "MENGE": f"{300 + (i * 5) % 500}.000",
            "MEINS": "KG",
            "WERKS": "1000",
            "ARBPL": "MIXING-ZONE-01",
            "GSTRI": order_date.date(),
            "GSTRP": (order_date + timedelta(days=1)).date(),
            "AEDAT": (order_date - timedelta(days=1)).date(),
            "AEZET": "08:00:00",
            "GLTRP": (order_date + timedelta(days=1)).date(),
            "GLTRI": order_date.date(),
            "STATU": "CNFM",
            "RUECK": "X",
            "PKPSE": "F",
        }

    return orders

AFKO = _generate_afko_orders()

# Process Order Operations (AFVC)
def _generate_afvc_operations():
    """Generate operations for all 100 process orders."""
    operations = {}
    base_date = datetime(2025, 6, 1)

    for i in range(1, 101):
        order_id = f"450001{i:04d}"
        order_date = base_date + timedelta(days=i % 30)

        # Determine compliance status
        is_compliant = i <= 95  # Orders 1-95 are compliant
        has_minor_deviation = 96 <= i <= 98  # Orders 96-98 have minor deviations
        has_critical_failure = i >= 99  # Orders 99-100 have critical failures

        # Mixing phase operation
        if is_compliant:
            actual_duration = 45  # Meets SOP requirement
        elif has_minor_deviation:
            actual_duration = 42  # 3 min below spec (minor)
        else:
            actual_duration = 15  # Major deviation (critical)

        mixing_start = order_date + timedelta(hours=14, minutes=30)
        mixing_end = mixing_start + timedelta(minutes=actual_duration)

        op_key = f"{order_id}-01"
        operations[op_key] = {
            "AUFNR": order_id,
            "VORNR": "0010",
            "LTXA4": "MIXING PHASE - ACTIVE PHARMACEUTICAL INGREDIENT",
            "ARBPL": "MIXING-ZONE-01",
            "VGART": "P",
            "LGORT": "0001",
            "BMSCH": f"{300 + (i * 5) % 500}.000",
            "BMEIN": "KG",
            "DZEIT": "45",
            "DZEIN": "MIN",
            "PZEIT": "45",
            "WKZEIT": "45",
            "ISMNW": str(actual_duration),
            "ISMNH": "0",
            "ISMNS": "0",
            "STAT": "CNFM",
            "GSTRP": mixing_start.isoformat(),
            "GLTRP": mixing_end.isoformat(),
            "VORMG": "1.000",
            "CRTDM": (order_date - timedelta(days=1)).date(),
        }

        # Cooling phase operation
        cooling_start = mixing_end + timedelta(minutes=5)
        cooling_end = cooling_start + timedelta(minutes=30)

        op_key = f"{order_id}-02"
        operations[op_key] = {
            "AUFNR": order_id,
            "VORNR": "0020",
            "LTXA4": "COOLING PHASE",
            "ARBPL": "COOLING-ZONE-01",
            "VGART": "P",
            "DZEIT": "30",
            "DZEIN": "MIN",
            "ISMNW": "30",
            "STAT": "CNFM",
            "GSTRP": cooling_start.isoformat(),
            "GLTRP": cooling_end.isoformat(),
        }

    return operations

AFVC = _generate_afvc_operations()

# Equipment Master Data (EQUI)
EQUI = {
    "MIXER-001": {
        "EQUNR": "MIXER-001",
        "EQART": "P",  # Production equipment
        "EQTXT": "High-Shear Mixing Vessel Unit A",
        "WERKS": "1000",
        "ARBPL": "MIXING-ZONE-01",
        "INBDT": datetime(2020, 1, 15).date(),  # Installation date
        "ANSDT": datetime(2021, 6, 1).date(),  # Start of operation
        "SERGE": "BATCH-SHP-2020-5678",
        "HERSTELLER": "PharmaMix GmbH",
        "TYPBEZ": "PM-5000-HC",
        "GEWICHT": "2500.000",
        "GEWEI": "KG",
        "STATUS": "1",  # In operation
    }
}

# Equipment Calibration Certification (Extended EQUI data)
def _generate_equipment_calibration():
    """Generate calibration data with varied expiry statuses."""
    calib_data = {}
    base_date = datetime(2025, 6, 15)

    # Create calibration records for equipment used
    # Most equipment has valid calibration, but specific mixers have expired ones
    for i in range(1, 11):
        equip_id = f"MIXER-{i:03d}"

        if i >= 9:  # Last 2 mixers have expired calibration (critical failure orders)
            expiry_date = base_date - timedelta(days=5)
            status = "EXPIRED"
        else:  # All others are valid
            expiry_date = base_date + timedelta(days=180)
            status = "VALID"

        calib_data[equip_id] = {
            "EQUNR": equip_id,
            "CERT_NUM": f"CAL-{equip_id}-2025",
            "CERT_TYPE": "TEMPERATURE_PRESSURE",
            "ISSUED_DATE": (base_date - timedelta(days=180)).date(),
            "EXPIRY_DATE": expiry_date.date(),
            "NEXT_DUE": (expiry_date + timedelta(days=180)).date(),
            "CERT_BODY": "DIN-Accredited Calibration Lab",
            "STATUS": status,
            "TOLERANCE_RANGE": "±0.5%",
        }

    return calib_data

EQUI_CALIB = _generate_equipment_calibration()

# Maintenance Order (AUFK) - Related to equipment
AUFK = {
    "3000005678": {
        "AUFNR": "3000005678",
        "AUART": "PM02",  # Preventive maintenance
        "EQUNR": "MIXER-001",
        "TPLNR": "1000-MIXING-ZONE-01",
        "ARBPL": "MIXING-ZONE-01",
        "ERDAT": datetime(2025, 5, 20).date(),
        "GSTRI": datetime(2025, 6, 1).date(),
        "GSTRP": datetime(2025, 6, 30).date(),
        "STATU": "CNFM",
        "LTXA4": "Calibration Certification - Temperature & Pressure",
        "STAT": "CNFM",
    }
}

# Quality Notifications (QMEL) - Deviation Flag
def _generate_quality_notifications():
    """Generate quality notifications for non-compliant orders."""
    qmel_data = {}
    base_date = datetime(2025, 6, 1)

    qm_counter = 90000000

    # Orders 96-98: Minor deviations
    for i in range(96, 99):
        order_id = f"450001{i:04d}"
        qm_counter += 1
        order_date = base_date + timedelta(days=i % 30)

        qm_id = str(qm_counter)
        qmel_data[qm_id] = {
            "QMNUM": qm_id,
            "QMTXT": "MINOR PROCESS TIME DEVIATION - MIXING PHASE",
            "MATNR": f"MAT-PHARMA-{(i % 10) + 1:03d}",
            "AUFNR": order_id,
            "VORNR": "0010",
            "BATCH": f"BATCH-2025-{order_date.month:02d}{order_date.day:02d}-{i:03d}",
            "LAGHR": "0001",
            "ERDAT": order_date.date(),
            "ERZET": "15:00:00",
            "QMSTAT": "CRTE",
            "QMSTP": "001",
            "ALTPL": "01",
            "KZMDL": "X",
            "KZOBJ": "X",
            "KZMDF": "X",
            "BESKR": "Actual process duration 42 minutes slightly below SOP requirement of 45 minutes. Minor deviation detected.",
            "GRNGRUPPE": "PROCESS",
            "PROBLEM_CODE": "002",
            "SEVERITY": "MEDIUM",
            "STATUS": "OPEN",
            "CREATED_BY": "SYSTEM",
        }

    # Orders 99-100: Critical failures
    for i in range(99, 101):
        order_id = f"450001{i:04d}"
        qm_counter += 1
        order_date = base_date + timedelta(days=i % 30)

        # Process time deviation
        qm_id = str(qm_counter)
        qmel_data[qm_id] = {
            "QMNUM": qm_id,
            "QMTXT": "CRITICAL PROCESS TIME DEVIATION - MIXING PHASE",
            "MATNR": f"MAT-PHARMA-{(i % 10) + 1:03d}",
            "AUFNR": order_id,
            "VORNR": "0010",
            "BATCH": f"BATCH-2025-{order_date.month:02d}{order_date.day:02d}-{i:03d}",
            "LAGHR": "0001",
            "ERDAT": order_date.date(),
            "ERZET": "15:05:00",
            "QMSTAT": "CRTE",
            "QMSTP": "001",
            "ALTPL": "01",
            "KZMDL": "X",
            "KZOBJ": "X",
            "KZMDF": "X",
            "BESKR": "Actual process duration 15 minutes critically below SOP requirement of 45 minutes. Major impact on product quality.",
            "GRNGRUPPE": "PROCESS",
            "PROBLEM_CODE": "001",
            "SEVERITY": "HIGH",
            "STATUS": "OPEN",
            "CREATED_BY": "SYSTEM",
        }

        # Equipment calibration expired
        qm_counter += 1
        qm_id = str(qm_counter)
        calib_equip_id = f"MIXER-{(8 if i == 99 else 9):03d}"
        qmel_data[qm_id] = {
            "QMNUM": qm_id,
            "QMTXT": "EQUIPMENT CALIBRATION EXPIRED",
            "MATNR": f"MAT-PHARMA-{(i % 10) + 1:03d}",
            "AUFNR": order_id,
            "VORNR": "0010",
            "BATCH": f"BATCH-2025-{order_date.month:02d}{order_date.day:02d}-{i:03d}",
            "LAGHR": "0001",
            "ERDAT": order_date.date(),
            "ERZET": "14:30:00",
            "QMSTAT": "CRTE",
            "QMSTP": "001",
            "ALTPL": "01",
            "KZMDL": "X",
            "KZOBJ": "X",
            "KZMDF": "X",
            "BESKR": f"Equipment {calib_equip_id} calibration expired 5 days before process execution. Cannot verify process parameters.",
            "GRNGRUPPE": "EQUIPMENT",
            "PROBLEM_CODE": "003",
            "SEVERITY": "CRITICAL",
            "STATUS": "OPEN",
            "CREATED_BY": "SYSTEM",
        }

    return qmel_data

QMEL = _generate_quality_notifications()

# Quality Control Results (QALS) - Lab test results
QALS = {
    "BATCH-2025-0615-001-TEST-001": {
        "BATCH": "BATCH-2025-0615-001",
        "MATNR": "MAT-PHARMA-001",
        "AUFNR": "4500012345",
        "INSPCODE": "CONTENT_ASSAY",
        "TEST_NAME": "Content Assay - Active Pharmaceutical Ingredient",
        "TEST_DATE": datetime(2025, 6, 15, 16, 30).date(),
        "RESULT": "96.8",
        "SPEC_LOWER": "95.0",
        "SPEC_UPPER": "105.0",
        "UNIT": "%",
        "STATUS": "FAILED",  # Below acceptable due to insufficient mixing time
        "REMARKS": "Result indicates incomplete dissolution/mixing of active ingredient",
    }
}

# Product Batch Record
BATCH_RECORD = {
    "BATCH-2025-0615-001": {
        "BATCH": "BATCH-2025-0615-001",
        "MATNR": "MAT-PHARMA-001",
        "WERKS": "1000",
        "AUFNR": "4500012345",
        "STATUS": "HOLD",  # On quality hold
        "MFG_DATE": datetime(2025, 6, 15).date(),
        "EXP_DATE": datetime(2027, 6, 14).date(),
        "QA_STATUS": "REJECTED",
        "HOLD_REASON": "Process deviation - insufficient mixing time and expired equipment calibration",
        "CREATED_DATE": datetime(2025, 6, 15).date(),
        "PRODUCT_CODE": "PHARMA-TABLET-500MG",
        "LOT_SIZE": "500 KG",
    }
}


def get_process_order(order_id: str) -> dict:
    """Retrieve process order header and operations."""
    if order_id not in AFKO:
        return {"error": f"Process order {order_id} not found"}

    order_data = {
        "header": AFKO[order_id],
        "operations": [],
    }

    # Get all operations for this order
    for op_key, op_data in AFVC.items():
        if op_data["AUFNR"] == order_id:
            order_data["operations"].append(op_data)

    return order_data


def get_equipment_data(equipment_id: str) -> dict:
    """Retrieve equipment master data with calibration status."""
    if equipment_id not in EQUI:
        return {"error": f"Equipment {equipment_id} not found"}

    return {
        "master": EQUI[equipment_id],
        "calibration": EQUI_CALIB.get(equipment_id, {}),
    }


def get_quality_deviations(batch_id: str = None, order_id: str = None) -> list:
    """Retrieve quality notifications/deviations."""
    deviations = []

    for qm_num, qm_data in QMEL.items():
        if batch_id and qm_data.get("BATCH") == batch_id:
            deviations.append(qm_data)
        elif order_id and qm_data.get("AUFNR") == order_id:
            deviations.append(qm_data)

    return deviations


def get_batch_record(batch_id: str) -> dict:
    """Retrieve product batch record."""
    if batch_id not in BATCH_RECORD:
        return {"error": f"Batch {batch_id} not found"}

    return BATCH_RECORD[batch_id]


def get_quality_test_results(batch_id: str) -> list:
    """Retrieve quality test results for a batch."""
    results = []

    for test_key, test_data in QALS.items():
        if test_data.get("BATCH") == batch_id:
            results.append(test_data)

    return results


def get_maintenance_orders(equipment_id: str) -> list:
    """Retrieve maintenance orders for equipment."""
    orders = []

    for aufnr, aufk_data in AUFK.items():
        if aufk_data.get("EQUNR") == equipment_id:
            orders.append(aufk_data)

    return orders


def audit_process_order(order_id: str) -> dict:
    """
    Comprehensive audit of a process order.
    Returns structured data for compliance analysis.
    """
    order = get_process_order(order_id)

    if "error" in order:
        return order

    # Extract critical data
    batch_id = None
    for op in order["operations"]:
        if "QMNUM" not in op:
            # Try to find batch from AFKO if available
            batch_id = f"BATCH-{order['header']['GSTRI'].isoformat()}-001"
            break

    # Build comprehensive audit record
    audit_data = {
        "order_id": order_id,
        "timestamp": datetime.now().isoformat(),
        "process_order": order,
        "equipment_used": [],
        "quality_deviations": get_quality_deviations(order_id=order_id),
        "batch_data": None,
        "quality_tests": [],
        "maintenance_history": [],
    }

    # Get equipment data (mixer from work center)
    if order["header"].get("ARBPL") == "MIXING-ZONE-01":
        equip_data = get_equipment_data("MIXER-001")
        audit_data["equipment_used"].append(equip_data)
        audit_data["maintenance_history"] = get_maintenance_orders("MIXER-001")

    # Get batch and test data if found
    if batch_id:
        audit_data["batch_data"] = get_batch_record(batch_id)
        audit_data["quality_tests"] = get_quality_test_results(batch_id)

    return audit_data


def get_all_process_orders() -> list:
    """Retrieve all process orders."""
    return list(AFKO.keys())


def calculate_order_risk(order_id: str) -> dict:
    """
    Calculate risk/compliance status for an order.
    Returns: {order_id, status, risk_level, critical_count, major_count, issues}
    """
    deviations = get_quality_deviations(order_id=order_id)

    critical_count = sum(1 for d in deviations if d.get("SEVERITY") == "CRITICAL")
    major_count = sum(1 for d in deviations if d.get("SEVERITY") == "HIGH")
    medium_count = sum(1 for d in deviations if d.get("SEVERITY") == "MEDIUM")

    total_issues = len(deviations)

    if critical_count > 0:
        risk_level = "CRITICAL"
        status = "NON-COMPLIANT"
    elif major_count > 0:
        risk_level = "HIGH"
        status = "NON-COMPLIANT"
    elif medium_count > 0:
        risk_level = "MEDIUM"
        status = "MINOR-DEVIATION"
    else:
        risk_level = "LOW"
        status = "COMPLIANT"

    return {
        "order_id": order_id,
        "status": status,
        "risk_level": risk_level,
        "critical_count": critical_count,
        "major_count": major_count,
        "medium_count": medium_count,
        "total_issues": total_issues,
    }


def get_all_orders_summary() -> list:
    """Get summary of all orders with risk assessment."""
    all_orders = get_all_process_orders()
    summaries = []

    for order_id in all_orders:
        order = AFKO.get(order_id, {})
        risk_data = calculate_order_risk(order_id)

        summaries.append({
            "order_id": order_id,
            "material": order.get("MATNR", "N/A"),
            "quantity": f"{order.get('MENGE', 'N/A')} {order.get('MEINS', '')}".strip(),
            "status": risk_data["status"],
            "risk_level": risk_data["risk_level"],
            "critical": risk_data["critical_count"],
            "major": risk_data["major_count"],
            "medium": risk_data["medium_count"],
            "total_issues": risk_data["total_issues"],
            "created_date": order.get("AEDAT", "N/A"),
        })

    return summaries


if __name__ == "__main__":
    # Test the mock database
    print("Testing Mock SAP Database")
    print("=" * 70)

    order = audit_process_order("4500012345")
    print("\nProcess Order Audit:")
    import json
    print(json.dumps(order, indent=2, default=str))
