"""
Mock SAP S/4HANA ERP database for GMP compliance testing.
Simulates critical SAP tables: AFKO, AFVC, EQUI, AUFK, QMEL.
"""

from datetime import datetime, timedelta

# Process Order Header (AFKO)
AFKO = {
    "4500012345": {
        "AUFNR": "4500012345",
        "AUART": "PP01",  # Process Order
        "MATNR": "MAT-PHARMA-001",
        "MENGE": "500.000",
        "MEINS": "KG",
        "WERKS": "1000",  # Plant
        "ARBPL": "MIXING-ZONE-01",  # Work center
        "GSTRI": datetime(2025, 6, 15).date(),  # Scheduled start
        "GSTRP": datetime(2025, 6, 16).date(),  # Scheduled finish
        "AEDAT": datetime(2025, 6, 14).date(),  # Creation date
        "AEZET": "08:00:00",
        "GLTRP": datetime(2025, 6, 16).date(),  # Actual finish
        "GLTRI": datetime(2025, 6, 15).date(),  # Actual start
        "STATU": "CNFM",  # Confirmed
        "RUECK": "X",  # Released for execution
        "PKPSE": "F",  # Planned/Actual
    }
}

# Process Order Operations (AFVC) - Mixing Phase Deviation
AFVC = {
    "4500012345-01": {
        "AUFNR": "4500012345",
        "VORNR": "0010",  # Operation 10
        "LTXA4": "MIXING PHASE - ACTIVE PHARMACEUTICAL INGREDIENT",
        "ARBPL": "MIXING-ZONE-01",
        "VGART": "P",  # Process operation
        "LGORT": "0001",
        "BMSCH": "500.000",
        "BMEIN": "KG",
        "DZEIT": "45",  # Standard duration in minutes (SOP requirement)
        "DZEIN": "MIN",
        "PZEIT": "45",  # Planned duration
        "WKZEIT": "45",
        "ISMNW": "28",  # ACTUAL duration in minutes - DEVIATION
        "ISMNH": "0",
        "ISMNS": "0",
        "STAT": "CNFM",
        "GSTRP": datetime(2025, 6, 15, 14, 30).isoformat(),  # Actual start
        "GLTRP": datetime(2025, 6, 15, 14, 58).isoformat(),  # Actual end - 28 min duration
        "VORMG": "1.000",
        "CRTDM": datetime(2025, 6, 14).date(),
    },
    "4500012345-02": {
        "AUFNR": "4500012345",
        "VORNR": "0020",
        "LTXA4": "COOLING PHASE",
        "ARBPL": "COOLING-ZONE-01",
        "VGART": "P",
        "DZEIT": "30",
        "DZEIN": "MIN",
        "ISMNW": "31",
        "STAT": "CNFM",
    }
}

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
EQUI_CALIB = {
    "MIXER-001": {
        "EQUNR": "MIXER-001",
        "CERT_NUM": "CAL-MIXER-001-2025",
        "CERT_TYPE": "TEMPERATURE_PRESSURE",
        "ISSUED_DATE": datetime(2024, 12, 15).date(),
        "EXPIRY_DATE": datetime(2025, 6, 10).date(),  # EXPIRED 5 days before the run
        "NEXT_DUE": datetime(2025, 12, 10).date(),
        "CERT_BODY": "DIN-Accredited Calibration Lab",
        "STATUS": "EXPIRED",
        "TOLERANCE_RANGE": "±0.5%",
    }
}

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
QMEL = {
    "0090045678": {
        "QMNUM": "0090045678",
        "QMTXT": "PROCESS TIME DEVIATION - MIXING PHASE",
        "MATNR": "MAT-PHARMA-001",
        "AUFNR": "4500012345",
        "VORNR": "0010",
        "BATCH": "BATCH-2025-0615-001",
        "LAGHR": "0001",
        "ERDAT": datetime(2025, 6, 15, 15, 5).date(),
        "ERZET": "15:05:00",
        "QMSTAT": "CRTE",  # Created
        "QMSTP": "001",  # Defect notification
        "ALTPL": "01",
        "KZMDL": "X",  # Defect
        "KZOBJ": "X",  # Object exists
        "KZMDF": "X",  # Material defect
        "BESKR": "Actual process duration 28 minutes significantly below SOP requirement of 45 minutes. Potential impact on mixing homogeneity and API dissolution.",
        "GRNGRUPPE": "PROCESS",
        "PROBLEM_CODE": "001",  # Inadequate processing time
        "SEVERITY": "HIGH",
        "STATUS": "OPEN",
        "CREATED_BY": "SYSTEM",
    }
}

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


if __name__ == "__main__":
    # Test the mock database
    print("Testing Mock SAP Database")
    print("=" * 70)

    order = audit_process_order("4500012345")
    print("\nProcess Order Audit:")
    import json
    print(json.dumps(order, indent=2, default=str))
