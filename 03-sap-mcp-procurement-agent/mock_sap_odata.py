%%writefile mock_sap_odata.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="Mock SAP OData API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BUSINESS_PARTNERS = [
    {"BusinessPartner": "BP001", "BusinessPartnerName": "Acme Supplies Ltd", "Country": "US", "CreditLimit": 100000, "PaymentTerms": "NET30", "Status": "Active"},
    {"BusinessPartner": "BP002", "BusinessPartnerName": "Global Office Solutions", "Country": "CA", "CreditLimit": 50000, "PaymentTerms": "NET45", "Status": "Active"},
    {"BusinessPartner": "BP003", "BusinessPartnerName": "TechParts Inc", "Country": "US", "CreditLimit": 200000, "PaymentTerms": "NET15", "Status": "Active"},
    {"BusinessPartner": "BP004", "BusinessPartnerName": "Sunrise Distributors", "Country": "MX", "CreditLimit": 75000, "PaymentTerms": "NET30", "Status": "Blocked"},
]
PURCHASE_ORDERS = [
    {"PurchaseOrder": "PO4500001", "Vendor": "BP001", "DocumentDate": "2026-05-01", "TotalNetAmount": 15000, "Currency": "USD", "Status": "Blocked", "BlockReason": "Invoice mismatch - quantity discrepancy", "Material": "MAT-OFFICE-001", "Quantity": 500, "Plant": "1010"},
    {"PurchaseOrder": "PO4500002", "Vendor": "BP002", "DocumentDate": "2026-05-10", "TotalNetAmount": 8200, "Currency": "USD", "Status": "Open", "BlockReason": None, "Material": "MAT-IT-042", "Quantity": 20, "Plant": "1010"},
    {"PurchaseOrder": "PO4500003", "Vendor": "BP003", "DocumentDate": "2026-04-28", "TotalNetAmount": 42000, "Currency": "USD", "Status": "Blocked", "BlockReason": "Goods receipt pending - delivery overdue by 12 days", "Material": "MAT-TECH-007", "Quantity": 100, "Plant": "2010"},
    {"PurchaseOrder": "PO4500004", "Vendor": "BP001", "DocumentDate": "2026-05-15", "TotalNetAmount": 3500, "Currency": "USD", "Status": "Complete", "BlockReason": None, "Material": "MAT-OFFICE-002", "Quantity": 200, "Plant": "1010"},
]
REQUISITIONS = []
REQ_COUNTER = 10000

class RequisitionRequest(BaseModel):
    Material: str
    Quantity: float
    Plant: str
    DeliveryDate: str
    Vendor: Optional[str] = None
    EstimatedValue: Optional[float] = None
    RequestedBy: Optional[str] = None
    Justification: Optional[str] = None

@app.get("/sap/opu/odata/BusinessPartner")
def get_business_partners(search: Optional[str] = None, status: Optional[str] = None):
    results = BUSINESS_PARTNERS.copy()
    if search:
        results = [bp for bp in results if search.lower() in bp["BusinessPartnerName"].lower()]
    if status:
        results = [bp for bp in results if bp["Status"].lower() == status.lower()]
    return {"d": {"results": results, "count": len(results)}}

@app.get("/sap/opu/odata/PurchaseOrders")
def get_purchase_orders(vendor: Optional[str] = None, status: Optional[str] = None):
    results = PURCHASE_ORDERS.copy()
    if vendor:
        results = [po for po in results if po["Vendor"] == vendor]
    if status:
        results = [po for po in results if po["Status"].lower() == status.lower()]
    return {"d": {"results": results, "count": len(results)}}

@app.post("/sap/opu/odata/PurchaseRequisitions", status_code=201)
def create_requisition(req: RequisitionRequest):
    global REQ_COUNTER
    REQ_COUNTER += 1
    new_req = {"PurchaseRequisition": f"PR{REQ_COUNTER}", "Material": req.Material, "Quantity": req.Quantity, "Plant": req.Plant, "DeliveryDate": req.DeliveryDate, "Vendor": req.Vendor, "EstimatedValue": req.EstimatedValue, "RequestedBy": req.RequestedBy, "Justification": req.Justification, "Status": "Created", "CreatedAt": "2026-05-19T10:00:00Z"}
    REQUISITIONS.append(new_req)
    return {"d": new_req}

@app.get("/health")
def health():
    return {"status": "ok", "service": "Mock SAP OData API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
