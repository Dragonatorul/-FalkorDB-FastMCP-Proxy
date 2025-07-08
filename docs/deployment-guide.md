# Deployment Guide

## Quick Start (Full Docker Deployment)

### Prerequisites
- Docker and Docker Compose installed
- Git for cloning the repository

### 1. Clone and Setup
```bash
git clone <repository-url>
cd FalkorDB-FastMCP-Proxy
```

### 2. Start All Services
```bash
# Start complete 3-service stack
docker-compose up -d

# Verify all services are running
docker-compose ps
```

Expected output:
```
NAME                  STATUS         PORTS
falkordb              Up 2 minutes   0.0.0.0:6379->6379/tcp
falkordb-mcp-server   Up 2 minutes   0.0.0.0:3000->3000/tcp
fastmcp-proxy         Up 2 minutes   0.0.0.0:3001->3001/tcp
```

### 3. Get Bearer Token
```bash
# Get the Bearer token from proxy startup logs
docker-compose logs fastmcp-proxy | grep "Bearer"

# Or start proxy locally to see token in console
python src/fastmcp_proxy.py
```

Expected output:
```
╭─ FastMCP 2.0 ────────────────────────────────────────────────────────────────╮
│     🖥️  Server name:     FalkorDB FastMCP Proxy                               │
│     📦 Transport:       Streamable-HTTP                                      │
│     🔗 Server URL:      http://0.0.0.0:3001/mcp/                             │
│     🏎️  FastMCP version: 2.10.2                                               │
│     🤝 MCP version:     1.10.1                                               │
╰──────────────────────────────────────────────────────────────────────────────╮

🔑 Development Test Token:
Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

**⚠️ Important**: Copy the Bearer token from the output - you'll need it for Claude Desktop configuration.

### 4. Validate Deployment
```bash
# Run integration tests
python tests/test_remote_mcp.py
```

Expected output:
```
🧪 Testing FalkorDB FastMCP Proxy for Remote Access
✅ Backend health: healthy
✅ OAuth Authorization Server Metadata endpoint working
✅ MCP endpoint accepts valid Bearer token
📊 Test Results: 3/3 passed
🎉 All tests passed! FastMCP proxy is ready for remote Claude Desktop connections.
```

### 5. Configure Claude Desktop

⚠️ **IMPORTANT**: Claude Desktop has two different integration methods. **Use the correct one!**

**✅ CORRECT**: Use **MCP Servers** configuration (JSON file)  
**❌ WRONG**: Don't use the **Integrations** section (that's for cloud services)

**📋 Quick Configuration**:
```json
{
  "mcpServers": {
    "falkordb": {
      "serverUrl": "http://localhost:3001/mcp/",
      "auth": {
        "type": "bearer",
        "token": "YOUR_BEARER_TOKEN_FROM_STEP_3"
      }
    }
  }
}
```

**📖 Detailed Setup**: See [Claude Desktop Integration Guide](./claude-desktop-integration.md) for complete step-by-step instructions and troubleshooting.

---

## Alternative Deployment Methods

### Full Docker Deployment ✅ RECOMMENDED
The current deployment method uses all services in Docker containers:

```bash
# Start complete 3-service stack  
docker-compose up -d

# All services running in containers:
# - FalkorDB: localhost:6379
# - MCPServer: localhost:3000  
# - FastMCP Proxy: localhost:3001/mcp/
```

### Production Deployment

#### Option 1: Systemd Service (Recommended)
Create `/etc/systemd/system/fastmcp-proxy.service`:

```ini
[Unit]
Description=FalkorDB FastMCP Proxy
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/FalkorDB-FastMCP-Proxy
ExecStartPre=/usr/bin/docker-compose up -d falkordb falkordb-mcp-server
ExecStart=/usr/bin/python3 src/fastmcp_proxy.py
ExecStop=/usr/bin/docker-compose stop
Restart=always
RestartSec=10

Environment=PYTHONPATH=/path/to/FalkorDB-FastMCP-Proxy
Environment=FALKORDB_MCPSERVER_URL=http://localhost:3000
Environment=PROXY_HOST=0.0.0.0
Environment=PROXY_PORT=3001

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable fastmcp-proxy
sudo systemctl start fastmcp-proxy
sudo systemctl status fastmcp-proxy
```

#### Option 2: Process Manager (PM2)
```bash
# Install PM2
npm install -g pm2

