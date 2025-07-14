"""
FalkorDB FastMCP Proxy

A FastMCP proxy server that provides access to FalkorDB MCPServer backend
using proper FastMCP proxy patterns with ProxyClient.

Architecture:
    Claude Desktop → FastMCP Proxy → FalkorDB MCPServer → FalkorDB

Environment Variables:
    FALKORDB_MCPSERVER_URL: Backend FalkorDB MCP server URL (default: http://localhost:3000)
    PROXY_PORT: Port for the proxy server (default: 3001)
    PROXY_HOST: Host interface to bind to (default: 0.0.0.0)
    ENABLE_AUTH: Enable Bearer token authentication (default: false)

Author: Claude Code Assistant
Version: 2.0.0
License: MIT
"""

import os
from fastmcp import FastMCP
from fastmcp.server.proxy import ProxyClient
from fastmcp.server.auth import BearerAuthProvider
from fastmcp.server.auth.providers.bearer import RSAKeyPair

# Configuration
BACKEND_URL = os.environ.get("FALKORDB_MCPSERVER_URL", "http://localhost:3000")
PROXY_HOST = os.environ.get("PROXY_HOST", "0.0.0.0")
PROXY_PORT = int(os.environ.get("PROXY_PORT", "3001"))
ENABLE_AUTH = os.environ.get("ENABLE_AUTH", "false").lower() == "true"

def setup_auth():
    """Setup Bearer token authentication."""
    if not ENABLE_AUTH:
        return None, None
        
    # For development, generate a key pair
    key_pair = RSAKeyPair.generate()
    
    # Create auth provider
    auth = BearerAuthProvider(
        public_key=key_pair.public_key,
        issuer="https://fastmcp-proxy.dev",
        audience="falkordb-proxy"
    )
    
    return auth, key_pair

def main():
    """Main entry point for the FalkorDB FastMCP Proxy."""
    print("🚀 Starting FalkorDB FastMCP Proxy v2.0")
    print(f"📡 Backend URL: {BACKEND_URL}")
    print(f"🌐 Server: http://{PROXY_HOST}:{PROXY_PORT}")
    print(f"🔐 Authentication: {'Enabled' if ENABLE_AUTH else 'Disabled'}")
    
    # Setup authentication if enabled
    auth, key_pair = setup_auth()
    
    # Create proxy using URL string (ProxyClient will be created automatically)
    proxy = FastMCP.as_proxy(
        BACKEND_URL,
        name="FalkorDB Proxy",
        auth=auth
    )
    
    if ENABLE_AUTH and key_pair:
        # Generate a development token
        dev_token = key_pair.create_token(
            subject="dev-user",
            issuer="https://fastmcp-proxy.dev",
            audience="falkordb-proxy",
            scopes=["read", "write"],
            expires_in_seconds=3600
        )
        
        print(f"\n🔑 Development Bearer Token:")
        print(f"Bearer {dev_token}")
        
        print(f"\n📋 Claude Desktop Configuration (with auth):")
        print(f"""{{
  "mcpServers": {{
    "falkordb": {{
      "command": "npx",
      "args": ["mcp-remote", "http://{PROXY_HOST}:{PROXY_PORT}/sse/"],
      "env": {{"MCP_AUTH_HEADER": "Bearer {dev_token}"}}
    }}
  }}
}}""")
    else:
        print(f"\n📋 Claude Desktop Configuration (no auth):")
        print(f"""{{
  "mcpServers": {{
    "falkordb": {{
      "command": "npx",
      "args": ["mcp-remote", "http://{PROXY_HOST}:{PROXY_PORT}/sse/"]
    }}
  }}
}}""")
    
    print(f"\n📡 SSE Endpoint: http://{PROXY_HOST}:{PROXY_PORT}/sse/")
    print(f"🔐 Authentication: {'Bearer token required' if ENABLE_AUTH else 'No authentication'}")
    
    # Start the proxy server
    proxy.run(transport="sse", host=PROXY_HOST, port=PROXY_PORT)

if __name__ == "__main__":
    main()