# FalkorDB FastMCP Proxy - Agent Instructions

## Core Rules
- **Commits**: Semantic versioning atomic commits (`feat:`, `docs:`, `fix:`) - NEVER commit without explicit user request
- **Documentation Hierarchy**: 
  - AGENTS.md = AI consumption (compact, descriptive for LLM understanding)
  - README.md = Human consumption (structured, concise summaries)
  - Detailed docs = Comprehensive information (verbose, well-formatted for humans)
- **Status**: Update `docs/STATUS.md` after each major milestone  
- **Context**: Use modular approach - read section AGENTS.md before using/updating any section
- **AI Knowledge**: Store AI-only information in `docs/project-knowledge-base/` (AI-maintained)
- **AGENTS.md Size**: Maintain this file as small as possible (target 50 lines, 100 max)
- **Tickets**: Maintain features/issues in `docs/project-management/` using state folders
- **Section Access Rule**: MUST read section AGENTS.md before working in any docs section

## Documentation Structure
```
docs/
├── AGENTS.md (AI) + README.md (Human) + detailed files
├── project-knowledge-base/ (AI ONLY - maintained by AI agents)
└── [section]/ (structured with AGENTS.md + README.md + content)
```

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
- `docs/STATUS.md` - Current status report
- `docs/` - All documentation (see section AGENTS.md files)

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

**Reference `docs/` for detailed information. Read section AGENTS.md before working in any section.**