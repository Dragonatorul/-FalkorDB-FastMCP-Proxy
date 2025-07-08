# FalkorDB FastMCP Proxy

A **remote-accessible** Model Context Protocol (MCP) server proxy that provides Claude Desktop and other MCP clients with **HTTP-based access** to FalkorDB graph databases through the FalkorDB MCPServer backend.

## 🚀 Key Features

### ✅ **Remote MCP Server**
- **Streamable-HTTP Transport**: Modern HTTP transport for reliable remote connections
- **OAuth 2.1 Authentication**: Bearer token validation with JWT
- **Authorization Server Metadata**: RFC8414 compliant discovery
- **Full Docker Deployment**: Production-ready containerized stack

### ✅ **MCP Tools**
- **falkordb_query**: Execute Cypher queries against FalkorDB graphs
- **falkordb_list_graphs**: List available graphs
- **falkordb_server_info**: Get server metadata and capabilities  
- **falkordb_health**: Check server health status

### ✅ **Production Integration**
- **FalkorDB MCPServer v1.1.0**: Production-tested backend
- **Multi-tenant Support**: Complete data isolation with JWT-based tenant authentication
- **Comprehensive Error Handling**: User-friendly error messages
- **Health Monitoring**: Backend connectivity monitoring

## Architecture

```
Claude Desktop ←HTTP/HTTPS→ FastMCP Proxy ←HTTP→ FalkorDB MCPServer v1.1.0 ←→ FalkorDB
    (Remote)                (Port 3001)        (Port 3000)              (Port 6379)
```

## Quick Start

### 1. Start the Stack

```bash
# Start all services (FalkorDB + MCPServer + FastMCP Proxy)
docker-compose up -d

# Check services are running
docker-compose ps
```

### 2. Get Bearer Token

```bash
# Generate development token
python src/fastmcp_proxy.py

# Copy the Bearer token from output for Claude Desktop configuration
```

### 3. Configure Claude Desktop

⚠️ **IMPORTANT**: Use the correct Claude Desktop integration method:

