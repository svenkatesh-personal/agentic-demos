# Google GenAI SDK — Vertex AI/Gemini

A demonstration of **Google's GenAI SDK** for **Gemini** (and Vertex AI integration). Google's unique strength is **integrated RAG and managed services**.

Key differentiator: You don't always need to build your own vector database—Vertex AI Search handles it for you.

---

## When to Use Google GenAI SDK

✅ **You want managed RAG** (Vector DB built-in via Vertex AI Search)  
✅ **You're invested in Google Cloud** (BigQuery, Firestore, etc.)  
✅ **You need Gemini's multimodal capabilities** (Vision, Audio, Video)  
✅ **You want to avoid infrastructure** (Fully managed service)  
✅ **Enterprise compliance** (SOC2, FedRAMP via Vertex AI)

❌ You need multi-model support (local LLMs, Claude, etc.)  
❌ You prefer on-premise or open-source-only  
❌ You have a small budget and need free tier  
❌ You want model switching flexibility

---

## Architecture Overview

```
User Query
   ↓
Gemini Model (google.generativeai)
   ↓
Tool Function Declarations
   ↓
Function Calling (Same as OpenAI)
   ↓
Your Tool Execution
   ↓
Result Loop
   ↓
Final Response (with optional Vertex AI Search integration)
```

---

## Setup

### Step 1: Navigate & Install Dependencies

```bash
cd google-genai-agent
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
export GOOGLE_API_KEY="your-actual-key-here"
```

**For Vertex AI (Optional):**
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
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
✨ Google Gemini Agent - Financial Advisor
============================================================

💬 Query: What is the tax on user U123's balance in NY?

🤖 Gemini Initial Response:

🔧 Tool Call #1:
  Function: get_user_balance
  Arguments: {'user_id': 'U123'}
  Result: User U123 has balance: $1500.00...

🔧 Tool Call #2:
  Function: calculate_tax
  Arguments: {'amount': 1500.0, 'state': 'NY'}
  Result: {"user_id":"","balance":0,"state":"NY","tax_rate":0.08,...}

============================================================
✅ Final Answer:
User U123 has a balance of $1500.00. In New York with an 8% tax rate,
the tax would be $120.00, making the total $1620.00.
============================================================
```

---

## Core Concepts

### 1. **Function Declaration (Different from OpenAI)**

```python
# Google uses protos for schema definition
tools = [genai.protos.Tool(
    function_declarations=[
        genai.protos.FunctionDeclaration(
            name="get_balance",
            description="Get user balance",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "user_id": genai.protos.Schema(
                        type=genai.protos.Type.STRING
                    )
                },
                required=["user_id"]
            )
        )
    ]
)]
```

### 2. **Tool Calling Loop**

```
Loop:
    1. model.generate_content(..., tools=tools)
    2. Check if response has function_calls
    3. If yes → Execute → Add to messages
    4. If no → Done
    5. Repeat
```

### 3. **Processing Function Calls**

```python
# Each part in response can be a function_call
for part in response.candidates[0].content.parts:
    if hasattr(part, 'function_call'):
        func_name = part.function_call.name
        func_args = part.function_call.args
        result = execute_function(func_name, func_args)
```

---

## Google vs OpenAI: Key Differences

| Aspect | Google GenAI | OpenAI |
|--------|-------------|--------|
| **Schema Format** | Protocol Buffers (protos) | JSON Schema |
| **RAG Integration** | Native (Vertex AI Search) | Manual setup |
| **Multimodal** | Yes (Vision, Audio, Video) | Image only (vision) |
| **Streaming** | `stream=True` | Using stream() context |
| **Function Schema Definition** | `genai.protos.*` | Dict-based JSON |
| **Managed Service Option** | Vertex AI | Separate platform |
| **Pricing Model** | Per-token (cheaper at scale) | Per-1K-tokens |

---

## Advanced: Vertex AI Search (Managed RAG)

Google's biggest advantage is **Vertex AI Search**—no vector DB setup needed:

```python
# Define a retrieval tool that uses Vertex AI Search
retrieval_tool = genai.protos.Tool(
    function_declarations=[
        genai.protos.FunctionDeclaration(
            name="search_docs",
            description="Search internal documents using Vertex AI Search",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "query": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="Search query"
                    )
                }
            )
        )
    ]
)

# The model handles the search automatically
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    tools=[retrieval_tool]
)
```

---

## Streaming Responses

```python
# Stream each chunk as it's generated
response = model.generate_content(
    contents=query,
    stream=True
)

for chunk in response:
    if chunk.text:
        print(chunk.text, end="", flush=True)
```

---

## Multimodal Capabilities (Google's Advantage)

```python
import PIL.Image

# Vision: Analyze an image
image = PIL.Image.open("receipt.jpg")
response = model.generate_content(
    ["What items are on this receipt?", image]
)

# Text + image together
response = model.generate_content([
    "Extract the total price from this receipt",
    image,
    {"role": "user", "content": "Is this over $100?"}
])
```

---

## Project Structure

```
google-genai-agent/
├── agent.py         # Main agent with Gemini
├── pyproject.toml   # Dependencies
└── README.md        # This file
```

---

## Comparison: All Four Frameworks

| Feature | LangChain | PydanticAI | OpenAI SDK | Google GenAI |
|---------|-----------|-----------|-----------|---|
| **Best For** | Flexible, multi-tool | Type-safe, production | GPT-only fast | Managed RAG, multimodal |
| **Lines of Code** | 100+ | 80 | 150 | 120 |
| **Learning Curve** | Moderate | Easy | Steep | Moderate |
| **Model Support** | 50+ | 10+ | 1 (GPT) | Gemini + Vertex AI |
| **RAG Built-in** | ❌ (300+ integrations) | ❌ | ❌ | ✅ (Vertex AI Search) |
| **Multimodal** | ✅ (via integrations) | ❌ | ✅ (Vision) | ✅✅ (Vision, Audio, Video) |
| **Type Safety** | Partial | Excellent | None | Partial |
| **Production Ready** | ✅✅ | ✅✅ | ✅ | ✅✅ |

---

## Troubleshooting

### "GOOGLE_API_KEY not found"
```bash
export GOOGLE_API_KEY="your-key-from-aistudio.google.com"
```

### Vertex AI Setup Issues
```bash
# Install gcloud CLI
brew install google-cloud-sdk

# Authenticate
gcloud auth application-default login

# Set project
gcloud config set project your-project-id
```

### Function Not Being Called
1. Check tool description is clear
2. Ensure parameters are properly defined
3. Verify `allowed_function_names` includes your tool

---

## References

- [Google GenAI Python SDK](https://ai.google.dev/)
- [Gemini API Documentation](https://ai.google.dev/api/python/google/generativeai)
- [Vertex AI Search](https://cloud.google.com/generative-ai-app-builder/docs)
- [Function Calling Guide](https://ai.google.dev/tutorials/function_calling_python)

---

## License

MIT
