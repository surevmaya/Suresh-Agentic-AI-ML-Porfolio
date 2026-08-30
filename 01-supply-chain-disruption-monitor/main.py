from fastapi import FastAPI, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from mock_engine import generate_report, COMMODITY_REGIONS

app = FastAPI(title="Supply Chain Risk Monitor")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def dashboard(request: Request):
    return templates.TemplateResponse(request,"dashboard.html" ,  {
  	"commodities": COMMODITY_REGIONS })

@app.get("/api/monitor")
async def monitor(
    commodity: str = Query(...),
    region: str = Query(...),
    live: bool = Query(False)
):
    report = generate_report(commodity, region, live_mode=live)
    return report

@app.get("/health")
async def health():
    return {"status": "ok", "mode": "demo"}
