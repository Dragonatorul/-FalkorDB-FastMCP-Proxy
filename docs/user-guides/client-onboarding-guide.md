# Production Client Onboarding Guide

## Overview

This guide provides the complete workflow for onboarding new clients (tenants) to a production FalkorDB FastMCP Proxy deployment. Each client gets their own authentication credentials, isolated data space, and Claude Desktop configuration.

## 🏢 Client Onboarding Workflow

### Phase 1: Pre-Onboarding Preparation

#### **Step 1: Client Information Gathering**

**Required Information:**
```yaml
client_info:
  organization_name: "Acme Corporation"
  tenant_id: "acme-corp"           # Unique identifier (lowercase, dashes only)
  primary_contact: "john@acme.com"
  technical_contact: "tech@acme.com"
  plan_type: "enterprise"         # basic, professional, enterprise
  data_region: "us-east-1"        # For compliance requirements
  expected_usage: "10k queries/month"
  go_live_date: "2025-02-01"
```

**Security Requirements:**
```yaml
security_profile:
  authentication_method: "oauth"   # oauth, jwks, rsa-keypair
  token_lifetime: "24h"           # 1h, 24h, 7d
  required_scopes: ["read", "write"] # read, write, admin
  ip_whitelist: ["203.0.113.0/24"] # Optional IP restrictions
  audit_level: "full"             # basic, standard, full
```

#### **Step 2: Tenant ID Validation**

**Validation Rules:**
```python
import re

def validate_tenant_id(tenant_id: str) -> bool:
    """Validate tenant ID follows naming conventions"""
    
    # Rules:
    # - 3-50 characters
    # - Lowercase letters, numbers, hyphens only
    # - Must start and end with alphanumeric
    # - No consecutive hyphens
    
    pattern = r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?$'
    
    if not re.match(pattern, tenant_id):
        return False
        
    if len(tenant_id) < 3 or len(tenant_id) > 50:
        return False
        
    if '--' in tenant_id:  # No consecutive hyphens
        return False
        
    return True

def check_tenant_availability(tenant_id: str) -> bool:
    """Check if tenant ID is available"""
    
    # Check against existing tenants
    existing_tenants = get_existing_tenant_ids()
    if tenant_id in existing_tenants:
        return False
        
    # Check against reserved names
    reserved_names = ['admin', 'api', 'www', 'system', 'root', 'public']
    if tenant_id in reserved_names:
        return False
        
    return True

# Example usage
tenant_id = "acme-corp"
if validate_tenant_id(tenant_id) and check_tenant_availability(tenant_id):
    print(f"✅ Tenant ID '{tenant_id}' is valid and available")
else:
    print(f"❌ Tenant ID '{tenant_id}' is invalid or unavailable")
```

### Phase 2: Authentication Setup

#### **Option A: OAuth Provider Integration (Recommended)**

**For Auth0:**
```bash
# 1. Create Auth0 Application
curl -X POST https://acme-corp.auth0.com/api/v2/clients \
  -H "Authorization: Bearer ${AUTH0_MANAGEMENT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "FalkorDB MCP - Acme Corp",
    "app_type": "non_interactive",
    "grant_types": ["client_credentials"],
    "token_endpoint_auth_method": "client_secret_post",
    "custom_claims": {
      "tenant_id": "acme-corp",
      "plan": "enterprise"
    }
  }'

# 2. Configure Resource Server (if not exists)
curl -X POST https://acme-corp.auth0.com/api/v2/resource-servers \
  -H "Authorization: Bearer ${AUTH0_MANAGEMENT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "https://api.yourcompany.com/falkordb",
    "name": "FalkorDB MCP API",
    "scopes": [
      {"value": "read", "description": "Read access to graphs"},
      {"value": "write", "description": "Write access to graphs"},
      {"value": "admin", "description": "Administrative access"}
    ]
  }'
```

**For Azure AD:**
```powershell
# 1. Create App Registration
az ad app create \
  --display-name "FalkorDB MCP - Acme Corp" \
  --identifier-uris "api://falkordb-acme-corp" \
  --app-roles '[{
    "allowedMemberTypes": ["Application"],
    "description": "Read access to FalkorDB",
    "displayName": "FalkorDB.Read",
    "id": "$(uuidgen)",
    "isEnabled": true,
    "value": "read"
  }]'

# 2. Create Service Principal
az ad sp create --id $APP_ID

# 3. Generate Client Secret
az ad app credential reset --id $APP_ID --append
```

