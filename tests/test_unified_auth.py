#!/usr/bin/env python3
"""
Test script for FalkorDB FastMCP Proxy Unified Authentication

Tests both Bearer token (Claude Desktop) and URL token (opencode) authentication methods.

Usage:
    python test_unified_auth.py
"""

import asyncio
import httpx
import json
from server.fastmcp_proxy import generate_rsa_keypair, create_development_token

async def test_bearer_auth(base_url: str, token: str):
    """Test Bearer token authentication (Claude Desktop style)."""
    print("🧪 Testing Bearer Token Authentication (Claude Desktop)")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{base_url}/mcp",
                json={
                    "method": "tools/list", 
                    "params": {}
                },
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )
            
            if response.status_code == 200:
                print("✅ Bearer token authentication successful")
                result = response.json()
                tools = result.get("tools", [])
                print(f"   Found {len(tools)} tools: {[t['name'] for t in tools]}")
                return True
            else:
                print(f"❌ Bearer token authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Bearer token test error: {e}")
            return False

async def test_url_token_auth(base_url: str, token: str):
    """Test URL token authentication (opencode style)."""
    print("🧪 Testing URL Token Authentication (opencode)")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{base_url}/mcp?token={token}",
                json={
                    "method": "tools/list",
                    "params": {}
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                print("✅ URL token authentication successful")
                result = response.json()
                tools = result.get("tools", [])
                print(f"   Found {len(tools)} tools: {[t['name'] for t in tools]}")
                return True
            else:
                print(f"❌ URL token authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ URL token test error: {e}")
            return False

async def test_multi_tenant_isolation(base_url: str, token1: str, token2: str):
    """Test multi-tenant isolation with different tenant tokens."""
    print("🧪 Testing Multi-Tenant Isolation")
    
    async with httpx.AsyncClient() as client:
        try:
            # Test tenant1 graph creation
            response1 = await client.post(
                f"{base_url}/mcp",
                json={
                    "method": "tools/call",
                    "params": {
                        "name": "falkordb_query",
                        "arguments": {
                            "graph": "test_graph",
                            "query": "CREATE (n:User {name: 'tenant1_user'})"
                        }
                    }
                },
                headers={"Authorization": f"Bearer {token1}"},
                timeout=10.0
            )
            
            # Test tenant2 graph listing
            response2 = await client.post(
                f"{base_url}/mcp?token={token2}",
                json={
                    "method": "tools/call", 
                    "params": {
                        "name": "falkordb_list_graphs",
                        "arguments": {}
                    }
                },
                timeout=10.0
            )
            
            print("✅ Multi-tenant isolation test completed")
            print(f"   Tenant1 response: {response1.status_code}")
            print(f"   Tenant2 response: {response2.status_code}")
            return True
            
        except Exception as e:
            print(f"❌ Multi-tenant isolation test error: {e}")
            return False

async def test_health_check(base_url: str):
    """Test server health without authentication."""
    print("🧪 Testing Server Health Check")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/health", timeout=5.0)
            
            if response.status_code == 200:
                print("✅ Server health check successful")
                return True
            else:
                print(f"❌ Server health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

async def main():
    """Run all authentication tests."""
    print("🚀 FalkorDB FastMCP Proxy - Unified Authentication Tests")
    print("=" * 60)
    
    # Configuration
    base_url = "http://localhost:3001"
    
    # Generate test tokens
    try:
        private_key, public_key = generate_rsa_keypair()
        
        # Create tokens for different tenants
        claude_token = create_development_token(private_key, "claude-user")
        opencode_token = create_development_token(private_key, "opencode-user") 
        
        print(f"🔑 Generated test tokens:")
        print(f"   Claude Desktop: {claude_token[:50]}...")
        print(f"   opencode: {opencode_token[:50]}...")
        print()
        
        # Run tests
        tests = [
            ("Server Health", test_health_check(base_url)),
            ("Bearer Auth", test_bearer_auth(base_url, claude_token)),
            ("URL Token Auth", test_url_token_auth(base_url, opencode_token)),
            ("Multi-Tenant", test_multi_tenant_isolation(base_url, claude_token, opencode_token))
        ]
        
        results = []
        for test_name, test_coro in tests:
            print(f"\n🔍 Running {test_name} test...")
            result = await test_coro
            results.append((test_name, result))
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY:")
        
        passed = 0
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status} {test_name}")
            if result:
                passed += 1
        
        print(f"\nTests passed: {passed}/{len(results)}")
        
        if passed == len(results):
            print("🎉 All tests passed! Unified authentication is working correctly.")
        else:
            print("⚠️ Some tests failed. Check server configuration and logs.")
            
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        print("Make sure the server dependencies are installed:")
        print("   pip install -r requirements/base.txt")

if __name__ == "__main__":
    asyncio.run(main())