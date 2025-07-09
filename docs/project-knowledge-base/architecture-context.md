# Architecture Context - AI Reference

## Summary (Lines 1-10)
Complete system architecture and component relationships for FalkorDB FastMCP Proxy.
Stack: Claude Desktop → FastMCP Proxy (3001) → MCPServer v1.1.0 (3000) → FalkorDB (6379).
Transport: SSE over HTTPS for remote access, HTTP between internal components.
Authentication: OAuth 2.1 Bearer tokens, RSA JWT with tenant extraction.
Tools: 4 MCP tools (query, list_graphs, server_info, health) proxied to backend.
Multi-tenancy: JWT tenant claims → graph prefixing for data isolation.
Current state: Implementation complete, services down, ready for first deployment.
Key files: src/fastmcp_proxy.py, docker-compose.yml, tests/test_remote_mcp.py.
Vector capability: FalkorDB 4.0+ native support, MCPServer lacks embedding tools.

## Component Architecture
- **FastMCP Proxy**: Port 3001, OAuth 2.1, SSE transport, 4 MCP tools
- **FalkorDB MCPServer**: Port 3000, v1.1.0, production backend
- **FalkorDB**: Port 6379, graph database with native vector support
- **Docker Stack**: 3-service deployment, internal networking

## Authentication Flow
1. Client sends Bearer token in Authorization header
2. Proxy validates RSA JWT (issuer/audience claims)
3. Extract tenant from JWT claims (optional)
4. Forward requests to MCPServer with tenant context
5. Apply tenant-aware graph prefixing for multi-tenancy

## MCP Tools Mapping
- `falkordb_query` → POST /api/mcp/context (Cypher execution)
- `falkordb_list_graphs` → GET /api/mcp/graphs (graph listing)
- `falkordb_server_info` → GET /api/mcp/metadata (capabilities)
- `falkordb_health` → GET /health (health status)

## Network Flow
```
Claude Desktop [Bearer Token] 
  ↓ SSE/HTTPS
FastMCP Proxy [JWT Validation + Tenant Extract]
  ↓ HTTP + API Key
FalkorDB MCPServer [Tenant-aware Processing]
  ↓ Redis Protocol
FalkorDB [Graph Operations + Vector Support]
```

## Security Model
- **Client Auth**: Bearer token required for all requests
- **Backend Auth**: API key between proxy and MCPServer
- **Tenant Isolation**: JWT claims → graph prefixing
- **Token Validation**: RSA signature verification
- **No Credential Logging**: Secure header forwarding only

## Configuration
- FALKORDB_MCPSERVER_URL=http://localhost:3000
- MCP_API_KEY=dev-api-key (backend auth)
- PROXY_HOST=0.0.0.0, PROXY_PORT=3001
- Development RSA keys (auto-generated, replace for production)