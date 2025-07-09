# Troubleshooting Database - AI Reference

## Summary (Lines 1-10)
Common issues, solutions, and debugging workflows for FalkorDB FastMCP Proxy.
Key problems: services not running, token validation, Claude Desktop config, port conflicts.
Quick diagnostics: docker-compose ps, logs review, token generation, endpoint testing.
Authentication errors: JWT validation, Bearer token format, issuer/audience claims.
Connection issues: port availability, service health, network connectivity.
Claude Desktop: config format, endpoint URL, token placement, MCP vs Integrations.
Performance: <50ms target latency, backend health monitoring, error mapping.
Tools debugging: individual MCP tool testing, backend API verification.
Vector issues: embedding generation gap, async job solution available.

## Service Issues
### Services Not Running
- **Symptom**: `docker-compose ps` shows no containers
- **Solution**: `docker-compose up -d`
- **Debug**: Check Docker daemon, port conflicts, compose file syntax

### Port Conflicts
- **Symptom**: "Port already in use" errors
- **Ports Used**: 3001 (proxy), 3000 (MCPServer), 6379 (FalkorDB)
- **Solution**: `docker-compose down`, check `netstat -tulpn`, kill conflicting processes

### Service Health
- **Check Command**: `docker-compose logs fastmcp-proxy`
- **Healthy Signs**: OAuth metadata served, backend connectivity confirmed
- **Unhealthy Signs**: Connection refused, JWT validation errors

## Authentication Errors
### Invalid Bearer Token
- **Symptom**: 401 Unauthorized responses
- **Generate New**: `python src/fastmcp_proxy.py`
- **Verify Format**: Should be long JWT string starting with "eyJ"
- **Common Issue**: Expired token (default 1 hour TTL)

### JWT Validation Errors
- **Symptom**: "Token validation failed" in logs
- **Check**: Issuer/audience claims in token
- **Debug**: RS256 signature verification, key mismatch

## Claude Desktop Issues
### Configuration Problems
- **Wrong Section**: Use "MCP Servers" not "Integrations"
- **URL Format**: `http://localhost:3001/mcp/` (note trailing slash)
- **Token Placement**: In auth.token field, not URL parameters

### Connection Failures
- **Test Endpoint**: `curl http://localhost:3001/.well-known/oauth-authorization-server`
- **Expected**: JSON metadata response
- **Debug**: Service running, port accessible, token valid

## MCP Tool Debugging
### Individual Tool Testing
- **Direct API**: Test backend MCPServer endpoints directly
- **Tool Mapping**: Verify proxy → backend endpoint mapping
- **Error Propagation**: Check error message translation

### Backend Connectivity
- **Health Check**: `curl http://localhost:3000/health`
- **API Key**: Verify MCP_API_KEY configuration
- **Timeout**: Default 30s, adjust if needed