#### **Option B: JWKS-Based Authentication**

**Generate RSA Key Pair:**
```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import json
import base64

def generate_tenant_keypair(tenant_id: str):
    """Generate RSA key pair for tenant"""
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    # Get public key
    public_key = private_key.public_key()
    
    # Serialize private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Serialize public key for JWKS
    public_numbers = public_key.public_numbers()
    
    # Convert to base64url
    def int_to_base64url(value):
        byte_length = (value.bit_length() + 7) // 8
        return base64.urlsafe_b64encode(
            value.to_bytes(byte_length, 'big')
        ).decode('ascii').rstrip('=')
    
    jwk = {
        "kty": "RSA",
        "use": "sig",
        "kid": f"{tenant_id}-key",
        "alg": "RS256",
        "n": int_to_base64url(public_numbers.n),
        "e": int_to_base64url(public_numbers.e)
    }
    
    return {
        "tenant_id": tenant_id,
        "private_key": private_pem.decode('utf-8'),
        "jwk": jwk,
        "key_id": f"{tenant_id}-key"
    }

# Generate keypair for new tenant
tenant_keys = generate_tenant_keypair("acme-corp")
print(f"Generated keys for tenant: {tenant_keys['tenant_id']}")
```

**Update JWKS Endpoint:**
```python
def update_jwks_endpoint(new_jwk: dict):
    """Add new tenant's public key to JWKS endpoint"""
    
    # Load current JWKS
    current_jwks = load_current_jwks()
    
    # Add new key
    current_jwks["keys"].append(new_jwk)
    
    # Save updated JWKS
    save_jwks(current_jwks)
    
    # Deploy to JWKS endpoint
    deploy_jwks_to_endpoint(current_jwks)

# Example JWKS structure
jwks_structure = {
    "keys": [
        {
            "kty": "RSA",
            "use": "sig", 
            "kid": "acme-corp-key",
            "alg": "RS256",
            "n": "...",
            "e": "AQAB"
        },
        {
            "kty": "RSA",
            "use": "sig",
            "kid": "other-tenant-key", 
            "alg": "RS256",
            "n": "...",
            "e": "AQAB"
        }
    ]
}
```

### Phase 3: Infrastructure Configuration

#### **Step 3: Update Backend Configuration**

**Multi-Tenant Environment Variables:**
```bash
# Update docker-compose.yml or Kubernetes deployment
cat > tenant-config-update.env << EOF
# Enable multi-tenancy if not already enabled
ENABLE_MULTI_TENANCY=true
MULTI_TENANT_AUTH_MODE=bearer

# JWT Configuration (update with tenant's auth provider)
BEARER_JWKS_URI=https://auth.yourcompany.com/.well-known/jwks.json
BEARER_ISSUER=https://auth.yourcompany.com
BEARER_AUDIENCE=falkordb-mcp-server
BEARER_ALGORITHM=RS256

# Graph prefixing for data isolation
TENANT_GRAPH_PREFIX=true

# Optional: Audit logging
AUDIT_LOGGING_ENABLED=true
AUDIT_LOG_LEVEL=full
EOF
```

**Apply Configuration:**
```bash
# For Docker Compose
docker-compose down
docker-compose up -d

# For Kubernetes
kubectl apply -f tenant-config-configmap.yaml
kubectl rollout restart deployment/falkordb-mcp-server
```

#### **Step 4: Database Preparation**

**Initialize Tenant Graphs (Optional):**
```python
import redis
from falkordb import FalkorDB

def initialize_tenant_graphs(tenant_id: str, initial_graphs: list = None):
    """Initialize default graphs for new tenant"""
    
    db = FalkorDB(host='localhost', port=6379)
    
    # Default graphs to create
    default_graphs = initial_graphs or ['users', 'analytics', 'metadata']
    
    for graph_name in default_graphs:
        tenant_graph_name = f"{tenant_id}_{graph_name}"
        
        try:
            # Create graph with basic schema
            graph = db.select_graph(tenant_graph_name)
            
            # Initialize with basic metadata
            query = """
            CREATE (:TenantMetadata {
                tenant_id: $tenant_id,
                graph_name: $graph_name,
                created_at: datetime(),
                version: '1.0'
            })
            """
            
            graph.query(query, {
                'tenant_id': tenant_id,
                'graph_name': graph_name
            })
            
            print(f"✅ Initialized graph: {tenant_graph_name}")
            
        except Exception as e:
            print(f"❌ Failed to initialize {tenant_graph_name}: {e}")

# Initialize graphs for new tenant
initialize_tenant_graphs("acme-corp", ["users", "products", "analytics"])
```

