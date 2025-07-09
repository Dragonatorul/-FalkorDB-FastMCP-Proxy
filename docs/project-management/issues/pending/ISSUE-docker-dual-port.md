# Issue: Docker Configuration for Dual-Port Deployment

**Status**: Pending  
**Priority**: Medium  
**Assigned**: Future Session  

## Problem Statement

Current Docker setup only runs single-device proxy on port 3001. Need to support dual-port deployment for both Claude Desktop (authenticated) and Claude (tenant-aware) access.

## Current Configuration

**docker-compose.yml**:
- Only exposes port 3001 (authenticated endpoint)
- ✅ **RESOLVED**: Uses `src/fastmcp_proxy.py` (supports both single and multi-device)
- No tenant-aware endpoint available

## Required Configuration

### Dual-Port Architecture
```yaml
# Port 3001: Claude Desktop (Bearer token authentication)
# Port 3003: Claude (URL token authentication with tenant isolation)
```

### Docker Service Options

#### Option 1: Single Service, Dual Ports
```yaml
services:
  fastmcp-proxy:
    ports:
      - "3001:3001"  # Authenticated endpoint
      - "3003:3003"  # Tenant-aware endpoint
    command: python src/fastmcp_proxy.py  # ✅ Now unified
```

#### Option 2: Separate Services
```yaml
services:
  fastmcp-proxy-auth:
    ports: ["3001:3001"]
    command: python src/fastmcp_proxy.py  # ✅ Now unified
    
  fastmcp-proxy-tenant:
    ports: ["3003:3003"] 
    command: python src/fastmcp_proxy.py  # ✅ Now unified
```

## Implementation Tasks

### 1. Create Dual-Port Proxy
✅ **RESOLVED**: `src/fastmcp_proxy.py` handles both authentication methods on single port:
```python
import asyncio
import uvicorn
from fastmcp_proxy import mcp_auth
from fastmcp_proxy_tenant import mcp_public

async def run_dual_servers():
    # Start authenticated server on 3001
    # Start tenant-aware server on 3003
```

### 2. Update docker-compose.yml
- Add port 3003 exposure
- Update command to use dual-port implementation
- Set environment variables for both ports

### 3. Update Dockerfile
- Ensure all dependencies available
- Set proper entry point for dual-server mode
- Configure logging for both services

## Files to Modify

1. `docker-compose.yml` - Add dual-port configuration
2. `Dockerfile` - Update for dual-server support
3. ✅ `src/fastmcp_proxy.py` - Unified single-server implementation

## Success Criteria

- [ ] Both endpoints accessible via Docker
- [ ] Port 3001: Claude Desktop authentication working
- [ ] Port 3003: Claude URL token authentication working  
- [ ] Docker logs show both servers starting
- [ ] Health checks work for both endpoints

## Testing Plan

1. `docker-compose up -d`
2. Test Claude Desktop connection to `:3001`
3. Test Claude connection to `:3003/?token=<jwt>`
4. Verify tenant isolation between different tokens
5. Check Docker service health and logs

## Dependencies

- Requires URL token authentication implementation
- Requires completed tenant-aware tools
- Backend services must remain accessible

## Configuration Examples

### Claude Desktop (Port 3001)
```json
{
  "name": "FalkorDB",
  "serverUrl": "http://localhost:3001/sse/",
  "auth": {
    "type": "bearer", 
    "token": "eyJhbG..."
  }
}
```

### Claude (Port 3003)
```json
{
  "name": "FalkorDB-Tenant",
  "type": "sse",
  "url": "http://localhost:3003/sse/?token=eyJhbG..."
}
```

## Estimated Effort

~1 hour to implement and test dual-port Docker configuration.

---

> **Note**: This document was created with assistance from Claude Sonnet 3.5, an AI assistant by Anthropic.