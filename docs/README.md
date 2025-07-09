# FalkorDB FastMCP Proxy - Documentation

## Overview

This documentation covers the FalkorDB FastMCP Proxy, a FastMCP server providing remote SSE access to FalkorDB MCPServer v1.1.0 backend for Claude Desktop integration.

## Documentation Structure

### 📋 Project Management (`project-management/`)
Project planning, tracking, and status documentation.

- **[features/](./project-management/features/)** - Planned features and enhancements
- **[issues/](./project-management/issues/)** - Current issues and bug tracking
- **[testing/](./project-management/testing/)** - Test results and validation
- **[implementation-plan.md](./project-management/implementation-plan.md)** - Overall project roadmap and progress
- **[tenant-implementation-plan.md](./project-management/tenant-implementation-plan.md)** - Multi-tenant feature planning
- **[deployment-status.md](./project-management/deployment-status.md)** - Current deployment state
- **[known-issues.md](./project-management/known-issues.md)** - Documented limitations and workarounds

### 🔧 Technical Guides (`technical-guides/`)
Architecture, deployment, and technical implementation documentation.

- **[architecture.md](./technical-guides/architecture.md)** - System architecture and design
- **[deployment-guide.md](./technical-guides/deployment-guide.md)** - Deployment procedures and configuration
- **[multi-tenant-authentication.md](./technical-guides/multi-tenant-authentication.md)** - Authentication system design
- **[mcp-vs-integrations.md](./technical-guides/mcp-vs-integrations.md)** - MCP protocol comparison and analysis

### 👥 User Guides (`user-guides/`)
End-user documentation for setup, configuration, and usage.

- **[claude-desktop-integration.md](./user-guides/claude-desktop-integration.md)** - Claude Desktop setup and configuration
- **[client-onboarding-guide.md](./user-guides/client-onboarding-guide.md)** - New user setup procedures
- **[REMOTE_ACCESS.md](./user-guides/REMOTE_ACCESS.md)** - Remote access configuration
- **[testing.md](./user-guides/testing.md)** - Testing procedures and validation

## Quick Start

1. **For Users**: Start with [user-guides/claude-desktop-integration.md](./user-guides/claude-desktop-integration.md)
2. **For Developers**: Review [technical-guides/architecture.md](./technical-guides/architecture.md)
3. **For Project Status**: Check [project-management/deployment-status.md](./project-management/deployment-status.md)

## Current Status

**Status**: ✅ Production Ready (95% Complete)
- Core FastMCP proxy implementation complete
- OAuth 2.1 authentication working
- Docker deployment stack operational
- Claude Desktop integration validated

## Architecture Overview

```
Claude Desktop ←SSE/HTTPS→ FastMCP Proxy ←HTTP→ FalkorDB MCPServer v1.1.0 ←→ FalkorDB
     (Remote)              (Port 3001)        (Port 3000)              (Port 6379)
```

## Key Features

- **FastMCP Protocol**: Server-Sent Events transport for Claude Desktop
- **OAuth 2.1 Authentication**: Bearer token with RS256 JWT validation
- **Multi-Tenant Support**: Tenant-aware graph prefixing and isolation
- **Docker Deployment**: Complete containerized stack
- **FalkorDB Integration**: Direct connection to FalkorDB MCPServer v1.1.0

## MCP Tools Available

1. `falkordb_query` - Execute Cypher queries
2. `falkordb_list_graphs` - List available graphs
3. `falkordb_server_info` - Server capabilities and metadata
4. `falkordb_health` - Health check and status

## Support

For issues and questions:
- Check [project-management/known-issues.md](./project-management/known-issues.md)
- Review [project-management/issues/](./project-management/issues/)
- Follow troubleshooting in [user-guides/testing.md](./user-guides/testing.md)

## Contributing

When updating documentation:
1. Follow the organizational structure above
2. Update relevant README files when adding new documents
3. Cross-reference related documentation
4. Keep technical and user documentation separate