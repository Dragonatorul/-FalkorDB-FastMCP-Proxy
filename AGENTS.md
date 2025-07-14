# FalkorDB FastMCP Proxy - Agent Instructions

## Rules
- NO commits without explicit user request
- Read section AGENTS.md before working in any docs section  
- Update `docs/STATUS.md` after milestones
- Use atomic semver compatible commits
- Use `gh` CLI for issues/project management
- Commit changes regularly, do not wait for user requests.

**Purpose**: Remote FastMCP proxy for FalkorDB MCPServer v1.1.0 + Claude Desktop
Use FastMCP Proxy with FastMCP.as_proxy  and ProxyClient with bearer token authentication.
If necessary, see https://gofastmcp.com/servers/proxy and https://gofastmcp.com/servers/auth/bearer for details. 
AUTHENTICATION IS MANDATORY to allow multi-tenant usage. Authentication will use ONLY bearer tokens as described in the FastMCP documentation. No other authentication middleware will be used. If there are authentication issues, they will be resolved on the client side by using alternative clients. 
The target audience has at least a Pro plan subscription to Claude Desktop. 
Use `npx` `mcp-remote` to connect to the proxy server or similar alternative clients if `mcp-remote` is not a valid option.
## Files
- `src/fastmcp_proxy.py` - Proxy
- `docker-compose.yml` - Stack
- `docs/STATUS.md` - Status
Keep the Status file updated with the current state of the project. Especially if you encounter an issue and implement a fix. Make sure you have the information in the Status file necessary to avoid confusion and running around in circles by creating issues that are already fixed or known to be broken. Maintain the `docs/STATUS.md` file as the single source of truth for the project status. Maintain it as compact as possible. This is a file for your own use, not for the users. It should be token efficient and contain only the most relevant information which you cannot easily infer otherwise. 

**See `docs/` for details**