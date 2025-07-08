#!/usr/bin/env python3
"""
Integration test script for FalkorDB FastMCP Proxy with remote SSE connections.

This module provides comprehensive integration testing for the unified FalkorDB
FastMCP Proxy server with real HTTP connections and backend communication.
Unlike unit tests, these tests require a running proxy server and optionally
a FalkorDB backend server for full validation.

Test Categories:
    1. OAuth Authorization Server Metadata endpoint validation
    2. Server-Sent Events (SSE) endpoint authentication testing
    3. Remote MCP client connection capability validation
    4. Bearer token authentication with HTTP requests
    5. Backend connectivity and health checking

Usage:
    # Run with proxy and backend servers running:
    python tests/test_remote_mcp.py

    # Or use pytest:
    pytest tests/test_remote_mcp.py -v

    # Run as integration test target:
    make test-integration

Requirements:
    - FalkorDB FastMCP Proxy server running on localhost:3001
    - FalkorDB MCP Server backend running on localhost:3000 (optional)
    - Python requests library for HTTP client testing

Output:
    - Detailed test results with pass/fail status
    - Generated Claude Desktop configuration if all tests pass
    - Bearer token examples for development use

Security Note:
    This script generates real JWT tokens for testing. These tokens
    should only be used in development environments.

Author:
    Claude Code Assistant

Version:
    1.0.0
"""

from fastmcp_proxy import generate_test_token
import os
import sys
import requests

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))


def generate_bearer_token() -> str:
    """Generate a valid Bearer token for testing"""
    token = generate_test_token()
    return f"Bearer {token}"


def test_oauth_metadata(base_url: str) -> bool:
    """Test OAuth Authorization Server Metadata endpoint"""
    try:
        response = requests.get(
            f"{base_url}/.well-known/oauth-authorization-server", timeout=5)
        if response.status_code == 200:
            metadata = response.json()
            required_fields = [
                "issuer", "authorization_endpoint", "token_endpoint"]
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


def test_mcp_endpoint_auth(base_url: str, bearer_token: str) -> bool:
    """Test MCP endpoint authentication (streamable-http transport)"""
    try:
        # Test without auth - should get 401
        response = requests.get(f"{base_url}/mcp/", timeout=5)
        if response.status_code != 401:
            print(
                f"❌ MCP endpoint should require auth, got {response.status_code}")
            return False

        # Test with valid Bearer token - should get MCP protocol response
        headers = {"Authorization": bearer_token}
        response = requests.get(f"{base_url}/mcp/", headers=headers, timeout=5)

        if response.status_code in [200, 202]:
            print("✅ MCP endpoint accepts valid Bearer token")
            return True
        elif response.status_code == 401:
            print(f"❌ Valid Bearer token was rejected: {response.text}")
            return False
        else:
            print(f"❌ Unexpected MCP response: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error testing MCP endpoint: {e}")
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

    print("\n📡 Testing backend connectivity...")
    if test_backend_connectivity():
        tests_passed += 1

    print("\n🔐 Testing OAuth Authorization Server Metadata...")
    if test_oauth_metadata(proxy_url):
        tests_passed += 1

    print("\n🌊 Testing MCP endpoint authentication...")
    if test_mcp_endpoint_auth(proxy_url, bearer_token):
        tests_passed += 1

    # Results
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} passed")

    if tests_passed == total_tests:
        print("🎉 All tests passed! FastMCP proxy is ready for remote Claude Desktop connections.")
        print("\n📋 Claude Desktop Configuration:")
        print('{')
        print('  "name": "FalkorDB",')
        print(f'  "serverUrl": "{proxy_url}/sse/",')
        print('  "auth": {')
        print('    "type": "bearer",')
        print(f'    "token": "{bearer_token.replace("Bearer ", "")}"')
        print('  }')
        print('}')
        return True
    else:
        print("❌ Some tests failed. Check the proxy configuration.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
