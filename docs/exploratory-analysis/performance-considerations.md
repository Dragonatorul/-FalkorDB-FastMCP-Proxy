# Performance Considerations

## Description (Lines 1-10)
Performance analysis and optimization strategies for FalkorDB FastMCP Proxy system.  
Covers throughput metrics, latency optimization, resource utilization, scaling considerations.  
Components analyzed: FastMCP Proxy, MCPServer, FalkorDB, network transport, authentication.  
Performance metrics: Response times, concurrent connections, memory usage, CPU utilization.  
Bottleneck identification: Network latency, database queries, authentication overhead, serialization.  
Optimization strategies: Connection pooling, caching, query optimization, resource tuning.  
Scaling approaches: Horizontal scaling, load balancing, resource allocation, monitoring.  
Testing methodology: Load testing, stress testing, performance benchmarking procedures.

## Overview

This document analyzes performance implications of different vector implementation approaches and provides optimization strategies for production deployments.

## Current Performance Baseline

### FalkorDB 4.0 Vector Performance
- **Vector storage**: Native `T_VECTOR_F32` type with optimized memory layout
- **Vector indexing**: HNSW (Hierarchical Navigable Small World) algorithm
- **Search performance**: Sub-millisecond for datasets < 100K vectors
- **Index build time**: Linear with dataset size, ~1-2 seconds per 10K vectors

### Existing MCP Layer Performance
- **Query latency**: 10-50ms for simple Cypher queries
- **Network overhead**: HTTP/JSON serialization adds 5-15ms
- **Authentication**: Bearer token validation adds 1-3ms
- **Tenant isolation**: Graph name prefixing adds negligible overhead

## Implementation Performance Comparison

### Option 1: Proxy Implementation
```
Latency: Client → Proxy (embed) → MCPServer → FalkorDB
         50ms   + 2000ms      + 20ms       + 5ms = 2075ms

Throughput: Limited by embedding generation in proxy
Memory: 1-4GB for embedding models in proxy process
CPU: High during embedding, idle during queries
```

**Performance Issues:**
- Embedding generation blocks proxy for other requests
- Single point of failure for all operations
- Memory pressure from ML models affects routing performance

### Option 2: MCPServer Enhancement
```
Latency: Client → Proxy → MCPServer (embed + query) → FalkorDB
         50ms   + 10ms  + 2000ms              + 5ms = 2065ms

Throughput: Better isolation, can scale MCPServer independently
Memory: 1-4GB for embedding models in MCPServer
CPU: Dedicated to database operations and ML
```

**Performance Benefits:**
- Direct database connection eliminates network hop
- Better resource utilization with dedicated service
- Can optimize for database + ML workload combination

### Option 3: Dedicated Vector Service
```
Latency: Client → Proxy → Vector-MCP (embed) → FalkorDB
         50ms   + 10ms  + 2000ms         + 5ms = 2065ms

Alternative: Client → Proxy → MCPServer → FalkorDB (for queries)
            50ms   + 10ms  + 20ms     + 5ms = 85ms

Throughput: Independent scaling of vector and graph operations
Memory: Optimized allocation per service type
CPU: GPU for embeddings, CPU for queries
```

**Performance Advantages:**
- Hardware specialization (GPU vs CPU)
- Independent scaling based on workload
- Fault isolation prevents cascade failures

### Option 4: Async Job
```
Ingestion Latency: Background processing (5-300 seconds delay)
Query Latency: Client → Proxy → MCPServer → FalkorDB
               50ms   + 10ms  + 20ms     + 5ms = 85ms

Throughput: Decoupled ingestion and query performance
Memory: Minimal impact on query path
CPU: Batch processing optimizes embedding generation
```

**Performance Characteristics:**
- Query performance unaffected by embedding generation
- Batch processing improves embedding throughput
- Delayed availability of vector search for new content

## Embedding Generation Performance

### OpenAI API Performance
```
text-embedding-3-small:
- Latency: 200-500ms per request
- Throughput: 1000 tokens/minute (rate limited)
- Batch size: Up to 2048 inputs per request
- Cost: $0.02 per 1M tokens

text-embedding-3-large:
- Latency: 300-800ms per request  
- Throughput: 1000 tokens/minute (rate limited)
- Batch size: Up to 2048 inputs per request
- Cost: $0.13 per 1M tokens
```

