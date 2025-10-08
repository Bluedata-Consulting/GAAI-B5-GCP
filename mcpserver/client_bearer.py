import asyncio
from fastmcp.client import Client

TOKEN = "dev-alice-token77"  # For StaticTokenVerifier above; replace with a real JWT in production

async def main():
    async with Client("http://localhost:8000/mcp", auth=TOKEN) as client:
        # list tools
        tools = await client.list_tools()
        print("TOOLS:", [t.name for t in tools])

        # call a tool
        res = await client.call_tool("add", arguments={"a": 2, "b": 3})
        print("add(2,3) ->", res)

if __name__ == "__main__":
    asyncio.run(main())
