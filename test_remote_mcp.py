#!/usr/bin/env python3
"""
Test script for FalkorDB FastMCP Proxy with remote SSE connections.

This script validates:
1. OAuth Authorization Server Metadata endpoint
2. SSE endpoint authentication 
3. Remote MCP client connection capability
"""

import os
import sys
import time
import subprocess
import requests
import json
from typing import Dict, Any

# Add src to path for imports
sys.path.append('src')
from fastmcp_proxy import key_pair

def generate_bearer_token() -> str:
    """Generate a valid Bearer token for testing"""
    token = key_pair.create_token(
        subject="test-user",
        issuer="https://falkordb-fastmcp-proxy",
        audience="falkordb-mcp-server", 
        scopes=["read", "write"],
        expires_in_seconds=3600
    )
    return f"Bearer {token}"

def test_oauth_metadata(base_url: str) -> bool:
    """Test OAuth Authorization Server Metadata endpoint"""
    try:
        response = requests.get(f"{base_url}/.well-known/oauth-authorization-server", timeout=5)
        if response.status_code == 200:
            metadata = response.json()
            required_fields = ["issuer", "authorization_endpoint", "token_endpoint"]
            if all(field in metadata for field in required_fields):
                print("✅ OAuth Authorization Server Metadata endpoint working")
                return True
            else:
                print(f"❌ OAuth metadata missing required fields: {metadata}")
                return False
        else:
            print(f"❌ OAuth metadata endpoint returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing OAuth metadata: {e}")
        return False

def test_sse_endpoint_auth(base_url: str, bearer_token: str) -> bool:
    """Test SSE endpoint authentication"""
    try:
        # Test without auth - should get 401
        response = requests.get(f"{base_url}/sse/", timeout=5)
        if response.status_code != 401:
            print(f"❌ SSE endpoint should require auth, got {response.status_code}")
            return False
        
        # Test with valid Bearer token - should get SSE connection
        headers = {"Authorization": bearer_token}
        response = requests.get(f"{base_url}/sse/", headers=headers, timeout=5, stream=True)
        
        if response.status_code in [200, 202]:
            print("✅ SSE endpoint accepts valid Bearer token")
            return True
        elif response.status_code == 401:
            print(f"❌ Valid Bearer token was rejected: {response.text}")
            return False
        else:
            print(f"❌ Unexpected SSE response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing SSE endpoint: {e}")
        return False

def test_backend_connectivity() -> bool:
    """Test connectivity to FalkorDB MCP Server backend"""
    try:
        response = requests.get("http://localhost:3000/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Backend health: {health.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing FalkorDB FastMCP Proxy for Remote Access")
    print("=" * 60)
    
    # Configuration
    proxy_url = "http://localhost:3001"
    
    # Generate test token
    print("🔑 Generating Bearer token...")
    bearer_token = generate_bearer_token()
    print(f"   Token: {bearer_token[:50]}...")
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    print(f"\n📡 Testing backend connectivity...")
    if test_backend_connectivity():
        tests_passed += 1
    
    print(f"\n🔐 Testing OAuth Authorization Server Metadata...")
    if test_oauth_metadata(proxy_url):
        tests_passed += 1
        
    print(f"\n🌊 Testing SSE endpoint authentication...")
    if test_sse_endpoint_auth(proxy_url, bearer_token):
        tests_passed += 1
    
    # Results
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! FastMCP proxy is ready for remote Claude Desktop connections.")
        print("\n📋 Claude Desktop Configuration:")
        print(f'{{')
        print(f'  "name": "FalkorDB",')
        print(f'  "serverUrl": "{proxy_url}/sse/",')
        print(f'  "auth": {{')
        print(f'    "type": "bearer",') 
        print(f'    "token": "{bearer_token.replace("Bearer ", "")}"')
        print(f'  }}')
        print(f'}}')
        return True
    else:
        print("❌ Some tests failed. Check the proxy configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)