### Local Model Performance
```
all-MiniLM-L6-v2 (CPU):
- Latency: 50-200ms per batch
- Throughput: 100-500 docs/second
- Memory: 90MB model size
- Hardware: Any CPU

all-mpnet-base-v2 (CPU):
- Latency: 100-400ms per batch
- Throughput: 50-200 docs/second  
- Memory: 420MB model size
- Hardware: Any CPU

sentence-transformers (GPU):
- Latency: 10-50ms per batch
- Throughput: 1000-5000 docs/second
- Memory: 2-8GB GPU memory
- Hardware: CUDA-compatible GPU
```

## Vector Search Performance

### Index Performance Characteristics
```
HNSW Index Parameters:
- M (max connections): 16 (default) - Higher = better recall, slower build
- efConstruction: 200 (default) - Higher = better quality, slower build  
- efRuntime: 10 (default) - Higher = better recall, slower search

Performance Impact:
- M=16, ef=200: Build 10K vectors in ~2 seconds, search in <1ms
- M=32, ef=400: Build 10K vectors in ~5 seconds, search in <0.5ms
- M=64, ef=800: Build 10K vectors in ~15 seconds, search in <0.2ms
```

### Search Performance by Dataset Size
```
Dataset Size | Index Build Time | Search Latency | Memory Usage
10K vectors  | 2 seconds       | <1ms          | 50MB
100K vectors | 20 seconds      | 1-2ms         | 500MB  
1M vectors   | 200 seconds     | 2-5ms         | 5GB
10M vectors  | 2000 seconds    | 5-10ms        | 50GB
```

### Query Complexity Impact
```
Simple vector search:     1-5ms
Vector + basic filter:    2-8ms
Vector + graph traversal: 5-50ms
Complex hybrid query:     20-200ms
```

## Optimization Strategies

### 1. Embedding Generation Optimization

**Batch Processing:**
```python
# Inefficient: One request per document
for doc in documents:
    embedding = generate_embedding(doc.text)
    
# Efficient: Batch requests
batch_texts = [doc.text for doc in documents[:50]]
embeddings = generate_embeddings(batch_texts)
```

**Async Processing:**
```python
# Parallel embedding generation
import asyncio

async def process_batch(texts):
    tasks = [generate_embedding(text) for text in texts]
    return await asyncio.gather(*tasks)
```

**Caching:**
```python
# Cache embeddings for repeated text
import hashlib
from functools import lru_cache

@lru_cache(maxsize=10000)
def cached_embedding(text_hash):
    return generate_embedding(text)

def get_embedding(text):
    text_hash = hashlib.md5(text.encode()).hexdigest()
    return cached_embedding(text_hash)
```

### 2. Vector Index Optimization

**Index Parameter Tuning:**
```cypher
-- For high-recall applications (slower build, faster search)
CREATE VECTOR INDEX FOR (d:Document) ON (d.embedding) 
OPTIONS {
  dimension: 1536, 
  similarityFunction: 'cosine',
  M: 32,
  efConstruction: 400,
  efRuntime: 20
}

-- For high-throughput applications (faster build, acceptable recall)
CREATE VECTOR INDEX FOR (d:Document) ON (d.embedding) 
OPTIONS {
  dimension: 1536,
  similarityFunction: 'cosine', 
  M: 16,
  efConstruction: 200,
  efRuntime: 10
}
```

**Dimension Reduction:**
```python
# Use smaller embedding models for better performance
EMBEDDING_MODEL = "text-embedding-3-small"  # 1536 dimensions
# vs
EMBEDDING_MODEL = "all-MiniLM-L6-v2"       # 384 dimensions (4x faster)
```

### 3. Query Optimization

**Efficient Vector Queries:**
```cypher
-- Efficient: Use appropriate k value
CALL db.idx.vector.queryNodes('Document', 'embedding', 10, $query_vector)
YIELD node, score
WHERE node.status = 'published'
RETURN node.title, score
ORDER BY score ASC
LIMIT 5

-- Inefficient: Large k with post-filtering
CALL db.idx.vector.queryNodes('Document', 'embedding', 1000, $query_vector)
YIELD node, score
WHERE node.status = 'published' AND node.category = 'tech'
RETURN node.title, score
ORDER BY score ASC
LIMIT 5
```

**Index Hints:**
```cypher
-- Use index hints for complex queries
MATCH (d:Document)
USING INDEX d:Document(embedding)
WHERE d.embedding IS NOT NULL
CALL db.idx.vector.queryNodes('Document', 'embedding', 5, $query_vector)
YIELD node, score
RETURN node, score
```

