# opencode Integration Guide

This guide shows how to integrate the FalkorDB FastMCP Proxy with [opencode](https://opencode.ai) using a local client proxy approach.

## Quick Setup

### 1. Architecture Overview

Since opencode doesn't support custom headers for remote MCP servers, we use the same local client pattern that works with Claude Desktop:

```
opencode → Local Client (uvx) → Remote FastMCP Proxy (Bearer auth) → FalkorDB MCPServer → FalkorDB
```

This approach:
- ✅ Works with opencode's local MCP server support
- ✅ Uses the same proven client proxy as Claude Desktop  
- ✅ Maintains full authentication and security
- ✅ Supports all FastMCP proxy features

### 2. opencode Configuration

Create or update your `opencode.json` configuration file:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "falkordb": {
      "type": "local",
      "command": [
        "uvx", 
        "--from", 
        "git+https://github.com/Dragonatorul/FalkorDB-FastMCP-Proxy", 
        "python", 
        "-m", 
        "client.claude_desktop_proxy"
      ],
      "environment": {
        "PROXY_URL": "http://localhost:3001/sse/",
        "PROXY_TOKEN": "YOUR_JWT_TOKEN_HERE"
      },
      "enabled": true
    }
  }
}
```

### 3. Get Authentication Token

Start the FastMCP proxy server to generate a development token:

```bash
python server/fastmcp_proxy.py
```

Copy the JWT token from the "opencode Configuration" section in the server output (the `PROXY_TOKEN` value).

### 4. Configuration Location

Place your `opencode.json` file in the appropriate location:

- **Linux/macOS**: `~/.config/opencode/opencode.json`
- **Windows**: `%APPDATA%/opencode/opencode.json`

## How It Works

1. **opencode** runs the local client using `uvx` (Python package runner)
2. **uvx** fetches and runs the client directly from the GitHub repository
3. **Local Client** connects to the remote FastMCP proxy using Bearer authentication
4. **FastMCP Proxy** forwards requests to the FalkorDB MCPServer backend
5. **Authentication** is handled transparently by the local client

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

For local development:

1. **Start the FalkorDB stack:**
```bash
docker-compose up --build
```

2. **Start the FastMCP proxy:**
```bash
python server/fastmcp_proxy.py
```

3. **Copy the configuration from server output:**
The server will display the complete opencode configuration with the correct token.

4. **Save to opencode.json:**
Copy the configuration to your opencode config file location.

5. **Restart opencode:**
```bash
opencode
```

## Authentication & Security

- **JWT Tokens**: Uses the same secure JWT authentication as Claude Desktop
- **Multi-tenant**: Supports tenant isolation via JWT subject claims
- **Encrypted**: All communication uses HTTPS/Bearer authentication
- **Token Expiry**: Development tokens expire in 1 hour (configurable for production)

## Troubleshooting

### Common Issues

**"Command not found: uvx"**:
```bash
# Install uv (which includes uvx)
pip install uv
# or
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**"Connection refused" errors:**
- Verify the FastMCP proxy server is running: `python server/fastmcp_proxy.py`
- Check Docker services: `docker-compose ps`
- Ensure port 3001 is accessible

**"Authentication failed" errors:**  
- Verify the JWT token is correctly copied from server output
- Check token expiration time (development tokens expire in 1 hour)
- Ensure `PROXY_TOKEN` matches the server's generated token

**"No tools available" errors:**
- Verify opencode.json is in the correct location
- Check JSON syntax is valid
- Ensure the MCP server is enabled (`"enabled": true`)
- Restart opencode after configuration changes

### Debug Mode

Enable debug logging in opencode to see MCP communication:

```bash
opencode --debug
```

### Test the Client Directly

You can test the client proxy independently:

```bash
# Set environment variables
export PROXY_URL="http://localhost:3001/sse/"
export PROXY_TOKEN="your_jwt_token_here"

# Run the client directly
uvx --from git+https://github.com/Dragonatorul/FalkorDB-FastMCP-Proxy python -m client.claude_desktop_proxy
```

## Advantages of Local Client Approach

1. **Compatibility**: Works with opencode's existing local MCP server support
2. **Security**: Maintains full Bearer token authentication
3. **Reliability**: Uses the same client code as Claude Desktop
4. **Flexibility**: Easy to modify or debug locally
5. **Future-proof**: Independent of opencode's remote MCP limitations

## Production Deployment

For production use:

1. **Deploy FastMCP Proxy** to a public server
2. **Update PROXY_URL** to point to your production server
3. **Generate production tokens** with appropriate expiry times
4. **Use HTTPS** for all connections
5. **Set SECRET_KEY** environment variable for consistent token generation

Example production configuration:
```json
{
  "environment": {
    "PROXY_URL": "https://your-fastmcp-proxy.com/sse/",
    "PROXY_TOKEN": "production_jwt_token"
  }
}
```

## Current Status

✅ **Local Client**: Fully working with uvx and GitHub integration  
✅ **Authentication**: Bearer token support via environment variables  
✅ **opencode Compatibility**: Uses supported local MCP server pattern  
✅ **Multi-tenant**: Full support for tenant isolation  

This approach provides a complete, working solution for opencode integration without the limitations of remote MCP authentication.

For additional support, see the [main documentation](../README.md) or the [technical guides](../technical-guides/).