# FalkorDB FastMCP Proxy - Agent Instructions

## Rules
- NO commits without explicit user request
- Read section AGENTS.md before working in any docs section  
- Update `docs/STATUS.md` after milestones
- Use atomic semver compatible commits
- Use `gh` CLI for issues/project management
- Commit changes regularly, do not wait for user requests.

**Purpose**: Unified remote FastMCP proxy for FalkorDB MCPServer v1.1.0 supporting both Claude Desktop (Bearer tokens) and opencode (URL tokens)
Use FastMCP with unified authentication middleware supporting Bearer token authentication AND URL token authentication.
If necessary, see https://gofastmcp.com/servers/proxy and https://gofastmcp.com/servers/auth/bearer for details. 
AUTHENTICATION IS MANDATORY to allow multi-tenant usage. Authentication supports BOTH Bearer tokens (Claude Desktop) and URL tokens (opencode) as described in the unified authentication implementation. No other authentication middleware will be used. If there are authentication issues, they will be resolved by using the appropriate authentication method for each client type.
The target audience includes Claude Desktop Pro plan subscribers AND opencode users.
Use Bearer tokens for Claude Desktop clients and URL tokens (?token=jwt) for opencode remote MCP server configuration.

## Files
- `server/fastmcp_proxy.py` - Unified Proxy (Bearer + URL Token auth)
- `client/claude_desktop_proxy.py` - Claude Desktop DXT Client
- `docs/user-guides/opencode-integration.md` - opencode Configuration Guide
- `opencode.example.json` - opencode Configuration Template
- `docker-compose.yml` - Stack
- `docs/STATUS.md` - Status
Keep the Status file updated with the current state of the project. Especially if you encounter an issue and implement a fix. Make sure you have the information in the Status file necessary to avoid confusion and running around in circles by creating issues that are already fixed or known to be broken. Maintain the `docs/STATUS.md` file as the single source of truth for the project status. Maintain it as compact as possible. This is a file for your own use, not for the users. It should be token efficient and contain only the most relevant information which you cannot easily infer otherwise. 

**See `docs/` for details**