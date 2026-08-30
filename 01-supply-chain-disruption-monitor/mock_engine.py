import random
from datetime import datetime, timedelta

COMMODITY_REGIONS = {
    "lithium": ["Australia", "Chile", "Argentina"],
    "semiconductors": ["Taiwan", "South Korea", "Japan"],
    "rare earths": ["China", "Myanmar", "Australia"],
    "crude oil": ["Saudi Arabia", "Russia", "USA"],
    "coffee": ["Brazil", "Colombia", "Vietnam"],
}

SCENARIOS = {
    ("lithium", "Australia"): {
        "base_risk": 65,
        "headline": "Flooding disrupts Pilbara mining operations",
        "alerts": [
            ("Port / Logistics Delay", "Port Hedland closure extended 72hrs", "High"),
            ("Weather / Natural Disaster", "Cyclone alerts for WA mining belt", "High"),
            ("Commodity Price Spike", "Spot lithium carbonate +12% this week", "Medium"),
        ]
    },
    ("semiconductors", "Taiwan"): {
        "base_risk": 78,
        "headline": "Taiwan Strait tensions trigger contingency planning",
        "alerts": [
            ("Geopolitical Event", "Military exercises near Kaohsiung port", "Critical"),
            ("Energy Disruption", "Grid instability reported in Hsinchu", "High"),
            ("Supplier Financial Stress", "TSMC supplier extends payment terms", "Medium"),
        ]
    },
}

def generate_report(commodity: str, region: str, live_mode: bool = False):
    key = (commodity.lower(), region)
    
    if key in SCENARIOS:
        scenario = SCENARIOS[key].copy()
    else:
        random.seed(f"{commodity}{region}{datetime.now().strftime('%Y%m%d')}")
        scenario = {
            "base_risk": random.randint(25, 85),
            "headline": f"Monitoring {commodity} supply chain in {region}",
            "alerts": random.sample([
                (cat, f"Detected anomaly in {commodity} logistics corridor", lvl)
                for cat in ["Weather / Natural Disaster", "Port / Logistics Delay", 
                           "Supplier Financial Stress", "Energy Disruption",
                           "Geopolitical Event", "Commodity Price Spike"]
                for lvl in ["Low", "Medium", "High"]
            ], k=random.randint(2, 4))
        }
    
    now = datetime.utcnow()
    for i, alert in enumerate(scenario["alerts"]):
        alert_time = now - timedelta(hours=i*6 + random.randint(0, 3))
        scenario["alerts"][i] = (*alert, alert_time.strftime("%Y-%m-%d %H:%M UTC"))
    
    scenario["commodity"] = commodity
    scenario["region"] = region
    scenario["generated_at"] = now.strftime("%Y-%m-%d %H:%M UTC")
    scenario["live_mode"] = live_mode
    
    return scenario
