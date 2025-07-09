# Configuration Reference - AI Reference

## Summary (Lines 1-10)
Complete configuration reference for all components and deployment scenarios.
Environment variables: FALKORDB_MCPSERVER_URL, MCP_API_KEY, PROXY_HOST, PROXY_PORT.
Docker stack: 3 services with internal networking, external ports 3001/3000/6379.
Authentication: Auto-generated RSA keys (dev), Bearer token config, JWT claims.
Claude Desktop: MCP servers config with serverUrl and auth.token fields.
Production: HTTPS required, replace dev keys, proper OAuth issuer/audience.
Multi-tenant: JWT tenant claims enable graph prefixing for data isolation.
Vector config: FalkorDB native support ready, async job for embedding generation.
Default ports: Proxy 3001, MCPServer 3000, FalkorDB 6379.

## Environment Variables
```bash
# Core Configuration
FALKORDB_MCPSERVER_URL=http://localhost:3000    # Backend MCPServer URL
MCP_API_KEY=dev-api-key                         # Backend authentication
PROXY_HOST=0.0.0.0                              # Proxy bind address
PROXY_PORT=3001                                 # Proxy listen port

# JWT Configuration (Optional)
JWT_ISSUER=http://localhost:3001                # Token issuer claim
JWT_AUDIENCE=falkordb-proxy                     # Token audience claim

# Development vs Production
ENVIRONMENT=development                         # or 'production'
```

## Docker Compose Structure
```yaml
services:
  falkordb:          # Port 6379, Redis protocol
  falkordb-mcp-server: # Port 3000, MCPServer v1.1.0
  fastmcp-proxy:     # Port 3001, OAuth 2.1 + SSE
```

## Claude Desktop Configuration
```json
{
  "mcpServers": {
    "falkordb": {
      "serverUrl": "http://localhost:3001/mcp/",
      "auth": {
        "type": "bearer",
        "token": "GENERATED_BEARER_TOKEN_HERE"
      }
    }
  }
}
```

## Authentication Configuration
### Development (Current)
- **RSA Keys**: Auto-generated on startup
- **Token TTL**: 1 hour default
- **Issuer**: http://localhost:3001
- **Audience**: falkordb-proxy

### Production Requirements
- **HTTPS**: Required for remote access
- **RSA Keys**: Replace with production keypair
- **Issuer URL**: Match actual domain
- **Audience**: Match service identifier

## Multi-Tenant Configuration
### JWT Claims for Tenancy
```json
{
  "iss": "https://your-domain.com",
  "aud": "falkordb-proxy",
  "sub": "user-id",
  "tenant": "tenant-id",    # Enables graph prefixing
  "exp": 1234567890
}
```

### Graph Prefixing
- **With Tenant**: `tenant-id_graph-name`
- **Without Tenant**: `graph-name` (default behavior)

## Network Configuration
### Internal (Docker)
- **falkordb**: Redis protocol on 6379
- **falkordb-mcp-server**: HTTP API on 3000
- **fastmcp-proxy**: HTTP/SSE on 3001

### External Access
- **Proxy Only**: Port 3001 exposed to host
- **Development**: All ports can be exposed for debugging
- **Production**: Only proxy port 3001 should be accessible