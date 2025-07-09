# Issue: Multi-Device Testing and Validation

**Status**: Pending  
**Priority**: High  
**Assigned**: Future Session  

## Problem Statement

Need to validate that multiple devices can access the same remote FalkorDB instance with proper tenant isolation and data sharing within tenants.

## Testing Scenarios

### Scenario 1: Same Tenant, Multiple Devices
**Setup**: Two opencode instances with same tenant token
**Expected**: Both see same data, changes visible to both
```
Device A (tenant: acme) → Creates graph "customers"
Device B (tenant: acme) → Should see "customers" graph
Device B (tenant: acme) → Adds data to "customers"  
Device A (tenant: acme) → Should see new data
```

### Scenario 2: Different Tenants, Data Isolation
**Setup**: Two opencode instances with different tenant tokens
**Expected**: Complete data isolation
```
Device A (tenant: acme) → Creates graph "customers"
Device B (tenant: widgets) → Should NOT see "customers" graph
Device B (tenant: widgets) → Creates graph "products"
Device A (tenant: acme) → Should NOT see "products" graph
```

### Scenario 3: Claude Desktop + opencode Mixed
**Setup**: Claude Desktop on port 3001, opencode on port 3003
**Expected**: Independent operation
```
Claude Desktop → Uses authenticated endpoint (global access)
opencode → Uses tenant-aware endpoint (isolated access)
Both should work simultaneously without interference
```

## Test Implementation

### Test Script Structure
```python
#!/usr/bin/env python3
"""Multi-device tenant isolation test"""

def test_same_tenant_data_sharing():
    # Generate token for tenant "acme"
    # Simulate two devices with same token
    # Verify data sharing within tenant
    
def test_different_tenant_isolation():
    # Generate tokens for "acme" and "widgets"
    # Verify complete data isolation
    
def test_mixed_endpoints():
    # Test Claude Desktop endpoint
    # Test opencode tenant endpoint
    # Verify no interference
```

### Required Test Infrastructure

1. **Token Generation Utility**
```python
def generate_test_tokens():
    return {
        "acme_admin": generate_tenant_token("acme", "admin"),
        "acme_user": generate_tenant_token("acme", "user"),
        "widgets_admin": generate_tenant_token("widgets", "admin")
    }
```

2. **Multi-Client Test Framework**
```python
class TenantTestClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token
        
    async def create_graph(self, name: str):
        # POST to /sse/?token=<token> with MCP call
        
    async def list_graphs(self):
        # GET graphs list via MCP
        
    async def query_graph(self, name: str, query: str):
        # Execute query via MCP
```

## Files to Create

1. `tests/test_multi_device.py` - Comprehensive multi-device test suite
2. `tests/test_tenant_isolation.py` - Focused tenant isolation tests  
3. `tests/utils/tenant_test_client.py` - Test client utilities
4. `tests/test_mixed_endpoints.py` - Claude Desktop + opencode tests

## Success Criteria

### Data Sharing (Same Tenant)
- [ ] Multiple devices see same graphs
- [ ] Data changes visible across devices
- [ ] Concurrent access works properly
- [ ] No data corruption with simultaneous writes

### Data Isolation (Different Tenants)  
- [ ] Tenant graphs completely isolated
- [ ] No cross-tenant data leakage
- [ ] Independent graph namespaces
- [ ] Tenant-specific error handling

### Mixed Endpoint Operation
- [ ] Claude Desktop and opencode work simultaneously
- [ ] No authentication conflicts
- [ ] Independent session management
- [ ] Proper error isolation

## Testing Environment

### Docker Stack Requirements
```yaml
# All services running:
# - FalkorDB (port 6379)
# - FalkorDB MCPServer v1.1.0 (port 3000)  
# - FastMCP Proxy Dual (ports 3001, 3003)
```

### Test Data Setup
```cypher
# Tenant: acme
CREATE (c:Customer {name: 'Acme Corp', id: 1})
CREATE (p:Product {name: 'Widget A', price: 100})

# Tenant: widgets  
CREATE (c:Customer {name: 'Widget Inc', id: 1})
CREATE (p:Product {name: 'Gadget B', price: 200})
```

## Validation Steps

1. **Environment Setup**
   - Start Docker stack
   - Verify all services healthy
   - Generate test tenant tokens

2. **Same-Tenant Testing**
   - Connect two test clients with same token
   - Create data on client A
   - Verify visibility on client B
   - Test concurrent operations

3. **Cross-Tenant Testing**
   - Connect clients with different tokens
   - Verify complete data isolation
   - Test namespace separation
   - Validate error handling

4. **Mixed-Endpoint Testing**
   - Test Claude Desktop authentication
   - Test opencode tenant authentication
   - Verify simultaneous operation
   - Check resource isolation

## Dependencies

- Requires completed URL token authentication
- Requires completed tenant-aware MCP tools
- Requires dual-port Docker configuration
- Backend tenant header support working

## Estimated Effort

~2-3 hours to implement comprehensive test suite and validate all scenarios.