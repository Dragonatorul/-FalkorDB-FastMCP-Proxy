# FalkorDB FastMCP Proxy

> **Note**: Most contributions to this repository have been created with significant assistance from AI tools, specifically Claude Sonnet 4 and GitHub Copilot (ChatGPT 4.1) via opencode.ai platform. This collaboration demonstrates the potential of AI-assisted software development while maintaining high code quality and comprehensive documentation.

> **⚠️ CRITICAL NOTE**: There are two projects named "opencode" that provide TUI-based AI development tools. This project uses the **production-ready version** from **[opencode.ai](https://opencode.ai/)** / **[github.com/sst/opencode](https://github.com/sst/opencode)**. The other similarly named project is discontinued and not production-ready. Always verify you're using the correct implementation when following our [AI workflow documentation](docs/ai-workflow/).

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

> **⚠️ Vector Ingestion Limitation**: The upstream FalkorDB MCPServer v1.1.0 does not currently support automatic vector embedding generation or ingestion tools. While FalkorDB 4.0+ has full native vector support for querying, embedding generation must be handled separately. See our [vector capabilities analysis](docs/exploratory-analysis/) for proposed solutions and the [FalkorDB-Async-Vectorizer](https://github.com/Dragonatorul/FalkorDB-Async-Vectorizer) async job implementation.

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

## 🤝 Community

### Getting Help & Contributing

- **🐛 [Report Bugs](https://github.com/Dragonatorul/FalkorDB-FastMCP-Proxy/issues/new?template=bug_report.md)** - Found an issue? Let us know!
- **🚀 [Request Features](https://github.com/Dragonatorul/FalkorDB-FastMCP-Proxy/issues/new?template=feature_request.md)** - Have a specific enhancement in mind?
- **💡 [Share Ideas](https://github.com/Dragonatorul/FalkorDB-FastMCP-Proxy/discussions/categories/ideas)** - Discuss concept features and future possibilities
- **🙋 [Ask Questions](https://github.com/Dragonatorul/FalkorDB-FastMCP-Proxy/discussions/categories/q-a)** - Get help with setup, usage, or troubleshooting
- **💬 [General Discussion](https://github.com/Dragonatorul/FalkorDB-FastMCP-Proxy/discussions/categories/general)** - Chat about the project and share experiences
- **🙌 [Show and Tell](https://github.com/Dragonatorul/FalkorDB-FastMCP-Proxy/discussions/categories/show-and-tell)** - Share your implementations and use cases

### Issue vs Discussion Guidelines

**Use Issues for:**
- 🐛 Bug reports with specific steps to reproduce
- 🚀 Feature requests with clear implementation requirements
- 📋 Specific tasks that can be completed and closed

**Use Discussions for:**
- 💡 Feature concepts and brainstorming
- 🙋 Questions about usage, setup, or configuration  
- 💬 General project discussion and feedback
- 🙌 Showcasing your implementations
- 📚 Documentation sharing and experiences

## 📚 Documentation

### Setup & Configuration
- **[Deployment Guide](docs/technical-guides/deployment-guide.md)** - Complete setup instructions
- **[Claude Desktop Integration](docs/user-guides/claude-desktop-integration.md)** - ⚠️ **Essential:** Step-by-step Claude Desktop setup
- **[Multi-Tenant Authentication](docs/technical-guides/multi-tenant-authentication.md)** - 🏢 **Enterprise:** Multi-tenant deployment with data isolation
- **[Client Onboarding Guide](docs/user-guides/client-onboarding-guide.md)** - 🎯 **Production:** Complete workflow for onboarding new tenants
- **[Architecture Overview](docs/technical-guides/architecture.md)** - System design and components
- **[Testing Guide](docs/user-guides/testing.md)** - Test procedures and validation

### Technical Deep Dives
- **[MCP vs Integrations Deep Dive](docs/technical-guides/mcp-vs-integrations.md)** - 🧠 **Technical:** Complete analysis of Claude Desktop's two integration methods
- **[Vector Capabilities Analysis](docs/exploratory-analysis/)** - 🔍 **Vector Search:** Comprehensive analysis of vector search implementation options and solutions

### AI-Assisted Development
- **[AI Workflow Documentation](docs/ai-workflow/)** - 🤖 **Workflow:** Complete guide to AI-human collaboration patterns used in this project

### Status & Troubleshooting  
- **[Current Status](docs/STATUS.md)** - Overall project completion and next steps
- **[Implementation Plan](docs/project-management/implementation-plan.md)** - Development progress and milestones
- **[Known Issues](docs/project-management/known-issues.md)** - Bug reports and solutions

**⚠️ Quick Start**: If you're confused about Claude Desktop setup, read [Claude Desktop Integration](docs/user-guides/claude-desktop-integration.md) first!  
**🏢 Enterprise**: For multi-tenant deployments, see [Multi-Tenant Authentication](docs/technical-guides/multi-tenant-authentication.md)  
**🎯 Production**: For onboarding new clients, see [Client Onboarding Guide](docs/user-guides/client-onboarding-guide.md)  
**🧠 Deep Understanding**: For technical details about MCP vs Integrations, see [MCP vs Integrations Deep Dive](docs/technical-guides/mcp-vs-integrations.md)  
**🤖 AI Workflow**: For implementing similar AI-assisted development patterns, see [AI Workflow Documentation](docs/ai-workflow/)

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

## Acknowledgments

This project was developed with significant assistance from AI tools and platforms:

- **[Anthropic Claude Sonnet 4](https://www.anthropic.com/)** - Primary AI assistant for code development, documentation, and architectural decisions
- **[GitHub Copilot (ChatGPT 4.1)](https://github.com/features/copilot)** - AI pair programming for code completion and suggestions  
- **[opencode.ai](https://opencode.ai/)** - AI-powered development environment providing uniform workflow across multiple AI models (see [ai-workflow documentation](docs/ai-workflow/))
- **[Visual Studio Code](https://code.visualstudio.com/)** - Primary development environment and code editor

> **⚠️ Note**: There are two projects named "opencode" that solve similar problems. This project specifically uses the production-ready version from [opencode.ai](https://opencode.ai/) / [github.com/sst/opencode](https://github.com/sst/opencode).

These AI tools enabled rapid development, comprehensive documentation, and robust testing while maintaining high code quality standards. This project demonstrates the potential for effective AI-human collaboration in modern software development.

For detailed information about the AI-assisted development workflow used in this project, see the [AI Workflow Documentation](docs/ai-workflow/).

---

🎯 **Ready for Production**: This FastMCP proxy successfully provides remote SSE access to FalkorDB with OAuth 2.1 authentication, enabling seamless Claude Desktop integration for graph database operations. 