# Create ecosystem file
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'fastmcp-proxy',
    script: 'python',
    args: 'src/fastmcp_proxy.py',
    cwd: '/path/to/FalkorDB-FastMCP-Proxy',
    env: {
      PYTHONPATH: '/path/to/FalkorDB-FastMCP-Proxy',
      FALKORDB_MCPSERVER_URL: 'http://localhost:3000',
      PROXY_HOST: '0.0.0.0',
      PROXY_PORT: '3001'
    }
  }]
}
EOF

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

---

## Configuration

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `FALKORDB_MCPSERVER_URL` | `http://localhost:3000` | MCPServer backend URL |
| `MCP_API_KEY` | `dev-api-key` | API key for MCPServer |
| `PROXY_HOST` | `0.0.0.0` | FastMCP proxy bind address |
| `PROXY_PORT` | `3001` | FastMCP proxy port |

### Docker Compose Configuration
The `docker-compose.yml` configures three services:

#### FalkorDB Service
- **Image**: `falkordb/falkordb:latest`
- **Port**: 6379
- **Data**: Persistent volume `falkordb_data`

#### MCPServer Service  
- **Image**: `ghcr.io/dragonatorul/falkordb-mcpserver:1.1.0`
- **Port**: 3000
- **Environment**: 
  - `FALKORDB_HOST=falkordb`
  - `MCP_API_KEY=dev-api-key`
  - `ENABLE_MULTI_TENANCY=false`

#### FastMCP Proxy Service (Currently Disabled)
- **Build**: Local Dockerfile
- **Port**: 3001
- **Status**: ⚠️ Not functional due to Docker initialization issue

---

## Monitoring & Maintenance

### Health Checks
```bash
# Check all services
docker-compose ps

# Check backend health
curl http://localhost:3000/health

# Check proxy OAuth metadata
curl http://localhost:3001/.well-known/oauth-authorization-server

# Run full integration test
python tests/test_remote_mcp.py
```

### Log Monitoring
```bash
# Docker service logs
docker-compose logs -f falkordb
docker-compose logs -f falkordb-mcp-server

# Local proxy logs (if running in background)
tail -f fastmcp_proxy.log
```

### Token Management
Tokens expire after 1 hour by default. To generate a new token:

1. Restart the FastMCP proxy
2. Copy the new Bearer token from startup output
3. Update Claude Desktop configuration

For production, consider implementing token refresh mechanisms or longer expiration times.

---

## Troubleshooting

### Common Issues

#### Services Won't Start
```bash
# Check Docker daemon
sudo systemctl status docker

# Check port conflicts
sudo netstat -tulpn | grep -E ":(3000|3001|6379)"

# Restart services
docker-compose down
docker-compose up -d falkordb falkordb-mcp-server
```

#### FastMCP Proxy Issues
```bash
# Check Python dependencies
pip install -r requirements.txt

# Verify no port conflicts
sudo lsof -i :3001

# Run with verbose output
python -v src/fastmcp_proxy.py
```

#### Integration Test Failures
```bash
# Check service status
docker-compose ps

# Test backend directly
curl http://localhost:3000/health

# Check proxy endpoints
curl http://localhost:3001/.well-known/oauth-authorization-server
```

### Performance Tuning

#### For High Load
- Increase MCPServer resources in docker-compose.yml
- Consider multiple FastMCP proxy instances behind a load balancer
- Monitor FalkorDB memory usage and adjust Docker limits

#### For Development
- Use development mode with auto-restart
- Enable debug logging
- Use shorter token expiration for testing

---

## Security Considerations

### Development vs Production

#### Development (Current Setup)
- ✅ Auto-generated RSA keys
- ✅ HTTP endpoints (localhost only)
- ✅ 1-hour token expiration
- ✅ Development API keys

#### Production Requirements
- 🔄 Use proper Certificate Authority for RSA keys
- 🔄 HTTPS endpoints with TLS certificates
- 🔄 Longer token expiration or refresh mechanism
- 🔄 Production API keys and secrets management
- 🔄 Network security (firewalls, VPN)
- 🔄 Log monitoring and alerting

### Network Security
- FastMCP proxy should only bind to localhost in development
- Use reverse proxy (nginx/Apache) for external access
- Implement rate limiting and request filtering
- Monitor and log authentication attempts

For production security hardening, see [security-guide.md](./security-guide.md) (coming soon).