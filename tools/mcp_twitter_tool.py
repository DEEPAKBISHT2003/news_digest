from mcp import ClientSession
from langchain_core.tools import tool
import asyncio

# Replace with actual MCP server URL
MCP_SERVER_URL = "https://your-mcp-server-url"

@tool
def fetch_twitter_mcp(query: str) -> str:
    """
    Fetch tweets using MCP server
    """

    async def run():
        async with ClientSession(MCP_SERVER_URL) as session:
            
            # Call MCP tool (example: search tweets)
            result = await session.call_tool(
                "search_tweets",   # depends on server tools
                {"query": query}
            )

            return str(result)

    return asyncio.run(run())