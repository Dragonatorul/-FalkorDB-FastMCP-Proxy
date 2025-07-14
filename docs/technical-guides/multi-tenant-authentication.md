# Multi-Tenant Authentication and Data Separation

## Overview

The FalkorDB FastMCP Proxy supports **multi-tenant deployments** where multiple organizations or users can access the same proxy instance while maintaining **complete data isolation**. This document explains how tenant authentication works, data separation mechanisms, and deployment strategies.

## 🏗️ Multi-Tenant Architecture

### System Components

```
┌─────────────────┐    JWT Token     ┌─────────────────┐   Tenant ID    ┌─────────────────┐
│   Tenant A      │ ─────────────→   │  FastMCP Proxy  │ ─────────────→ │ FalkorDB        │
│   Claude Desktop│    (sub: "a")    │                 │   (a_graph)    │ MCPServer       │
└─────────────────┘                  │                 │                │                 │
                                     │  Authentication │                │ Tenant Graph    │
┌─────────────────┐    JWT Token     │  & Routing      │   Tenant ID    │ Prefixing       │
│   Tenant B      │ ─────────────→   │                 │ ─────────────→ │                 │
│   Claude Desktop│    (sub: "b")    │                 │   (b_graph)    │ Data Isolation  │
└─────────────────┘                  └─────────────────┘                └─────────────────┘
```

### Data Flow

1. **Authentication**: Each tenant gets unique JWT tokens with tenant ID in `subject` claim
2. **Proxy Routing**: FastMCP extracts tenant ID from JWT and forwards to backend
3. **Graph Prefixing**: Backend prefixes graph names with tenant ID (`tenant_graph`)
4. **Data Isolation**: FalkorDB stores separate graph databases per tenant

## 🔐 Authentication Mechanisms

### JWT Token Structure

Multi-tenant JWT tokens include tenant identification in the `subject` claim:

```json
{
  "iss": "https://your-auth-provider.com",
  "sub": "tenant-alpha",
  "aud": "falkordb-mcp-server", 
  "iat": 1641024000,
  "exp": 1641027600,
  "scope": "read write",
  "custom_claims": {
    "organization": "Alpha Corp",
    "plan": "enterprise"
  }
}
```

**Key Claims:**
- **`sub` (subject)**: **Primary tenant identifier** - used for data isolation
- **`iss` (issuer)**: Your authentication provider
- **`aud` (audience)**: Must match configured audience
- **`scope`**: Permissions (read, write, admin)

### Authentication Providers

#### **Option 1: Multiple RSA Key Pairs (Simple)**
Generate separate RSA key pairs per tenant:

```python
# Tenant A configuration
tenant_a_keypair = RSAKeyPair.generate()
tenant_a_auth = BearerAuthProvider(
    public_key=tenant_a_keypair.public_key,
    issuer="https://auth.tenant-a.com",
    audience="falkordb-mcp-server",
    algorithm="RS256"
)

# Tenant B configuration  
tenant_b_keypair = RSAKeyPair.generate()
tenant_b_auth = BearerAuthProvider(
    public_key=tenant_b_keypair.public_key,
    issuer="https://auth.tenant-b.com", 
    audience="falkordb-mcp-server",
    algorithm="RS256"
)
```

#### **Option 2: JWKS Endpoint (Recommended)**
Use a centralized JWKS endpoint supporting multiple tenants:

```python
# Multi-tenant JWKS configuration
auth = BearerAuthProvider(
    jwks_url="https://auth.yourcompany.com/.well-known/jwks.json",
    issuer="https://auth.yourcompany.com",
    audience="falkordb-mcp-server",
    algorithm="RS256"
)
```

JWKS endpoint serves multiple public keys:
```json
{
  "keys": [
    {
      "kid": "tenant-a-key",
      "kty": "RSA",
      "use": "sig",
      "n": "...",
      "e": "AQAB"
    },
    {
      "kid": "tenant-b-key", 
      "kty": "RSA",
      "use": "sig",
      "n": "...",
      "e": "AQAB"
    }
  ]
}
```

