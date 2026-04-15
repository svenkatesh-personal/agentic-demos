# Local MCP Weather Server

A local [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server built with **uv** and the **MCP Python SDK**. It exposes weather tools (alerts & forecasts) powered by the free [National Weather Service (NWS) API](https://www.weather.gov/documentation/services-web-api) — no API key required.

Built following the official guide: <https://modelcontextprotocol.io/docs/develop/build-server>

**References:**
- [MCP Inspector Tool](https://modelcontextprotocol.io/docs/tools/inspector) — Web UI for testing servers
- [Python SDK Examples](https://github.com/modelcontextprotocol/python-sdk/tree/main/examples)
- [National Weather Service API Docs](https://www.weather.gov/documentation/services-web-api)

---

## Tools Provided

| Tool | Description |
| --- | --- |
| `get_alerts(state)` | Get active weather alerts for a US state (two-letter code, e.g. `CA`, `NY`) |
| `get_forecast(latitude, longitude)` | Get the weather forecast for a given lat/lon location |

---

## Prerequisites

- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** — fast Python package manager

Install uv (if not already installed):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Setup

```bash
# 1. Navigate to the project directory
cd local-mcp-weather

# 2. Sync / install all dependencies (creates .venv automatically)
uv sync
```

---

## Running the Server

### Option 1 — Run directly (stdio transport)

```bash
uv run python weather.py
```

The server communicates over **stdio** and is meant to be launched by an MCP client (e.g. Claude Desktop, an IDE plugin, or the MCP Inspector).

### Option 2 — Run with the MCP Inspector (recommended for development)

```bash
uv run mcp dev weather.py
```

This starts the [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) — a web-based UI where you can browse available tools, send test requests, and see responses. The Inspector URL will be printed in the terminal (typically `http://localhost:5173`).

### Option 3 — Install into Claude Desktop

```bash
uv run mcp install weather.py
```

This registers the server with the Claude Desktop app so it can use the weather tools during conversations.

### Stop / Restart

- To stop the running server, terminate the process:
  - If started in a terminal: press `Ctrl+C`
  - If running in the background, use `ps aux | grep '[w]eather.py'` and then `kill <PID>`
- `uv stop` is not required for this project.
- To restart the server after stopping it, run:

```bash
cd local-mcp-weather
uv run --directory . python weather.py
```

> If the server is installed in Claude Desktop, you do not need to reinstall after code changes. Simply stop the running process and start it again.

---

## Configuring in an MCP Client (manual JSON)

If your MCP client requires a JSON config entry (e.g. Claude Desktop `claude_desktop_config.json`), add:

```json
{
  "mcpServers": {
    "weather": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/local-mcp-weather",
        "run",
        "python",
        "weather.py"
      ]
    }
  }
}
```

> Replace `/ABSOLUTE/PATH/TO/local-mcp-weather` with the real absolute path on your machine.

---

## Example Usage (via MCP Inspector)

1. Start the inspector:
   ```bash
   uv run mcp dev weather.py
   ```
2. Open the Inspector URL shown in the terminal.
3. Click **Tools** to see `get_alerts` and `get_forecast`.
4. Try `get_alerts` with `state = "CA"` to see active California weather alerts.
5. Try `get_forecast` with `latitude = 37.7749` and `longitude = -122.4194` for a San Francisco forecast.

---

## Project Structure

```
local-mcp-weather/
├── weather.py        # MCP server – defines tools & runs stdio transport
├── pyproject.toml    # Project metadata & dependencies
├── uv.lock           # Locked dependency versions
├── .python-version   # Python version pin
└── README.md         # This file
```

---

## License

MIT

