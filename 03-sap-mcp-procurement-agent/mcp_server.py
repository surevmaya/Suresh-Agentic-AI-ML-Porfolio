
%%writefile mcp_server.py
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import requests, logging, uvicorn, json, os
from datetime import datetime

app = FastAPI(title="SAP MCP Server", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SAP_BASE_URL = "http://localhost:8000/sap/opu/odata"
MCP_API_KEY = os.getenv("MCP_API_KEY", "demo-mcp-key-123")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

def verify_api_key(x_api_key=None):
    if x_api_key != MCP_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

def log_tool_call(tool_name, params):
    logger.info(f"TOOL CALL: {tool_name} | params: {params}")

@app.get("/mcp/tools")
def get_tools():
    return {"tools": [
        {"type": "function", "function": {"name": "search_vendors", "description": "Search SAP Business Partners by name or status. Returns vendor details including credit limits and payment terms.", "parameters": {"type": "object", "properties": {"search": {"type": "string", "description": "Partial vendor name"}, "status": {"type": "string", "enum": ["Active", "Blocked"]}}, "required": []}}},
        {"type": "function", "function": {"name": "get_purchase_orders", "description": "Retrieve SAP Purchase Orders. Find blocked invoices or check order status. Blocked orders include the block reason.", "parameters": {"type": "object", "properties": {"vendor": {"type": "string", "description": "Vendor BP ID e.g. BP001"}, "status": {"type": "string", "enum": ["Open", "Blocked", "Complete"]}}, "required": []}}},
        {"type": "function", "function": {"name": "create_requisition", "description": "Create a new SAP Purchase Requisition. Returns the new requisition number.", "parameters": {"type": "object", "properties": {"Material": {"type": "string"}, "Quantity": {"type": "number"}, "Plant": {"type": "string"}, "DeliveryDate": {"type": "string"}, "Vendor": {"type": "string"}, "EstimatedValue": {"type": "number"}, "RequestedBy": {"type": "string"}, "Justification": {"type": "string"}}, "required": ["Material", "Quantity", "Plant", "DeliveryDate"]}}}
    ]}

@app.get("/mcp/tools/search_vendors")
def search_vendors(search: Optional[str] = None, status: Optional[str] = None, x_api_key: Optional[str] = Header(None)):
    verify_api_key(x_api_key)
    log_tool_call("search_vendors", {"search": search, "status": status})
    params = {}
    if search: params["search"] = search
    if status: params["status"] = status
    resp = requests.get(f"{SAP_BASE_URL}/BusinessPartner", params=params, timeout=5)
    data = resp.json()
    return {"tool": "search_vendors", "result": data["d"]["results"], "count": data["d"]["count"]}

@app.get("/mcp/tools/get_purchase_orders")
def get_purchase_orders(vendor: Optional[str] = None, status: Optional[str] = None, x_api_key: Optional[str] = Header(None)):
    verify_api_key(x_api_key)
    log_tool_call("get_purchase_orders", {"vendor": vendor, "status": status})
    params = {}
    if vendor: params["vendor"] = vendor
    if status: params["status"] = status
    resp = requests.get(f"{SAP_BASE_URL}/PurchaseOrders", params=params, timeout=5)
    data = resp.json()
    return {"tool": "get_purchase_orders", "result": data["d"]["results"], "count": data["d"]["count"]}

class RequisitionInput(BaseModel):
    Material: str
    Quantity: float
    Plant: str
    DeliveryDate: str
    Vendor: Optional[str] = None
    EstimatedValue: Optional[float] = None
    RequestedBy: Optional[str] = None
    Justification: Optional[str] = None

@app.post("/mcp/tools/create_requisition", status_code=201)
def create_requisition(req: RequisitionInput, x_api_key: Optional[str] = Header(None)):
    verify_api_key(x_api_key)
    if req.EstimatedValue and req.EstimatedValue > 50000:
        return {"tool": "create_requisition", "status": "PENDING_APPROVAL", "message": f"Requisition value ${req.EstimatedValue:,.0f} exceeds $50,000 threshold. Routed to procurement manager for approval.", "data": req.dict()}
    log_tool_call("create_requisition", req.dict())
    resp = requests.post(f"{SAP_BASE_URL}/PurchaseRequisitions", json=req.dict(), timeout=5)
    data = resp.json()
    return {"tool": "create_requisition", "status": "CREATED", "result": data["d"]}

@app.get("/health")
def health():
    return {"status": "ok", "service": "SAP MCP Server"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