#### **Option 3: OAuth Provider Integration**
Integrate with enterprise OAuth providers:

**Auth0 Example:**
```python
auth = BearerAuthProvider(
    jwks_url="https://your-tenant.auth0.com/.well-known/jwks.json",
    issuer="https://your-tenant.auth0.com/",
    audience="https://api.yourcompany.com/falkordb",
    algorithm="RS256"
)
```

**Azure AD Example:**
```python
auth = BearerAuthProvider(
    jwks_url="https://login.microsoftonline.com/{tenant-id}/discovery/v2.0/keys",
    issuer="https://login.microsoftonline.com/{tenant-id}/v2.0",
    audience="api://falkordb-mcp-server",
    algorithm="RS256"
)
```

## 🗄️ Data Separation Mechanisms

### Backend Multi-Tenancy Configuration

The FalkorDB MCPServer v1.1.0 backend supports multi-tenancy through configuration:

```env
# Enable multi-tenancy
ENABLE_MULTI_TENANCY=true
MULTI_TENANT_AUTH_MODE=bearer

# JWT Configuration
BEARER_JWKS_URI=https://auth.yourcompany.com/.well-known/jwks.json
BEARER_ISSUER=https://auth.yourcompany.com
BEARER_AUDIENCE=falkordb-mcp-server
BEARER_ALGORITHM=RS256

# Graph prefixing for data isolation
TENANT_GRAPH_PREFIX=true
```

### Graph Name Resolution

The backend automatically prefixes graph names with tenant IDs:

**Without Multi-Tenancy:**
- Request: `falkordb_query(graphName="social_network", query="...")`
- FalkorDB Graph: `social_network`

**With Multi-Tenancy:**
- Request: `falkordb_query(graphName="social_network", query="...")` 
- JWT Subject: `"tenant-alpha"`
- FalkorDB Graph: `tenant-alpha_social_network`

### Data Isolation Examples

**Tenant A requests:**
```python
# Request from Tenant A (subject: "company-a")
await falkordb_query(
    graphName="users",
    query="MATCH (u:User) RETURN u.name"
)
# Accesses graph: "company-a_users"
```

**Tenant B requests:**
```python  
# Request from Tenant B (subject: "company-b")
await falkordb_query(
    graphName="users", 
    query="MATCH (u:User) RETURN u.name"
)
# Accesses graph: "company-b_users"
```

**Result**: Complete data isolation - tenants cannot access each other's data.

## 🔧 Implementation Guide

### Step 1: Configure Multi-Tenant Backend

Update your `docker-compose.yml` to enable multi-tenancy:

```yaml
services:
  falkordb-mcp-server:
    image: ghcr.io/dragonatorul/falkordb-mcpserver:1.1.0
    environment:
      - ENABLE_MULTI_TENANCY=true
      - MULTI_TENANT_AUTH_MODE=bearer
      - BEARER_JWKS_URI=https://auth.yourcompany.com/.well-known/jwks.json
      - BEARER_ISSUER=https://auth.yourcompany.com
      - BEARER_AUDIENCE=falkordb-mcp-server
      - BEARER_ALGORITHM=RS256
      - TENANT_GRAPH_PREFIX=true
```

### Step 2: Configure FastMCP Proxy for Multi-Tenancy

Update the proxy to extract and forward tenant information:

```python
import jwt
from fastmcp import FastMCP, Context
from fastmcp.server.auth import BearerAuthProvider

# Multi-tenant auth configuration
auth = BearerAuthProvider(
    jwks_url="https://auth.yourcompany.com/.well-known/jwks.json",
    issuer="https://auth.yourcompany.com",
    audience="falkordb-mcp-server",
    algorithm="RS256"
)

mcp = FastMCP("Multi-Tenant FalkorDB Proxy", auth=auth)

async def call_backend_with_tenant(
    method: str, 
    endpoint: str, 
    tenant_id: str,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Call backend with tenant context"""
    
    # Create JWT token for backend with tenant context
    backend_token = create_backend_token(tenant_id)
    
    headers = {
        "Authorization": f"Bearer {backend_token}",
        "Content-Type": "application/json"
    }
    
    # Make backend request with tenant context
    url = f"{BACKEND_URL}{endpoint}"
    response = await http_client.request(method, url, headers=headers, json=data)
    return response.json()

@mcp.tool
async def falkordb_query(
    ctx: Context,
    graphName: str,
    query: str,
    parameters: Optional[Dict[str, Any]] = None
) -> str:
    """Execute tenant-isolated Cypher query"""
    
    # Extract tenant ID from authenticated context
    tenant_id = ctx.auth.subject  # JWT subject claim
    
    # Call backend with tenant context
    result = await call_backend_with_tenant(
        "POST", 
        "/api/mcp/context",
        tenant_id,
        {
            "graphName": graphName,
            "query": query, 
            "parameters": parameters or {}
        }
    )
    
    return format_response(result)
```

