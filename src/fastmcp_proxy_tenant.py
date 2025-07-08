import os
import httpx
import uvicorn
from typing import Dict, Any, Optional
from fastmcp import FastMCP, Context
from fastmcp.server.auth import BearerAuthProvider
from fastmcp.server.auth.providers.bearer import RSAKeyPair
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
from urllib.parse import urlparse, parse_qs
import jwt
import hashlib

# Configuration
BACKEND_URL = os.environ.get("FALKORDB_MCPSERVER_URL", "http://localhost:3000")
API_KEY = os.environ.get("MCP_API_KEY", "dev-api-key")
PROXY_PORT = int(os.environ.get("PROXY_PORT", "3001"))
PROXY_HOST = os.environ.get("PROXY_HOST", "0.0.0.0")
PUBLIC_PORT = int(os.environ.get("PUBLIC_PORT", "3003"))
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# Generate development RSA key pair for authentication
key_pair = RSAKeyPair.generate()

# Configure Bearer Token Authentication for authenticated endpoint
auth = BearerAuthProvider(
    public_key=key_pair.public_key,
    issuer="https://falkordb-fastmcp-proxy",
    audience="falkordb-mcp-server",
    algorithm="RS256"
)

def generate_test_token():
    """Generate a test token for development purposes"""
    return key_pair.create_token(
        subject="dev-user",
        issuer="https://falkordb-fastmcp-proxy",
        audience="falkordb-mcp-server",
        scopes=["read", "write"],
        expires_in_seconds=3600
    )

