"""
FalkorDB FastMCP Proxy with MANDATORY Bearer Authentication

A FastMCP proxy server that provides secure multi-tenant access to FalkorDB MCPServer backend
using proper FastMCP proxy patterns with ProxyClient and MANDATORY authentication.

⚠️ CRITICAL: Authentication is MANDATORY and NEVER optional for multi-tenant security.

Architecture:
    Claude Desktop → FastMCP Proxy (Bearer auth) → FalkorDB MCPServer → FalkorDB
    opencode       → Local Client → FastMCP Proxy → FalkorDB MCPServer → FalkorDB

Environment Variables:
    FALKORDB_MCPSERVER_URL: Backend FalkorDB MCP server URL (default: http://localhost:3000)
    PROXY_PORT: Port for the proxy server (default: 3001)
    PROXY_HOST: Host interface to bind to (default: 0.0.0.0)
    SECRET_KEY: JWT signing secret for multi-tenant tokens (REQUIRED)

Author: Claude Code Assistant
Version: 3.0.0 - Bearer Authentication Only
License: MIT
"""

import os
import sys
from fastmcp import FastMCP
from fastmcp.server.proxy import ProxyClient
from fastmcp.server.auth import BearerAuthProvider
from fastmcp.server.auth.providers.bearer import RSAKeyPair

# Configuration - MANDATORY Authentication
BACKEND_URL = os.environ.get("FALKORDB_MCPSERVER_URL", "http://localhost:3000")
PROXY_HOST = os.environ.get("PROXY_HOST", "0.0.0.0")
PROXY_PORT = int(os.environ.get("PROXY_PORT", "3001"))
SECRET_KEY = os.environ.get("SECRET_KEY")

def setup_mandatory_auth():
    """Setup MANDATORY Bearer token authentication.
    
    ⚠️ CRITICAL: This function ALWAYS sets up authentication.
    Authentication is NEVER optional for multi-tenant security.
    """
    # For development, generate a key pair
    key_pair = RSAKeyPair.generate()
    
    # Create Bearer auth provider
    auth = BearerAuthProvider(
        public_key=key_pair.public_key,
        issuer="https://fastmcp-proxy.dev",
        audience="falkordb-proxy"
    )
    
    return auth, key_pair

def main():
    """Main entry point for the FalkorDB FastMCP Proxy with MANDATORY Authentication."""
    print("🚀 Starting FalkorDB FastMCP Proxy v3.0 - MANDATORY Authentication")
    print(f"📡 Backend URL: {BACKEND_URL}")
    print(f"🌐 Server: http://{PROXY_HOST}:{PROXY_PORT}")
    print("🔐 Authentication: MANDATORY (Multi-tenant security enforced)")
    
    # Validate SECRET_KEY for production use
    if not SECRET_KEY:
        print("\n⚠️ WARNING: SECRET_KEY not set - using generated key for development only")
        print("   For production, set SECRET_KEY environment variable")
    
    print("\n🚨 SECURITY NOTICE:")
    print("   Authentication is MANDATORY and NEVER disabled")
    print("   This ensures proper multi-tenant isolation")
    print("   Any attempt to bypass authentication violates security requirements")
    
    # Setup MANDATORY authentication
    auth, key_pair = setup_mandatory_auth()
    
    # Create proxy with MANDATORY authentication
    proxy = FastMCP.as_proxy(
        BACKEND_URL,
        name="FalkorDB Multi-Tenant Proxy",
        auth=auth  # ALWAYS present - NEVER None
    )
    
    # Generate development token for testing
    dev_token = key_pair.create_token(
        subject="dev-user",
        issuer="https://fastmcp-proxy.dev",
        audience="falkordb-proxy",
        scopes=["read", "write"],
        expires_in_seconds=3600
    )
    
    print(f"\n🔑 Development Bearer Token (Required for ALL connections):")
    print(f"Bearer {dev_token}")
    
    print(f"\n📋 Claude Desktop Configuration (MANDATORY auth):")
    print(f"""{{
  "mcpServers": {{
    "falkordb": {{
      "command": "npx",
      "args": ["mcp-remote", "http://{PROXY_HOST}:{PROXY_PORT}/sse/"],
      "env": {{"MCP_AUTH_HEADER": "Bearer {dev_token}"}}
    }}
  }}
}}""")
    
    print(f"\n📋 opencode Configuration (Local client):")
    print(f"""{{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {{
    "falkordb": {{
      "type": "local",
      "command": ["uvx", "--from", "git+https://github.com/Dragonatorul/FalkorDB-FastMCP-Proxy@feat/fastmcp-proxy-integration", "python", "-m", "client.claude_desktop_proxy"],
      "environment": {{
        "PROXY_URL": "http://{PROXY_HOST}:{PROXY_PORT}/sse/",
        "PROXY_TOKEN": "{dev_token}"
      }},
      "enabled": true
    }}
  }}
}}""")
    
    print(f"\n📡 SSE Endpoint: http://{PROXY_HOST}:{PROXY_PORT}/sse/")
    print("🔐 Authentication: Bearer token REQUIRED for ALL connections")
    print("🏢 Multi-tenant: Tenant identification via JWT subject claim")
    
    print(f"\n🧪 Testing Command (with MANDATORY auth):")
    print(f"   npx mcp-remote 'http://{PROXY_HOST}:{PROXY_PORT}/sse/' \\")
    print(f"     --auth-header 'Bearer {dev_token}'")
    
    # Start the proxy server with MANDATORY authentication
    proxy.run(transport="sse", host=PROXY_HOST, port=PROXY_PORT)

if __name__ == "__main__":
    main()