### Step 3: Tenant Token Generation

Create tenant-specific tokens for each Claude Desktop instance:

```python
def generate_tenant_token(tenant_id: str, scopes: List[str] = None) -> str:
    """Generate JWT token for specific tenant"""
    
    payload = {
        "iss": "https://auth.yourcompany.com",
        "sub": tenant_id,  # Tenant identifier
        "aud": "falkordb-mcp-server",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=24),
        "scope": " ".join(scopes or ["read", "write"])
    }
    
    return jwt.encode(payload, private_key, algorithm="RS256")

# Generate tokens for different tenants
tenant_a_token = generate_tenant_token("company-a", ["read", "write"])
tenant_b_token = generate_tenant_token("company-b", ["read"])
tenant_c_token = generate_tenant_token("company-c", ["read", "write", "admin"])
```

### Step 4: Claude Desktop Configuration Per Tenant

Each tenant gets their own Claude Desktop configuration:

**Tenant A Configuration:**
```json
{
  "mcpServers": {
    "falkordb": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:3001/sse/"],
      "env": {
        "MCP_AUTH_HEADER": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...TENANT_A_TOKEN"
      }
    }
  }
}
```

**Tenant B Configuration:**
```json
{
  "mcpServers": {
    "falkordb": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:3001/sse/"],
      "env": {
        "MCP_AUTH_HEADER": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...TENANT_B_TOKEN"
      }
    }
  }
}
```

## 🔒 Security Considerations

### Authentication Security

**JWT Best Practices:**
- **Short Token Lifetimes**: 1-24 hours maximum
- **Token Rotation**: Implement refresh token flows
- **Secure Storage**: Store tokens securely in Claude Desktop
- **Revocation**: Implement token blacklisting capabilities

**Key Management:**
- **Production Keys**: Use proper OAuth providers or HSMs
- **Key Rotation**: Regular rotation of signing keys
- **Separate Keys**: Different keys per tenant for enhanced security

### Authorization Controls

**Scope-Based Permissions:**
```json
{
  "tenant-admin": ["read", "write", "admin", "manage-users"],
  "tenant-user": ["read", "write"],
  "tenant-readonly": ["read"]
}
```

**Graph-Level Permissions:**
```python
def validate_graph_access(tenant_id: str, graph_name: str, operation: str) -> bool:
    """Validate tenant access to specific graphs"""
    
    tenant_config = get_tenant_config(tenant_id)
    
    # Check if tenant has access to this graph
    if graph_name not in tenant_config.allowed_graphs:
        return False
        
    # Check operation permissions
    if operation == "write" and "write" not in tenant_config.scopes:
        return False
        
    return True
```

### Data Isolation Verification

**Graph Listing Security:**
```python
@mcp.tool
async def falkordb_list_graphs(ctx: Context) -> str:
    """List only tenant-accessible graphs"""
    
    tenant_id = ctx.auth.subject
    all_graphs = await call_backend("GET", "/api/mcp/graphs", tenant_id)
    
    # Filter to only show tenant's graphs (those with tenant prefix)
    tenant_graphs = [
        graph for graph in all_graphs 
        if graph.startswith(f"{tenant_id}_")
    ]
    
    # Remove tenant prefix from display names
    display_graphs = [
        graph.replace(f"{tenant_id}_", "") 
        for graph in tenant_graphs
    ]
    
    return format_graph_list(display_graphs)
```

