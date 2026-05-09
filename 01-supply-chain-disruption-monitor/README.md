# 01 Supply Chain Disruption Monitor Agent

## What this agent does
Monitors news and data sources for supply chain 
disruption signals and produces a structured 
risk report.

## Disruptions it monitors
- 🌪️ Weather / natural disasters
- 🚢 Port / logistics delays
- 🏭 Supplier financial stress
- ⚡ Energy disruption
- 🌍 Geopolitical events
- 📈 Commodity price spikes

## Tech stack
- Python
- Anthropic Claude (claude-sonnet-4-6)
- News API
- Claude Agent SDK

## How to run
1. Clone this repo
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your keys
4. Run: `python agent.py`

## Example use
```python
python agent.py --commodity "lithium" --region "Australia"
```

## Sample output
See `outputs/sample_report.md`

## Real world use case
Early warning system for procurement teams
to get ahead of supply disruptions before
they impact operations.
