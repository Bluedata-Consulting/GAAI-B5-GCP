# app.py
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams
import os
from dotenv import load_dotenv
from .prompt import prompt

load_dotenv()
GITHUB_PERSONAL_ACCESS_TOKEN = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
if not GITHUB_PERSONAL_ACCESS_TOKEN:
    raise RuntimeError("Missing GITHUB_TOKEN in environment (.env)")



server_params = {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github", "stdio"],
        "env": {**os.environ, "GITHUB_TOKEN": GITHUB_PERSONAL_ACCESS_TOKEN},
    }

conn = StdioConnectionParams(server_params=server_params, timeout=120)


github_toolset = MCPToolset(connection_params=conn)

# Minimal instruction; keep it simple.
instruction = (
    "You are a GitHub assistant. "
    "Use MCP tools when available. "
    "For directory listings, call get_file_contents with a directory path."
)

root_agent = LlmAgent(
    name="github_agent",
    model="gemini-2.0-flash",
    instruction=instruction,
    tools=[github_toolset],
)