**✅ CORRECT**: **Settings → Features → Model Context Protocol** (MCP Servers)  
**❌ WRONG**: Settings → Integrations (that's for cloud services like GitHub)

**Quick Configuration**:
```json
{
  "mcpServers": {
    "falkordb": {
      "serverUrl": "http://localhost:3001/mcp/",
      "auth": {
        "type": "bearer",
        "token": "YOUR_BEARER_TOKEN_HERE"
      }
    }
  }
}
```

**📖 Complete Setup Guide**: See [docs/claude-desktop-integration.md](docs/claude-desktop-integration.md) for detailed step-by-step instructions.

### 4. Test Connection

```bash
# Run comprehensive test
python test_remote_mcp.py

# Expected output:
# ✅ Backend health: healthy
# ✅ OAuth Authorization Server Metadata endpoint working  
# ✅ MCP endpoint accepts valid Bearer token
# 🎉 All tests passed!
```

## Usage in Claude Desktop

Once configured, you can use these tools in Claude Desktop:

- **Query graphs**: "Execute a Cypher query to find all nodes in the social_network graph"
- **List graphs**: "Show me all available graphs"
- **Check status**: "Check the FalkorDB server health"
- **Get info**: "What are the server capabilities?"

## Example Cypher Queries

### Creating and Querying Data

```cypher
# Create nodes and relationships
CREATE (alice:Person {name: "Alice", age: 30})
CREATE (bob:Person {name: "Bob", age: 25})
CREATE (alice)-[:KNOWS]->(bob)
RETURN alice, bob

# Query relationships
MATCH (p1:Person)-[r:KNOWS]->(p2:Person)
RETURN p1.name, r, p2.name
```

### Complex Graph Analysis

```cypher
# Find common connections
MATCH (p1:Person)-[:KNOWS]-(mutual:Person)-[:KNOWS]-(p2:Person)
WHERE p1.name = "Alice" AND p2.name != "Alice" AND p1 <> p2
RETURN DISTINCT p2.name as mutual_connection

# Calculate centrality
MATCH (p:Person)-[:KNOWS]-(connected:Person)
RETURN p.name, count(connected) as connections
ORDER BY connections DESC
```

## Remote Access

### For Production Deployment

1. **Configure Domain**: Point your domain to the server
2. **Setup HTTPS**: Use reverse proxy (nginx/Cloudflare) with SSL
3. **Generate Production Keys**: Replace development RSA keys
4. **Configure OAuth**: Setup proper JWKS/OAuth provider

### OAuth Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/.well-known/oauth-authorization-server` | Server metadata discovery |
| `/authorize` | OAuth authorization |
| `/token` | Token exchange |
| `/register` | Dynamic client registration |
| `/sse/` | SSE connection (requires Bearer token) |

See **[REMOTE_ACCESS.md](REMOTE_ACCESS.md)** for detailed remote deployment guide.

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FALKORDB_MCPSERVER_URL` | `http://localhost:3000` | Backend MCPServer URL |
| `MCP_API_KEY` | `dev-api-key` | Backend API key |
| `PROXY_HOST` | `0.0.0.0` | FastMCP proxy host |
| `PROXY_PORT` | `3001` | FastMCP proxy port |

### Docker Services

- **falkordb**: FalkorDB graph database (port 6379)
- **falkordb-mcp-server**: Production MCPServer v1.1.0 (port 3000)
- **fastmcp-proxy**: FastMCP proxy with SSE transport (port 3001)

## Testing

```bash
# Test backend connectivity
pytest tests/

# Test proxy functionality  
python test_proxy.py

# Test remote MCP capabilities
python test_remote_mcp.py
```

## 📚 Documentation

### Setup & Configuration
- **[Deployment Guide](docs/deployment-guide.md)** - Complete setup instructions
- **[Claude Desktop Integration](docs/claude-desktop-integration.md)** - ⚠️ **Essential:** Step-by-step Claude Desktop setup
- **[Multi-Tenant Authentication](docs/multi-tenant-authentication.md)** - 🏢 **Enterprise:** Multi-tenant deployment with data isolation
- **[Client Onboarding Guide](docs/client-onboarding-guide.md)** - 🎯 **Production:** Complete workflow for onboarding new tenants
- **[Architecture Overview](docs/architecture.md)** - System design and components
- **[Testing Guide](docs/testing.md)** - Test procedures and validation

### Technical Deep Dives
- **[MCP vs Integrations Deep Dive](docs/mcp-vs-integrations.md)** - 🧠 **Technical:** Complete analysis of Claude Desktop's two integration methods

### Status & Troubleshooting  
- **[Deployment Status](docs/deployment-status.md)** - Current production readiness
- **[Known Issues](docs/known-issues.md)** - Bug reports and solutions
- **[Implementation Plan](docs/implementation-plan.md)** - Development progress and milestones

**⚠️ Quick Start**: If you're confused about Claude Desktop setup, read [docs/claude-desktop-integration.md](docs/claude-desktop-integration.md) first!  
**🏢 Enterprise**: For multi-tenant deployments, see [docs/multi-tenant-authentication.md](docs/multi-tenant-authentication.md)  
**🎯 Production**: For onboarding new clients, see [docs/client-onboarding-guide.md](docs/client-onboarding-guide.md)  
**🧠 Deep Understanding**: For technical details about MCP vs Integrations, see [docs/mcp-vs-integrations.md](docs/mcp-vs-integrations.md)

## Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| SSE Transport | ✅ Complete | FastMCP 2.10.2 with remote SSE |
| Bearer Auth | ✅ Complete | OAuth 2.1 with RSA256 JWT |
| OAuth Metadata | ✅ Complete | RFC8414 compliant discovery |
| MCP Tools | ✅ Complete | 4 tools mapping to backend API |
| Docker Stack | ✅ Complete | Production-ready deployment |
| Remote Access | ✅ Complete | Ready for Claude Desktop remote connections |

## Architecture Benefits

- **Remote-First**: SSE transport enables remote Claude Desktop connections
- **OAuth 2.1 Compliant**: Standard authentication with Bearer tokens
- **Production-Ready**: Leverages tested FalkorDB MCPServer v1.1.0 backend
- **Low Latency**: < 50ms additional overhead for proxy translation
- **Scalable**: Backend can serve multiple proxy instances
- **Secure**: JWT validation with configurable issuer/audience claims

## Troubleshooting

### Common Issues

- **401 Unauthorized**: Check Bearer token validity and expiration
- **Connection refused**: Verify docker-compose services are running
- **Backend unavailable**: Check FalkorDB MCPServer health endpoint
- **Token validation failed**: Verify issuer/audience configuration

### Debug Commands

```bash
# Check service status
docker-compose ps

# View proxy logs
docker-compose logs fastmcp-proxy

# Test OAuth metadata
curl http://localhost:3001/.well-known/oauth-authorization-server

# Test with Bearer token
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:3001/sse/
```

---

🎯 **Ready for Production**: This FastMCP proxy successfully provides remote SSE access to FalkorDB with OAuth 2.1 authentication, enabling seamless Claude Desktop integration for graph database operations. 
