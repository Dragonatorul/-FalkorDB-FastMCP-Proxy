#!/usr/bin/env python3
"""
Test script for the FastMCP proxy server
"""
import asyncio
import os
import sys
sys.path.append('src')

from fastmcp_proxy import call_backend, list_tools, call_tool

async def test_backend_connection():
    """Test direct backend connection"""
    print("Testing backend connection...")
    try:
        result = await call_backend("GET", "/health")
        print(f"✅ Health check: {result}")
        
        result = await call_backend("GET", "/api/mcp/metadata")
        print(f"✅ Metadata: {result}")
        
        result = await call_backend("GET", "/api/mcp/graphs")
        print(f"✅ Graphs: {result}")
        
    except Exception as e:
        print(f"❌ Backend error: {e}")
        return False
    return True

async def test_mcp_tools():
    """Test MCP tool implementations"""
    print("\nTesting MCP tools...")
    
    # Test tool listing
    try:
        tools = await list_tools()
        print(f"✅ Found {len(tools.tools)} tools:")
        for tool in tools.tools:
            print(f"  - {tool.name}: {tool.description}")
    except Exception as e:
        print(f"❌ Tool listing error: {e}")
        return False
    
    # Test individual tools
    test_cases = [
        ("falkordb_health", {}),
        ("falkordb_server_info", {}),
        ("falkordb_list_graphs", {}),
        ("falkordb_query", {
            "graphName": "test",
            "query": "RETURN 1 as one"
        })
    ]
    
    for tool_name, params in test_cases:
        try:
            result = await call_tool(tool_name, params)
            print(f"✅ {tool_name}: Success")
            if result.content:
                content = result.content[0].text[:100] + "..." if len(result.content[0].text) > 100 else result.content[0].text
                print(f"   Result: {content}")
        except Exception as e:
            print(f"❌ {tool_name}: {e}")
    
    return True

async def main():
    # Set environment variables
    os.environ["FALKORDB_MCPSERVER_URL"] = "http://localhost:3000"
    os.environ["MCP_API_KEY"] = "dev-api-key"
    
    print("FastMCP Proxy Test")
    print("=" * 50)
    
    # Test backend connectivity
    backend_ok = await test_backend_connection()
    if not backend_ok:
        print("❌ Backend tests failed, aborting")
        return
    
    # Test MCP tools
    tools_ok = await test_mcp_tools()
    
    if backend_ok and tools_ok:
        print("\n✅ All tests passed! FastMCP proxy is working correctly.")
    else:
        print("\n❌ Some tests failed.")

if __name__ == "__main__":
    asyncio.run(main())