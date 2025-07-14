# opencode Integration Guide

This guide shows how to integrate the FalkorDB FastMCP Proxy with [opencode](https://opencode.ai), enabling remote access to FalkorDB graph databases directly from opencode's command line interface.

## Quick Setup

### 1. Add Remote MCP Server to opencode

Create or update your `opencode.json` configuration file:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "falkordb": {
      "type": "remote",
      "url": "http://localhost:3001/sse/",
      "enabled": true,
      "headers": {
        "Authorization": "Bearer <JWT_TOKEN>"
      }
    }
  }
}
```

**Note**: This configuration assumes opencode supports custom headers for remote MCP servers. If opencode doesn't support the `headers` field, you may need to use a different authentication method.

### 2. Get Authentication Token

Contact your FalkorDB proxy administrator to obtain a JWT authentication token, or if running locally:

```bash
# Start local proxy to generate development token
python server/fastmcp_proxy.py

# Copy the Bearer token from output (without "Bearer " prefix)
# Example output: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...
```

### 3. Configure with Token

Replace `<JWT_TOKEN>` in your opencode.json with your actual JWT token:

```json
{
  "$schema": "https://opencode.ai/config.json", 
  "mcp": {
    "falkordb": {
      "type": "remote",
      "url": "http://localhost:3001/sse/",
      "enabled": true,
      "headers": {
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."
      }
    }
  }
}
```

## Alternative Configuration (if headers not supported)

If opencode doesn't support custom headers, try this basic configuration:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "falkordb": {
      "type": "remote", 
      "url": "http://localhost:3001/sse/",
      "enabled": true
    }
  }
}
```

**Note**: This will only work if the FastMCP proxy is configured without authentication, which is not recommended for production use.

## Available Tools

Once configured, opencode will have access to these FalkorDB tools:

- **falkordb_query** - Execute Cypher queries against FalkorDB graphs
- **falkordb_list_graphs** - List available FalkorDB graphs  
- **falkordb_server_info** - Get FalkorDB server information and capabilities
- **falkordb_health** - Check FalkorDB server health status

## Example Usage

Ask opencode to use FalkorDB tools in natural language:

```
Show me all graphs available in FalkorDB
```

```
Create a graph called "social" and add some nodes representing users
```

```  
Query the social graph to find all users connected to each other
```

## Local Development Setup

For local development with Docker Compose:

1. **Start the FalkorDB stack:**
```bash
docker-compose up --build
```

2. **Start the FastMCP proxy:**
```bash
python server/fastmcp_proxy.py
```

3. **Copy the token from proxy output:**
```
🔑 Development Bearer Token (Required for ALL connections):
Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...
```

4. **Configure opencode.json:**
```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "falkordb-local": {
      "type": "remote",
      "url": "http://localhost:3001/sse/",
      "enabled": true,
      "headers": {
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."
      }
    }
  }
}
```

## Authentication Requirements

The FalkorDB FastMCP Proxy uses JWT tokens for authentication with these requirements:

- **Algorithm**: RSA-256 (RS256)
- **Issuer**: `https://fastmcp-proxy.dev` (configurable)
- **Audience**: `falkordb-proxy` (configurable)  
- **Subject**: Tenant identifier for multi-tenant setups
- **Scopes**: `["read", "write"]` for full access

## Troubleshooting

### Common Issues

**"Connection refused" errors:**
- Verify the proxy server is running: `python server/fastmcp_proxy.py`
- Check Docker services: `docker-compose ps`
- Ensure port 3001 is accessible

**"Authentication failed" errors:**  
- Verify the JWT token is correctly formatted
- Check token expiration time (development tokens expire in 1 hour)
- Ensure opencode supports custom headers in remote MCP configuration

**"No tools available" errors:**
- Verify opencode.json is in the correct location
- Check JSON syntax is valid
- Ensure the MCP server is enabled (`"enabled": true`)
- Restart opencode after configuration changes

### opencode Configuration Location

The opencode.json file should be located in:
- **Linux/macOS**: `~/.config/opencode/opencode.json`
- **Windows**: `%APPDATA%/opencode/opencode.json`

### Debug Mode

Enable debug logging in opencode to see MCP communication:

```bash
opencode --debug
```

### Server Health Check

Test proxy server connectivity:

```bash
# Without authentication (will fail if auth is required)
curl http://localhost:3001/health

# With authentication  
curl -H "Authorization: Bearer <JWT_TOKEN>" http://localhost:3001/health
```

## Current Limitations

1. **opencode Header Support**: This integration assumes opencode supports custom headers for remote MCP servers. If this feature is not available, authentication may not work properly.

2. **Authentication Method**: The current setup uses Bearer token authentication. If opencode doesn't support custom headers, alternative authentication methods may be needed.

3. **Token Management**: Development tokens expire in 1 hour. For production use, implement proper token management.

## Next Steps

1. **Verify opencode Headers**: Test if opencode actually supports the `headers` field for remote MCP servers
2. **Alternative Auth**: If headers aren't supported, investigate URL-based authentication or other methods
3. **Production Deployment**: Set up proper token management for production environments
4. **Documentation Updates**: Update this guide based on actual opencode behavior

For additional support, see the [main documentation](../README.md) or the [FastMCP proxy documentation](../technical-guides/).