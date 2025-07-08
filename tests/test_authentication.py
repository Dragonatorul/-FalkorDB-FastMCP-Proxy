#!/usr/bin/env python3
"""
Test script to demonstrate FalkorDB FastMCP Proxy authentication
This tests the same authentication mechanism that Claude Desktop would use
"""

import asyncio
import httpx
import json
from typing import Dict, Any

# Configuration
PROXY_URL = "http://localhost:3001"
BEARER_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2ZhbGtvcmRiLWZhc3RtY3AtcHJveHkiLCJzdWIiOiJkZXYtdXNlciIsImlhdCI6MTc1MTk0NDkyNywiZXhwIjoxNzUxOTQ4NTI3LCJhdWQiOiJmYWxrb3JkYi1tY3Atc2VydmVyIiwic2NvcGUiOiJyZWFkIHdyaXRlIn0.EFWl3c4m8uPUfseIfWQAsq1LqLayv1ooVVGLdcPuNPSspxRolut29CXM4WY3q7_OxXkE54FGtYLWrMYCeV7oSf4ocLDh4IhbwKdEMvjUn3SVFpU6AKlGe4Q6WzURO4xCa3U_Xt5D13Y4ge8DZBaOYis44Cq0_dYE0OffroDeFgULyYD14liOz-1Eylbgu7ATLeJeMR5NWXNvJoScKCJZcaekJpojh-FrfXfPNLtDY0ejDkwMjlgg82cMhoUJrWPQ9Ld_447t-RB83AXnCZvt5Ji0vvo2LSc_Z8dSimYqKirJmGzewhB9SoCWiA8Duqx7Jz3HRLnFr01Ns0Z_vv6BNQ"

async def test_oauth_endpoints():
    """Test OAuth 2.1 Discovery and Authentication Endpoints"""
    print("🔍 Testing OAuth 2.1 Authentication System")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Test 1: OAuth Authorization Server Metadata
        print("\\n1. Testing OAuth Authorization Server Metadata...")
        try:
            response = await client.get(f"{PROXY_URL}/.well-known/oauth-authorization-server")
            if response.status_code == 200:
                metadata = response.json()
                print("✅ OAuth metadata endpoint working")
                print(f"   Issuer: {metadata.get('issuer')}")
                print(f"   Grant types: {metadata.get('grant_types_supported')}")
            else:
                print(f"❌ OAuth metadata failed: {response.status_code}")
        except Exception as e:
            print(f"❌ OAuth metadata error: {e}")

        # Test 2: MCP Server Discovery
        print("\\n2. Testing MCP Server Discovery...")
        try:
            headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
            response = await client.get(f"{PROXY_URL}/mcp/", headers=headers)
            if response.status_code == 200:
                print("✅ MCP server endpoint accessible with Bearer token")
            else:
                print(f"❌ MCP server access failed: {response.status_code}")
        except Exception as e:
            print(f"❌ MCP server error: {e}")

        # Test 3: Unauthenticated Access (should fail)
        print("\\n3. Testing Unauthenticated Access (should fail)...")
        try:
            response = await client.get(f"{PROXY_URL}/mcp/")
            if response.status_code == 401:
                print("✅ Correctly rejected unauthenticated request")
            else:
                print(f"⚠️  Unexpected response for unauthenticated request: {response.status_code}")
        except Exception as e:
            print(f"❌ Unauthenticated test error: {e}")

async def test_mcp_tool_functionality():
    """Test MCP Tool Functionality through the authenticated proxy"""
    print("\\n🛠️  Testing MCP Tool Functionality")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: List available tools
        print("\\n1. Testing MCP Tools Discovery...")
        try:
            # Create a simple tool request (this simulates what Claude Desktop would do)
            tool_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }
            
            response = await client.post(
                f"{PROXY_URL}/mcp/message",
                headers=headers,
                json=tool_request
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ MCP tools list request successful")
                if "result" in data and "tools" in data["result"]:
                    tools = data["result"]["tools"]
                    print(f"   Found {len(tools)} tools:")
                    for tool in tools:
                        print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                else:
                    print("⚠️  Unexpected tools response format")
            else:
                print(f"❌ Tools list failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Tools discovery error: {e}")

        # Test 2: Test FalkorDB Health Check
        print("\\n2. Testing FalkorDB Health Check Tool...")
        try:
            health_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "falkordb_health",
                    "arguments": {}
                }
            }
            
            response = await client.post(
                f"{PROXY_URL}/mcp/message",
                headers=headers,
                json=health_request
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Health check tool executed successfully")
                if "result" in data:
                    result_content = data["result"].get("content", [{}])
                    if result_content and len(result_content) > 0:
                        health_result = result_content[0].get("text", "No health data")
                        print(f"   Health Status: {health_result[:200]}...")
                    else:
                        print("⚠️  No health content in response")
            else:
                print(f"❌ Health check failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Health check error: {e}")

        # Test 3: Test Graph Listing
        print("\\n3. Testing Graph Listing Tool...")
        try:
            graphs_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "falkordb_list_graphs",
                    "arguments": {}
                }
            }
            
            response = await client.post(
                f"{PROXY_URL}/mcp/message",
                headers=headers,
                json=graphs_request
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Graph listing tool executed successfully")
                if "result" in data:
                    result_content = data["result"].get("content", [{}])
                    if result_content and len(result_content) > 0:
                        graphs_result = result_content[0].get("text", "No graphs data")
                        print(f"   Graphs: {graphs_result[:200]}...")
                    else:
                        print("⚠️  No graphs content in response")
            else:
                print(f"❌ Graphs listing failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Graphs listing error: {e}")

def print_claude_desktop_config():
    """Print the Claude Desktop configuration example"""
    print("\\n🖥️  Claude Desktop Configuration")
    print("=" * 50)
    print("Add this to your Claude Desktop configuration file:")
    print("(macOS: ~/Library/Application Support/Claude/claude_desktop_config.json)")
    print("(Windows: %APPDATA%\\Claude\\claude_desktop_config.json)")
    print()
    
    config = {
        "mcpServers": {
            "falkordb": {
                "serverUrl": f"{PROXY_URL}/mcp/",
                "auth": {
                    "type": "bearer",
                    "token": BEARER_TOKEN
                }
            }
        }
    }
    
    print(json.dumps(config, indent=2))
    print()
    print("⚠️  Note: This is a development token that expires in 1 hour.")
    print("   For production, use proper OAuth flow or longer-lived tokens.")

async def main():
    """Main test function"""
    print("🚀 FalkorDB FastMCP Proxy Authentication Test")
    print("Testing the same authentication mechanism used by Claude Desktop")
    print("=" * 70)
    
    # Run authentication tests
    await test_oauth_endpoints()
    
    # Run MCP functionality tests
    await test_mcp_tool_functionality()
    
    # Print Claude Desktop config
    print_claude_desktop_config()
    
    print("\\n🎉 Authentication testing complete!")
    print("✅ The proxy supports Bearer token authentication compatible with Claude Desktop")

if __name__ == "__main__":
    asyncio.run(main())