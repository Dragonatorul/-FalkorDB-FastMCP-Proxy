#!/bin/bash
# Test script for FastMCP proxy

echo "=== Testing FastMCP Proxy MCP Tools ==="

# Test 1: List available tools
echo "1. Testing tools/list..."
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | timeout 10 npx mcp-remote http://localhost:3001/sse/ 2>/tmp/mcp_test1.log &
sleep 5
pkill -f "npx mcp-remote"
echo "Response logged to /tmp/mcp_test1.log"

sleep 2

# Test 2: Test falkordb_health tool
echo "2. Testing falkordb_health tool..."
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "falkordb_health", "arguments": {}}}' | timeout 10 npx mcp-remote http://localhost:3001/sse/ 2>/tmp/mcp_test2.log &
sleep 5
pkill -f "npx mcp-remote"
echo "Response logged to /tmp/mcp_test2.log"

sleep 2

# Test 3: Test falkordb_list_graphs tool
echo "3. Testing falkordb_list_graphs tool..."
echo '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "falkordb_list_graphs", "arguments": {}}}' | timeout 10 npx mcp-remote http://localhost:3001/sse/ 2>/tmp/mcp_test3.log &
sleep 5
pkill -f "npx mcp-remote"
echo "Response logged to /tmp/mcp_test3.log"

echo "=== Test Results ==="
for i in 1 2 3; do
    echo "--- Test $i Results ---"
    cat /tmp/mcp_test$i.log | grep -A 5 -B 5 "Remote→Local" || echo "No response found"
    echo
done