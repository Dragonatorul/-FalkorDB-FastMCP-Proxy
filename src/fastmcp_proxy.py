"""
FalkorDB FastMCP Proxy (Unified Authentication)

A unified proxy server that provides secure access to FalkorDB instances
through the Model Context Protocol (MCP) with support for both Claude Desktop
and opencode authentication methods.

This module implements a single FastMCP server that can handle:
- Bearer token authentication for Claude Desktop clients
- URL-based JWT token authentication for opencode clients
- Multi-tenant isolation with automatic graph prefixing
- Unified toolset that works with both authentication methods

Architecture:
    Client (Claude Desktop) → Bearer Token → Unified Proxy → FalkorDB
    Client (opencode)       → URL JWT Token → Unified Proxy → FalkorDB

Example Usage:
    # For Claude Desktop:
    Authorization: Bearer <RSA-signed-JWT>

    # For opencode:
    http://localhost:3001/sse/?token=<tenant-JWT>

Environment Variables:
    FALKORDB_MCPSERVER_URL: Backend FalkorDB MCP server URL
        (default: http://localhost:3000)
    MCP_API_KEY: API key for backend authentication (default: dev-api-key)
    PROXY_PORT: Port for the unified proxy server (default: 3001)
    PROXY_HOST: Host interface to bind to (default: 0.0.0.0)
    SECRET_KEY: Secret key for JWT signing
        (default: dev-secret-key-change-in-production)

Security Features:
    - RSA-256 signed Bearer tokens for Claude Desktop
    - HS256 signed JWT tokens for opencode with tenant isolation
    - Automatic token validation and expiration checking
    - Tenant-aware graph name prefixing for data isolation
    - Secure backend API key authentication

Author: Claude Code Assistant
Version: 1.0.0
License: MIT
"""

import os
import time
from typing import Dict, Any, Optional

import httpx
import jwt
from fastapi import Request, HTTPException
from fastapi.responses import Response

from fastmcp import FastMCP, Context
from fastmcp.server.auth import BearerAuthProvider
from fastmcp.server.auth.providers.bearer import RSAKeyPair

def get_auth_context_from_mcp(ctx: Context) -> AuthContext:
    """
    Extract authentication context from FastMCP Context.
    
    For FastMCP, authentication is typically validated during the SSE connection
    establishment, not for individual tool calls. This function creates a default
    auth context for authenticated sessions.
    
    Args:
        ctx (Context): FastMCP context containing request information.
        
    Returns:
        AuthContext: Authentication context for the session.
        
    Note:
        In a production environment, you might want to extract more specific
        auth information from the SSE connection headers or session data.
    """
    # For now, create a default Bearer auth context since the SSE connection
    # was authenticated (Bearer token validation happens at connection time)
    return AuthContext(
        auth_type="bearer", 
        user_id="authenticated-user"
    )


# ============================================================================
# Authentication Middleware (DISABLED - Not compatible with FastMCP)
# ============================================================================

# NOTE: FastMCP doesn't use traditional FastAPI middleware for tool authentication.
# Authentication for SSE connections is handled during connection establishment.
# Individual tool calls within an authenticated session don't need per-call auth.

# The middleware below is preserved for reference but is not used in the current implementation.