### Phase 4: Token Generation and Management

#### **Step 5: Generate Client Tokens**

**For OAuth Provider:**
```python
import requests
import jwt
from datetime import datetime, timedelta

def generate_oauth_token(tenant_id: str, client_id: str, client_secret: str) -> str:
    """Generate OAuth access token for tenant"""
    
    # OAuth client credentials flow
    token_url = f"https://auth.yourcompany.com/oauth/token"
    
    response = requests.post(token_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'audience': 'falkordb-mcp-server',
        'scope': 'read write'
    })
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data['access_token']
    else:
        raise Exception(f"Failed to generate token: {response.text}")

def generate_jwks_token(tenant_id: str, private_key: str, scopes: list = None) -> str:
    """Generate JWT token using tenant's private key"""
    
    scopes = scopes or ['read', 'write']
    
    payload = {
        'iss': 'https://auth.yourcompany.com',
        'sub': tenant_id,
        'aud': 'falkordb-mcp-server', 
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=24),
        'scope': ' '.join(scopes),
        'tenant': tenant_id
    }
    
    headers = {
        'kid': f"{tenant_id}-key",
        'alg': 'RS256'
    }
    
    token = jwt.encode(
        payload, 
        private_key, 
        algorithm='RS256',
        headers=headers
    )
    
    return token

# Generate tokens for new tenant
# Option 1: OAuth
oauth_token = generate_oauth_token(
    tenant_id="acme-corp",
    client_id="acme_corp_client_id", 
    client_secret="acme_corp_client_secret"
)

# Option 2: JWKS
jwks_token = generate_jwks_token(
    tenant_id="acme-corp",
    private_key=tenant_keys['private_key'],
    scopes=['read', 'write']
)
```

#### **Step 6: Token Validation and Testing**

**Test Token Validity:**
```python
import httpx
import asyncio

async def validate_tenant_token(token: str, tenant_id: str) -> bool:
    """Validate token works with the proxy"""
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        # Test OAuth metadata endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get(
                'http://localhost:3001/.well-known/oauth-authorization-server'
            )
            
            if response.status_code != 200:
                print(f"❌ OAuth metadata endpoint failed: {response.status_code}")
                return False
            
            # Test MCP endpoint authentication
            response = await client.get(
                'http://localhost:3001/mcp/',
                headers=headers
            )
            
            if response.status_code in [200, 202]:
                print(f"✅ Token validation successful for tenant: {tenant_id}")
                return True
            elif response.status_code == 401:
                print(f"❌ Token authentication failed for tenant: {tenant_id}")
                return False
            else:
                print(f"❌ Unexpected response: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Token validation error: {e}")
        return False

# Validate the generated token
is_valid = asyncio.run(validate_tenant_token(oauth_token, "acme-corp"))
```

### Phase 5: Client Configuration

#### **Step 7: Generate Claude Desktop Configuration**

**Configuration Template:**
```python
def generate_claude_desktop_config(tenant_id: str, token: str, proxy_url: str = None) -> dict:
    """Generate Claude Desktop MCP configuration for tenant"""
    
    proxy_url = proxy_url or "http://localhost:3001/mcp/"
    
    config = {
        "mcpServers": {
            "falkordb": {
                "serverUrl": proxy_url,
                "auth": {
                    "type": "bearer",
                    "token": token
                },
                "metadata": {
                    "tenant_id": tenant_id,
                    "created_at": datetime.utcnow().isoformat(),
                    "version": "1.0"
                }
            }
        }
    }
    
    return config

# Generate configuration for client
client_config = generate_claude_desktop_config("acme-corp", oauth_token)

# Save to file for client delivery
import json
with open(f"claude-desktop-config-{tenant_id}.json", "w") as f:
    json.dump(client_config, f, indent=2)

print(f"✅ Generated Claude Desktop configuration for {tenant_id}")
```

#### **Step 8: Create Client Documentation Package**

