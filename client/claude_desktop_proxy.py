#!/usr/bin/env python3
"""
FastMCP STDIO Proxy for Claude Desktop Integration

This creates a FastMCP proxy server that runs via STDIO transport for Claude Desktop,
while connecting to our authenticated FastMCP proxy server via Bearer token authentication.

Architecture:
    Claude Desktop ←STDIO→ FastMCP Proxy ←Bearer Token→ Authenticated FastMCP Server ←HTTP→ MCPServer ←→ FalkorDB

Usage:
    python claude_desktop_proxy.py

Author: Claude Code Assistant
Version: 1.0.0 - FastMCP STDIO Proxy with Bearer Authentication
License: MIT
"""

import os
import sys
from fastmcp import FastMCP
from fastmcp.client import Client
from fastmcp.client.auth import BearerAuth

# Configuration
PROXY_URL = os.environ.get("FASTMCP_PROXY_URL", "http://localhost:3001/sse/")
BEARER_TOKEN = os.environ.get("FASTMCP_BEARER_TOKEN")

def create_authenticated_proxy():
    """Create FastMCP proxy with Bearer token authentication for Claude Desktop."""
    
    if not BEARER_TOKEN:
        print("Error: FASTMCP_BEARER_TOKEN environment variable is required", file=sys.stderr)
        print("Generate a token by running: python src/fastmcp_proxy.py", file=sys.stderr)
        sys.exit(1)
    
    # Create authenticated client
    client = Client(
        PROXY_URL,
        auth=BearerAuth(token=BEARER_TOKEN)
    )
    
    # Create FastMCP proxy for Claude Desktop STDIO transport
    proxy = FastMCP.as_proxy(
        client, 
        name="FalkorDB Remote Proxy"
    )
    
    return proxy

def main():
    """Main entry point for Claude Desktop STDIO proxy."""
    print("🚀 Starting FalkorDB FastMCP STDIO Proxy for Claude Desktop", file=sys.stderr)
    print(f"📡 Connecting to: {PROXY_URL}", file=sys.stderr)
    print("🔐 Using Bearer token authentication", file=sys.stderr)
    
    # Create and run the authenticated proxy
    proxy = create_authenticated_proxy()
    
    print("✅ FastMCP STDIO proxy ready for Claude Desktop", file=sys.stderr)
    print("🔌 Claude Desktop will communicate via STDIO transport", file=sys.stderr)
    
    # Run the proxy with STDIO transport (default for FastMCP)
    proxy.run()

if __name__ == "__main__":
    main()