# FalkorDB FastMCP Proxy - Agent Instructions

## Rules
- NO commits without explicit user request
- Read section AGENTS.md before working in any docs section  
- Update `docs/STATUS.md` after milestones
- Use semantic commits (`feat:`, `docs:`, `fix:`)
- Use `gh` CLI for issues/project management

## Status: 98% Complete - Ready for Deployment
**Purpose**: Remote FastMCP proxy for FalkorDB MCPServer v1.1.0 + Claude Desktop

## Commands
```bash
docker-compose up -d                    # Start
python src/fastmcp_proxy.py             # Token
```

## State
- Implementation: Complete
- Services: Down 
- Next: Deploy + test

## Files
- `src/fastmcp_proxy.py` - Proxy
- `docker-compose.yml` - Stack
- `docs/STATUS.md` - Status

**See `docs/` for details**