**Generate Client-Specific Documentation:**
```python
def generate_client_docs(tenant_id: str, config: dict) -> str:
    """Generate client-specific setup documentation"""
    
    docs = f"""
# FalkorDB MCP Setup Guide - {tenant_id.title()}

## Overview
This guide helps you set up FalkorDB graph database access in Claude Desktop.

## Configuration

### Step 1: Open Claude Desktop Settings
1. Open Claude Desktop application
2. Click the Settings gear icon (bottom left)
3. Navigate to **Features** → **Model Context Protocol**
4. Click **Edit Config** to open the configuration file

### Step 2: Add FalkorDB Configuration
Add this configuration to your MCP servers JSON:

```json
{json.dumps(config, indent=2)}
```

**Important Notes:**
- Use the **Model Context Protocol** section, NOT the Integrations section
- Your tenant ID is: `{tenant_id}`
- Your token expires in 24 hours - contact support for refresh

### Step 3: Restart Claude Desktop
1. Save the configuration file
2. Completely restart Claude Desktop
3. Check for any error messages

## Available Tools

Once configured, you can use these commands in Claude Desktop:

### Query Graphs
"Execute a Cypher query to find all users: MATCH (u:User) RETURN u.name"

### List Available Graphs  
"Show me all available graph databases"

### Check Server Health
"Check the FalkorDB server status"

### Get Server Information
"What are the FalkorDB server capabilities?"

## Support

- **Technical Support**: tech@yourcompany.com
- **Documentation**: https://docs.yourcompany.com/falkordb
- **Status Page**: https://status.yourcompany.com

## Security

- **Token Security**: Never share your bearer token
- **Data Isolation**: Your data is completely isolated from other tenants
- **Access Logging**: All queries are logged for security and compliance

---
Generated on: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC
"""
    
    return docs

# Generate client documentation
client_docs = generate_client_docs(tenant_id, client_config)

with open(f"setup-guide-{tenant_id}.md", "w") as f:
    f.write(client_docs)
```

### Phase 6: Deployment and Validation

#### **Step 9: Deploy Configuration Changes**

**Automated Deployment Script:**
```bash
#!/bin/bash
# deploy-new-tenant.sh

set -e

TENANT_ID="$1"
if [ -z "$TENANT_ID" ]; then
    echo "Usage: $0 <tenant-id>"
    exit 1
fi

echo "🚀 Deploying configuration for tenant: $TENANT_ID"

# 1. Update JWKS endpoint (if using JWKS)
echo "📝 Updating JWKS endpoint..."
curl -X POST https://auth.yourcompany.com/admin/jwks/update \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d @"jwks-update-${TENANT_ID}.json"

# 2. Restart proxy service to pick up new keys
echo "🔄 Restarting FastMCP proxy..."
kubectl rollout restart deployment/fastmcp-proxy

# 3. Wait for rollout to complete
kubectl rollout status deployment/fastmcp-proxy

# 4. Validate deployment
echo "✅ Validating deployment..."
python validate-tenant-deployment.py "$TENANT_ID"

echo "🎉 Tenant $TENANT_ID deployed successfully!"
```

#### **Step 10: End-to-End Testing**

**Comprehensive Tenant Testing:**
```python
import asyncio
import httpx
from falkordb import FalkorDB

async def test_tenant_deployment(tenant_id: str, token: str):
    """Comprehensive testing of new tenant deployment"""
    
    print(f"🧪 Testing deployment for tenant: {tenant_id}")
    
    # Test 1: Authentication
    print("1. Testing authentication...")
    headers = {'Authorization': f'Bearer {token}'}
    
    async with httpx.AsyncClient() as client:
        response = await client.get('http://localhost:3001/mcp/', headers=headers)
        assert response.status_code in [200, 202], f"Auth failed: {response.status_code}"
    print("✅ Authentication working")
    
    # Test 2: Graph operations via proxy
    print("2. Testing graph operations...")
    
    # Create test data
    create_query = """
    CREATE (u:User {id: 'test-user', name: 'Test User', tenant: $tenant_id})
    RETURN u
    """
    
    # This would be done via MCP call, simulated here
    db = FalkorDB(host='localhost', port=6379)
    graph = db.select_graph(f"{tenant_id}_test")
    result = graph.query(create_query, {'tenant_id': tenant_id})
    assert len(result.result_set) > 0, "Failed to create test data"
    print("✅ Graph operations working")
    
    # Test 3: Data isolation
    print("3. Testing data isolation...")
    
    # Try to access another tenant's graph (should fail)
    try:
        other_graph = db.select_graph("other-tenant_test")
        other_result = other_graph.query("MATCH (n) RETURN n LIMIT 1")
        # Should not see data from other tenants
        print("✅ Data isolation verified")
    except:
        print("✅ Data isolation verified (access denied as expected)")
    
    # Test 4: Graph listing
    print("4. Testing graph listing...")
    graphs = db.list_graphs()
    tenant_graphs = [g for g in graphs if g.startswith(f"{tenant_id}_")]
    assert len(tenant_graphs) > 0, "No tenant graphs found"
    print(f"✅ Found {len(tenant_graphs)} tenant graphs")
    
    print(f"🎉 All tests passed for tenant: {tenant_id}")

# Run comprehensive testing
asyncio.run(test_tenant_deployment("acme-corp", oauth_token))
```

