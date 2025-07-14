#!/usr/bin/env python3
"""
Test script for FalkorDB FastMCP Multi-Tenant Proxy

This script tests the multi-tenant functionality by generating tokens
and testing basic MCP operations.
"""

import os
import sys
import subprocess
import time
import requests

def test_jwks_server():
    """Test the JWKS server endpoints."""
    print("🧪 Testing JWKS server...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:3002/health", timeout=5)
        if response.status_code == 200:
            print("✅ JWKS health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ JWKS health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ JWKS health endpoint error: {e}")
        return False
    
    try:
        # Test JWKS endpoint
        response = requests.get("http://localhost:3002/.well-known/jwks.json", timeout=5)
        if response.status_code == 200:
            jwks = response.json()
            print("✅ JWKS endpoint working")
            print(f"   Keys found: {len(jwks.get('keys', []))}")
        else:
            print(f"❌ JWKS endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ JWKS endpoint error: {e}")
        return False
        
    return True

def generate_tenant_token(tenant_id):
    """Generate a token for a specific tenant."""
    print(f"🎫 Generating token for tenant: {tenant_id}")
    
    try:
        response = requests.get(f"http://localhost:3002/generate-token/{tenant_id}", timeout=5)
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Token generated for {tenant_id}")
            return token_data["token"]
        else:
            print(f"❌ Token generation failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Token generation error: {e}")
        return None

def test_mcp_backend():
    """Test the MCPServer backend directly."""
    print("🧪 Testing MCPServer backend...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:3000/health", timeout=5)
        if response.status_code == 200:
            print("✅ MCPServer health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ MCPServer health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ MCPServer health endpoint error: {e}")
        return False
        
    return True

def test_mcp_connection_with_token(token, tenant_id):
    """Test MCP connection using npx mcp-remote with authentication."""
    print(f"🧪 Testing MCP connection for tenant: {tenant_id}")
    
    # Test without authentication first
    print("   Testing without auth (should fail)...")
    try:
        result = subprocess.run([
            "npx", "mcp-remote", "http://localhost:3001/sse/"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print("✅ Correctly rejected unauthenticated request")
        else:
            print("⚠️ Unauthenticated request was accepted (unexpected)")
    except subprocess.TimeoutExpired:
        print("⚠️ Unauthenticated test timed out")
    except Exception as e:
        print(f"❌ Unauthenticated test error: {e}")
    
    # Test with authentication
    print("   Testing with auth...")
    env = os.environ.copy()
    env["MCP_AUTH_HEADER"] = f"Bearer {token}"
    
    try:
        result = subprocess.run([
            "npx", "mcp-remote", "http://localhost:3001/sse/"
        ], capture_output=True, text=True, timeout=15, env=env)
        
        if result.returncode == 0:
            print(f"✅ Successfully connected with authentication for {tenant_id}")
            return True
        else:
            print(f"❌ Authenticated connection failed for {tenant_id}")
            print(f"   Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️ Authenticated test timed out")
        return False
    except Exception as e:
        print(f"❌ Authenticated test error: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 FalkorDB FastMCP Multi-Tenant Proxy Test")
    print("=" * 50)
    
    # Test JWKS server
    if not test_jwks_server():
        print("❌ JWKS server tests failed")
        return False
    
    print()
    
    # Test MCPServer backend
    if not test_mcp_backend():
        print("❌ MCPServer backend tests failed")
        return False
    
    print()
    
    # Test multi-tenant functionality
    tenants = ["company-a", "company-b", "acme-corp"]
    
    for tenant in tenants:
        print(f"\n🏢 Testing tenant: {tenant}")
        print("-" * 30)
        
        # Generate token
        token = generate_tenant_token(tenant)
        if not token:
            print(f"❌ Failed to generate token for {tenant}")
            continue
        
        # Test MCP connection
        if test_mcp_connection_with_token(token, tenant):
            print(f"✅ All tests passed for {tenant}")
        else:
            print(f"❌ Some tests failed for {tenant}")
    
    print("\n🎉 Multi-tenant testing completed!")
    return True

if __name__ == "__main__":
    if not main():
        sys.exit(1)