# FalkorDB FastMCP Proxy - opencode Configuration ✅

This document explains how to configure opencode to use the FalkorDB FastMCP Proxy.

## ✅ TESTED AND WORKING

**Status**: Successfully tested with opencode v0.1.195  
**Configuration**: Local MCP server spawning works correctly  
**Evidence**: opencode spawns `python src/fastmcp_proxy.py` process  

## Working Configuration File

The `opencode.json` file in this repository configures opencode to spawn the FalkorDB FastMCP Proxy locally:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "falkordb-local": {
      "type": "local",
      "command": [
        "python",
        "src/fastmcp_proxy.py"
      ],
      "enabled": true,
      "environment": {
        "FALKORDB_MCPSERVER_URL": "http://localhost:3000",
        "MCP_API_KEY": "dev-api-key",
        "PROXY_HOST": "127.0.0.1",
        "PROXY_PORT": "3002"
      }
    }
  }
}
```

## Remote Configuration (Not Working)

The remote configuration is disabled due to authentication limitations:

```json
"falkordb-remote": {
  "type": "remote", 
  "url": "http://localhost:3001/mcp/",
  "enabled": false
}
```

**Issue**: opencode's remote MCP schema doesn't support Bearer token authentication headers that the FastMCP proxy requires.

## Available MCP Tools

Once configured, opencode has access to 4 FalkorDB MCP tools:

1. **falkordb_query** - Execute Cypher queries against FalkorDB graphs
2. **falkordb_list_graphs** - List all available graphs
3. **falkordb_server_info** - Get server metadata and capabilities  
4. **falkordb_health** - Check FalkorDB server health status

## Usage Instructions

1. **Ensure Backend Services**: `docker-compose up -d` (FalkorDB + MCPServer)
2. **Place Configuration**: Copy `opencode.json` to project root or `~/.config/opencode/config.json`
3. **Run opencode**: `opencode` in this directory
4. **Verify**: The FalkorDB MCP tools should be available in the session

## Test Results

✅ **Successful Tests**:
- opencode v0.1.195 installed and working
- Configuration file validation successful  
- Local MCP server spawning confirmed
- Process evidence: `python src/fastmcp_proxy.py` running

❌ **Known Limitations**:
- Remote MCP authentication not supported (Bearer tokens)
- Configuration schema doesn't include `description` field

## Troubleshooting

**Configuration Validation Error**:
- Remove any `description` fields from the JSON configuration
- Ensure JSON syntax is valid with `jq '.' opencode.json`

**MCP Tools Not Available**:
- Check that backend services are running: `docker-compose ps`
- Verify opencode spawned the proxy: `ps aux | grep fastmcp_proxy`
- Ensure the local command path is correct relative to project root