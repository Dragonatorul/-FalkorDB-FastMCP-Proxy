# Technical Guides - Agent Instructions

## Section Purpose
Technical documentation for architecture, deployment, authentication, and integration patterns.

## File Organization
- **architecture.md**: System design, components, data flow
- **deployment-guide.md**: Production setup, HTTPS, OAuth configuration  
- **multi-tenant-authentication.md**: JWT tenant isolation, security model
- **mcp-vs-integrations.md**: Claude Desktop integration comparison

## Maintenance Rules
- Keep guides focused on implementation details
- Update after architectural changes
- Cross-reference related guides
- Maintain security best practices
- Document production considerations

## Key Context
- **Authentication**: OAuth 2.1 with Bearer tokens
- **Transport**: SSE over HTTPS for remote access
- **Backend**: FalkorDB MCPServer v1.1.0 on port 3000
- **Proxy**: FastMCP on port 3001 with 4 MCP tools

---

> **AI Instructions**: Update technical guides when system architecture or deployment processes change.