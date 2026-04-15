# PydanticAI Agent — The Standard Agent Core

A demonstration of **PydanticAI**, the production-grade agent framework that combines **type safety**, **structured outputs**, and **clean architecture**.

PydanticAI is built by the Pydantic team and treats LLMs like functions that return validated Python objects:

```
Traditional LLM Call: "AI returns a string" → Parse/Extract/Validate (messy)
PydanticAI:          "AI returns a Pydantic model" → Use directly (type-safe)
```

---

## When to Use PydanticAI

✅ **You need strict type safety** and want to avoid runtime errors  
✅ **Production applications** where data accuracy is critical  
✅ **Structured outputs** are required (reports, data extraction)  
✅ **You want clean dependency injection** (like FastAPI)  
✅ **You're building APIs** that clients expect type-safe responses from

❌ You need 100+ vector store integrations  
❌ You want to easily swap between LLM providers  
❌ You prefer loose, dynamic typing

---

## Architecture Overview

```
User Query
   ↓
PydanticAI Agent (with dependencies)
   ↓
Dependency Injection (Database, Config, State)
   ↓
Tool Selection & Execution
   ↓
LLM Call with Context
   ↓
Validation Against Pydantic Model
   ↓
Type-Safe Result Object
   ↓
Direct Usage (no parsing!)
```

---

## Setup

### Step 1: Navigate & Install Dependencies

```bash
cd pydantic-ai-agent
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

**Key Difference from LangChain:**

```python
# LangChain: Get string, then parse
result = executor.invoke({"input": query})
text = result['output']  # String to parse

# PydanticAI: Get typed object directly
result = await agent.run(query, deps=db)
report = result.data  # FinancialReport object
```

---

## Core Concepts

### 1. **Dependency Injection (like FastAPI)**

Define a dependency class:

```python
class DatabaseContext:
    def get_balance(self, user_id: str) -> float:
        return db.query(user_id)

# Pass it to the agent
agent = Agent(model='openai:gpt-4o', deps_type=DatabaseContext)

# Use in tools
@agent.tool
def get_balance(ctx: RunContext[DatabaseContext], user_id: str):
    return ctx.deps.get_balance(user_id)

# Run with the dependency
result = await agent.run(query, deps=DatabaseContext())
```

### 2. **Type-Safe Structured Output**

Declare your output type:

```python
class FinancialReport(BaseModel):
    user_id: str
    balance: float
    tax_amount: float
    recommendation: str

# Agent validates LLM output against the model
agent = Agent(result_type=FinancialReport, ...)
result = await agent.run(query)

# result.data is guaranteed to be a FinancialReport object
print(result.data.user_id)  # ✅ No type checking needed
```

### 3. **Tools as Decorated Methods**

Clean, Pythonic syntax:

```python
@agent.tool
def calculate_tax(ctx: RunContext[DatabaseContext], amount: float, state: str) -> str:
    """Calculate sales tax for a given amount in a specific state."""
    tax_rate = ctx.deps.get_tax_rate(state)
    return f"Tax: ${amount * tax_rate:.2f}"
```

PydanticAI automatically:
- Extracts the docstring as the tool description
- Parses type hints for parameters
- Validates tool calls before execution

---

## Pydantic vs PydanticAI

| Aspect | Pydantic | PydanticAI |
|--------|----------|-----------|
| **Purpose** | Data validation library | Agent framework |
| **Best For** | APIs, configs, data cleaning | Building chatbots, agents, RAG |
| **Talks to LLMs?** | No | Yes (native support) |
| **Output** | Python objects | Validated agent responses |
| **Complexity** | Lightweight | Robust, "FastAPI for AI" |

**You use both together:**

```python
# Pydantic: Define the data contract
class User(BaseModel):
    id: int
    name: str

# PydanticAI: Use it as your agent's output type
agent = Agent(result_type=User, ...)
```

---

## Using Pydantic with LangChain (for comparison)

```python
from pydantic import BaseModel
from langchain_openai import ChatOpenAI

class Person(BaseModel):
    name: str
    age: int

llm = ChatOpenAI(model="gpt-4o")
structured_llm = llm.with_structured_output(Person)

result = structured_llm.invoke("Extract person from: John is 34")
print(result.name)  # ✅ Type-safe access
```

**Comparison:**

| Feature | LangChain + Pydantic | PydanticAI |
|---------|---------------------|-----------|
| Lines of code | 8-10 | 6-8 |
| Dependency injection | Manual | Built-in |
| Tool definitions | Via `@tool` decorator | Via `@agent.tool` |
| Multi-step workflows | Via AgentExecutor | Via `RunContext` |
| Async support | `ainvoke()` | `async/await` native |

---

## Advanced Example: Multi-Step Workflow

```python
@agent.tool
def search_docs(ctx: RunContext[DatabaseContext], query: str) -> str:
    """Search internal documents using RAG."""
    return ctx.deps.vector_db.search(query)

@agent.tool
def fetch_policy(ctx: RunContext[DatabaseContext], policy_id: str) -> str:
    """Fetch a specific policy document."""
    return ctx.deps.policy_db.get(policy_id)

# Agent automatically chains these based on the query
result = await agent.run(
    "Find policies about healthcare benefits",
    deps=DatabaseContext()
)
```

---

## Project Structure

```
pydantic-ai-agent/
├── agent.py         # Main agent with tools and examples
├── pyproject.toml   # Dependencies (pydantic-ai, openai)
└── README.md        # This file
```

---

## Error Handling & Validation

PydanticAI validates at multiple levels:

```python
# ✅ Type validation
@agent.tool
def transfer_money(ctx: RunContext[DB], amount: float) -> str:
    # `amount` is guaranteed to be a float
    # No runtime conversion needed
    pass

# ✅ Pydantic model validation
class PaymentRequest(BaseModel):
    amount: float = Field(gt=0)  # Must be > 0
    recipient: str = Field(min_length=3)

# ✅ Tool execution validation
result_type = PaymentRequest
# LLM must return JSON that matches this schema
```

---

## Comparison with Other Frameworks

| Feature | LangChain | PydanticAI | OpenAI SDK | Google GenAI |
|---------|-----------|-----------|-----------|------------|
| Type Safety | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| Ease of Use | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Production Ready | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Dependency Injection | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| Model Flexibility | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |

---

## Troubleshooting

### Missing API Key
```
Error: OPENAI_API_KEY is not set
```
Solution:
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### Validation Error on Tool Output
PydanticAI validates tool return types. Ensure:
```python
@agent.tool
def my_tool(ctx: RunContext[DB], param: str) -> str:  # ← Returns str
    return "valid string"  # ← Must match return type
```

### Type Hints Missing
Always add type hints to tool parameters:
```python
# ❌ Bad
def my_tool(ctx, param):
    pass

# ✅ Good
def my_tool(ctx: RunContext[DB], param: str) -> str:
    pass
```

---

## References

- [PydanticAI Docs](https://ai.pydantic.dev/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Dependency Injection Pattern](https://en.wikipedia.org/wiki/Dependency_injection)

---

## License

MIT
