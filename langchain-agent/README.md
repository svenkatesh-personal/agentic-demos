# LangChain Agent — The Ecosystem King

A demonstration of **LangChain**, the most mature framework for building multi-tool, multi-model AI agents. LangChain excels at:
- **Easy model swapping** (OpenAI → Anthropic → Local LLMs)
- **300+ vector store integrations** for RAG
- **Native MCP support** (best-in-class)
- **Complex, multi-step workflows**

---

## When to Use LangChain

✅ You need to support **multiple LLM providers**  
✅ You want **pre-built integrations** (Databases, APIs, Search engines)  
✅ You're building a **complex multi-agent system**  
✅ You value **community plugins & ecosystem**

❌ You want minimal dependencies  
❌ You need strict type safety  
❌ You're 100% committed to one vendor

---

## Architecture Overview

```
User Query
   ↓
LangChain Prompt Template (LCEL)
   ↓
LLM (ChatOpenAI, Anthropic, Claude, etc.)
   ↓
Function Calling (Tool Selection)
   ↓
Tool Execution (get_balance, calculate_tax, etc.)
   ↓
Result + Memory
   ↓
Agent Executor (Looping until done)
   ↓
Structured Output (Pydantic Validated)
```

---

## Setup

### Step 1: Navigate & Install Dependencies

```bash
cd langchain-agent
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

This runs a financial assistant that:
1. Retrieves a user's account balance
2. Calculates state tax
3. Provides a summary

**Expected Output:**
```
🦜 LangChain Agent - Multi-Tool Financial Assistant
============================================================

Query: What is the tax on user U123's balance in NY?

============================================================
Agent: I'll help you find the user's balance and calculate the tax.

[Tool Calls]
→ get_user_balance("U123") = 1500.0
→ calculate_tax(1500.0, "NY") = 120.0

Final Summary: User U123 has a balance of $1500.00. The tax in NY is $120.00.
============================================================
```

---

## Key Concepts

### 1. **LCEL (LangChain Expression Language)**

The pipe operator `|` chains components together:

```python
chain = prompt | llm | output_parser
result = chain.invoke({"topic": "finance"})
```

Benefits:
- Automatic streaming support
- Batch processing
- Async compatibility
- Built-in observability

### 2. **Function Calling with Pydantic**

Define tools as Python functions with type hints:

```python
@tool
def get_user_balance(user_id: str) -> float:
    """Look up a user's current account balance."""
    return database.query(user_id)
```

LangChain automatically converts this to OpenAI Function Calling schema.

### 3. **Agent Executor**

The executor loops until the agent says it's done:

```
Loop:
  1. Agent decides which tool to call
  2. Tool executes
  3. Result fed back to agent
  4. Repeat until "Final Answer"
```

---

## Advanced Examples

### RAG with LangChain

```python
from langchain_community.vectorstores import Pinecone
from langchain_openai import OpenAIEmbeddings

# Load documents into vector store
vectorstore = Pinecone.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings()
)

# Add as a tool
retriever_tool = create_retriever_tool(
    retriever=vectorstore.as_retriever(),
    name="search_docs",
    description="Search internal documents"
)
```

### Multi-Agent Coordination

```python
from langchain.agents import AgentType, initialize_agent

agent = initialize_agent(
    tools=[tool1, tool2, tool3],
    llm=llm,
    agent=AgentType.OPENAI_MULTI_FUNCTIONS,
    verbose=True
)
```

---

## Project Structure

```
langchain-agent/
├── agent.py         # Main agent implementation
├── pyproject.toml   # Dependencies
└── README.md        # This file
```

---

## Comparison with Other Frameworks

| Feature | LangChain | PydanticAI | OpenAI SDK | Google GenAI |
|---------|-----------|-----------|-----------|------------|
| Model Flexibility | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Type Safety | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| Ease of Use | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| MCP Support | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Ecosystem Size | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

---

## Troubleshooting

### Missing OpenAI API Key
```
Error: OPENAI_API_KEY environment variable is required
```
Solution:
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### Agent loops infinitely
Set a max iteration limit:
```python
executor = AgentExecutor(agent=agent, tools=tools, max_iterations=5)
```

### Tool not being called
Check that tool description is clear and relevant to the query.

---

## References

- [LangChain Docs](https://python.langchain.com/)
- [LCEL Documentation](https://python.langchain.com/docs/expression_language/)
- [Tool Calling Guide](https://python.langchain.com/docs/modules/tools/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

---

## License

MIT
