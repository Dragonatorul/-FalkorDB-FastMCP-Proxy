import os
import requests
import pytest

MCP_URL = os.environ.get("FALKORDB_MCPSERVER_URL", "http://localhost:3000")
API_KEY = os.environ.get("MCP_API_KEY", "dev-api-key")
HEADERS = {"x-api-key": API_KEY}

def test_health():
    r = requests.get(f"{MCP_URL}/health")
    assert r.status_code == 200
    j = r.json()
    assert j["status"] == "healthy"
    assert "timestamp" in j
    assert "services" in j
    assert j["services"]["database"]["connected"] is True

def test_metadata():
    r = requests.get(f"{MCP_URL}/api/mcp/metadata", headers=HEADERS)
    assert r.status_code == 200
    j = r.json()
    assert j["provider"] == "FalkorDB MCP Server"
    assert "version" in j
    assert "capabilities" in j

def test_list_graphs():
    r = requests.get(f"{MCP_URL}/api/mcp/graphs", headers=HEADERS)
    assert r.status_code == 200
    j = r.json()
    assert "data" in j
    assert "metadata" in j
    assert "count" in j["metadata"]

def test_query():
    data = {
        "graphName": "test",
        "query": "RETURN 1 as one"
    }
    r = requests.post(f"{MCP_URL}/api/mcp/context", headers=HEADERS, json=data)
    assert r.status_code == 200
    j = r.json()
    assert "data" in j
    assert "metadata" in j
    assert j["data"]["data"][0]["one"] == 1
