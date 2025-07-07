#!/usr/bin/env python3
"""
Test script to debug FastMCP Bearer token authentication
"""

import sys
import os
sys.path.append('src')

from fastmcp_proxy import mcp, auth, generate_test_token, key_pair
import asyncio
import jwt
import httpx
import threading
import uvicorn
import time

def test_token_validation():
    """Test token generation and validation logic"""
    print("🔍 Testing token generation and validation...")
    
    # Generate token
    token = generate_test_token()
    print(f"✅ Generated token: {token[:50]}...")
    
    # Decode without verification
    decoded = jwt.decode(token, options={'verify_signature': False})
    print(f"✅ Token claims: {decoded}")
    
    # Verify with public key
    try:
        verified = jwt.decode(
            token, 
            key_pair.public_key, 
            algorithms=['RS256'],
            issuer='https://falkordb-fastmcp-proxy',
            audience='falkordb-mcp-server'
        )
        print(f"✅ Token verification successful")
        return token
    except Exception as e:
        print(f"❌ Token verification failed: {e}")
        return None

def start_server_thread():
    """Start FastMCP server in background thread"""
    print("🚀 Starting FastMCP server...")
    
    def run_server():
        try:
            app = mcp.sse_app
            uvicorn.run(app, host='0.0.0.0', port=3001, log_level="info")
        except Exception as e:
            print(f"❌ Server error: {e}")
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    return server_thread

async def test_sse_endpoint(token):
    """Test SSE endpoint with Bearer token"""
    print("🌐 Testing SSE endpoint...")
    
    # Wait for server to start
    await asyncio.sleep(3)
    
    # Test without auth
    print("📋 Testing without authentication...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get('http://localhost:3001/sse/')
            print(f"   Status: {response.status_code}")
            if response.status_code != 200:
                print(f"   Body: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test with Bearer token
    print("🔐 Testing with Bearer token...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                'http://localhost:3001/sse/',
                headers={'Authorization': f'Bearer {token}'}
            )
            print(f"   Status: {response.status_code}")
            if response.status_code != 200:
                print(f"   Body: {response.text[:200]}")
            else:
                print("   ✅ Authentication successful!")
    except Exception as e:
        print(f"   Error: {e}")

async def test_oauth_endpoints():
    """Test OAuth endpoints"""
    print("🔗 Testing OAuth endpoints...")
    
    endpoints = [
        "/.well-known/oauth-authorization-server",
        "/authorize",
        "/token"
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for endpoint in endpoints:
            try:
                response = await client.get(f'http://localhost:3001{endpoint}')
                print(f"   {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    print(f"      ✅ Working")
                else:
                    print(f"      Body: {response.text[:100]}")
            except Exception as e:
                print(f"   {endpoint}: Error - {e}")

async def main():
    """Main test function"""
    print("🧪 FastMCP Authentication Debug Test")
    print("=" * 50)
    
    # Test token validation
    token = test_token_validation()
    if not token:
        print("❌ Token validation failed, aborting")
        return
    
    print(f"\n🔑 Using token: {token}")
    
    # Start server
    start_server_thread()
    
    # Test endpoints
    await test_sse_endpoint(token)
    await test_oauth_endpoints()
    
    print("\n🏁 Test complete!")

if __name__ == "__main__":
    asyncio.run(main())