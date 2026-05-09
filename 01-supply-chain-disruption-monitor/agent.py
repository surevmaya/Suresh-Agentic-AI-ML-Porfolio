import anthropic
from dotenv import load_dotenv
from tools import (
    search_news,
    search_weather_disruptions,
    search_port_disruptions,
    search_commodity_price
)

load_dotenv()

# Define tools Claude can call
TOOLS = [
    {
        "name": "search_news",
        "description": "Search recent news for supply chain disruptions",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query e.g. 'lithium supply shortage Australia'"
                },
                "days_back": {
                    "type": "integer",
                    "description": "How many days back to search, default 7"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_weather_disruptions",
        "description": "Search for weather events affecting supply chains",
        "input_schema": {
            "type": "object",
            "properties": {
                "region": {
                    "type": "string",
                    "description": "Region to check e.g. 'Australia', 'Southeast Asia'"
                }
            },
            "required": ["region"]
        }
    },
    {
        "name": "search_port_disruptions",
        "description": "Search for port and logistics disruptions",
        "input_schema": {
            "type": "object",
            "properties": {
                "region": {
                    "type": "string",
                    "description": "Region to check e.g. 'Singapore', 'US West Coast'"
                }
            },
            "required": ["region"]
        }
    },
    {
        "name": "search_commodity_price",
        "description": "Get commodity price context via news",
        "input_schema": {
            "type": "object",
            "properties": {
                "commodity": {
                    "type": "string",
                    "description": "Commodity name e.g. 'lithium', 'steel', 'LNG'"
                }
            },
            "required": ["commodity"]
        }
    }
]


def run_tool(tool_name: str, tool_input: dict) -> str:
    """Execute the tool Claude chose to call"""
    if tool_name == "search_news":
        return search_news(
            tool_input["query"],
            tool_input.get("days_back", 7)
        )
    elif tool_name == "search_weather_disruptions":
        return search_weather_disruptions(tool_input["region"])
    elif tool_name == "search_port_disruptions":
        return search_port_disruptions(tool_input["region"])
    elif tool_name == "search_commodity_price":
        return search_commodity_price(tool_input["commodity"])
    return "Tool not found"


def run_agent(commodity: str, region: str):
    """Main agent loop"""
    client = anthropic.Anthropic()

    # Load system prompt
    with open("prompts/system.md", "r") as f:
        system_prompt = f.read()

    # Initial user message
    user_message = f"""
    Please analyse supply chain disruption risks for:
    - Commodity: {commodity}
    - Region: {region}

    Produce a structured risk report with:
    1. Executive Summary
    2. Key Risks Identified (with risk level)
    3. Evidence and Sources
    4. Recommended Actions
    5. Monitoring Priorities
    """

    messages = [{"role": "user", "content": user_message}]

    print(f"\n🔍 Analysing supply chain risks...")
    print(f"   Commodity: {commodity}")
    print(f"   Region: {region}")
    print("=" * 50)

    # Agent loop
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=system_prompt,
            tools=TOOLS,
            messages=messages
        )

        # Final response — print report
        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    print(block.text)
            break

        # Tool use — execute and feed back
        if response.stop_reason == "tool_use":
            messages.append({
                "role": "assistant",
                "content": response.content
            })

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"⚙️  Calling: {block.name}({block.input})")
                    result = run_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            messages.append({
                "role": "user",
                "content": tool_results
            })


if __name__ == "__main__":
    # Example run
    run_agent(
        commodity="LNG",
        region="Australia"
    )
