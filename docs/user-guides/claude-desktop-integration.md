---
summary: "Step-by-step configuration guide for integrating FalkorDB FastMCP Proxy with Claude Desktop"
scope: "MCP server configuration, JSON setup, authentication token configuration"
important: "Distinguishes between MCP servers and integrations (two different features)"
config_location: "Claude Desktop → Settings → Features → Model Context Protocol"
format: "JSON format with serverUrl, authentication type, Bearer token setup"
testing: "Connection verification, tool availability, query execution tests"
troubleshooting: "URL formatting, authentication failures, network connectivity problems"
alternatives: "Manual server testing, configuration validation, debug procedures"
---

# Claude Desktop Integration Guide

## ⚠️ **IMPORTANT: Two Different Integration Methods**

Claude Desktop has **two distinct ways** to connect external services. **Choose the correct one** to avoid confusion:

### **🔧 Method 1: MCP Servers (JSON Config) ← USE THIS ONE**
**Location**: Settings → Features → Model Context Protocol  
**Configuration**: JSON file with server definitions  
**Purpose**: Local MCP servers and tools (like our FalkorDB proxy)  
**✅ **This is what our FastMCP proxy uses**

### **🌐 Method 2: Integrations (Name/URL Form) ← NOT FOR US**
**Location**: Settings → Integrations  
**Configuration**: Simple name + URL form  
**Purpose**: Third-party cloud services (GitHub, Google Drive, etc.)  
**❌ **Don't use this for our MCP server**

**🧠 Want to understand WHY these are different?** See [MCP vs Integrations Deep Dive](./mcp-vs-integrations.md) for complete technical analysis.

---

## ✅ **Correct Setup: MCP Servers Configuration**

### **Step 1: Access MCP Settings**
1. Open **Claude Desktop**
2. Click the **Settings** gear icon (bottom left)
3. Navigate to **Features** → **Model Context Protocol**
4. Click **Edit Config** (opens JSON configuration file)

### **Step 2: Get Your Bearer Token**

**Option A: From Console Output (Recommended)**
```bash
# Start proxy locally to see token
python src/fastmcp_proxy.py
```

Look for this output:
```
🔑 Development Test Token:
Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Option B: From Docker Logs (May be limited)**
```bash
docker-compose up -d
docker-compose logs fastmcp-proxy | grep "Bearer"
```

### **Step 3: Add Configuration to MCP JSON**

Add this configuration to your MCP servers JSON file:

```json
{
  "mcpServers": {
    "falkordb": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:3001/sse/"],
      "env": {
        "MCP_AUTH_HEADER": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2ZhbGtvcmRiLWZhc3RtY3AtcHJveHkiLCJzdWIiOiJkZXYtdXNlciIsImlhdCI6MTc1MTkzNTU0MywiZXhwIjoxNzUxOTM5MTQzLCJhdWQiOiJmYWxrb3JkYi1tY3Atc2VydmVyIiwic2NvcGUiOiJyZWFkIHdyaXRlIn0.mW3XWliVqamnWQpyinoRTCy88KXg8WHqUdI2pYyg3VM-BnEoz140pGFmI0wiMoh7cLmz1Hg-Z95uO_1dGAKW1Z3GmF4olsm7fhZpWUrPxFpSvYUuNbpp6nQIFXWDFlGJUvusZ9HJFfUBVa29BvPxMgRv7t2aJfTgfrfNrEi5ks3BhCDmZKIy4yEeASkIluHft6Y242pUaQ1DcxMzpzScT1LGg4dLPORMm-9se1ve5QpQ1B3bUtr2FMdA9QfARWcUFgC_qJsVQGy88CiLQD_JTb35hSPCa6wTUBB79QRrs4pGRuCeo--rpynceSH8iSsibMam9K9yPG_0ra-xfCc_7Q"
      }
    }
  }
}
```

**Important Notes:**
- Replace `PASTE_YOUR_BEARER_TOKEN_HERE` with your actual token
- Use `/sse/` endpoint with mcp-remote transport
- Include the word "Bearer" before the token in MCP_AUTH_HEADER

### **Step 4: Save and Restart**
1. **Save** the JSON configuration file
2. **Restart Claude Desktop** completely
3. Check for any error messages in Claude Desktop

### **Step 5: Verify Integration**

Once configured, you should see these **4 MCP tools** available in Claude Desktop:

1. **`falkordb_query`** - Execute Cypher queries against FalkorDB
2. **`falkordb_list_graphs`** - List available graph databases  
3. **`falkordb_server_info`** - Get FalkorDB server metadata
4. **`falkordb_health`** - Check FalkorDB server health status

---

## 🚫 **Common Mistakes to Avoid**

### **❌ Don't Use the Integrations Section**
- The **Integrations** section is for cloud services like GitHub
- Our FastMCP proxy is an **MCP server**, not a generic integration
- Using the wrong section will result in connection failures

### **❌ Don't Use the SSE Endpoint Directly**
- The `/sse/` endpoint requires the `mcp-remote` bridge
- Use `npx mcp-remote` command, not direct serverUrl
- Direct SSE connections are not supported by Claude Desktop

### **❌ Don't Forget "Bearer" in MCP_AUTH_HEADER**
```json
// ❌ WRONG
"MCP_AUTH_HEADER": "eyJhbGciOiJSUzI1NiIs..."

