from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams
import os

server_params = {"command":"python",
                 "args":["/home/zadmin/Desktop/test/GAAI-B5-GCP/mcpserver/mcpserver2.py","stdio"]}

conn = StdioConnectionParams(server_params=server_params,timeout=120)

tools = MCPToolset(connection_params=conn)

root_agent = LlmAgent(name="TredenceAgent",
                      model="gemini-2.0-flash",
                      instruction="you are an expert assistant to human users who can provide correct information, based on internet search results to the users.",
                      description="Assitant Agent",
                      tools=[tools])

