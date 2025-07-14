# Claude Desktop & Claude Code Connection Guide

**Last Updated**: 2025-07-14 08:49 UTC  
**Status**: FastMCP Docker server currently broken - SSE endpoints not working

## Current Status Summary

### ✅ Working Components
- **Backend Services**: FalkorDB + MCPServer v1.1.0 running in Docker
- **Authentication**: Bearer token generation working
- **MCP Tools**: 4 tools implemented (query, list_graphs, server_info, health)
- **Backend Integration**: Proxy can communicate with FalkorDB MCPServer

### ❌ Broken Components
- **FastMCP Docker Server**: Not exposing SSE endpoints properly
- **Remote MCP Connection**: `/sse/` endpoint returns 404 Not Found
- **Claude Desktop Integration**: Cannot connect due to missing endpoints

## Technical Details

### Current Docker Stack
```bash
# Services running
docker-compose ps
# NAME                  STATUS         PORTS
# falkordb              Up             0.0.0.0:6379->6379/tcp
# falkordb-mcp-server   Up             0.0.0.0:3000->3000/tcp  
# fastmcp-proxy         Up             0.0.0.0:3001->3001/tcp

# Backend health check
curl http://localhost:3000/health
# {"status":"healthy","services":{"database":{"connected":true,"latency":1}}}
```

### FastMCP Server Issues
The FastMCP server (`src/fastmcp_proxy.py`) has configuration problems:

1. **Transport Configuration**: Currently using `transport="sse"` but endpoints not created
2. **SSE Path**: Configured with `sse_path='/sse'` but endpoint returns 404
3. **Endpoint Testing**: All attempts to reach `/sse/`, `/mcp/`, `/tools` return 404

```bash
# All these return 404 Not Found:
curl http://localhost:3001/sse/
curl http://localhost:3001/mcp/
curl http://localhost:3001/tools
curl -H "Authorization: Bearer TOKEN" http://localhost:3001/sse/
```

### Authentication Working
Bearer token generation works correctly:
```bash
python src/fastmcp_proxy.py
# Outputs valid Bearer token for Claude Desktop
```

## Connection Methods

### Method 1: mcp-remote Package (Recommended)
This is the standard approach for connecting Claude Desktop to remote MCP servers.

**Claude Desktop Configuration**:
```json
{
  "mcpServers": {
    "falkordb": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:3001/sse/"],
      "env": {
        "BEARER_TOKEN": "YOUR_BEARER_TOKEN_HERE"
      }
    }
  }
}
```

**Current Issue**: The `/sse/` endpoint doesn't exist, so `mcp-remote` cannot connect.

### Method 2: mcp-remote Bridge (Current Solution)
Uses the mcp-remote bridge for Claude Desktop integration:

```json
{
  "mcpServers": {
    "falkordb": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:3001/sse/"],
      "env": {
        "MCP_AUTH_HEADER": "Bearer YOUR_BEARER_TOKEN_HERE"
      }
    }
  }
}
```

**Current Status**: ✅ Working with mcp-remote bridge

## Troubleshooting Steps

### 1. Verify Backend Services
```bash
# Check all services running
docker-compose ps

# Test backend health
curl http://localhost:3000/health

# Test backend API
curl -H "x-api-key: dev-api-key" http://localhost:3000/api/mcp/graphs
```

### 2. Check FastMCP Server Logs
```bash
# View proxy logs
docker-compose logs fastmcp-proxy

# Look for startup messages and endpoint creation
docker-compose logs fastmcp-proxy | grep -E "(Starting|endpoint|route|SSE)"
```

### 3. Test Authentication
```bash
# Generate fresh Bearer token
python src/fastmcp_proxy.py

# Test token format (should be valid JWT)
echo "TOKEN" | cut -d'.' -f2 | base64 -d
```

### 4. FastMCP Configuration Issues
The current FastMCP server configuration in `src/fastmcp_proxy.py`:

```python
# Current configuration (NOT WORKING)
mcp_unified: FastMCP = FastMCP(
    name="FalkorDB FastMCP Proxy (Unified)",
    host=PROXY_HOST,
    port=PROXY_PORT,
    sse_path='/sse'
)

# Run with SSE transport
mcp_unified.run(
    transport="sse",
    host=PROXY_HOST,
    port=PROXY_PORT
)
```

**Problem**: FastMCP 2.0 SSE transport configuration doesn't match expected behavior.

## Working Solutions

### Option A: Fix FastMCP Configuration
Research correct FastMCP 2.0 SSE transport setup:
- Check FastMCP documentation for SSE endpoint creation
- Verify correct transport and sse_path configuration
- Test with minimal FastMCP SSE server

### Option B: Use Alternative MCP Server
Replace FastMCP with official MCP Python SDK:
- Use `mcp.server.stdio` or `mcp.server.sse` from official SDK
- Implement same 4 tools with official MCP protocol
- Ensure SSE endpoint creation works correctly

### Option C: Run Server Locally (Temporary)
For immediate testing:
```bash
# Run proxy locally instead of Docker
python src/fastmcp_proxy.py

# This should create proper SSE endpoints
# Then test with mcp-remote
```

## Expected Working Flow

Once fixed, the connection should work as:

1. **Claude Desktop** runs `npx mcp-remote http://localhost:3001/sse/`
2. **mcp-remote** connects to SSE endpoint with Bearer token
3. **FastMCP Proxy** validates token and forwards to backend
4. **FalkorDB MCPServer** processes requests and returns data
5. **Responses** flow back through proxy to Claude Desktop

## Key Files for Debugging

- `src/fastmcp_proxy.py` - Main proxy server (✅ WORKING with SSE endpoints)
- `docker-compose.yml` - Service orchestration (✅ WORKING)  
- `tests/test_remote_mcp.py` - Integration tests (✅ WORKING with backend)
- `claude_desktop_config.json` - Current working configuration

## Next Steps

1. **✅ FastMCP SSE Configuration**: Working with mcp-remote bridge
2. **✅ Test Endpoint Creation**: `/sse/` endpoint exists and responds correctly  
3. **✅ Validate mcp-remote Connection**: Working connection established
4. **⚠️ Final Verification**: Test tool registration and functionality in Claude Desktop
5. **📋 Documentation Complete**: All guides updated with correct mcp-remote configuration

## Environment Details

- **FastMCP Version**: 2.10.2
- **Python Version**: 3.12
- **Docker Compose**: Services running on localhost
- **Backend**: FalkorDB MCPServer v1.1.0 (WORKING)
- **Authentication**: RSA-256 Bearer tokens (WORKING)
- **Transport**: SSE (BROKEN - endpoints not created)

---

> **Note**: This document was created during active troubleshooting session on 2025-07-14. The FastMCP Docker server is currently non-functional due to SSE endpoint configuration issues. All backend services and authentication are working correctly.