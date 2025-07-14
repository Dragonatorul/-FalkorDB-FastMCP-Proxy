# DXT Client Packaging Guide

This guide covers packaging the FalkorDB FastMCP **client** as a Desktop Extension (.dxt) for Claude Desktop.

## Overview

The FalkorDB FastMCP client has been packaged as a Desktop Extension to enable one-click installation in Claude Desktop. **This package contains ONLY the client components** - the server must be deployed separately.

### Client vs Server Architecture

```
CLIENT SIDE (DXT Package)                    SERVER SIDE (Separate Deployment)
┌─────────────────────────────┐             ┌────────────────────────────────┐
│ Claude Desktop              │   Bearer    │ FastMCP Proxy Server           │
│ ├── DXT Extension           │◄──Token────►│ ├── src/fastmcp_proxy.py       │
│ │   └── claude_desktop_proxy│             │ ├── Docker Services            │
│ └── User Config UI          │             │ │   ├── FalkorDB               │
└─────────────────────────────┘             │ │   ├── MCPServer v1.1.0       │
                                            │ │   └── FastMCP Proxy          │
                                            │ └── Authentication (RSA-256)   │
                                            └────────────────────────────────┘
```

**DXT Package**: Contains only the STDIO client proxy for Claude Desktop
**Server Deployment**: Separate infrastructure with FalkorDB + MCPServer + FastMCP Proxy

## Client Package Structure

```
FalkorDB-FastMCP-Proxy.dxt (8.1kB)
├── manifest.json                    # Extension metadata and user configuration
├── claude_desktop_proxy.py          # FastMCP STDIO client proxy
├── client-requirements.txt          # Minimal client dependencies
├── LICENSE                          # MIT License
└── README.md                        # Project documentation
```

**What's Included**: Only client-side components for connecting to remote servers
**What's Excluded**: All server code, Docker configs, tests, development files

## DXT Client Manifest Configuration

The `manifest.json` defines the client-side configuration:

### User Configuration Schema
```json
"user_config": {
  "proxy_url": {
    "type": "string",
    "title": "FastMCP Proxy URL",
    "description": "URL of your remote FalkorDB FastMCP proxy server",
    "required": true,
    "default": "https://localhost:3001/sse/"
  },
  "bearer_token": {
    "type": "string",
    "title": "Bearer Token", 
    "description": "Authentication token for the FastMCP proxy server",
    "sensitive": true,
    "required": true
  }
}
```

### Client Configuration
```json
"server": {
  "type": "python",
  "entry_point": "claude_desktop_proxy.py",
  "mcp_config": {
    "command": "python",
    "args": ["${__dirname}/claude_desktop_proxy.py"],
    "env": {
      "FASTMCP_PROXY_URL": "${user_config.proxy_url}",
      "FASTMCP_BEARER_TOKEN": "${user_config.bearer_token}"
    }
  }
}
```

**Key Changes**: 
- Entry point directly references `claude_desktop_proxy.py` (no server subdirectory)
- User provides remote server URL (not localhost)
- Bearer token for authentication to remote server

## Development Workflow

### Prerequisites
```bash
# Install DXT toolchain
npm install -g @anthropic-ai/dxt
# or locally:
npm install @anthropic-ai/dxt --save-dev
```

### Build Process
```bash
# 1. Validate manifest
npx dxt validate manifest.json

# 2. Package extension
npx dxt pack

# 3. Verify package
npx dxt info FalkorDB-FastMCP-Proxy.dxt

# 4. Test unpacking (optional)
npx dxt unpack FalkorDB-FastMCP-Proxy.dxt test-output/
```

### Client Package Optimization

The `.dxtignore` file excludes all server-side code:
```
# SERVER CODE (exclude all server components)
src/
server/
docker-compose.yml
Dockerfile
pyproject.toml

# DEVELOPMENT FILES
.venv/
docs/
.mypy_cache/
tests/
requirements/
```

**Result**: Client package size is 8.1kB (only essential client files)

## Client Installation Flow

1. **Download**: User downloads `FalkorDB-FastMCP-Proxy.dxt` (client only)
2. **Install**: Drag .dxt file into Claude Desktop Settings
3. **Configure**: Claude Desktop prompts for:
   - **Proxy URL**: Remote FastMCP server endpoint (e.g., `https://your-server.com:3001/sse/`)
   - **Bearer Token**: Authentication token (stored securely in OS keychain)
4. **Connect**: Client automatically connects to remote server with authentication

## Server Deployment (Separate)

The server must be deployed independently:

### Development Server
```bash
# Start local server stack
docker-compose up

# Generate Bearer tokens
python src/fastmcp_proxy.py
```

### Production Server
```bash
# Deploy FastMCP proxy server
# Configure with proper security, HTTPS, certificates
# Generate production Bearer tokens for clients
```

**Important**: The DXT client connects to remote servers - it does not include server components.

## Tools Available

Once installed, the extension provides:
- `falkordb_query` - Execute Cypher queries
- `falkordb_list_graphs` - List available graphs  
- `falkordb_server_info` - Get server metadata
- `falkordb_health` - Check server health

## Deployment Architecture

### Client-Server Separation
```
USER'S MACHINE                           REMOTE INFRASTRUCTURE
┌─────────────────────┐                  ┌──────────────────────────┐
│ Claude Desktop      │                  │ FalkorDB FastMCP Server  │
│ ├── DXT Extension   │◄─────Bearer─────►│ ├── FastMCP Proxy        │
│ │   (8.1kB client)  │     Token        │ ├── MCPServer v1.1.0     │
│ └── Local execution │                  │ ├── FalkorDB Database    │
└─────────────────────┘                  │ └── Docker Stack         │
                                         └──────────────────────────┘
```

### Benefits of Client-Only Packaging
- **Lightweight**: 8.1kB download vs 100MB+ with server components
- **Security**: No local server infrastructure to secure
- **Scalability**: Multiple clients can connect to shared servers
- **Maintenance**: Server updates don't require client reinstalls
- **Enterprise**: Centralized server management and access control

## Security Considerations

- **Bearer Tokens**: Stored securely in OS keychain by Claude Desktop
- **Template Variables**: DXT automatically injects config without exposing secrets
- **HTTPS Required**: Production deployments should use HTTPS endpoints
- **Token Rotation**: Support for updating tokens through Claude Desktop settings

## Extension Submission

To submit to Claude Desktop extension directory:
1. Test extension installation and functionality
2. Ensure cross-platform compatibility (Windows, macOS, Linux)
3. Submit via [Extension Submission Form](https://docs.google.com/forms/d/14_Dmcig4z8NeRMB_e7TOyrKzuZ88-BLYdLvS6LPhiZU/edit)
4. Review process includes quality and security validation

## Troubleshooting

### Common Issues
- **Package Too Large**: Check `.dxtignore` includes development files
- **Manifest Invalid**: Validate JSON syntax and required fields
- **Python Dependencies**: Ensure `requirements.txt` includes `fastmcp>=2.10.2`
- **Authentication Fails**: Verify Bearer token format and proxy URL

### Validation Commands
```bash
# Validate manifest syntax
npx dxt validate manifest.json

# Check package contents
npx dxt info FalkorDB-FastMCP-Proxy.dxt

# Test unpacking
npx dxt unpack FalkorDB-FastMCP-Proxy.dxt test/
```

## Future Enhancements

- **Multi-Tenant Support**: Tenant scoping and graph name prefixing
- **Token Management**: Automatic token refresh and validation
- **Server Discovery**: Automatic detection of available proxy servers
- **Enhanced Security**: Certificate pinning and additional authentication methods