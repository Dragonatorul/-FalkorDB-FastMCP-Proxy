#!/usr/bin/env python3
"""
Direct MCP Protocol Test

This script tests the MCP protocol directly with our FastMCP server
to verify that tools are properly registered and accessible.
"""

import asyncio
import json
from contextlib import asynccontextmanager

import httpx
from mcp import ClientSession
from mcp.client.sse import sse_client


async def test_mcp_connection():
    """Test direct MCP connection to our FastMCP server."""
    
    # Bearer token from Docker logs
    bearer_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2ZhbGtvcmRiLWZhc3RtY3AtcHJveHkiLCJzdWIiOiJkZXYtdXNlciIsImlhdCI6MTc1MjQ4NTI2MywiZXhwIjoxNzUyNDg4ODYzLCJhdWQiOiJmYWxrb3JkYi1tY3Atc2VydmVyIiwic2NvcGUiOiJyZWFkIHdyaXRlIn0.Aeql3cnZ3i5m5wbVEm4F5iny-obL7SCGA5XUFvI3BXdZOOZzrDSlbV6iIb4wj6RlXgJRXmBzOYadxItjKn21pb_m09ZdER86AAn2IvcSoFUxZjV2Qr3ZHGXwdVf6XWbF3nhs-EItjyR7YP9-vG93bfPCvcjecrNS2XnltsLXTTevkEAodr3CAVQc85TWQNiUHYL8KymZWrSiRtXaoW7g7XPbXbJ6FGAURejuazB3SvHzKXEv4Rvgc_lHDIn1CTghfD1hP46N789d0_Jxoh_bvdF8FE1EyWyQU0fCSzTA5RTXV5lAZqPB2sxMFA37ZEa1Nojt8Fr75tu6otEyiLHWLQ"
    
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "User-Agent": "MCP-Test-Client/1.0"
    }
    
    print("🔗 Connecting to FastMCP server...")
    
    try:
        async with sse_client("http://localhost:3001/sse", headers=headers) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                print("✅ Connected! Initializing...")
                
                # Initialize the session
                result = await session.initialize()
                print(f"📋 Server info: {result.serverInfo}")
                print(f"🔧 Capabilities: {result.capabilities}")
                
                # List available tools
                print("\n🛠️  Listing tools...")
                tools_result = await session.list_tools()
                
                if tools_result.tools:
                    print(f"✅ Found {len(tools_result.tools)} tools:")
                    for tool in tools_result.tools:
                        print(f"  - {tool.name}: {tool.description}")
                else:
                    print("❌ No tools found!")
                    
                # Try to call a tool if available
                if tools_result.tools:
                    health_tool = next((t for t in tools_result.tools if t.name == "falkordb_health"), None)
                    if health_tool:
                        print(f"\n🏥 Testing {health_tool.name}...")
                        call_result = await session.call_tool(health_tool.name, {})
                        print(f"Result: {call_result.content}")
                    else:
                        print("❌ falkordb_health tool not found")
                        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_mcp_connection())