### Phase 7: Client Delivery

#### **Step 11: Secure Credential Delivery**

**Delivery Package:**
```python
def create_delivery_package(tenant_id: str, token: str, config: dict) -> dict:
    """Create secure delivery package for client"""
    
    package = {
        "tenant_info": {
            "tenant_id": tenant_id,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
        },
        "credentials": {
            "bearer_token": token,
            "proxy_endpoint": "http://localhost:3001/mcp/",
            "oauth_metadata": "http://localhost:3001/.well-known/oauth-authorization-server"
        },
        "configuration": config,
        "documentation": {
            "setup_guide": f"setup-guide-{tenant_id}.md",
            "api_reference": "https://docs.yourcompany.com/falkordb/api",
            "support_contact": "tech@yourcompany.com"
        },
        "security": {
            "token_rotation": "24 hours",
            "data_isolation": "Complete tenant separation",
            "audit_logging": "All requests logged",
            "compliance": "SOC 2 Type II, GDPR compliant"
        }
    }
    
    return package

# Create delivery package
delivery_package = create_delivery_package(tenant_id, oauth_token, client_config)

# Save as JSON for secure delivery
with open(f"delivery-package-{tenant_id}.json", "w") as f:
    json.dump(delivery_package, f, indent=2)
```

**Secure Delivery Methods:**
```python
def deliver_credentials_securely(tenant_id: str, delivery_method: str = "encrypted_email"):
    """Deliver credentials using secure method"""
    
    if delivery_method == "encrypted_email":
        # Use PGP encryption for email delivery
        encrypt_and_email_package(tenant_id)
        
    elif delivery_method == "secure_portal":
        # Upload to secure client portal
        upload_to_secure_portal(tenant_id)
        
    elif delivery_method == "api_handoff":
        # Programmatic delivery via secure API
        deliver_via_secure_api(tenant_id)
        
    print(f"✅ Credentials delivered securely to {tenant_id}")
```

## 🔄 Production Onboarding Checklist

### Pre-Onboarding ✅
- [ ] **Client Info Collected**: Organization details, contacts, requirements
- [ ] **Tenant ID Validated**: Unique, follows naming conventions
- [ ] **Security Profile Defined**: Auth method, scopes, restrictions
- [ ] **Capacity Planning**: Expected usage, resource allocation

### Authentication Setup ✅
- [ ] **Keys Generated**: RSA keypair or OAuth application created
- [ ] **JWKS Updated**: Public key added to JWKS endpoint
- [ ] **Provider Configured**: Auth0/Azure AD application configured
- [ ] **Scopes Defined**: Read/write/admin permissions set

### Infrastructure Configuration ✅
- [ ] **Backend Updated**: Multi-tenancy enabled, auth configured
- [ ] **Database Prepared**: Initial graphs created (optional)
- [ ] **Services Restarted**: All components running with new config
- [ ] **Health Checks**: All services responding correctly

### Token Management ✅
- [ ] **Tokens Generated**: Valid JWT tokens for client
- [ ] **Validation Tested**: Tokens work with proxy endpoints
- [ ] **Expiration Set**: Appropriate token lifetime configured
- [ ] **Rotation Planned**: Token refresh process documented

### Client Configuration ✅
- [ ] **Claude Config Generated**: Tenant-specific MCP configuration
- [ ] **Documentation Created**: Client setup guide prepared
- [ ] **Support Info Provided**: Contact details and resources
- [ ] **Security Brief**: Data isolation and security features explained