def generate_tenant_token(tenant_id: str, user_id: str = "user") -> str:
    """Generate a URL-safe token for tenant authentication"""
    import time
    payload = {
        "tenant": tenant_id,
        "user": user_id,
        "exp": int(time.time()) + 3600  # 1 hour expiry
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_tenant_token(token: str) -> Dict[str, str]:
    """Verify and decode tenant token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {
            "tenant": payload.get("tenant", "default"),
            "user": payload.get("user", "anonymous")
        }
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid tenant token")

# Create authenticated FastMCP server (existing)
mcp_auth = FastMCP(
    name="FalkorDB FastMCP Proxy (Authenticated)",
    auth=auth
)

# Create custom FastAPI app for tenant-aware public endpoint
app_public = FastAPI(title="FalkorDB FastMCP Proxy (Tenant-Aware)")

# HTTP client for backend communication
http_client = httpx.AsyncClient(timeout=30.0)

class TenantContext:
    def __init__(self, tenant_id: str, user_id: str):
        self.tenant = tenant_id
        self.user = user_id

async def call_backend_with_tenant(method: str, endpoint: str, tenant_context: TenantContext, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Call the FalkorDB MCP Server backend API with tenant context"""
    headers = {
        "x-api-key": API_KEY,
        "x-tenant-id": tenant_context.tenant,
        "x-user-id": tenant_context.user
    }
    if data:
        headers["Content-Type"] = "application/json"
    
    url = f"{BACKEND_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = await http_client.get(url, headers=headers)
        elif method.upper() == "POST":
            response = await http_client.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        raise Exception(f"Backend API error: {e}")

async def call_backend(method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Call the FalkorDB MCP Server backend API (for authenticated endpoint)"""
    headers = {"x-api-key": API_KEY}
    if data:
        headers["Content-Type"] = "application/json"
    
    url = f"{BACKEND_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = await http_client.get(url, headers=headers)
        elif method.upper() == "POST":
            response = await http_client.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        raise Exception(f"Backend API error: {e}")

# Middleware to extract tenant context from URL for public endpoint
@app_public.middleware("http")
async def tenant_auth_middleware(request: Request, call_next):
    # Only apply to SSE endpoints
    if request.url.path.startswith("/sse/") or request.url.path.startswith("/mcp/"):
        # Extract token from query parameters
        token = request.query_params.get("token")
        if not token:
            return Response("Missing tenant token in URL", status_code=401)
        
        try:
            tenant_info = verify_tenant_token(token)
            # Store tenant context in request state
            request.state.tenant_context = TenantContext(
                tenant_info["tenant"], 
                tenant_info["user"]
            )
        except HTTPException as e:
            return Response(f"Authentication failed: {e.detail}", status_code=e.status_code)
    
    response = await call_next(request)
    return response

# Create tenant-aware MCP server using FastMCP with custom FastAPI app
mcp_public = FastMCP(
    name="FalkorDB FastMCP Proxy (Tenant-Aware)",
    app=app_public  # Use our custom FastAPI app with middleware
)

# Define tools for authenticated server (no tenant context)
@mcp_auth.tool
async def falkordb_query(
    ctx: Context,
    graphName: str,
    query: str,
    parameters: Optional[Dict[str, Any]] = None
) -> str:
    """Execute a Cypher query against a FalkorDB graph"""
    if parameters is None:
        parameters = {}
    
    try:
        result = await call_backend("POST", "/api/mcp/context", {
            "graphName": graphName,
            "query": query,
            "parameters": parameters
        })
        
        # Format response
        if "data" in result and "data" in result["data"]:
            data_results = result["data"]["data"]
            metadata_info = result.get("metadata", {})
            
            if data_results:
                formatted_results = []
                for i, row in enumerate(data_results, 1):
                    row_text = f"**Result {i}:**\n"
                    for key, value in row.items():
                        row_text += f"- {key}: {value}\n"
                    formatted_results.append(row_text)
                
                response_text = f"Query executed successfully on graph '{graphName}':\n\n"
                response_text += "\n".join(formatted_results)
                response_text += f"\n**Metadata:**\n- Query time: {metadata_info.get('queryTime', 'N/A')}ms\n"
                response_text += f"- Provider: {metadata_info.get('provider', 'N/A')}"
            else:
                response_text = f"Query executed successfully on graph '{graphName}' with no results returned."
        else:
            response_text = f"Query executed on graph '{graphName}' but unexpected response format."
        
        return response_text
        
    except Exception as e:
        return f"Error executing query on graph '{graphName}': {str(e)}"

# Define tenant-aware tools for public server
@mcp_public.tool
async def falkordb_query_tenant(
    ctx: Context,
    graphName: str,
    query: str,
    parameters: Optional[Dict[str, Any]] = None
) -> str:
    """Execute a Cypher query against a FalkorDB graph (tenant-aware)"""
    if parameters is None:
        parameters = {}
    
    # Get tenant context from request state
    tenant_context = getattr(ctx.request.state, 'tenant_context', None)
    if not tenant_context:
        return "Error: No tenant context available"
    
    # Prefix graph name with tenant ID for isolation
    tenant_graph_name = f"{tenant_context.tenant}_{graphName}"
    
    try:
        result = await call_backend_with_tenant("POST", "/api/mcp/context", tenant_context, {
            "graphName": tenant_graph_name,
            "query": query,
            "parameters": parameters
        })
        
        # Format response
        if "data" in result and "data" in result["data"]:
            data_results = result["data"]["data"]
            metadata_info = result.get("metadata", {})
            
            if data_results:
                formatted_results = []
                for i, row in enumerate(data_results, 1):
                    row_text = f"**Result {i}:**\n"
                    for key, value in row.items():
                        row_text += f"- {key}: {value}\n"
                    formatted_results.append(row_text)
                
                response_text = f"Query executed successfully on graph '{graphName}' (tenant: {tenant_context.tenant}):\n\n"
                response_text += "\n".join(formatted_results)
                response_text += f"\n**Metadata:**\n- Query time: {metadata_info.get('queryTime', 'N/A')}ms\n"
                response_text += f"- Provider: {metadata_info.get('provider', 'N/A')}\n"
                response_text += f"- Tenant: {tenant_context.tenant}"
            else:
                response_text = f"Query executed successfully on tenant graph '{tenant_context.tenant}_{graphName}' with no results returned."
        else:
            response_text = f"Query executed on tenant graph but unexpected response format."
        
        return response_text
        
    except Exception as e:
        return f"Error executing query on tenant graph '{tenant_context.tenant}_{graphName}': {str(e)}"

# Add similar tenant-aware versions for other tools...

if __name__ == "__main__":
    print("🚀 Starting FalkorDB FastMCP Proxy Servers")
    print(f"📡 Backend URL: {BACKEND_URL}")
    print(f"🔐 Authenticated Server: http://{PROXY_HOST}:{PROXY_PORT}")
    print(f"🏢 Tenant-Aware Server: http://{PROXY_HOST}:{PUBLIC_PORT}")
    
    # Print test tokens
    test_token = generate_test_token()
    print(f"\n🔑 Development Test Token (Authenticated):")
    print(f"Bearer {test_token}")
    
    # Generate sample tenant tokens
    tenant_tokens = {
        "acme": generate_tenant_token("acme", "admin"),
        "widgets": generate_tenant_token("widgets", "user1")
    }
    
    print(f"\n🏢 Sample Tenant Tokens:")
    for tenant, token in tenant_tokens.items():
        print(f"  {tenant}: {token}")
        print(f"  URL: http://{PROXY_HOST}:{PUBLIC_PORT}/sse/?token={token}")
    
    print(f"\n📋 opencode configuration examples:")
    for tenant, token in tenant_tokens.items():
        print(f'  {tenant}: "url": "http://{PROXY_HOST}:{PUBLIC_PORT}/sse/?token={token}"')
    
    # Start authenticated server only for now
    mcp_auth.run(
        transport="streamable-http",
        host=PROXY_HOST,
        port=PROXY_PORT
    )