// ✅ CORRECT  
"MCP_AUTH_HEADER": "Bearer eyJhbGciOiJSUzI1NiIs..."
```

---

## 🔧 **Troubleshooting**

### **Problem: "Connection Failed" or "Server Not Found"**
**Solution**: 
1. Verify Docker stack is running: `docker-compose ps`
2. Test endpoints manually:
   ```bash
   curl http://localhost:3001/sse
   npx mcp-remote http://localhost:3001/sse/
   ```
3. Check that you're using the **MCP Servers** section, not Integrations

### **Problem: "Authentication Failed" or "Invalid Token"**
**Solution**:
1. Generate a fresh token: `python src/fastmcp_proxy.py`
2. Copy the complete token (without "Bearer" prefix)
3. Update your MCP configuration and restart Claude Desktop

### **Problem: "MCP Tools Not Showing Up"**
**Solution**:
1. Verify JSON syntax is valid (no trailing commas, proper quotes)
2. Restart Claude Desktop completely (not just refresh)
3. Check Claude Desktop logs/console for error messages

---

## 📋 **Complete Working Example**

Here's a complete MCP configuration file with our FalkorDB proxy:

```json
{
  "mcpServers": {
    "falkordb": {
      "serverUrl": "http://localhost:3001/mcp/",
      "auth": {
        "type": "bearer",
        "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2ZhbGtvcmRiLWZhc3RtY3AtcHJveHkiLCJzdWIiOiJkZXYtdXNlciIsImlhdCI6MTc1MTkzNTU0MywiZXhwIjoxNzUxOTM5MTQzLCJhdWQiOiJmYWxrb3JkYi1tY3Atc2VydmVyIiwic2NvcGUiOiJyZWFkIHdyaXRlIn0.mW3XWliVqamnWQpyinoRTCy88KXg8WHqUdI2pYyg3VM-BnEoz140pGFmI0wiMoh7cLmz1Hg-Z95uO_1dGAKW1Z3GmF4olsm7fhZpWUrPxFpSvYUuNbpp6nQIFXWDFlGJUvusZ9HJFfUBVa29BvPxMgRv7t2aJfTgfrfNrEi5ks3BhCDmZKIy4yEeASkIluHft6Y242pUaQ1DcxMzpzScT1LGg4dLPORMm-9se1ve5QpQ1B3bUtr2FMdA9QfARWcUFgC_qJsVQGy88CiLQD_JTb35hSPCa6wTUBB79QRrs4pGRuCeo--rpynceSH8iSsibMam9K9yPG_0ra-xfCc_7Q"
    }
  }
}
```

**Remember**: Replace the token with your actual generated token!

---

## 🎯 **Future Reference Quick Guide**

**When setting up FalkorDB FastMCP Proxy in Claude Desktop:**

1. ✅ Use **Settings → Features → Model Context Protocol** 
2. ✅ Add to **MCP Servers** JSON configuration
3. ✅ Use command: `["npx", "mcp-remote", "http://localhost:3001/sse/"]`
4. ✅ Get token from: `python src/fastmcp_proxy.py`
5. ❌ Don't use **Settings → Integrations** (that's for cloud services)
6. ❌ Don't use direct serverUrl (use mcp-remote bridge)

**Expected Result**: 4 FalkorDB tools available in Claude Desktop for graph database operations.

---

> **Note**: This document was created with assistance from Claude Sonnet 3.5, an AI assistant by Anthropic.