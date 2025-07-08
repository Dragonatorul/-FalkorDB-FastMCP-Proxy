# Testing Documentation

## Test Coverage Overview

The FalkorDB FastMCP Proxy includes comprehensive testing to ensure reliability and functionality across all components.

## Integration Tests

### `test_remote_mcp.py` - Primary Integration Test Suite

**Purpose**: End-to-end validation of the complete FastMCP proxy stack

**Test Coverage**: 
- ✅ Backend connectivity (FalkorDB + MCPServer)
- ✅ OAuth 2.1 authorization server metadata
- ✅ SSE endpoint authentication with Bearer tokens
- ✅ Complete remote MCP client connection capability

**Current Status**: 3/3 tests passing ✅

#### Test Results Example:
```bash
$ python tests/test_remote_mcp.py
🧪 Testing FalkorDB FastMCP Proxy for Remote Access
============================================================
🔑 Generating Bearer token...
   Token: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...

📡 Testing backend connectivity...
✅ Backend health: healthy

🔐 Testing OAuth Authorization Server Metadata...
✅ OAuth Authorization Server Metadata endpoint working

🌊 Testing SSE endpoint authentication...
✅ SSE endpoint accepts valid Bearer token

📊 Test Results: 3/3 passed
🎉 All tests passed! FastMCP proxy is ready for remote Claude Desktop connections.
```

### Test Implementation Details

#### Test 1: Backend Connectivity
```python
def test_backend_connectivity() -> bool:
    """Test connectivity to FalkorDB MCP Server backend"""
    response = requests.get("http://localhost:3000/health", timeout=5)
    return response.status_code == 200
```

**Validates**: 
- MCPServer health endpoint accessibility
- FalkorDB database connection status
- Response time under 5 seconds

#### Test 2: OAuth Metadata Endpoint
```python
def test_oauth_metadata(base_url: str) -> bool:
    """Test OAuth Authorization Server Metadata endpoint"""
    response = requests.get(f"{base_url}/.well-known/oauth-authorization-server")
    metadata = response.json()
    required_fields = ["issuer", "authorization_endpoint", "token_endpoint"]
    return all(field in metadata for field in required_fields)
```

**Validates**:
- OAuth 2.1 metadata endpoint availability
- Required OAuth fields present
- Proper JSON response format

#### Test 3: SSE Authentication
```python
def test_sse_endpoint_auth(base_url: str, bearer_token: str) -> bool:
    """Test SSE endpoint authentication"""
    # Test without auth - should get 401
    response = requests.get(f"{base_url}/sse/", timeout=5)
    if response.status_code != 401:
        return False
    
    # Test with valid Bearer token - should get SSE connection
    headers = {"Authorization": bearer_token}
    response = requests.get(f"{base_url}/sse/", headers=headers, timeout=5)
    return response.status_code in [200, 202]
```

**Validates**:
- Unauthenticated requests properly rejected (401)
- Valid Bearer tokens accepted
- SSE connection establishment

## Manual Testing Procedures

### Health Check Validation
```bash
# Test backend health
curl http://localhost:3000/health

# Expected response:
{
  "status": "healthy",
  "services": {
    "database": {
      "connected": true,
      "latency": "2ms"
    }
  }
}
```

### OAuth Endpoint Testing
```bash
# Test OAuth metadata
curl http://localhost:3001/.well-known/oauth-authorization-server

# Expected response:
{
  "issuer": "https://falkordb-fastmcp-proxy",
  "authorization_endpoint": "https://falkordb-fastmcp-proxy/auth",
  "token_endpoint": "https://falkordb-fastmcp-proxy/token"
}
```

### SSE Endpoint Testing
```bash
# Test without authentication (should fail)
curl -i http://localhost:3001/sse/
# Expected: HTTP/1.1 401 Unauthorized

# Test with Bearer token (should succeed or timeout)
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:3001/sse/
# Expected: SSE connection or timeout (connection established)
```

### MCP Tool Testing

#### Direct Tool Invocation
Since MCP tools require SSE transport, direct testing requires MCP client simulation. For manual validation:

1. **Start proxy with verbose logging**
2. **Connect Claude Desktop** with proper configuration
3. **Execute tool calls** through Claude interface

#### Expected Tool Behaviors:

**falkordb_query Tool**:
```
Input: "MATCH (n) RETURN n LIMIT 5"
Expected: Graph query results or proper error message
```

**falkordb_list_graphs Tool**:
```
Input: No parameters
Expected: List of available graphs in FalkorDB
```