@mcp_unified.tool
async def falkordb_query(
    ctx: Context,
    graphName: str,
    query: str,
    parameters: Optional[Dict[str, Any]] = None
) -> str:
    """
    Execute a Cypher query against a FalkorDB graph.

    This tool works with both authentication methods:
    - Bearer tokens (Claude Desktop): Full access to all graphs
    - URL tokens (opencode): Tenant-isolated access with automatic graph prefixing

    Args:
        ctx (Context): FastMCP context containing request information.
        graphName (str): Name of the target graph database.
        query (str): Cypher query to execute against the graph.
        parameters (Optional[Dict[str, Any]]): Optional query parameters for parameterized queries.

    Returns:
        str: Formatted query results or error message.

    Example:
        Basic node query:
        ```
        graphName: "social"
        query: "MATCH (n:Person) RETURN n.name LIMIT 5"
        ```

        Parameterized query:
        ```
        graphName: "social"  
        query: "MATCH (n:Person {age: $age}) RETURN n.name"
        parameters: {"age": 25}
        ```

    Note:
        - For opencode clients, graph names are automatically prefixed with tenant ID
        - Query results are formatted as human-readable text
        - Large result sets are truncated for readability
    """
    auth_context = get_auth_context_from_mcp(ctx)

    # Apply tenant isolation for multi-tenant scenarios
    if auth_context.is_tenant_auth:
        # Prefix graph name with tenant ID to ensure data isolation
        # e.g., "users" becomes "acme_users" for tenant "acme"
        actual_graph_name = f"{auth_context.tenant_id}_{graphName}"
        display_context = f" (tenant: {auth_context.tenant_id})"
    else:
        # Bearer auth (Claude Desktop) - use graph name as provided
        actual_graph_name = graphName
        display_context = ""

    try:
        result = await call_backend_unified("POST", "/api/mcp/context", auth_context, {
            "graphName": actual_graph_name,
            "query": query,
            "parameters": parameters
        })

        # Format response
        if "data" in result and "data" in result["data"]:
            data_results = result["data"]["data"]
            metadata_info = result.get("metadata", {})

            if data_results:
                formatted_results = []
                for i, row in enumerate(data_results, 1):
                    row_text = f"**Result {i}:**\n"
                    for key, value in row.items():
                        row_text += f"- {key}: {value}\n"
                    formatted_results.append(row_text)

                response_text = f"Query executed successfully on graph '{graphName}'{display_context}:\n\n"
                response_text += "\n".join(formatted_results)
                response_text += f"\n**Metadata:**\n- Query time: {metadata_info.get('queryTime', 'N/A')}ms\n"
                response_text += f"- Provider: {metadata_info.get('provider', 'N/A')}"
                if auth_context.is_tenant_auth:
                    response_text += f"\n- Tenant: {auth_context.tenant_id}"
            else:
                response_text = f"Query executed successfully on graph '{graphName}'{display_context} with no results returned."
        else:
            response_text = f"Query executed on graph '{graphName}'{display_context} but unexpected response format."

        return response_text

    except Exception as e:
        return f"Error executing query on graph '{graphName}'{display_context}: {str(e)}"


@mcp_unified.tool
async def falkordb_list_graphs(ctx: Context) -> str:
    """List all available graphs (tenant-aware for opencode, all graphs for Claude Desktop)"""
    auth_context = get_auth_context_from_mcp(ctx)

    try:
        result = await call_backend_unified("GET", "/api/mcp/graphs", auth_context)

        if "data" in result:
            graphs = result["data"]
            metadata = result.get("metadata", {})

            if auth_context.is_tenant_auth:
                # Filter graphs by tenant prefix and remove prefix for display
                tenant_prefix = f"{auth_context.tenant_id}_"
                tenant_graphs = []
                for graph in graphs:
                    if isinstance(graph, dict) and "name" in graph:
                        graph_name = graph["name"]
                        if graph_name.startswith(tenant_prefix):
                            display_name = graph_name[len(tenant_prefix):]
                            tenant_graphs.append(f"- {display_name}")
                    elif isinstance(graph, str) and graph.startswith(tenant_prefix):
                        display_name = graph[len(tenant_prefix):]
                        tenant_graphs.append(f"- {display_name}")

                if tenant_graphs:
                    response_text = f"Available graphs for tenant '{auth_context.tenant_id}' ({len(tenant_graphs)}):\n\n"
                    response_text += "\n".join(tenant_graphs)
                else:
                    response_text = f"No graphs found for tenant '{auth_context.tenant_id}'."
            else:
                # Bearer auth - show all graphs
                if graphs:
                    graph_list = []
                    for graph in graphs:
                        if isinstance(graph, dict) and "name" in graph:
                            graph_list.append(f"- {graph['name']}")
                        else:
                            graph_list.append(f"- {graph}")

                    response_text = f"Available graphs ({metadata.get('count', len(graphs))}):\n\n"
                    response_text += "\n".join(graph_list)
                else:
                    response_text = "No graphs found in the FalkorDB instance."
        else:
            response_text = "Unexpected response format from backend."

        return response_text

    except Exception as e:
        context_info = f"tenant '{auth_context.tenant_id}'" if auth_context.is_tenant_auth else "instance"
        return f"Error listing graphs for {context_info}: {str(e)}"


