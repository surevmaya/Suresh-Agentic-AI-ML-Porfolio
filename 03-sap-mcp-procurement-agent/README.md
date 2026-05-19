# SAP MCP Procurement Agent

OpenAI-powered procurement agent connected to mock SAP S/4HANA via an MCP server.

## Architecture
User → OpenAI gpt-4o-mini → MCP Server (auth + logging + guardrails) → Mock SAP OData API

## Features
- Natural language interface to SAP procurement data
- Vendor search, purchase order lookup, requisition creation
- Human-in-the-loop approval for requisitions exceeding $50,000
- API key authentication and request logging on MCP layer

## Demo scenarios
- "Show me all blocked purchase orders"
- "Why is PO4500003 blocked?"
- "Create a requisition for 200 units of MAT-TECH-007 at plant 2010, needed by 2026-06-30, estimated value $75,000"

## Stack
Python, FastAPI, OpenAI API, mock SAP OData, MCP protocol pattern

## Setup
pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."
python mock_sap_odata.py   # Terminal 1
python mcp_server.py       # Terminal 2
python agent.py            # Terminal 3