## 🚀 Deployment Strategies

### Single Proxy Instance (Recommended)

**Architecture:**
```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   Tenant A  │   │   Tenant B  │   │   Tenant C  │
│   Token A   │   │   Token B   │   │   Token C   │
└──────┬──────┘   └──────┬──────┘   └──────┬──────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
              ┌──────────▼──────────┐
              │   FastMCP Proxy     │
              │   Multi-Tenant      │
              │   Authentication    │
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │ FalkorDB MCPServer  │
              │ Tenant Graph        │
              │ Prefixing           │
              └─────────────────────┘
```

**Benefits:**
- Single deployment to manage
- Shared resource utilization
- Centralized monitoring and updates
- Cost-effective for multiple tenants

### Multi-Instance Deployment (High Security)

**Architecture:**
```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   Tenant A  │       │   Tenant B  │       │   Tenant C  │
└──────┬──────┘       └──────┬──────┘       └──────┬──────┘
       │                     │                     │
┌──────▼──────┐       ┌──────▼──────┐       ┌──────▼──────┐
│ Proxy A     │       │ Proxy B     │       │ Proxy C     │
│ Port 3001   │       │ Port 3002   │       │ Port 3003   │
└──────┬──────┘       └──────┬──────┘       └──────┬──────┘
       │                     │                     │
┌──────▼──────┐       ┌──────▼──────┐       ┌──────▼──────┐
│MCPServer A  │       │MCPServer B  │       │MCPServer C  │
│Port 4001    │       │Port 4002    │       │Port 4003    │
└─────────────┘       └─────────────┘       └─────────────┘
```

**Benefits:**
- Complete infrastructure isolation
- Independent scaling per tenant
- Enhanced security boundaries
- Separate monitoring and alerting

## 📊 Monitoring and Auditing

### Request Tracking

```python
import logging
from datetime import datetime

logger = logging.getLogger("tenant-audit")

@mcp.tool
async def falkordb_query(ctx: Context, graphName: str, query: str) -> str:
    """Audited tenant query execution"""
    
    tenant_id = ctx.auth.subject
    request_id = generate_request_id()
    
    # Audit log entry
    logger.info({
        "event": "graph_query",
        "request_id": request_id,
        "tenant_id": tenant_id,
        "graph_name": graphName,
        "query_hash": hash_query(query),
        "timestamp": datetime.utcnow().isoformat(),
        "user_agent": ctx.request.headers.get("user-agent")
    })
    
    try:
        result = await call_backend_with_tenant("POST", "/api/mcp/context", tenant_id, {
            "graphName": graphName,
            "query": query
        })
        
        logger.info({
            "event": "query_success",
            "request_id": request_id,
            "tenant_id": tenant_id,
            "execution_time_ms": result.get("metadata", {}).get("queryTime"),
            "rows_returned": len(result.get("data", {}).get("data", []))
        })
        
        return format_response(result)
        
    except Exception as e:
        logger.error({
            "event": "query_error", 
            "request_id": request_id,
            "tenant_id": tenant_id,
            "error": str(e)
        })
        raise
```

### Usage Analytics

```python
class TenantMetrics:
    def __init__(self):
        self.redis = redis.Redis()
        
    async def record_usage(self, tenant_id: str, operation: str):
        """Record tenant usage metrics"""
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Daily counters
        await self.redis.incr(f"tenant:{tenant_id}:requests:{today}")
        await self.redis.incr(f"tenant:{tenant_id}:operations:{operation}:{today}")
        
    async def get_tenant_usage(self, tenant_id: str, days: int = 30) -> Dict:
        """Get tenant usage statistics"""
        
        usage = {}
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            requests = await self.redis.get(f"tenant:{tenant_id}:requests:{date}")
            usage[date] = int(requests or 0)
            
        return usage
```

## 🧪 Testing Multi-Tenancy

### Integration Tests

