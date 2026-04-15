# OpenAI Agent SDK — The Minimalist

A demonstration of OpenAI's native **Agent SDK**, released to compete with LangChain. Provides the **lowest latency** and **best GPT performance** at the cost of flexibility.

OpenAI's philosophy: *"If you're using GPT-4, why add layers?"*

---

## When to Use OpenAI SDK

✅ **You're 100% committed to OpenAI** (GPT-4, GPT-4o)  
✅ **You need minimal latency** (no abstraction overhead)  
✅ **You want the latest OpenAI features** first  
✅ **Your use case is GPT-only** (no Claude, Gemini, local LLMs)  
✅ **You prefer simplicity** over flexibility

❌ You need multi-model support  
❌ You want to use open-source LLMs  
❌ You need 300+ integrations

---

## Architecture Overview

```
User Query
   ↓
OpenAI Chat Completions API
   ↓
GPT-4o (direct, no abstraction)
   ↓
Tool Function Calling Schema
   ↓
Tool Execution (Your Functions)
   ↓
Result Loop (Until "stop_reason" = "end_turn")
   ↓
Final Response
```

---

## Setup

### Step 1: Navigate & Install Dependencies

```bash
cd openai-agent
uv sync
```

### Step 2: Configure API Keys

Two options:

**Option A: Environment Variables (Recommended for Development)**

```bash
# Copy the template
cp .env.example .env

# Edit .env and add your actual API key
# .env is in .gitignore, so secrets won't be committed
nano .env  # or use your editor
```

**Option B: Export in Terminal**

```bash
export OPENAI_API_KEY="sk-your-actual-key-here"
```

**⚠️ Security Note:**
- **Never** commit `.env` to git (it's in `.gitignore`)
- Use `.env.example` as a template for developers
- Each developer maintains their own `.env` locally

---

## Running the Agent

### Basic Example

```bash
uv run python agent.py
```

**Output:**

```
🚀 OpenAI Agent SDK - Multi-Tool Financial Assistant
============================================================

💬 Query: What is the tax on user U123's balance in NY?

🤖 Initial Response:
  Stop Reason: tool_calls

🔧 Tool Call #1:
  Function: get_user_balance
  Input: {'user_id': 'U123'}
  Result: User U123 balance: $1500.00...

🔧 Tool Call #2:
  Function: calculate_tax
  Input: {'amount': 1500.0, 'state': 'NY'}
  Result: {"user_id":"","amount":1500.0,"state":"NY",...}

============================================================
✅ Final Answer:
User U123 has a balance of $1500.00 in New York. 
The sales tax on this amount at 8% is $120.00, for a total of $1620.00.
============================================================
```

---

## Core Concepts

### 1. **Tool Schema Format**

OpenAI uses JSON Schema for tool definitions:

```python
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_user_balance",
            "description": "Get the current balance for a user",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID like U123"
                    }
                },
                "required": ["user_id"]
            }
        }
    }
]
```

### 2. **Tool Calling Loop**

```
Loop:
    1. Call chat.completions.create(..., tools=TOOLS)
    2. Check response.stop_reason
    3. If "tool_calls" → Execute tools → Add results to messages
    4. If "end_turn" → Done
    5. Repeat
```

### 3. **Processing Tool Results**

```python
# LLM returns tool_calls
for tool_call in response.choices[0].message.tool_calls:
    tool_name = tool_call.function.name
    tool_input = json.loads(tool_call.function.arguments)
    
    # Execute the tool
    result = process_tool_call(tool_name, tool_input)
    
    # Add result back to conversation
    messages.append({
        "tool_call_id": tool_call.id,
        "role": "tool",
        "content": result
    })
```

---

## Comparison: OpenAI SDK vs LangChain vs PydanticAI

| Aspect | OpenAI SDK | LangChain | PydanticAI |
|--------|-----------|-----------|-----------|
| **Lines of Code** | ~150 | ~100 | ~80 |
| **Model Support** | GPT-4 only | 50+ models | 10+ models |
| **Tool Definition** | JSON Schema | Python @tool | Python @tool |
| **Latency** | Baseline | +5-20ms (overhead) | +5-15ms (overhead) |
| **Learning Curve** | Steep | Moderate | Gentle |
| **Production Ready** | Yes | Yes | Yes (newer) |
| **MCP Support** | Emerging | Best | Good |

---

## Advanced Examples

### With Structured Output (Pydantic)

```python
from pydantic import BaseModel

class TaxReport(BaseModel):
    user_id: str
    balance: float
    tax_amount: float
    total: float

# Use OpenAI's structured output
response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=TOOLS,
    response_format={"type": "json_schema", "json_schema": TaxReport.model_json_schema()}
)
```

### Streaming Tool Calls

```python
with client.chat.completions.stream(
    model="gpt-4o",
    messages=messages,
    tools=TOOLS,
) as stream:
    for event in stream:
        if event.type == "tool_calls":
            print(f"Tool: {event.tool_name}")
```

### Assistants API (Higher-level Alternative)

```python
from openai.types.beta import Assistant

# Create an assistant once
assistant = client.beta.assistants.create(
    name="Financial Advisor",
    model="gpt-4o",
    tools=TOOLS
)

# Create a thread for conversation
thread = client.beta.threads.create()

# Add messages and run
client.beta.threads.messages.create(thread.id, role="user", content=query)
run = client.beta.threads.runs.create(thread.id, assistant_id=assistant.id)
```

---

## Key Differences from LangChain

### LangChain (Abstraction Layer)
```python
agent = create_openai_functions_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)
result = executor.invoke({"input": query})
```

### OpenAI SDK (Direct API)
```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": query}],
    tools=TOOLS
)
# Handle response.stop_reason manually
```

**Trade-off:**
- LangChain: More abstraction, easier to switch models
- OpenAI SDK: Less boilerplate, better perf for GPT-only

---

## Project Structure

```
openai-agent/
├── agent.py         # Main agent implementation
├── pyproject.toml   # Dependencies (openai, pydantic)
└── README.md        # This file
```

---

## Troubleshooting

### "tool_calls is None"
Make sure you're accessing it correctly:
```python
# ❌ Wrong
tool_name = response.choices[0].message.tool_calls[0]

# ✅ Correct
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    tool_name = tool_call.function.name
```

### Missing OPENAI_API_KEY
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### Tool Never Gets Called
Check:
1. Tool schema is valid JSON
2. Tool description is clear
3. Query is relevant to the tool
4. `tool_choice="auto"` is set

---

## Comparison Table: When to Use What

| Need | Best Choice | Why |
|------|-------------|-----|
| Multi-model support | LangChain | 50+ models, easy switching |
| Type safety + production | PydanticAI | Built for this |
| Pure GPT-4 speed | OpenAI SDK | Minimal overhead |
| RAG + Complex workflows | LangChain | 300+ integrations |
| Startups / MVPs | PydanticAI | Clean code, fast ship |
| Enterprise flexibility | LangChain | Proven at scale |

---

## References

- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [Chat Completion API](https://platform.openai.com/docs/api-reference/chat/create)
- [Assistants API](https://platform.openai.com/docs/assistants/overview)

---

## License

MIT
