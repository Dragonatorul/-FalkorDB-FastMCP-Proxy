#!/usr/bin/env python3
"""
Claude Desktop Proxy for FalkorDB FastMCP Server

This proxy server runs locally via STDIO (which Claude Desktop supports)
and forwards requests to the remote FalkorDB FastMCP server running on HTTP.

Usage:
    python claude_desktop_proxy.py

Claude Desktop Configuration:
    {
      "mcpServers": {
        "falkordb": {
          "command": "python",
          "args": ["path/to/claude_desktop_proxy.py"],
          "env": {
            "BEARER_TOKEN": "your-bearer-token-here"
          }
        }
      }
    }
"""

import os
from fastmcp import FastMCP, Client
from fastmcp.client.auth import BearerAuth

# Get configuration from environment
REMOTE_SERVER_URL = os.environ.get("REMOTE_SERVER_URL", "http://localhost:3001/mcp/")
BEARER_TOKEN = os.environ.get("BEARER_TOKEN")

if not BEARER_TOKEN:
    raise ValueError("BEARER_TOKEN environment variable is required")

# Create authenticated client to connect to remote FastMCP server
client = Client(
    REMOTE_SERVER_URL,
    auth=BearerAuth(token=BEARER_TOKEN)
)

# Create proxy using the authenticated client
proxy = FastMCP.as_proxy(
    client, 
    name="FalkorDB Remote Proxy"
)

if __name__ == "__main__":
    # Run via STDIO for Claude Desktop
    proxy.run()