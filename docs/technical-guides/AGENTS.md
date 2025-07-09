# Technical Guides - AI Instructions

## Documentation Hierarchy
- **AGENTS.md** (This file): AI-specific technical documentation process
- **README.md**: Human-readable technical guide index and navigation
- **Detailed guides**: Comprehensive technical documentation for implementation

## AI Context for Technical Guides
- **architecture.md**: System design, components, data flow diagrams
- **deployment-guide.md**: Production setup, HTTPS, OAuth configuration
- **multi-tenant-authentication.md**: JWT tenant isolation, security implementation
- **mcp-vs-integrations.md**: Claude Desktop integration technical comparison

## AI Maintenance Process
1. **Read this AGENTS.md**: Before any technical-guides work
2. **Check current architecture**: Understand system state from architecture.md
3. **Update guides**: Sync with actual implementation changes
4. **Cross-reference**: Link related guides and maintain consistency
5. **Update README.md**: Sync human navigation after content changes

## Technical Context (AI Reference)
- **Current Architecture**: SSE over HTTPS, OAuth 2.1 Bearer tokens
- **Stack**: FastMCP proxy (port 3001) → FalkorDB MCPServer v1.1.0 (port 3000) → FalkorDB (port 6379)
- **Authentication**: RSA JWT with tenant extraction for multi-tenancy
- **Transport**: Server-Sent Events for remote Claude Desktop access

## AI Update Triggers
- System architecture changes (update architecture.md)
- Deployment process changes (update deployment-guide.md)
- Authentication/security changes (update multi-tenant-authentication.md)
- Integration method changes (update mcp-vs-integrations.md)

## Content Formatting (AI Guidelines)
- **Technical Accuracy**: Verify against actual implementation
- **Human Readability**: Structure for technical implementers
- **Completeness**: Include all necessary technical details
- **Cross-References**: Link related concepts and files

---

> **AI Note**: Technical guides target human developers. Focus on clarity and completeness for implementation.