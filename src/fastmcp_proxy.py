import os
import httpx
import uvicorn
from typing import Dict, Any, Optional
from fastmcp import FastMCP, Context
from fastmcp.server.auth import BearerAuthProvider
from fastmcp.server.auth.providers.bearer import RSAKeyPair

# Configuration
BACKEND_URL = os.environ.get("FALKORDB_MCPSERVER_URL", "http://localhost:3000")
API_KEY = os.environ.get("MCP_API_KEY", "dev-api-key")
PROXY_PORT = int(os.environ.get("PROXY_PORT", "3001"))
PROXY_HOST = os.environ.get("PROXY_HOST", "0.0.0.0")

# Generate development RSA key pair for authentication
# In production, use proper OAuth provider or pre-generated keys
key_pair = RSAKeyPair.generate()

# Configure Bearer Token Authentication
auth = BearerAuthProvider(
    public_key=key_pair.public_key,
    issuer="https://falkordb-fastmcp-proxy",
    audience="falkordb-mcp-server",
    algorithm="RS256"
)

# Generate a development token for testing
def generate_test_token():
    """Generate a test token for development purposes"""
    return key_pair.create_token(
        subject="dev-user",
        issuer="https://falkordb-fastmcp-proxy",
        audience="falkordb-mcp-server",
        scopes=["read", "write"],
        expires_in_seconds=3600
    )

# Create FastMCP server with authentication
mcp = FastMCP(
    name="FalkorDB FastMCP Proxy",
    auth=auth
)

# TODO: Add OAuth 2.1 endpoints via custom routes
# Currently having issues with custom_route decorator - will implement via FastAPI directly if needed

# HTTP client for backend communication
http_client = httpx.AsyncClient(timeout=30.0)

async def call_backend(method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Call the FalkorDB MCP Server backend API"""
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

@mcp.tool
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
        
        # Format response for Claude Desktop
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

@mcp.tool
async def falkordb_list_graphs(ctx: Context) -> str:
    """List all available graphs in the FalkorDB instance"""
    try:
        result = await call_backend("GET", "/api/mcp/graphs")
        
        if "data" in result:
            graphs = result["data"]
            metadata = result.get("metadata", {})
            
            if graphs:
                graph_list = []
                for graph in graphs:
                    if isinstance(graph, dict) and "name" in graph:
                        graph_list.append(f"- {graph['name']}")
                    else:
                        graph_list.append(f"- {graph}")
                
                response_text = f"Available graphs ({metadata.get('count', len(graphs))}):\n\n"
                response_text += "\n".join(graph_list)
            else:
                response_text = "No graphs found in the FalkorDB instance."
        else:
            response_text = "Unexpected response format from backend."
        
        return response_text
        
    except Exception as e:
        return f"Error listing graphs: {str(e)}"

@mcp.tool
async def falkordb_server_info(ctx: Context) -> str:
    """Get FalkorDB server metadata and capabilities"""
    try:
        result = await call_backend("GET", "/api/mcp/metadata")
        
        provider = result.get("provider", "Unknown")
        version = result.get("version", "Unknown")
        capabilities = result.get("capabilities", [])
        
        response_text = f"**FalkorDB Server Information:**\n\n"
        response_text += f"- Provider: {provider}\n"
        response_text += f"- Version: {version}\n"
        response_text += f"- Capabilities: {', '.join(capabilities) if capabilities else 'None listed'}"
        
        return response_text
        
    except Exception as e:
        return f"Error getting server info: {str(e)}"

@mcp.tool
async def falkordb_health(ctx: Context) -> str:
    """Check FalkorDB server health status"""
    try:
        result = await call_backend("GET", "/health")
        
        status = result.get("status", "unknown")
        services = result.get("services", {})
        database = services.get("database", {})
        
        response_text = f"**FalkorDB Health Status:**\n\n"
        response_text += f"- Overall Status: {status}\n"
        response_text += f"- Database Connected: {database.get('connected', 'Unknown')}\n"
        response_text += f"- Database Latency: {database.get('latency', 'Unknown')}ms"
        
        return response_text
        
    except Exception as e:
        return f"Error checking health: {str(e)}"

if __name__ == "__main__":
    print("🚀 Starting FalkorDB FastMCP Proxy Server")
    print(f"📡 Backend URL: {BACKEND_URL}")
    print(f"🔐 Authentication: Bearer Token (Development)")
    print(f"🌐 Server: http://{PROXY_HOST}:{PROXY_PORT}")
    
    # Print test token for development
    test_token = generate_test_token()
    print(f"\n🔑 Development Test Token:")
    print(f"Bearer {test_token}")
    print(f"\n📋 Use this token in Claude Desktop MCP configuration:")
    print(f'  "auth": {{"type": "bearer", "token": "{test_token}"}}')
    print(f"\n📍 OAuth Authorization Server Metadata:")
    print(f"   http://{PROXY_HOST}:{PROXY_PORT}/.well-known/oauth-authorization-server")
    
    # Try streamable-http transport instead of deprecated SSE
    print(f"\n🔧 Using streamable-http transport for Docker compatibility")
    mcp.run(
        transport="streamable-http",
        host=PROXY_HOST,
        port=PROXY_PORT
    )