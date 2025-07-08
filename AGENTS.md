# FalkorDB FastMCP Proxy - Agent Instructions

## Project Overview
**Purpose**: FastMCP proxy providing remote SSE access to FalkorDB MCPServer v1.1.0 backend for Claude Desktop integration.

**Architecture**: 
```
Claude Desktop ←SSE/HTTPS→ FastMCP Proxy ←HTTP→ FalkorDB MCPServer v1.1.0 ←→ FalkorDB
     (Remote)              (Port 3001)        (Port 3000)              (Port 6379)
```

**Status**: 95% complete - Core implementation done, ready for Claude Desktop testing

## Key Files
- `src/fastmcp_proxy.py` - FastMCP server with OAuth 2.1 and 4 MCP tools
- `docker-compose.yml` - 3-service stack (FalkorDB + MCPServer + Proxy)
- `tests/test_remote_mcp.py` - Comprehensive integration tests
- `requirements.txt` - Dependencies (fastmcp, cryptography, pyjwt[crypto])

## Core Commands
**Start Stack**: `docker-compose up -d`
**Check Status**: `docker-compose ps`
**Test Proxy**: `python tests/test_remote_mcp.py`
**Get Token**: `python src/fastmcp_proxy.py` (shows Bearer token in output)
**Logs**: `docker-compose logs fastmcp-proxy`

## MCP Tools Implemented
1. `falkordb_query` → `POST /api/mcp/context` (Execute Cypher queries)
2. `falkordb_list_graphs` → `GET /api/mcp/graphs` (List graphs)
3. `falkordb_server_info` → `GET /api/mcp/metadata` (Server capabilities)
4. `falkordb_health` → `GET /health` (Health check)

## Claude Desktop Config
```json
{
  "name": "FalkorDB",
  "serverUrl": "http://localhost:3001/sse/",
  "auth": {
    "type": "bearer",
    "token": "YOUR_BEARER_TOKEN_HERE"
  }
}
```

## Authentication
- **OAuth 2.1**: Bearer token with RS256 JWT
- **Development Keys**: Auto-generated RSA keypair
- **Token Validation**: Issuer/audience claims checked
- **Endpoints**: `/.well-known/oauth-authorization-server`, `/sse/`

## Backend Integration
- **FalkorDB MCPServer v1.1.0**: Production-ready backend on port 3000
- **Multi-tenant**: Supports JWT tenant extraction and graph prefixing
- **Error Mapping**: All backend errors mapped to MCP error codes
- **Health Monitoring**: Backend health proxied through `/health`

## Environment Variables
```env
FALKORDB_MCPSERVER_URL=http://localhost:3000
MCP_API_KEY=dev-api-key
PROXY_HOST=0.0.0.0
PROXY_PORT=3001
```

## Testing Strategy
- **Integration**: Test with real FalkorDB MCPServer v1.1.0 container
- **Authentication**: OAuth flow and SSE endpoint validation
- **Performance**: Target < 50ms additional latency
- **Claude Integration**: End-to-end MCP tool functionality

## Known Issues
- **Services Down**: Docker stack needs to be started
- **Previous Auth Issue**: Resolved in current implementation

## Progress Tracking
**CRITICAL**: Always update `docs/implementation-plan.md` after:
- Completing any significant milestone
- Before conversation compacts (when user says "compact", "session handoff", "handoff", "wrap up", "done for the day", or similar session-ending phrases)
- When major issues are resolved or discovered
- When changing project direction or priorities

**Progress Updates Must Include**:
- Current completion percentage
- What was just completed
- Any new issues discovered
- Updated next steps with priorities
- Current blocking issues (if any)

## Next Steps
1. Start Docker services (`docker-compose up -d`)
2. Verify service health and connectivity
3. Test Claude Desktop integration with generated Bearer token
4. Performance validation and production deployment prep

## Build, Lint, and Test Commands
- **Test**: `python tests/test_remote_mcp.py` (comprehensive proxy tests)
- **Python Style**: `black src/` (if available)
- **Type Check**: `mypy src/` (if configured)
- **Docker Build**: `docker-compose build`

## Code Style Guidelines
- Python: 4 spaces, snake_case, type hints where possible
- Error handling: Comprehensive with structured responses
- Security: No credential logging, secure header forwarding
- Comments: Minimal, code should be self-documenting

## Commit Guidelines
- Format: `<type>(<scope>): <description>`
- Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
- Breaking changes: add `!` after type or `BREAKING CHANGE:` in body
- Never commit without explicit user request
- Use semantic versioning principles

## Production Deployment
- **HTTPS**: Required for remote access
- **Production Keys**: Replace dev RSA keys with proper issuer URLs
- **Domain Setup**: Configure OAuth issuer/audience for production
- **Monitoring**: Health checks and structured logging ready