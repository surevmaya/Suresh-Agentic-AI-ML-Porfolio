#!/usr/bin/env python3
"""
GMP Compliance Agent - Streamlit Dashboard
Interactive frontend for SAP process order compliance auditing.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from tools import audit_sap_order, get_process_order_data, verify_equipment_calibration, scan_qm_deviations
from agent import generate_compliance_report
from mock_sap_db import (
    AFKO, AFVC, EQUI, EQUI_CALIB, AUFK, QMEL, QALS, BATCH_RECORD,
    get_all_process_orders, get_all_orders_summary, calculate_order_risk
)

# Helper functions for graceful field handling
def safe_get(obj, key, default="N/A"):
    """Safely retrieve a value from a dictionary, return default if missing/None/empty."""
    if not obj or not isinstance(obj, dict):
        return default
    value = obj.get(key, default)
    if value is None or value == "" or value == {}:
        return default
    return value

def format_value(value, unit=""):
    """Format a value with optional unit, handling None/empty cases."""
    if value is None or value == "" or value == {}:
        return "N/A"
    formatted = str(value)
    return f"{formatted} {unit}".strip() if unit else formatted

def get_status_badge(status, yes_icon="🟢", no_icon="🔴"):
    """Return status badge based on presence of data."""
    return yes_icon if status else no_icon

def format_badge_text(count, singular="", plural=""):
    """Format a count with appropriate singular/plural badge text."""
    if count == 0:
        return f"🟢 No {plural or 'Items'}"
    elif count == 1:
        return f"⚠️ {count} {singular or 'Item'}"
    else:
        return f"🔴 {count} {plural or 'Items'}"

# Page configuration
st.set_page_config(
    page_title="GMP Compliance Agent",
    page_icon="✓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .compliant {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .non-compliant {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 14px;
        opacity: 0.9;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🔍 GMP Compliance Agent")
st.sidebar.markdown("---")

# View Mode Selection
view_mode = st.sidebar.radio(
    "View Mode:",
    ["📋 Single Order Audit", "📊 Bulk Operations"],
    help="Switch between single order audit and bulk operations dashboard"
)

st.sidebar.markdown("---")

# Process Order Selection (only for single order mode)
if view_mode == "📋 Single Order Audit":
    st.sidebar.subheader("Select Process Order")
    available_orders = list(AFKO.keys())
    selected_order = st.sidebar.selectbox(
        "Process Order ID:",
        available_orders,
        help="Select a process order from SAP S/4HANA"
    )

    st.sidebar.markdown("---")
    st.sidebar.info(
        f"**Selected Order:** {selected_order}\n\n"
        f"**Available Orders:** {len(available_orders)}\n\n"
        f"**Mock Data Source:** AFKO/AFVC/EQUI/QMEL tables"
    )
else:
    available_orders = list(AFKO.keys())
    st.sidebar.info(
        f"**Total Orders:** {len(available_orders)}\n\n"
        f"**Status Distribution:**\n"
        f"- 95 Compliant\n"
        f"- 3 Minor Deviations\n"
        f"- 2 Critical Failures\n\n"
        f"**Mock Data Source:** AFKO/AFVC/EQUI/QMEL tables"
    )

# Main Content
if view_mode == "📋 Single Order Audit":
    st.title("📊 GMP Compliance Audit Dashboard")
    st.markdown(f"**Order ID:** `{selected_order}` | **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
else:
    st.title("📊 Bulk Operations Dashboard")
    st.markdown(f"**Total Orders:** 100 | **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.markdown("---")

# Initialize session state for audit results
if "audit_results" not in st.session_state:
    st.session_state.audit_results = None
if "report_text" not in st.session_state:
    st.session_state.report_text = None
if "show_exceptions_only" not in st.session_state:
    st.session_state.show_exceptions_only = False

# BULK OPERATIONS VIEW
if view_mode == "📊 Bulk Operations":
    st.subheader("📈 Process Order Compliance Summary")

    # Filter toggle
    col1, col2 = st.columns([3, 1])
    with col2:
        st.session_state.show_exceptions_only = st.checkbox(
            "Show Exceptions Only",
            value=st.session_state.show_exceptions_only,
            help="Hide compliant orders and show only those requiring review"
        )

    # Get all orders summary
    @st.cache_data
    def load_all_orders_summary():
        return get_all_orders_summary()

    all_orders_data = load_all_orders_summary()

    # Sort by risk level (CRITICAL > HIGH > MEDIUM > LOW)
    risk_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    all_orders_data_sorted = sorted(
        all_orders_data,
        key=lambda x: (risk_order.get(x["risk_level"], 4), -x["total_issues"])
    )

    # Apply exception filter
    if st.session_state.show_exceptions_only:
        all_orders_data_sorted = [o for o in all_orders_data_sorted if o["status"] != "COMPLIANT"]

    # Display statistics
    col1, col2, col3, col4, col5 = st.columns(5)

    compliant_count = sum(1 for o in all_orders_data if o["status"] == "COMPLIANT")
    minor_count = sum(1 for o in all_orders_data if o["status"] == "MINOR-DEVIATION")
    non_compliant_count = sum(1 for o in all_orders_data if o["status"] == "NON-COMPLIANT")
    critical_count = sum(1 for o in all_orders_data if o["risk_level"] == "CRITICAL")
    high_count = sum(1 for o in all_orders_data if o["risk_level"] == "HIGH")

    with col1:
        st.metric("Total Orders", len(all_orders_data))
    with col2:
        st.metric("✓ Compliant", compliant_count)
    with col3:
        st.metric("⚠️ Minor Dev", minor_count)
    with col4:
        st.metric("🔴 Critical", critical_count)
    with col5:
        st.metric("📊 High Risk", high_count)

    st.markdown("---")

    # Data table
    st.subheader("All Process Orders - Risk Sorted")

    # Create display dataframe
    display_df = pd.DataFrame(all_orders_data_sorted)
    display_df = display_df.rename(columns={
        "order_id": "Process Order ID",
        "material": "Material Code",
        "quantity": "Quantity",
        "status": "Compliance Status",
        "risk_level": "Risk Level",
        "critical": "Critical Issues",
        "major": "Major Issues",
        "medium": "Medium Issues",
        "total_issues": "Total Issues",
        "created_date": "Creation Date",
    })

    # Format for display
    display_columns = ["Process Order ID", "Material Code", "Quantity", "Compliance Status", "Risk Level", "Critical Issues", "Major Issues", "Medium Issues", "Total Issues", "Creation Date"]
    display_df = display_df[display_columns]

    # Color coding by risk level
    def style_risk(val):
        if val == "CRITICAL":
            return "background-color: #ff4444; color: white"
        elif val == "HIGH":
            return "background-color: #ff9933; color: white"
        elif val == "MEDIUM":
            return "background-color: #ffdd33; color: black"
        else:
            return "background-color: #33cc33; color: white"

    def style_status(val):
        if val == "NON-COMPLIANT":
            return "background-color: #ff4444; color: white; font-weight: bold"
        elif val == "MINOR-DEVIATION":
            return "background-color: #ffdd33; color: black; font-weight: bold"
        else:
            return "background-color: #33cc33; color: white; font-weight: bold"

    styled_df = display_df.style.applymap(
        lambda x: style_risk(x) if isinstance(x, str) and x in ["CRITICAL", "HIGH", "MEDIUM", "LOW"] else "",
        subset=["Risk Level"]
    ).applymap(
        lambda x: style_status(x) if isinstance(x, str) and x in ["COMPLIANT", "NON-COMPLIANT", "MINOR-DEVIATION"] else "",
        subset=["Compliance Status"]
    )

    st.dataframe(styled_df, use_container_width=True, height=600)

    # Export button
    st.markdown("---")
    col1, col2 = st.columns([1, 3])
    with col1:
        csv_data = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Export CSV",
            data=csv_data,
            file_name=f"orders_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

    st.stop()  # Stop here for bulk view, don't render single order sections


# Load order data for single order audit
@st.cache_data
def load_order_data(order_id):
    """Load process order data from mock database."""
    order_data = {
        "header": AFKO.get(order_id, {}),
        "operations": [],
        "equipment": {},
        "quality_deviations": [],
        "batch_records": {},
        "test_results": []
    }

    # Get operations for this order
    for op_key, op_data in AFVC.items():
        if op_data.get("AUFNR") == order_id:
            order_data["operations"].append(op_data)

    # Get equipment data
    if order_data["header"].get("ARBPL") == "MIXING-ZONE-01":
        # Find the appropriate mixer for this order
        mixer_num = (int(order_id[-4:]) % 10) + 1
        mixer_id = f"MIXER-{mixer_num:03d}"
        if mixer_id in EQUI:
            order_data["equipment"][mixer_id] = {
                "master": EQUI.get(mixer_id, {}),
                "calibration": EQUI_CALIB.get(mixer_id, {})
            }

    # Get quality deviations
    for qm_num, qm_data in QMEL.items():
        if qm_data.get("AUFNR") == order_id:
            order_data["quality_deviations"].append(qm_data)

    # Get batch records
    for batch_id, batch_data in BATCH_RECORD.items():
        if batch_data.get("AUFNR") == order_id:
            order_data["batch_records"][batch_id] = batch_data

    # Get quality test results
    for test_key, test_data in QALS.items():
        if test_data.get("AUFNR") == order_id:
            order_data["test_results"].append(test_data)

    return order_data

# Auto-load audit results for selected order
@st.cache_data
def auto_load_audit_results(order_id):
    """Automatically load audit results on page load."""
    return audit_sap_order(order_id)

# Set selected_order for single order view
if view_mode == "📋 Single Order Audit":
    # selected_order is already set from sidebar radio button
    order_data = load_order_data(selected_order)
else:
    # Not needed in bulk view, but set a default for safety
    selected_order = None
    order_data = None

# Single Order Audit View
if view_mode == "📋 Single Order Audit":
    # Auto-load and cache audit results
    if st.session_state.audit_results is None:
        try:
            st.session_state.audit_results = auto_load_audit_results(selected_order)
        except Exception as e:
            st.warning(f"Could not auto-load audit results: {str(e)}")

    # KPI Metrics Section
    st.subheader("📈 Key Performance Indicators")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.session_state.audit_results:
            status = st.session_state.audit_results["compliance_summary"]["overall_status"]
            critical = st.session_state.audit_results["compliance_summary"]["critical_findings"]
            major = st.session_state.audit_results["compliance_summary"]["major_findings"]

            # Grade calculation: A (0 critical, 0 major), B (0 critical, <3 major), C (0 critical, >=3 major), D (1-2 critical), F (>2 critical)
            if critical == 0 and major == 0:
                grade = "A"
            elif critical == 0 and major < 3:
                grade = "B"
            elif critical == 0:
                grade = "C"
            elif critical <= 2:
                grade = "D"
            else:
                grade = "F"

            color = "compliant" if status == "COMPLIANT" else "non-compliant"
            st.markdown(f"""
                <div class="metric-card {color}">
                    <div class="metric-label">Compliance Grade</div>
                    <div class="metric-value">{grade}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="metric-card">
                    <div class="metric-label">Compliance Grade</div>
                    <div class="metric-value">-</div>
                </div>
            """, unsafe_allow_html=True)

    with col2:
        critical_findings = len(order_data["quality_deviations"])
        color = "non-compliant" if critical_findings > 0 else "compliant"
        st.markdown(f"""
            <div class="metric-card {color}">
                <div class="metric-label">Quality Deviations</div>
                <div class="metric-value">{critical_findings}</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        safety_risk = "HIGH" if critical_findings > 0 else "LOW"
        color = "non-compliant" if critical_findings > 0 else "compliant"
        st.markdown(f"""
            <div class="metric-card {color}">
                <div class="metric-label">Safety Risk Level</div>
                <div class="metric-value">{safety_risk}</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        if st.session_state.audit_results:
            status = st.session_state.audit_results["compliance_summary"]["overall_status"]
            icon = "✓" if status == "COMPLIANT" else "✗"
            status_text = status if len(status) < 12 else ("PASS" if status == "COMPLIANT" else "FAIL")
            st.markdown(f"""
                <div class="metric-card {'compliant' if status == 'COMPLIANT' else 'non-compliant'}">
                    <div class="metric-label">Overall Status</div>
                    <div class="metric-value">{status_text}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="metric-card">
                    <div class="metric-label">Overall Status</div>
                    <div class="metric-value">-</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📋 Process Order", "🏭 Equipment Data", "⚠️ Quality Deviations", "🧪 Test Results", "📄 Compliance Report"]
    )

    # Tab 1: Process Order Details
    with tab1:
        st.subheader("Process Order Details")

        if order_data["header"]:
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Order Header Information**")
                header_df = pd.DataFrame([order_data["header"]])
                st.dataframe(header_df, use_container_width=True)

            with col2:
                st.write("**Quick Summary**")
                menge = safe_get(order_data["header"], "MENGE", "N/A")
                meins = safe_get(order_data["header"], "MEINS", "")
                summary_data = {
                    "Order ID": safe_get(order_data["header"], "AUFNR", "N/A"),
                    "Material": safe_get(order_data["header"], "MATNR", "N/A"),
                    "Quantity": f"{menge} {meins}".strip() if menge != "N/A" else "N/A",
                    "Plant": safe_get(order_data["header"], "WERKS", "N/A"),
                    "Work Center": safe_get(order_data["header"], "ARBPL", "N/A"),
                    "Status": safe_get(order_data["header"], "STATU", "N/A"),
                }
                st.json(summary_data)

        st.write("**Operations / Process Steps**")
        if order_data["operations"]:
            ops_df = pd.DataFrame(order_data["operations"])
            st.dataframe(ops_df, use_container_width=True)
        else:
            st.info("No operations data available")

    # Tab 2: Equipment Data
    with tab2:
        st.subheader("Equipment Master Data & Calibration")

        if order_data["equipment"]:
            for equip_id, equip_data in order_data["equipment"].items():
                st.write(f"**Equipment: {equip_id}**")

                col1, col2 = st.columns(2)

                with col1:
                    st.write("*Master Data*")
                    master_df = pd.DataFrame([equip_data["master"]])
                    st.dataframe(master_df, use_container_width=True)

                with col2:
                    st.write("*Calibration Certificate*")
                    calib = equip_data.get("calibration", {})

                    if calib:
                        calib_df = pd.DataFrame([calib])
                        st.dataframe(calib_df, use_container_width=True)

                        # Calibration status indicator
                        status = calib.get("STATUS", "UNKNOWN")
                        expiry_date = calib.get("EXPIRY_DATE")

                        if status == "EXPIRED" and expiry_date:
                            days_expired = (datetime.now().date() - expiry_date).days
                            st.error(f"🔴 **Calibration EXPIRED** - {days_expired} days overdue")
                        elif status == "EXPIRED":
                            st.error(f"🔴 **Calibration Status: EXPIRED**")
                        else:
                            st.success(f"🟢 **Calibration VALID** - Status: {status}")
                    else:
                        st.info("ℹ️ **No Calibration Data** - N/A - Status unknown")
        else:
            st.info("No equipment data for this order")

    # Tab 3: Quality Deviations
    with tab3:
        st.subheader("Quality Notifications & Deviations")

        if order_data["quality_deviations"]:
            st.warning(f"⚠️ **{len(order_data['quality_deviations'])} Quality Deviation(s) Found**")
            st.markdown("---")
            for qm in order_data["quality_deviations"]:
                severity = safe_get(qm, "SEVERITY", "UNKNOWN")
                severity_icon = "🔴" if severity == "HIGH" else "🟡" if severity == "MEDIUM" else "🟢"
                with st.expander(f"{severity_icon} QM #{safe_get(qm, 'QMNUM')} - {safe_get(qm, 'QMTXT')}", expanded=True):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("**Notification Details**")
                        st.write(f"**Description:** {safe_get(qm, 'QMTXT', 'No description')}")
                        st.write(f"**Batch:** {safe_get(qm, 'BATCH', 'N/A')}")
                        st.write(f"**Severity:** {severity}")
                        st.write(f"**Status:** {safe_get(qm, 'QMSTAT', 'N/A')}")

                    with col2:
                        st.write("**Problem Description**")
                        st.write(safe_get(qm, 'BESKR', 'No description provided'))
                        st.write(f"**Problem Code:** {safe_get(qm, 'PROBLEM_CODE', 'N/A')}")
                        st.write(f"**Created:** {safe_get(qm, 'ERDAT', 'N/A')}")
        else:
            st.success("🟢 **No Active Deviations** - This order is compliant for quality notifications")

    # Tab 4: Test Results
    with tab4:
        st.subheader("Quality Control Test Results")

        if order_data["test_results"]:
            for test in order_data["test_results"]:
                test_status = test.get("STATUS", "UNKNOWN")
                status_icon = "✗ FAILED" if test_status == "FAILED" else "✓ PASSED"

                with st.expander(f"{status_icon} - {test.get('TEST_NAME')}", expanded=(test_status == "FAILED")):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("**Test Details**")
                        st.write(f"**Test:** {test.get('TEST_NAME')}")
                        st.write(f"**Result:** {test.get('RESULT')} {test.get('UNIT')}")
                        st.write(f"**Status:** {test_status}")

                    with col2:
                        st.write("**Specification Range**")
                        st.write(f"**Lower Limit:** {test.get('SPEC_LOWER')}")
                        st.write(f"**Upper Limit:** {test.get('SPEC_UPPER')}")
                        st.write(f"**Remarks:** {test.get('REMARKS', 'N/A')}")
        else:
            st.info("No test results available")

    # Tab 5: Compliance Report
    with tab5:
        st.subheader("AI Compliance Audit Report")

        # Auto-generate report if audit results exist but report hasn't been generated
        if st.session_state.audit_results and not st.session_state.report_text:
            try:
                st.session_state.report_text = generate_compliance_report(st.session_state.audit_results)
            except Exception as e:
                st.warning(f"Could not generate report: {str(e)}")

        # Run Audit Button
        if st.button("🚀 Run AI Compliance Audit", use_container_width=True, type="primary"):
            with st.spinner("Running comprehensive GMP compliance audit..."):
                try:
                    # Execute the audit
                    audit_results = audit_sap_order(selected_order)

                    if "error" in audit_results:
                        st.error(f"Audit Error: {audit_results['error']}")
                    else:
                        # Store results in session state
                        st.session_state.audit_results = audit_results

                        # Generate compliance report
                        report = generate_compliance_report(audit_results)
                        st.session_state.report_text = report

                        st.success("✓ Audit completed successfully!")
                        st.rerun()

                except Exception as e:
                    st.error(f"Error during audit execution: {str(e)}")

        # Display Report if available
        if st.session_state.report_text:
            st.markdown("---")
            st.subheader("Generated Report")

            # Display as markdown in code block for formatting
            st.markdown("```\n" + st.session_state.report_text + "\n```")

            # Download button
            col1, col2 = st.columns([3, 1])
            with col2:
                st.download_button(
                    label="📥 Download Report",
                    data=st.session_state.report_text,
                    file_name=f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )

            # Detailed Audit Findings
            if st.session_state.audit_results:
                st.markdown("---")
                st.subheader("Detailed Audit Findings")

                audit = st.session_state.audit_results

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Critical Findings", audit["compliance_summary"]["critical_findings"])

                with col2:
                    st.metric("Major Findings", audit["compliance_summary"]["major_findings"])

                with col3:
                    st.metric("Overall Status", audit["compliance_summary"]["overall_status"])

                # Process Time Analysis
                st.write("**Process Time Analysis**")
                if "time_analysis" in audit["process_time_analysis"]:
                    time_analysis_df = pd.DataFrame(audit["process_time_analysis"]["time_analysis"])
                    st.dataframe(time_analysis_df, use_container_width=True)

                # Equipment Compliance
                st.write("**Equipment Compliance Status**")
                if audit["equipment_compliance"]:
                    equip_df = pd.DataFrame([
                        {
                            "Equipment ID": e["equipment_id"],
                            "Description": e["equipment_description"],
                            "Status": e["compliance_status"],
                            "Days Expired": e["days_expired"]
                        }
                        for e in audit["equipment_compliance"]
                    ])
                    st.dataframe(equip_df, use_container_width=True)

                # Quality Deviations Summary
                st.write("**Quality Deviations Summary**")
                qm_summary = {
                    "Total Deviations": audit["quality_deviations"]["total_deviations"],
                    "Open Issues": len(audit["quality_deviations"]["open_deviations"]),
                    "Critical Issues": len(audit["quality_deviations"]["critical_issues"])
                }
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total", qm_summary["Total Deviations"])
                with col2:
                    st.metric("Open", qm_summary["Open Issues"])
                with col3:
                    st.metric("Critical", qm_summary["Critical Issues"])

        else:
            st.info("👆 Click the **Run AI Compliance Audit** button to generate a compliance report")

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #888; font-size: 12px; padding: 20px;">
        <p>GMP Compliance Agent | SAP S/4HANA Mock Database | Powered by Claude AI</p>
        <p>© 2025 - Pharmaceutical Manufacturing Compliance System</p>
    </div>
""", unsafe_allow_html=True)