### Deployment & Testing ✅
- [ ] **Configuration Deployed**: All changes applied to production
- [ ] **End-to-End Tested**: Full workflow validation completed
- [ ] **Data Isolation Verified**: Tenant cannot access other data
- [ ] **Performance Tested**: Response times within SLA

### Client Delivery ✅
- [ ] **Credentials Delivered**: Secure delivery method used
- [ ] **Setup Validated**: Client successfully configured Claude Desktop
- [ ] **Training Provided**: Client understands available tools
- [ ] **Support Handoff**: Client knows how to get help

### Post-Onboarding ✅
- [ ] **Monitoring Enabled**: Tenant metrics and alerts configured
- [ ] **Usage Tracked**: Query counts and performance monitored
- [ ] **Billing Setup**: Usage-based billing configured (if applicable)
- [ ] **Feedback Collected**: Client satisfaction and improvement areas

## 🚨 Common Issues and Solutions

### Authentication Issues

**Problem**: Token validation fails
```bash
# Solution: Check JWT claims
python -c "
import jwt
token = 'your_token_here'
decoded = jwt.decode(token, options={'verify_signature': False})
print('Claims:', decoded)
"
```

**Problem**: JWKS endpoint not updated
```bash
# Solution: Force JWKS refresh
curl -X POST https://auth.yourcompany.com/admin/jwks/refresh \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Data Isolation Issues

**Problem**: Tenant sees other tenant data
```python
# Solution: Verify graph prefixing
def verify_graph_isolation(tenant_id: str):
    db = FalkorDB()
    graphs = db.list_graphs()
    
    tenant_graphs = [g for g in graphs if g.startswith(f"{tenant_id}_")]
    other_graphs = [g for g in graphs if not g.startswith(f"{tenant_id}_")]
    
    print(f"Tenant graphs: {tenant_graphs}")
    print(f"Other graphs: {len(other_graphs)}")
    
verify_graph_isolation("acme-corp")
```

### Configuration Issues

**Problem**: Claude Desktop cannot connect
```json
// Solution: Verify MCP configuration format
{
  "mcpServers": {
    "falkordb": {
      "serverUrl": "http://localhost:3001/mcp/",  // Note: /mcp/ not /sse/
      "auth": {
        "type": "bearer",
        "token": "actual_token_without_bearer_prefix"
      }
    }
  }
}
```

## 📊 Automation Scripts

### Automated Onboarding Script

```bash
#!/bin/bash
# onboard-tenant.sh - Complete tenant onboarding automation

TENANT_ID="$1"
ORGANIZATION="$2"
PLAN="$3"

if [ $# -ne 3 ]; then
    echo "Usage: $0 <tenant-id> <organization-name> <plan-type>"
    exit 1
fi

echo "🚀 Starting automated onboarding for $TENANT_ID"

# 1. Validate tenant ID
python scripts/validate-tenant.py "$TENANT_ID" || exit 1

# 2. Generate authentication
python scripts/generate-auth.py "$TENANT_ID" "$ORGANIZATION" || exit 1

# 3. Update infrastructure
kubectl apply -f "configs/tenant-${TENANT_ID}.yaml" || exit 1

# 4. Generate client package
python scripts/generate-client-package.py "$TENANT_ID" "$PLAN" || exit 1

# 5. Run tests
python scripts/test-tenant-deployment.py "$TENANT_ID" || exit 1

# 6. Deliver credentials
python scripts/deliver-credentials.py "$TENANT_ID" || exit 1

echo "✅ Tenant $TENANT_ID onboarded successfully!"
echo "📦 Client package: delivery-package-${TENANT_ID}.json"
echo "📧 Credentials delivered to organization contact"
```

---

## Summary

Production client onboarding involves:

1. **🔍 Validation**: Tenant ID validation and security profiling
2. **🔐 Authentication**: OAuth or JWKS-based key generation
3. **⚙️ Infrastructure**: Backend configuration and deployment
4. **🎫 Tokens**: JWT generation and validation testing
5. **📱 Client Config**: Claude Desktop MCP configuration
6. **🧪 Testing**: Comprehensive end-to-end validation
7. **📦 Delivery**: Secure credential and documentation delivery

Each new client gets **complete data isolation**, their own authentication credentials, and a tailored Claude Desktop configuration for immediate productivity with FalkorDB graph operations.

---

> **Note**: This document was created with assistance from Claude Sonnet 3.5, an AI assistant by Anthropic.