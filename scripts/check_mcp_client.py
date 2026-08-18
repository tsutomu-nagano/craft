import asyncio
import os

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main() -> None:
    url = os.getenv("MCP_URL", "http://127.0.0.1:8000/mcp")
    async with streamablehttp_client(url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()

    print(f"MCP URL: {url}")
    print("Tools:")
    for tool in tools.tools:
        print(f"- {tool.name}: {tool.description}")


if __name__ == "__main__":
    asyncio.run(main())