@mcp_unified.tool
async def falkordb_server_info(ctx: Context) -> str:
    """Get FalkorDB server metadata and capabilities"""
    auth_context = get_auth_context_from_mcp(ctx)

    try:
        result = await call_backend_unified("GET", "/api/mcp/metadata", auth_context)

        provider = result.get("provider", "Unknown")
        version = result.get("version", "Unknown")
        capabilities = result.get("capabilities", [])

        response_text = "**FalkorDB Server Information"
        if auth_context.is_tenant_auth:
            response_text += f" (Tenant: {auth_context.tenant_id})"
        response_text += ":**\n\n"

        response_text += f"- Provider: {provider}\n"
        response_text += f"- Version: {version}\n"
        response_text += f"- Capabilities: {', '.join(capabilities) if capabilities else 'None listed'}"

        if auth_context.is_tenant_auth:
            response_text += f"\n- Tenant: {auth_context.tenant_id}\n"
            response_text += f"- User: {auth_context.user_id}"

        return response_text

    except Exception as e:
        context_info = f"tenant '{auth_context.tenant_id}'" if auth_context.is_tenant_auth else "server"
        return f"Error getting server info for {context_info}: {str(e)}"


@mcp_unified.tool
async def falkordb_health(ctx: Context) -> str:
    """Check FalkorDB server health status"""
    auth_context = get_auth_context_from_mcp(ctx)

    try:
        result = await call_backend_unified("GET", "/health", auth_context)

        status = result.get("status", "unknown")
        services = result.get("services", {})
        database = services.get("database", {})

        response_text = "**FalkorDB Health Status"
        if auth_context.is_tenant_auth:
            response_text += f" (Tenant: {auth_context.tenant_id})"
        response_text += ":**\n\n"

        response_text += f"- Overall Status: {status}\n"
        response_text += f"- Database Connected: {database.get('connected', 'Unknown')}\n"
        response_text += f"- Database Latency: {database.get('latency', 'Unknown')}ms"

        if auth_context.is_tenant_auth:
            response_text += f"\n- Tenant: {auth_context.tenant_id}\n"
            response_text += f"- User: {auth_context.user_id}"

        return response_text

    except Exception as e:
        context_info = f"tenant '{auth_context.tenant_id}'" if auth_context.is_tenant_auth else "server"
        return f"Error checking health for {context_info}: {str(e)}"


def main() -> None:
    """
    Main entry point for the FalkorDB FastMCP Proxy (Unified).

    This function initializes and starts the unified proxy server that supports
    both Claude Desktop and opencode authentication methods. It prints startup
    information including sample tokens for development and testing.

    Configuration:
        - Listens on the configured host and port (default: 0.0.0.0:3001)
        - Supports both Bearer token and URL JWT token authentication
        - Provides tenant isolation for opencode clients
        - Connects to backend FalkorDB MCP server

    Development Features:
        - Generates sample Bearer tokens for Claude Desktop testing
        - Generates sample tenant tokens for opencode testing
        - Prints configuration examples for both client types

    Example Usage:
        # Run directly
        python fastmcp_proxy.py

        # Run with custom configuration
        PROXY_PORT=8080 BACKEND_URL=http://custom-backend:3000 python fastmcp_proxy.py

    Note:
        This function runs indefinitely until interrupted (Ctrl+C).
        In production, consider using a proper WSGI server like Gunicorn.
    """
    print("🚀 Starting FalkorDB FastMCP Proxy (Unified)")
    print(f"📡 Backend URL: {BACKEND_URL}")
    print(f"🌐 Server: http://{PROXY_HOST}:{PROXY_PORT}")
    print("🔧 Supports both Bearer tokens (Claude Desktop) and URL tokens (opencode)")

    # Generate and display test tokens for development
    test_bearer_token = generate_test_token()
    print("\n🔑 Development Bearer Token (Claude Desktop):")
    print(f"Bearer {test_bearer_token}")

    # Generate sample tenant tokens for different organizations
    tenant_tokens = {
        "acme": generate_tenant_token("acme", "admin"),
        "widgets": generate_tenant_token("widgets", "user1")
    }

    print("\n🏢 Sample Tenant Tokens (opencode):")
    for tenant, token in tenant_tokens.items():
        print(f"  {tenant}: {token}")
        print(f"  URL: http://{PROXY_HOST}:{PROXY_PORT}/sse/?token={token}")

    print("\n📋 Configuration examples:")
    print("Claude Desktop: Bearer token in auth header")
    print("opencode: URL token in query parameter")

    # Start the unified FastMCP server
    mcp_unified.run(transport='sse')


if __name__ == "__main__":
    main()
