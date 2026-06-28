# GMP Compliance Agent - Streamlit Dashboard

A clean, interactive frontend for the GMP Compliance Agent that lets you audit pharmaceutical manufacturing process orders against regulatory requirements.

## Features

### 1. **Sidebar Process Order Selection**
   - Dropdown menu to select from available Process Order IDs in the mock SAP database
   - Quick stats on selected order
   - Real-time data source indicator

### 2. **KPI Metrics Dashboard**
   - **Compliance Grade**: A-F grade based on audit results
   - **Quality Deviations**: Count of quality notifications for the order
   - **Safety Risk Level**: HIGH/LOW based on deviations
   - **Overall Status**: ✓/✗ compliance indicator

### 3. **Multi-Tab Data Views**

   **📋 Process Order Tab**
   - Header information (Order ID, Material, Quantity, Plant, Work Center, Status)
   - Operations/Process Steps table with standard vs. actual durations
   
   **🏭 Equipment Data Tab**
   - Equipment master data
   - Calibration certificate status and expiry dates
   - Visual warnings for expired calibrations
   
   **⚠️ Quality Deviations Tab**
   - Expandable quality notifications (QMEL)
   - Deviation descriptions and severity levels
   - Problem codes and root cause info
   
   **🧪 Test Results Tab**
   - Quality control (QC) test results
   - Specification ranges and pass/fail status
   - Test remarks and anomalies
   
   **📄 Compliance Report Tab**
   - Run AI Compliance Audit button
   - Generates detailed markdown report
   - Download report as TXT file
   - Detailed audit findings breakdown

### 4. **AI Compliance Audit**
   - Click **"Run AI Compliance Audit"** button to trigger comprehensive audit
   - Analyzes:
     - Process time deviations
     - Equipment calibration compliance
     - Quality notifications and deviations
     - Batch test results
   - Generates structured compliance report with findings and corrective actions

## Running the Dashboard

### Prerequisites
Ensure dependencies are installed:
```bash
pip install -r requirements.txt
```

### Start the Dashboard
```bash
streamlit run dashboard.py
```

The dashboard will open at `http://localhost:8501/` in your browser.

## Data Sources

The dashboard integrates with mock SAP S/4HANA tables:
- **AFKO**: Process Order Headers
- **AFVC**: Process Order Operations
- **EQUI**: Equipment Master Data
- **EQUI_CALIB**: Equipment Calibration Certificates
- **AUFK**: Maintenance Orders
- **QMEL**: Quality Notifications/Deviations
- **QALS**: Quality Control Test Results
- **BATCH_RECORD**: Product Batch Records

## Available Process Orders

Currently available test order:
- **4500012345**: Pharma tablet manufacturing with mixing phase deviation

## Example Workflow

1. **Select Order**: Choose `4500012345` from sidebar
2. **Review Order Data**: Check Process Order and Equipment tabs
3. **Inspect Deviations**: Review Quality Deviations tab for issues
4. **Run Audit**: Click "Run AI Compliance Audit" button
5. **View Report**: Read generated compliance report with findings
6. **Download**: Export report as text file for archiving/sharing

## Report Contents

The generated compliance report includes:

1. **Audit Details** - Order ID, timestamps, summary statistics
2. **Process Time Analysis** - Duration deviations vs. SOP requirements
3. **Equipment Calibration Compliance** - Certificate status and expiry
4. **Quality Deviations & Notifications** - Open/closed issues
5. **Batch Quality Status** - Test results and batch hold status
6. **Compliance Findings** - Critical issues requiring action
7. **Recommendations & Next Steps** - Immediate, short-term, and follow-up actions

## Integration with Agent

The dashboard uses the core GMP Compliance Agent functions:
- `audit_sap_order()` - Comprehensive audit orchestration
- `generate_compliance_report()` - Report formatting
- Mock SAP database functions - Data retrieval

## Customization

To add new process orders, edit `mock_sap_db.py`:
- Add entries to AFKO (headers), AFVC (operations), etc.
- Update the available_orders list in the sidebar
- New data automatically appears in dashboard

## Styling

The dashboard uses:
- Streamlit native components
- Custom CSS for metric cards with gradient backgrounds
- Color-coded status indicators (green for compliant, red for non-compliant)
- Responsive layout for mobile and desktop

## Performance Notes

- Data is cached with `@st.cache_data` to reduce recompute
- Audit runs are synchronous; consider async processing for production
- Mock database supports 1-2 concurrent users efficiently

## Next Steps

For production deployment:
- Connect to real SAP S/4HANA system via OData API
- Add authentication/authorization
- Implement database backend for audit history
- Add scheduled audit capabilities
- Integrate with compliance tracking systems