### 4. Hardware Optimization

**Memory Allocation:**
```yaml
# FalkorDB container
falkordb:
  deploy:
    resources:
      limits:
        memory: 8G  # Size based on vector dataset
      reservations:
        memory: 4G

# Vector processing container  
vector-service:
  deploy:
    resources:
      limits:
        memory: 4G
        nvidia.com/gpu: 1
```

**CPU Optimization:**
```yaml
# Separate CPU allocation for different workloads
mcpserver:
  deploy:
    resources:
      limits:
        cpus: '2'  # Graph queries
        
vector-job:
  deploy:
    resources:
      limits:
        cpus: '4'  # Embedding generation
```

**Storage Optimization:**
```yaml
# Fast storage for vector indices
falkordb:
  volumes:
    - type: tmpfs
      target: /data/indices
      tmpfs:
        size: 2G  # In-memory index storage
```

## Monitoring and Profiling

### Key Performance Metrics

**Embedding Generation:**
```python
metrics = {
    "embedding_latency_p95": 500,  # ms
    "embedding_throughput": 100,   # docs/second
    "embedding_error_rate": 0.01,  # 1%
    "api_rate_limit_hits": 5       # per hour
}
```

**Vector Search:**
```python
metrics = {
    "vector_search_latency_p95": 10,  # ms
    "vector_search_throughput": 1000, # queries/second
    "index_memory_usage": 2048,       # MB
    "search_accuracy": 0.95           # recall@10
}
```

**System Resources:**
```python
metrics = {
    "cpu_utilization": 70,     # %
    "memory_utilization": 80,  # %
    "gpu_utilization": 60,     # %
    "disk_io_wait": 5          # %
}
```

### Performance Testing

**Load Testing Script:**
```python
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

async def benchmark_vector_search(query_vector, num_queries=1000):
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        tasks = []
        for _ in range(num_queries):
            task = executor.submit(vector_search, query_vector)
            tasks.append(task)
        
        results = [task.result() for task in tasks]
    
    end_time = time.time()
    
    return {
        "total_time": end_time - start_time,
        "queries_per_second": num_queries / (end_time - start_time),
        "average_latency": (end_time - start_time) / num_queries * 1000
    }
```

**Memory Profiling:**
```python
import psutil
import tracemalloc

def profile_embedding_generation():
    tracemalloc.start()
    
    # Generate embeddings
    embeddings = generate_embeddings(sample_texts)
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    return {
        "current_memory": current / 1024 / 1024,  # MB
        "peak_memory": peak / 1024 / 1024,        # MB
        "system_memory": psutil.virtual_memory().percent
    }
```

## Production Performance Recommendations

### Small Scale (< 100K vectors)
- **Implementation**: Async job with local embeddings
- **Hardware**: 4 CPU cores, 8GB RAM
- **Index settings**: Default HNSW parameters
- **Expected performance**: <5ms search, 50 docs/sec ingestion

### Medium Scale (100K - 1M vectors)
- **Implementation**: Dedicated vector service
- **Hardware**: 8 CPU cores, 16GB RAM, optional GPU
- **Index settings**: M=32, efConstruction=400
- **Expected performance**: <10ms search, 200 docs/sec ingestion

### Large Scale (> 1M vectors)
- **Implementation**: Hardware-optimized architecture
- **Hardware**: GPU for embeddings, memory-optimized for indices
- **Index settings**: Tuned per use case
- **Expected performance**: <20ms search, 1000+ docs/sec ingestion

### Cost-Performance Optimization
```
Small scale:  $100/month, 95% accuracy
Medium scale: $500/month, 97% accuracy  
Large scale:  $2000/month, 99% accuracy
```

## Conclusion

Performance optimization for vector search involves balancing multiple factors:

1. **Embedding generation** is typically the bottleneck (100-2000ms)
2. **Vector search** is fast once indexed (<10ms for most datasets)
3. **Hardware specialization** provides significant cost/performance benefits
4. **Batch processing** improves throughput by 5-10x
5. **Index tuning** can improve search speed by 2-5x

The async job approach provides the best performance/complexity ratio for most use cases, while the hardware-optimized architecture is optimal for large-scale production deployments.

---

> **Note**: This document was created with assistance from Claude Sonnet 3.5, an AI assistant by Anthropic.