```python
import pytest
from fastmcp.testing import MCPTestClient

@pytest.fixture
def tenant_a_client():
    return MCPTestClient(
        server=mcp,
        auth_token=generate_tenant_token("tenant-a")
    )

@pytest.fixture  
def tenant_b_client():
    return MCPTestClient(
        server=mcp,
        auth_token=generate_tenant_token("tenant-b")
    )

async def test_tenant_data_isolation(tenant_a_client, tenant_b_client):
    """Test that tenants cannot access each other's data"""
    
    # Tenant A creates a graph
    await tenant_a_client.call_tool("falkordb_query", {
        "graphName": "test_graph",
        "query": "CREATE (n:Node {id: 'tenant-a-data'})"
    })
    
    # Tenant B tries to access the same graph name
    result = await tenant_b_client.call_tool("falkordb_query", {
        "graphName": "test_graph", 
        "query": "MATCH (n:Node) RETURN n"
    })
    
    # Should return empty results (accessing tenant-b_test_graph, not tenant-a_test_graph)
    assert len(result.data) == 0

async def test_graph_listing_isolation(tenant_a_client, tenant_b_client):
    """Test that graph listings are tenant-specific"""
    
    # Create graphs for different tenants
    await tenant_a_client.call_tool("falkordb_query", {
        "graphName": "private_graph",
        "query": "CREATE (n:Node {tenant: 'a'})"
    })
    
    await tenant_b_client.call_tool("falkordb_query", {
        "graphName": "secret_graph", 
        "query": "CREATE (n:Node {tenant: 'b'})"
    })
    
    # List graphs for each tenant
    a_graphs = await tenant_a_client.call_tool("falkordb_list_graphs", {})
    b_graphs = await tenant_b_client.call_tool("falkordb_list_graphs", {})
    
    # Each tenant should only see their own graphs
    assert "private_graph" in a_graphs.text
    assert "secret_graph" not in a_graphs.text
    
    assert "secret_graph" in b_graphs.text
    assert "private_graph" not in b_graphs.text
```

## 📋 Production Checklist

### Security Verification
- [ ] **JWT Validation**: Tokens properly validated with correct issuer/audience
- [ ] **Key Management**: Production-grade key storage and rotation
- [ ] **Scope Enforcement**: Proper permission checking per operation
- [ ] **Token Expiration**: Short-lived tokens with refresh capabilities
- [ ] **Audit Logging**: Complete request/response logging per tenant

### Data Isolation Verification  
- [ ] **Graph Prefixing**: Backend correctly prefixes all graph names
- [ ] **List Operations**: Graph listings filtered by tenant
- [ ] **Query Isolation**: Cross-tenant data access impossible
- [ ] **Metadata Isolation**: Tenant metadata properly segregated
- [ ] **Error Messages**: No data leakage in error responses

### Performance & Scalability
- [ ] **Connection Pooling**: Efficient database connection management
- [ ] **Caching Strategy**: Tenant-aware caching implementation
- [ ] **Rate Limiting**: Per-tenant request rate limits
- [ ] **Resource Monitoring**: Per-tenant resource usage tracking
- [ ] **Auto-scaling**: Horizontal scaling based on tenant load

### Operational Readiness
- [ ] **Monitoring**: Tenant-specific metrics and alerting
- [ ] **Backup Strategy**: Tenant data backup and restore procedures
- [ ] **Disaster Recovery**: Multi-tenant disaster recovery plan
- [ ] **Incident Response**: Tenant-aware incident management
- [ ] **Documentation**: Complete deployment and operational guides

---

## Summary

Multi-tenant support in the FalkorDB FastMCP Proxy provides **enterprise-grade data isolation** through:

- **JWT-based Authentication**: Tenant identification via JWT subject claims
- **Graph Prefixing**: Automatic tenant prefix for all graph operations  
- **Complete Data Isolation**: No cross-tenant data access possible
- **Flexible Deployment**: Single instance or multi-instance options
- **Production Security**: OAuth integration, audit logging, monitoring

This architecture enables **secure SaaS deployment** where multiple organizations can safely share the same FalkorDB infrastructure while maintaining complete data privacy and security.

---

> **Note**: This document was created with assistance from Claude Sonnet 3.5, an AI assistant by Anthropic.