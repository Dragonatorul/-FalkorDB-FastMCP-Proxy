# Issue: FastMCP URL Token Authentication Support

**Status**: In Progress  
**Priority**: High  
**Assigned**: Next Session  

## Problem Statement

Claude Desktop integration works 100% with Bearer token authentication, but opencode requires URL-based token passing for MCP connections. FastMCP currently only supports Bearer tokens in headers, not URL query parameters.

## Technical Details

**Current State**:
- FastMCP uses `BearerAuthProvider` which expects `Authorization: Bearer <token>` headers
- opencode hardcodes SSE transport with no authentication header support
- opencode only supports: `{"type": "sse", "url": "http://host:port/sse/"}`

**Required State**:
- FastMCP should accept tokens from URL query parameters: `/sse/?token=<jwt_token>`
- Maintain backward compatibility with Bearer header authentication
- Support both authentication methods simultaneously

## Implementation Approach

### Option 1: Custom Authentication Provider
```python
class URLTokenAuthProvider(BearerAuthProvider):
    async def authenticate(self, request: Request) -> Optional[Dict[str, Any]]:
        # Try URL token first
        token = request.query_params.get("token")
        if token:
            return await self.verify_token(token)
        
        # Fallback to Bearer header
        return await super().authenticate(request)
```

### Option 2: Middleware-Based Authentication
```python
@app.middleware("http")
async def url_token_middleware(request: Request, call_next):
    if token := request.query_params.get("token"):
        # Convert URL token to Authorization header
        request.headers = request.headers.mutablecopy()
        request.headers["authorization"] = f"Bearer {token}"
    
    return await call_next(request)
```

## Files to Modify

1. `src/fastmcp_proxy_tenant.py` - Update authentication logic
2. `src/fastmcp_proxy.py` - Add URL token support for single-device mode
3. `test_remote_mcp.py` - Update tests for URL-based authentication

## Success Criteria

- [ ] FastMCP accepts tokens from URL query parameters
- [ ] Backward compatibility with Bearer headers maintained  
- [ ] opencode can connect using: `http://host:port/sse/?token=<jwt>`
- [ ] All existing Claude Desktop functionality preserved
- [ ] Tests pass for both authentication methods

## Testing Plan

1. Test URL token authentication: `GET /sse/?token=<valid_jwt>`
2. Test Bearer header authentication: `GET /sse/` with `Authorization: Bearer <token>`
3. Test invalid token scenarios for both methods
4. Test opencode connection with generated tenant tokens

## Dependencies

- Requires completion of tenant-aware MCP tools
- May need FastMCP library updates or custom authentication provider
- Should maintain compatibility with existing Claude Desktop setup

## Notes

This is the critical blocker for opencode integration. Once resolved, multi-device remote access will be fully functional.