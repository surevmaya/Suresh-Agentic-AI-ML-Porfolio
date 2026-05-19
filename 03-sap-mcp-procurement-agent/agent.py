import os, json, requests
from openai import OpenAI

OPENAI_API_KEY = "sk-your-key-here"  # paste your key
MCP_BASE_URL   = "http://localhost:8001/mcp/tools"
MCP_API_KEY    = "demo-mcp-key-123"
MCP_HEADERS    = {"x-api-key": MCP_API_KEY}

client = OpenAI(api_key=OPENAI_API_KEY, timeout=30.0)

def load_tools():
    resp = requests.get(MCP_BASE_URL, timeout=5)
    return resp.json()["tools"]

def call_mcp_tool(tool_name, tool_args):
    if tool_name == "search_vendors":
        resp = requests.get(f"{MCP_BASE_URL}/search_vendors", params=tool_args, headers=MCP_HEADERS, timeout=5)
    elif tool_name == "get_purchase_orders":
        resp = requests.get(f"{MCP_BASE_URL}/get_purchase_orders", params=tool_args, headers=MCP_HEADERS, timeout=5)
    elif tool_name == "create_requisition":
        resp = requests.post(f"{MCP_BASE_URL}/create_requisition", json=tool_args, headers=MCP_HEADERS, timeout=5)
    else:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    return json.dumps(resp.json(), indent=2)

SYSTEM_PROMPT = """You are a SAP Procurement Agent. Help procurement teams manage
vendors, purchase orders, and requisitions. Always check SAP data before answering. Be concise."""

tools = load_tools()
conversation = [{"role": "system", "content": SYSTEM_PROMPT}]

print("\n" + "="*55)
print("  SAP Procurement Agent (OpenAI + MCP + mock SAP)")
print("="*55)
print("Try: 'Show me all blocked purchase orders'")
print("Try: 'Why is PO4500003 blocked?'")
print("Try: 'Create a requisition for 200 units of MAT-TECH-007 at plant 2010, needed by 2026-06-30, estimated value $75,000'")
print("Type 'quit' to exit\n")

while True:
    user_input = input("You: ").strip()
    if not user_input or user_input.lower() in ("quit", "exit"):
        print("Goodbye.")
        break

    conversation.append({"role": "user", "content": user_input})

    while True:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=conversation,
                tools=tools,
                tool_choice="auto",
                temperature=0.2,
            )
        except Exception as e:
            print(f"\nError: {e}\n")
            conversation.pop()
            break

        message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason
        conversation.append(message)

        if finish_reason == "stop":
            print(f"\nAgent: {message.content}\n")
            break
        elif finish_reason == "tool_calls":
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                print(f"  [calling {tool_name}({tool_args})]")
                result = call_mcp_tool(tool_name, tool_args)
                conversation.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
