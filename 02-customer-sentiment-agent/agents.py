import anthropic

def run_agent(vendor: str, product: str, 
              contract_value: float,
              decision_days: int,
              api_key: str = None):
    
    client = anthropic.Anthropic(api_key=api_key)
    
    system_prompt = """
You are a vendor sentiment analyst agent
for a large enterprise organisation.

Your job is to analyse vendor and product
sentiment to support contract decisions.

When analysing a vendor you will:
1. Search for recent company news
2. Search for customer reviews
3. Count positive vs negative sentiment
4. Synthesise findings into a report

Scoring:
- Over 75% positive → RENEW ✅
- 50-75% positive → RENEGOTIATE 🔄
- Under 50% positive → REPLACE ❌

Always provide:
- Evidence for recommendation
- Key risks identified
- Negotiating points if renegotiating
- Alternative vendors if replacing
"""

    user_message = f"""
Please analyse this vendor contract decision:

Vendor: {vendor}
Product: {product}
Contract Value: ${contract_value:,.0f}
Decision needed in: {decision_days} days

Produce a structured report with:
1. Executive Summary
2. Company Health (news analysis)
3. Customer Sentiment (review analysis)
4. Sentiment Score (% positive)
5. Key Risks
6. Recommendation: RENEW / RENEGOTIATE / REPLACE
7. Action Points
"""

    messages = [{"role": "user", "content": user_message}]

    print(f"\n🔍 Analysing vendor: {vendor}")
    print(f"   Product: {product}")
    print(f"   Contract: ${contract_value:,.0f}")
    print(f"   Decision in: {decision_days} days")
    print("=" * 50)

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=system_prompt,
            tools=TOOLS,
            messages=messages
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    print(block.text)
            break

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

# Run it!
run_agent(
    vendor="SAP",
    product="S/4HANA",
    contract_value=2500000,
    decision_days=90,
    api_key="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"
)
