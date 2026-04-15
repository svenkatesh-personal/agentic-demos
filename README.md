# Agentic Demos

A comprehensive collection of demonstrations showcasing **Agent Frameworks**, **Model Context Protocol (MCP)**, and agentic AI patterns. Each project is self-contained with its own dependencies and environment.

---

## Projects

### 📍 Project 0: Local MCP Weather Server
A local MCP server built with **uv** and the **MCP Python SDK** that exposes weather tools powered by the free [National Weather Service (NWS) API](https://www.weather.gov/documentation/services-web-api). Includes weather alerts and forecast capabilities with no API key required.

**Tech**: Python, MCP SDK, uv, stdio transport  
📖 [View Project README](./local-mcp-weather/README.md)

---

## Agent Framework Comparison Projects

The following 4 projects implement **the same financial advisor agent** in different frameworks to demonstrate trade-offs and design decisions:

### 🦜 Project 1: LangChain Agent
**The Ecosystem King** — Best for complex multi-tool applications with easy model/vector store swapping.

**Strengths:**
- ✅ 50+ LLM providers supported
- ✅ 300+ vector store integrations
- ✅ Native MCP adapter (best-in-class)
- ✅ Mature, battle-tested ecosystem

**When to use:** Multi-model flexibility, complex RAG workflows, niche tool integrations

**Stack**: Python, LangChain, OpenAI API, uv  
📖 [View Project README](./langchain-agent/README.md)

---

### 🏗️ Project 2: PydanticAI Agent
**The Standard Agent Core** — Production-grade type-safe framework with strict data validation.

**Strengths:**
- ✅ Excellent type safety (no runtime errors)
- ✅ Built-in dependency injection (like FastAPI)
- ✅ Structured outputs guaranteed
- ✅ Clean, Pythonic API

**When to use:** Production apps where data accuracy is critical, startups/MVPs, APIs requiring type safety

**Stack**: Python, PydanticAI, Pydantic v2, OpenAI API, uv  
📖 [View Project README](./pydantic-ai-agent/README.md)

---

### 🚀 Project 3: OpenAI Agent SDK
**The Minimalist** — Low latency, GPT-native with minimal dependencies and overhead.

**Strengths:**
- ✅ Lowest latency (direct API, no abstraction)
- ✅ Built-in tool calling (no external library)
- ✅ Latest OpenAI features first
- ✅ Simple, straightforward API

**When to use:** 100% committed to OpenAI/GPT-4, latency-critical apps, minimal overhead

**Stack**: Python, OpenAI SDK, uv  
📖 [View Project README](./openai-agent/README.md)

---

### ✨ Project 4: Google GenAI Agent
**The Managed RAG Choice** — Integrated vector DB, multimodal capabilities, enterprise-friendly.

**Strengths:**
- ✅ Managed RAG (Vertex AI Search built-in)
- ✅ Multimodal (Vision, Audio, Video)
- ✅ Enterprise compliance options
- ✅ Google Cloud integration (BigQuery, Firestore)

**When to use:** Managed infrastructure preferred, Need multimodal, Google Cloud ecosystem, Startup with limited ops

**Stack**: Python, Google GenAI SDK, Gemini API, uv  
📖 [View Project README](./google-genai-agent/README.md)

---

## Quick Comparison Matrix

| Framework | Best For | Model Flexibility | Type Safety | Setup Complexity | MCP Support | RAG Integration |
|-----------|----------|------------------|-------------|------------------|------------|-----------------|
| **LangChain** | Multi-tool, complex | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Moderate | ⭐⭐⭐⭐⭐ | 300+ options |
| **PydanticAI** | Production, type-safe | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Easy | ⭐⭐⭐⭐ | Manual setup |
| **OpenAI SDK** | GPT-only, fast | ⭐⭐ | ⭐⭐ | Easy | ⭐⭐⭐ | Manual setup |
| **Google GenAI** | Managed RAG, multimodal | ⭐⭐⭐ | ⭐⭐ | Moderate | ⭐⭐ | ✅ Built-in |

---

## Getting Started

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager

### Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Setup an Agent Project

```bash
# Navigate to a project
cd langchain-agent

# Install dependencies
uv sync

# Copy the .env template (never committed to git)
cp .env.example .env

# Edit .env and add your actual API key
# (Use your editor: nano .env, or open it in VS Code)

# Run the agent
uv run python agent.py
```

---

## Environment Variables & Security

Each project directory includes a **`.env.example`** file showing required variables.

### Setup Pattern (Safe for Teams)

1. **`.env.example`** — Committed to git, shows required variables (no values)
   ```
   OPENAI_API_KEY=sk-your-api-key-here
   ```

2. **`.env`** — Each developer's local copy (in `.gitignore`, never committed)
   ```
   OPENAI_API_KEY=sk-actual-key-12345
   ```

3. **CI/CD** — Use GitHub Secrets or environment variables (not files)

### Load `.env` in Your Code

Add to the top of any agent script:

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Loads .env file

api_key = os.getenv("OPENAI_API_KEY")
```

**The agents already include this!** So just run:

```bash
uv run python agent.py
```

---

## Decision Guide

### Choose LangChain if...
- You want to test multiple LLM providers
- You need 300+ pre-built integrations
- Building RAG with unusual vector stores
- Working with Agents + RAG + Tools extensively

### Choose PydanticAI if...
- Building production services
- Type safety is non-negotiable
- You love FastAPI's dependency injection
- Structured outputs are required

### Choose OpenAI SDK if...
- Exclusively using OpenAI/GPT-4
- Latency is critical
- You prefer minimal dependencies
- Simple, direct API is preferred

### Choose Google GenAI if...
- Managed infrastructure is preferred
- You need multimodal (Vision, Audio, Video)
- Google Cloud is your infra
- Don't want to manage vector databases

---

## Project Structure

```
agentic-demos/
├── README.md                 # This file
├── .gitignore               # Git configuration
├── .vscode/settings.json    # VS Code workspace settings
│
├── local-mcp-weather/       # MCP Server Example
│   ├── weather.py
│   ├── pyproject.toml
│   └── README.md
│
├── langchain-agent/         # LangChain Framework
│   ├── agent.py
│   ├── pyproject.toml
│   └── README.md
│
├── pydantic-ai-agent/       # PydanticAI Framework
│   ├── agent.py
│   ├── pyproject.toml
│   └── README.md
│
├── openai-agent/            # OpenAI SDK Framework
│   ├── agent.py
│   ├── pyproject.toml
│   └── README.md
│
└── google-genai-agent/      # Google GenAI Framework
    ├── agent.py
    ├── pyproject.toml
    └── README.md
```

---

## Running All Agents (Sequentially)

To test all frameworks one by one:

```bash
# 1. LangChain
echo "🦜 Running LangChain Agent..."
cd langchain-agent && uv sync && uv run python agent.py && cd ..

# 2. PydanticAI
echo "🏗️  Running PydanticAI Agent..."
cd pydantic-ai-agent && uv sync && uv run python agent.py && cd ..

# 3. OpenAI SDK
echo "🚀 Running OpenAI SDK Agent..."
cd openai-agent && uv sync && uv run python agent.py && cd ..

# 4. Google GenAI
echo "✨ Running Google GenAI Agent..."
cd google-genai-agent && uv sync && uv run python agent.py && cd ..
```

---

## Key Takeaways

1. **LangChain** = Flexibility & Ecosystem (Choose this if unsure)
2. **PydanticAI** = Type Safety & Production (Choose for critical systems)
3. **OpenAI SDK** = Speed & Simplicity (Choose for GPT-only shops)
4. **Google GenAI** = Managed Services & Multimodal (Choose for Google ecosystem)

**Pro Tip for Senior Architects:** Consider building a abstraction layer that lets you swap frameworks via dependency injection. This allows teams to make the best choice for each use case.

---

## References

- [LangChain Documentation](https://python.langchain.com/)
- [PydanticAI Documentation](https://ai.pydantic.dev/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Google GenAI Documentation](https://ai.google.dev/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

---

## License

MIT
