"""Exercise actual MCP stdio handshake, schemas, calls, errors and recovery."""
import asyncio
import json
import sys
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

CASES = [('getZiweiChart', {'date': '1990-03-24', 'hour': 10, 'gender': '男'}, {'date': '2026-02-30', 'hour': 10, 'gender': '男'})]

@pytest.mark.asyncio
async def test_stdio_protocol():
    async def scenario():
        params = StdioServerParameters(command=sys.executable, args=["-c", "from shunshi_ziwei_mcp.server import main; main()"])
        async with stdio_client(params) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                listed = await session.list_tools()
                assert {t.name for t in listed.tools} == {c[0] for c in CASES}
                for tool in listed.tools:
                    assert tool.description and tool.inputSchema["type"] == "object"
                for name, valid, invalid in CASES:
                    result = await session.call_tool(name, valid)
                    assert not result.isError, result
                    payload = json.loads(result.content[0].text)
                    assert len(payload["chart"]["palaces"]) == 12
                    error = await session.call_tool(name, invalid)
                    assert error.isError
                    again = await session.call_tool(name, valid)
                    assert not again.isError
    await asyncio.wait_for(scenario(), timeout=90)
