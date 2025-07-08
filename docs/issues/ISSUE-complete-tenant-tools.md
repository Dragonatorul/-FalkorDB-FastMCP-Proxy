# Issue: Complete Tenant-Aware MCP Tools

**Status**: Pending  
**Priority**: High  
**Assigned**: Next Session  

## Problem Statement

✅ **RESOLVED**: The unified proxy (`src/fastmcp_proxy.py`) now has all 4 MCP tools implemented with tenant context for full functionality.

## Current Implementation Status

### ✅ Completed (1/4)
- `falkordb_query_tenant` - Execute Cypher queries with tenant isolation

### ⏳ Pending (3/4)
- `falkordb_list_graphs_tenant` - List graphs with tenant prefix filtering
- `falkordb_server_info_tenant` - Server metadata with tenant context
- `falkordb_health_tenant` - Health check with tenant information

## Implementation Details

### Required Pattern
Each tenant-aware tool should:
1. Extract tenant context from request state
2. Apply tenant-specific graph name prefixing
3. Forward tenant headers to backend
4. Include tenant information in responses

### Code Template
```python
@mcp_public.tool
async def falkordb_<function>_tenant(ctx: Context, ...args) -> str:
    # Get tenant context
    tenant_context = getattr(ctx.request.state, 'tenant_context', None)
    if not tenant_context:
        return "Error: No tenant context available"
    
    # Apply tenant logic (graph prefixing, etc.)
    
    # Call backend with tenant headers
    result = await call_backend_with_tenant("GET/POST", "/endpoint", tenant_context, data)
    
    # Format response with tenant information
    return formatted_response_with_tenant_info
```

## Files to Modify

1. ✅ `src/fastmcp_proxy.py` - All 4 tenant-aware tools implemented
2. `test_remote_mcp.py` - Add tests for new tenant tools

## Implementation Tasks

### 1. falkordb_list_graphs_tenant
- Filter graph list to show only tenant-prefixed graphs
- Remove tenant prefix from displayed names
- Show tenant context in metadata

### 2. falkordb_server_info_tenant  
- Include tenant ID in server information
- Show tenant-specific capabilities/limits
- Add tenant usage statistics if available

### 3. falkordb_health_tenant
- Include tenant connectivity status
- Show tenant-specific health metrics
- Validate tenant token freshness

## Success Criteria

- [ ] All 4 MCP tools implemented with tenant awareness
- [ ] Tenant isolation working (graph name prefixing)
- [ ] Tenant context visible in all responses
- [ ] No cross-tenant data leakage possible
- [ ] Tests validate tenant isolation

## Testing Requirements

For each tool:
1. Test with valid tenant token
2. Test tenant isolation (different tenants see different data)
3. Test error handling (invalid/missing tenant context)
4. Verify tenant information in responses

## Dependencies

- Requires URL token authentication (ISSUE-fastmcp-url-tokens.md)
- Backend must support tenant headers (already implemented)
- JWT token generation/validation working (already implemented)

## Estimated Effort

~1-2 hours to implement all 3 remaining tools following the established pattern.