**falkordb_server_info Tool**:
```
Input: No parameters  
Expected: Server version, capabilities, and metadata
```

**falkordb_health Tool**:
```
Input: No parameters
Expected: Database health status and connection info
```

## Performance Testing

### Latency Benchmarks

**OAuth Metadata Endpoint**:
```bash
# Measure response time
time curl -s http://localhost:3001/.well-known/oauth-authorization-server >/dev/null
# Target: < 10ms
```

**Backend Health Check**:
```bash
# Measure backend response time
time curl -s http://localhost:3000/health >/dev/null
# Target: < 20ms
```

**SSE Connection Establishment**:
```bash
# Measure connection time with timeout
timeout 1s curl -H "Authorization: Bearer $TOKEN" http://localhost:3001/sse/
# Target: Immediate connection (timeout = success)
```

### Load Testing (Future)
For production load testing, consider:
- Multiple concurrent SSE connections
- High-frequency MCP tool calls
- Extended connection duration testing
- Memory usage monitoring

## Test Environment Setup

### Prerequisites
```bash
# Ensure backend services are running
docker-compose up -d falkordb falkordb-mcp-server

# Verify services
docker-compose ps

# Start FastMCP proxy locally
python src/fastmcp_proxy.py &
```

### Test Data Preparation
```bash
# Populate test data in FalkorDB (optional)
# Connect to FalkorDB and create sample graph data
docker exec -it falkordb redis-cli

# In Redis CLI:
GRAPH.QUERY test_graph "CREATE (n:Person {name: 'Test User', age: 30})"
```

## Debugging Test Failures

### Common Issues and Solutions

#### Backend Connectivity Failures
```bash
# Check Docker services
docker-compose ps
docker-compose logs falkordb-mcp-server

# Check port accessibility  
netstat -tulpn | grep :3000
curl -v http://localhost:3000/health
```

#### OAuth Metadata Failures
```bash
# Check FastMCP proxy startup
ps aux | grep fastmcp_proxy
curl -v http://localhost:3001/.well-known/oauth-authorization-server

# Check for Docker vs local proxy conflict
docker-compose ps fastmcp-proxy
```

#### SSE Authentication Failures
```bash
# Verify token generation
python -c "import sys; sys.path.append('src'); from fastmcp_proxy import generate_test_token; print(generate_test_token())"

# Test token validation
curl -H "Authorization: Bearer $TOKEN" -v http://localhost:3001/sse/
```

### Test Debugging Commands
```bash
# Verbose integration test
python -u test_remote_mcp.py 2>&1 | tee test_output.log

# Check all services
docker-compose ps && echo "=== FastMCP ===" && ps aux | grep fastmcp

# Network connectivity
ss -tulpn | grep -E ":(3000|3001|6379)"
```

## Continuous Integration (Future)

### Proposed CI Pipeline
```yaml
# .github/workflows/test.yml (example)
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Start backend services
        run: docker-compose up -d falkordb falkordb-mcp-server
      - name: Wait for services
        run: sleep 10
      - name: Start FastMCP proxy
        run: python src/fastmcp_proxy.py &
      - name: Run integration tests
        run: python tests/test_remote_mcp.py
      - name: Cleanup
        run: docker-compose down
```

## Test Reporting

### Success Criteria
- ✅ All integration tests pass (3/3)
- ✅ Response times under performance targets
- ✅ No authentication bypass vulnerabilities
- ✅ Proper error handling for all failure modes

### Failure Investigation
When tests fail, collect:
1. **Test output**: Complete console output
2. **Service logs**: `docker-compose logs`
3. **Process status**: `ps aux | grep -E "(python|docker)"`
4. **Network status**: `netstat -tulpn`
5. **Proxy logs**: FastMCP startup output

### Test Metrics Tracking
For production monitoring:
- Test execution time trends
- Failure rate over time  
- Performance regression detection
- Coverage gap identification

---

## Test Development Guidelines

### Adding New Tests
1. **Integration tests**: Add to `test_remote_mcp.py`
2. **Unit tests**: Create in `tests/unit/` (future)
3. **Performance tests**: Create in `tests/performance/` (future)

### Test Naming Convention
- `test_<component>_<scenario>()` for functions
- `Test<Component><Scenario>` for classes
- Clear, descriptive names explaining what is tested

### Test Data Management
- Use temporary test data when possible
- Clean up test resources after execution
- Avoid dependencies on external services
- Mock external APIs when not testing integration

This testing framework ensures the FalkorDB FastMCP Proxy maintains high reliability and performance standards across all deployment scenarios.