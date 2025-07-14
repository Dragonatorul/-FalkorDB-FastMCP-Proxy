#!/usr/bin/env python3
"""Simple MCP client to test FastMCP proxy"""

import asyncio
import json
import aiohttp
import sys
from typing import Dict, Any

async def test_mcp_tools():
    """Test MCP tools via HTTP SSE"""
    
    # Test 1: List tools
    print("=== Testing MCP Tools via FastMCP Proxy ===")
    
    try:
        # Direct backend test first
        print("1. Testing backend health directly...")
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:3000/health", 
                                  headers={"X-API-Key": "dev-api-key"}) as resp:
                backend_health = await resp.json()
                print(f"   Backend Status: {backend_health['status']}")
        
        # Test FastMCP tools
        print("\n2. Testing FastMCP proxy tools...")
        
        # Import and test the tools directly
        import sys
        sys.path.insert(0, 'src')
        from fastmcp_proxy import mcp, call_backend
        from fastmcp import Context
        
        ctx = Context(fastmcp=mcp)
        
        # Test health via proxy
        print("   Testing health via proxy...")
        health_result = await call_backend("GET", "/health")
        print(f"   Proxy Health Result: {health_result['status']}")
        
        # Test graphs listing
        print("   Testing graphs listing via proxy...")
        graphs_result = await call_backend("GET", "/api/mcp/graphs")
        print(f"   Graphs Result: {graphs_result}")
        
        # Test server info
        print("   Testing server metadata via proxy...")
        metadata_result = await call_backend("GET", "/api/mcp/metadata")
        print(f"   Server Info: {metadata_result['provider']} v{metadata_result['version']}")
        
        print("\n✅ All proxy backend calls working successfully!")
        
        # Test tools registration
        tools = await mcp.get_tools()
        print(f"\n3. Registered Tools: {len(tools)} tools")
        for name, tool in tools.items():
            print(f"   - {name}: {tool.description}")
            
        print("\n✅ FastMCP proxy is working correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())