# FalkorDB FastMCP Proxy - Agent Instructions

## Core Rules
- **Commits**: Semantic versioning atomic commits (`feat:`, `docs:`, `fix:`) - NEVER commit without explicit user request
- **Documentation**: Maintain comprehensive docs in `docs/` folder for modular context
- **Status**: Update `docs/STATUS.md` after each major milestone  
- **Context**: Use modular approach - refer to docs/ for additional context when needed
- **AI Files**: Store AI knowledge files in `docs/project-knowledge-base/` with README
- **AGENTS.md Size**: Maintain this file as small as possible (target 50 lines, 100 max) - offload context to docs/
- **Tickets**: Maintain features/issues in `docs/project-management/` using state folders (see docs/project-management/AGENTS.md)
- **Section AGENTS.md**: Maintain compact AGENTS.md files in each docs section for context and processes

## Project Status: 98% Complete - Ready for Initial Deployment

**Purpose**: Remote FastMCP proxy for FalkorDB MCPServer v1.1.0 + Claude Desktop integration

## Essential Commands
```bash
docker-compose up -d                    # Start stack
python tests/test_remote_mcp.py         # Test
python src/fastmcp_proxy.py             # Get Bearer token
```

## Current State
- **Implementation**: Complete (proxy, auth, tools, docs, CI/CD)
- **Services**: Down (need first deployment)
- **Next Step**: Deploy and test Claude Desktop integration

## Key Files
- `src/fastmcp_proxy.py` - Main proxy server
- `docker-compose.yml` - 3-service stack  
- `tests/test_remote_mcp.py` - Integration tests
- `docs/STATUS.md` - Current status report
- `docs/` - All documentation

## Claude Desktop Config
```json
{
  "mcpServers": {
    "falkordb": {
      "serverUrl": "http://localhost:3001/mcp/",
      "auth": { "type": "bearer", "token": "YOUR_BEARER_TOKEN_HERE" }
    }
  }
}
```

**Reference `docs/` for detailed information.**