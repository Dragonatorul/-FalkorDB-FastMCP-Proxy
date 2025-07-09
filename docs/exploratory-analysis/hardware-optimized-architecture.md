# Hardware-Optimized Architecture

## Overview

This document outlines a cost-effective, hardware-aware deployment strategy that optimizes resource allocation for different workload types in the FalkorDB vector search ecosystem.

## Core Concept

**Separate ML workloads from graph operations** by deploying them on hardware optimized for their specific requirements:

- **Vector ingestion**: GPU-enabled instances for embedding generation
- **Graph operations**: CPU-optimized instances for database queries
- **Vector search**: Can run on either, depending on scale

## Architecture Design

### Proposed Deployment
```
Claude Desktop → FastMCP Proxy → FalkorDB-Vector-MCP (GPU instance)
                              ↘ FalkorDB-MCPServer (CPU instance) → FalkorDB
```

### Hardware Allocation
- **Vector-MCP**: GPU-enabled instance (A100, V100, or consumer GPUs)
- **MCPServer**: Standard CPU instance (2-4 cores, 8GB RAM)
- **FalkorDB**: Memory-optimized instance (high RAM, fast storage)
- **Proxy**: Lightweight instance (1-2 cores, 2GB RAM)

## Smart Proxy Routing

### Workload-Based Tool Routing

```python
# In FastMCP Proxy
VECTOR_INGESTION_TOOLS = {
    "falkordb_embed_and_store",
    "falkordb_bulk_embed_documents", 
    "falkordb_generate_embeddings",
    "falkordb_process_documents"
}

VECTOR_SEARCH_TOOLS = {
    "falkordb_vector_search",
    "falkordb_create_vector_index",
    "falkordb_hybrid_search"
}

GRAPH_TOOLS = {
    "falkordb_query",
    "falkordb_list_graphs", 
    "falkordb_server_info",
    "falkordb_health"
}

async def route_tool_call(tool_name: str, args: dict, auth_context: AuthContext):
    if tool_name in VECTOR_INGESTION_TOOLS:
        # Route to GPU-enabled Vector-MCP for embedding generation
        return await call_vector_mcp_ingestion(tool_name, args, auth_context)
    
    elif tool_name in VECTOR_SEARCH_TOOLS:
        # Route to Vector-MCP for vector operations (can use CPU inference)
        return await call_vector_mcp_search(tool_name, args, auth_context)
    
    elif tool_name in GRAPH_TOOLS:
        # Route to standard MCPServer for graph operations
        return await call_backend_unified("POST", f"/api/mcp/{tool_name}", auth_context, args)
```

### Hybrid Operations Example

```python
async def falkordb_hybrid_search(ctx, query, graphName, k=10):
    # Step 1: Generate query embedding (GPU-accelerated)
    embedding = await call_vector_mcp_ingestion("generate_embedding", {"text": query})
    
    # Step 2: Vector search (can be CPU-based)  
    vector_results = await call_vector_mcp_search("vector_search", {
        "embedding": embedding, "k": k, "graphName": graphName
    })
    
    # Step 3: Graph traversal (CPU-optimized)
    for result in vector_results:
        graph_context = await call_backend_unified("POST", "/api/mcp/context", {
            "query": f"MATCH (n) WHERE id(n) = {result.node_id} MATCH (n)-[r]-(connected) RETURN connected",
            "graphName": graphName
        })
        result.graph_context = graph_context
    
    return vector_results
```

## Cost Analysis

### Traditional Monolithic Approach
```
Single GPU instance for everything:
- GPU: $2.50/hour (A100) × 24/7 = ~$1,800/month
- Always running, even for simple graph queries
- Inefficient resource utilization
```

### Hardware-Optimized Approach
```
Vector-MCP (GPU): $2.50/hour × 8 hours/day = $600/month
MCPServer (CPU): $0.10/hour × 24/7 = $73/month  
FalkorDB (Memory): $0.20/hour × 24/7 = $146/month
Proxy (CPU): $0.05/hour × 24/7 = $37/month
Total: ~$856/month (52% cost savings)
```

### Cost Optimization Strategies

**GPU Usage Patterns:**
- **Peak hours**: 9 AM - 5 PM for document ingestion
- **Off-peak**: Minimal GPU usage for search-only operations
- **Auto-scaling**: Scale GPU instances based on embedding queue depth

**Resource Efficiency:**
- **CPU instances**: Handle 90% of operations (queries, health checks, metadata)
- **GPU instances**: Only active during embedding generation
- **Memory instances**: Optimized for FalkorDB's graph storage requirements

## Performance Benefits

### Embedding Generation (GPU-accelerated)
- **Batch processing**: 1000 documents in 30 seconds vs 10 minutes on CPU
- **Model loading**: Keep embedding models warm on dedicated GPU instance
- **Concurrent processing**: Multiple embedding requests in parallel
- **Throughput**: 10x improvement for large document ingestion

### Graph Operations (CPU-optimized)
- **Lower latency**: No GPU context switching overhead
- **Better resource utilization**: CPU cores optimized for graph traversal
- **Cost efficiency**: No GPU costs for simple CRUD operations
- **Scalability**: Can scale CPU instances independently

### Vector Search Operations
- **Flexible deployment**: Can run on CPU for small datasets, GPU for large
- **Index optimization**: Vector indices stored in memory-optimized instances
- **Query routing**: Intelligent routing based on query complexity

## Deployment Configurations

### Cloud-Native Deployment

