# Known Issues & Bug Reports

## Critical Issues

### ✅ ISSUE-001: Docker FastMCP Initialization Failure

**Status**: RESOLVED ✅  
**Priority**: High (was blocking Docker deployment)  
**Affects**: Docker deployment  
**Discovered**: 2025-07-08  
**Resolved**: 2025-07-08  
**Resolution**: Switch from SSE to streamable-http transport

#### Problem Description (RESOLVED)
The FastMCP proxy failed to initialize properly when running inside a Docker container with SSE transport. Container would fall back to plain uvicorn instead of FastMCP transport.

#### Root Cause Identified
**Transport-Specific Issue**: FastMCP's SSE transport has compatibility issues with Docker containerized environments. The streamable-http transport works reliably in both local and Docker environments.

#### Solution Applied
**Transport Change**: Switch from `transport="sse"` to `transport="streamable-http"`

```python
# ❌ BROKEN in Docker
mcp.run(transport="sse", host=PROXY_HOST, port=PROXY_PORT)

# ✅ WORKS in Docker  
mcp.run(transport="streamable-http", host=PROXY_HOST, port=PROXY_PORT)
```

#### Results After Fix
- ✅ **Docker Deployment**: Full stack runs in containers
- ✅ **FastMCP Transport**: Proper initialization with banner display (local)
- ✅ **OAuth Endpoints**: `/.well-known/oauth-authorization-server` working
- ✅ **MCP Endpoints**: `/mcp/` properly requires authentication
- ✅ **Integration Tests**: 3/3 tests passing with new endpoints
- ✅ **Production Ready**: No hybrid deployment needed

#### Updated Claude Desktop Configuration
```json
{
  "name": "FalkorDB",
  "serverUrl": "http://localhost:3001/mcp/", 
  "auth": {
    "type": "bearer",
    "token": "YOUR_BEARER_TOKEN_HERE"
  }
}
```

#### Technical Details - Resolution
```bash
# Full Docker deployment now works
docker-compose up -d

# All services in containers:
# - FalkorDB: localhost:6379  
# - MCPServer: localhost:3000
# - FastMCP Proxy: localhost:3001/mcp/
```

**Commit**: `5cfe758` - `fix(docker): resolve FastMCP Docker initialization issue`
- SSE transport initialized on http://0.0.0.0:3001/sse/
- OAuth metadata endpoint active
- Bearer token authentication working

Docker Execution (BROKEN):
- Silent startup, no FastMCP banner
- Uvicorn server on port 3001
- Missing /sse/ and /.well-known/ endpoints
- All requests return 404
```

#### Potential Solutions (Future Investigation)
1. **FastMCP Team Contact**: Report Docker compatibility issue
2. **Alternative Initialization**: Try different FastMCP startup methods
3. **Manual Transport**: Implement custom SSE endpoint using FastAPI
4. **Container Config**: Test different base images or runtime settings

#### Impact Assessment
- **Development**: ✅ No impact (local deployment works)
- **Testing**: ✅ No impact (all tests pass with hybrid setup)
- **Production**: ⚠️ Requires local FastMCP process (manageable)
- **Scalability**: ⚠️ Limited by single FastMCP instance

---

## Minor Issues

### 🐛 ISSUE-002: Docker Compose Version Warning

**Status**: Open - Cosmetic  
**Priority**: Low  
**Affects**: Docker Compose output

#### Problem
Docker Compose shows warning about obsolete `version` attribute:
```
level=warning msg="docker-compose.yml: the attribute `version` is obsolete"
```

#### Solution
Remove `version: '3.8'` line from docker-compose.yml (modern Docker Compose doesn't require it).

#### Impact
Cosmetic only - no functional impact.

---

## Resolved Issues

### ✅ ISSUE-003: Bearer Token Validation Mismatch  

**Status**: Resolved  
**Date Resolved**: 2025-07-08  
**Resolution**: Use startup token instead of test-generated token

#### Problem (Resolved)
Integration tests were failing SSE authentication because test script generated new RSA keypair instead of using the running proxy's keypair.

#### Solution Applied
Modified test approach to use the actual Bearer token printed by the proxy at startup, ensuring token validation consistency.

#### Result
All 3/3 integration tests now pass consistently.

---

## Test Results Summary

### Integration Test Status
```bash
$ python test_remote_mcp.py
🧪 Testing FalkorDB FastMCP Proxy for Remote Access
✅ Backend health: healthy
✅ OAuth Authorization Server Metadata endpoint working  
✅ SSE endpoint accepts valid Bearer token
📊 Test Results: 3/3 passed
```

### Manual Validation Status
- ✅ OAuth metadata endpoint (`/.well-known/oauth-authorization-server`)
- ✅ SSE endpoint authentication (`/sse/`)
- ✅ Bearer token generation and validation
- ✅ MCP tools execution (all 4 tools functional)
- ✅ Backend health monitoring
- ✅ Claude Desktop integration ready

---

## Reporting New Issues

When reporting issues, please include:

1. **Environment**: Local vs Docker deployment
2. **Command**: Exact command that triggered the issue  
3. **Expected**: What should happen
4. **Actual**: What actually happened
5. **Logs**: Relevant log output
6. **Reproduction**: Steps to reproduce the issue

For Docker issues, also include:
- `docker --version`
- `docker-compose --version`  
- Container logs: `docker-compose logs [service-name]`