```yaml
# docker-compose.gpu.yml
services:
  falkordb-vector-mcp:
    image: falkordb/vector-mcp:1.0.0
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - CUDA_VISIBLE_DEVICES=0
      - EMBEDDING_BATCH_SIZE=32
      - MODEL_CACHE_SIZE=4GB
      
  falkordb-mcpserver:
    image: falkordb/mcpserver:1.1.0  
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
    # No GPU requirements
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vector-mcp
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: vector-mcp
        image: falkordb/vector-mcp:1.0.0
        resources:
          limits:
            nvidia.com/gpu: 1
            memory: 8Gi
          requests:
            nvidia.com/gpu: 1
            memory: 4Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcpserver
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: mcpserver
        image: falkordb/mcpserver:1.1.0
        resources:
          limits:
            cpu: 2
            memory: 4Gi
          requests:
            cpu: 1
            memory: 2Gi
```

### Auto-scaling Configuration

```yaml
# HPA for CPU-based services
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: mcpserver-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: mcpserver
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70

---
# Custom scaling for GPU services based on queue depth
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: vector-mcp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: vector-mcp
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: External
    external:
      metric:
        name: embedding_queue_depth
      target:
        type: Value
        value: "100"
```

## Development vs Production

### Environment-Aware Configuration

```python
class ProxyConfig:
    def __init__(self):
        if os.getenv("ENVIRONMENT") == "development":
            # Single instance for development
            self.vector_mcp_url = "http://localhost:3002"
            self.mcpserver_url = "http://localhost:3000"
        else:
            # Separate GPU/CPU instances for production
            self.vector_mcp_url = "http://gpu-vector-mcp:3002"  
            self.mcpserver_url = "http://cpu-mcpserver:3000"
```

### Development Setup
```yaml
# docker-compose.dev.yml - Single machine, shared resources
services:
  falkordb-vector-mcp:
    image: falkordb/vector-mcp:1.0.0
    # CPU-only for development
    environment:
      - USE_CPU_ONLY=true
      
  falkordb-mcpserver:
    image: falkordb/mcpserver:1.1.0
```

## Edge Deployment Options

### Option 1: Local GPU + Cloud CPU
```
Local Development:
- Vector-MCP: Local RTX 4090 (embedding generation)
- MCPServer: Cloud CPU instance (queries)
- FalkorDB: Cloud memory instance (storage)

Benefits:
- Low latency embeddings
- Scalable queries
- Cost-effective for development
```

### Option 2: Hybrid Cloud
```
Production Deployment:
- Vector-MCP: AWS p3.2xlarge (V100)
- MCPServer: AWS t3.medium  
- FalkorDB: AWS r5.large

Benefits:
- Professional GPU instances
- Managed scaling
- Enterprise reliability
```

### Option 3: On-Premise + Cloud Burst
```
Hybrid Deployment:
- Base load: On-premise hardware
- Peak load: Cloud GPU instances
- Storage: On-premise FalkorDB

Benefits:
- Cost control for base load
- Scalability for peaks
- Data sovereignty
```

## Monitoring and Observability

### Resource Utilization Metrics
```python
class HardwareMetrics:
    def collect_metrics(self):
        return {
            "gpu_utilization": self.get_gpu_utilization(),
            "gpu_memory_usage": self.get_gpu_memory(),
            "cpu_utilization": self.get_cpu_utilization(),
            "embedding_queue_depth": self.get_queue_depth(),
            "cost_per_hour": self.calculate_current_cost(),
            "requests_per_service": {
                "vector_mcp": self.vector_requests,
                "mcpserver": self.graph_requests
            }
        }
```

### Cost Optimization Alerts
```python
class CostOptimizationAlerting:
    async def check_efficiency(self):
        # GPU underutilization
        if self.get_gpu_utilization() < 20:
            await self.send_alert("GPU underutilized - consider scaling down")
            
        # Inefficient routing
        if self.get_cpu_vector_requests() > self.get_gpu_vector_requests():
            await self.send_alert("Vector requests being handled by CPU - check routing")
            
        # Cost threshold exceeded
        if self.get_hourly_cost() > self.cost_threshold:
            await self.send_alert("Hourly cost threshold exceeded")
```

## Benefits Summary

### ✅ Technical Advantages
- **Hardware specialization**: GPU for embeddings, CPU for graph operations
- **Performance optimization**: 10x improvement for embedding generation
- **Independent scaling**: Scale embedding and query workloads separately
- **Fault isolation**: GPU service failures don't affect basic graph operations

### ✅ Operational Advantages
- **Resource efficiency**: No idle GPU costs during graph-only operations
- **Development flexibility**: Teams can work on services independently
- **Deployment options**: Mix cloud GPU with on-premise CPU, or vice versa
- **Gradual adoption**: Can start with CPU-only and add GPU service later

### ✅ Business Advantages
- **Cost predictability**: GPU costs scale with actual ML usage (52% savings)
- **Performance guarantees**: Dedicated resources for each workload type
- **Vendor flexibility**: Different cloud providers for different services
- **Future-proofing**: Easy to upgrade GPU instances without affecting other services

## Conclusion

The hardware-optimized architecture provides the optimal balance of performance, cost, and operational complexity. By separating ML workloads from graph operations and deploying them on appropriate hardware, organizations can achieve significant cost savings while improving performance and maintaining architectural flexibility.

This approach is particularly valuable for production deployments where cost efficiency and performance optimization are critical requirements.

---

> **Note**: This document was created with assistance from Claude Sonnet 3.5, an AI assistant by Anthropic.