# Async Vector Job Solution

## Overview

A simple, standalone background job that automatically adds vectors to nodes that don't have them yet. This solution follows the KISS principle while providing immediate value with minimal architectural changes.

## Core Concept

**Keep the current implementation unchanged** and add a single background process that:
1. Polls the database for nodes needing vectors
2. Generates embeddings using external APIs
3. Updates nodes with computed vectors
4. Runs continuously or on schedule

## Architecture

```
Claude Desktop → FastMCP Proxy → FalkorDB-MCPServer → FalkorDB
                                                    ↗
Background Job ────────────────────────────────────┘
```

**Key Points:**
- No changes to existing services
- Direct FalkorDB connection for efficiency
- Independent deployment and scaling
- Technology choice freedom (Python for ML)

## Implementation

### Complete Solution: `vector_backfill_job.py`

```python
#!/usr/bin/env python3
"""
Simple background job to add vectors to nodes that don't have them.
Connects directly to FalkorDB and uses OpenAI API for embeddings.
"""

import os
import time
import logging
from typing import List, Dict, Any
import redis
import openai
from falkordb import FalkorDB

# Configuration
FALKORDB_HOST = os.getenv('FALKORDB_HOST', 'localhost')
FALKORDB_PORT = int(os.getenv('FALKORDB_PORT', '6379'))
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '50'))
SLEEP_INTERVAL = int(os.getenv('SLEEP_INTERVAL', '300'))  # 5 minutes

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleVectorJob:
    def __init__(self):
        self.db = FalkorDB(host=FALKORDB_HOST, port=FALKORDB_PORT)
        self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
    def find_nodes_needing_vectors(self, graph_name: str) -> List[Dict]:
        \"\"\"Find nodes that have text but no embedding\"\"\"
        graph = self.db.select_graph(graph_name)
        
        result = graph.query(f\"\"\"
            MATCH (n) 
            WHERE n.text IS NOT NULL 
              AND n.embedding IS NULL
            RETURN n.id as id, n.text as text, labels(n)[0] as label
            LIMIT {BATCH_SIZE}
        \"\"\")
        
        return [{\"id\": row[0], \"text\": row[1], \"label\": row[2]} 
                for row in result.result_set]
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        \"\"\"Generate embeddings using OpenAI API\"\"\"
        try:
            response = self.openai_client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=texts
            )
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            logger.error(f\"Failed to generate embeddings: {e}\")
            raise
    
    def update_nodes_with_embeddings(self, graph_name: str, nodes: List[Dict], embeddings: List[List[float]]):
        \"\"\"Update nodes with their embeddings\"\"\"
        graph = self.db.select_graph(graph_name)
        
        for node, embedding in zip(nodes, embeddings):
            try:
                # Convert embedding to string format for Cypher
                embedding_str = str(embedding).replace('[', '').replace(']', '')
                
                graph.query(f\"\"\"
                    MATCH (n) WHERE n.id = {node['id']}
                    SET n.embedding = vecf32([{embedding_str}])
                \"\"\")
                
                logger.info(f\"Updated node {node['id']} with embedding\")
                
            except Exception as e:
                logger.error(f\"Failed to update node {node['id']}: {e}\")
    
    def process_graph(self, graph_name: str):
        \"\"\"Process one batch of nodes for a graph\"\"\"
        logger.info(f\"Processing graph: {graph_name}\")
        
        # Find nodes needing vectors
        nodes = self.find_nodes_needing_vectors(graph_name)
        if not nodes:
            logger.info(f\"No nodes need vectors in graph {graph_name}\")
            return 0
        
        logger.info(f\"Found {len(nodes)} nodes needing vectors\")
        
        # Generate embeddings
        texts = [node['text'] for node in nodes]
        embeddings = self.generate_embeddings(texts)
        
        # Update database
        self.update_nodes_with_embeddings(graph_name, nodes, embeddings)
        
        return len(nodes)
    
    def get_all_graphs(self) -> List[str]:
        \"\"\"Get list of all graphs in the database\"\"\"
        try:
            return self.db.list()
        except Exception as e:
            logger.error(f\"Failed to list graphs: {e}\")
            return []
    
    def run_once(self):
        \"\"\"Run one iteration of the job\"\"\"
        logger.info(\"Starting vector backfill job\")
        
        graphs = self.get_all_graphs()
        total_processed = 0
        
        for graph_name in graphs:
            try:
                processed = self.process_graph(graph_name)
                total_processed += processed
            except Exception as e:
                logger.error(f\"Error processing graph {graph_name}: {e}\")
                continue
        
        logger.info(f\"Completed job iteration. Processed {total_processed} nodes total\")
        return total_processed
    
    def run_forever(self):
        \"\"\"Run the job continuously\"\"\"
        logger.info(f\"Starting continuous vector backfill job (interval: {SLEEP_INTERVAL}s)\")
        
        while True:
            try:
                self.run_once()
            except Exception as e:
                logger.error(f\"Job iteration failed: {e}\")
            
            logger.info(f\"Sleeping for {SLEEP_INTERVAL} seconds\")
            time.sleep(SLEEP_INTERVAL)

if __name__ == \"__main__\":
    if not OPENAI_API_KEY:
        logger.error(\"OPENAI_API_KEY environment variable required\")
        exit(1)
    
    job = SimpleVectorJob()
    
    # Run once or continuously based on argument
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == \"--once\":
        job.run_once()
    else:
        job.run_forever()
```

### Dependencies: `requirements.txt`

```txt
falkordb>=1.0.0
openai>=1.0.0
redis>=4.0.0
```

## Deployment Options

### Option 1: Docker Container (Recommended)

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy job script
COPY vector_backfill_job.py .

# Run the job
CMD [\"python\", \"vector_backfill_job.py\"]
```

**Add to docker-compose.yml:**
```yaml
services:
  # ... existing services ...
  
  vector-job:
    build: ./vector-job
    environment:
      - FALKORDB_HOST=falkordb
      - FALKORDB_PORT=6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - EMBEDDING_MODEL=text-embedding-3-small
      - BATCH_SIZE=50
      - SLEEP_INTERVAL=300
    depends_on:
      - falkordb
    restart: unless-stopped
```

### Option 2: Cron Job

```bash
# Run every 5 minutes
*/5 * * * * cd /path/to/job && python vector_backfill_job.py --once >> /var/log/vector-job.log 2>&1
```

### Option 3: Systemd Service

```ini
[Unit]
Description=FalkorDB Vector Backfill Job
After=network.target

[Service]
Type=simple
User=vector-job
WorkingDirectory=/opt/vector-job
ExecStart=/usr/bin/python3 vector_backfill_job.py
Restart=always
RestartSec=30
Environment=FALKORDB_HOST=localhost
Environment=OPENAI_API_KEY=your-key-here

[Install]
WantedBy=multi-user.target
```

## Configuration

### Environment Variables

```bash
# Required
export OPENAI_API_KEY=\"sk-...\"

# Optional (with defaults)
export FALKORDB_HOST=\"localhost\"
export FALKORDB_PORT=\"6379\"
export EMBEDDING_MODEL=\"text-embedding-3-small\"  # or text-embedding-3-large
export BATCH_SIZE=\"50\"                           # Adjust for rate limits
export SLEEP_INTERVAL=\"300\"                      # 5 minutes between runs
```

### Embedding Model Options

```bash
# OpenAI Models
EMBEDDING_MODEL=\"text-embedding-3-small\"   # Fast, cost-effective
EMBEDDING_MODEL=\"text-embedding-3-large\"   # Higher quality, more expensive

# Future: Local models (requires additional dependencies)
EMBEDDING_MODEL=\"all-MiniLM-L6-v2\"         # Fast local model
EMBEDDING_MODEL=\"all-mpnet-base-v2\"        # Better quality local model
```

## Usage Flow

### 1. User Adds Data
```cypher
-- Via existing falkordb_query tool
CREATE (d:Document {
  id: 123,
  text: \"FalkorDB supports vector search\",
  created_at: datetime()
})
```

### 2. Job Automatically Processes
```
2024-01-15 10:05:00 INFO Starting vector backfill job
2024-01-15 10:05:01 INFO Processing graph: knowledge_base
2024-01-15 10:05:01 INFO Found 1 nodes needing vectors
2024-01-15 10:05:02 INFO Updated node 123 with embedding
2024-01-15 10:05:02 INFO Completed job iteration. Processed 1 nodes total
```

### 3. User Can Search
```cypher
-- Via existing falkordb_query tool
CALL db.idx.vector.queryNodes(
  'Document', 'embedding', 5, 
  vecf32([0.1, 0.2, 0.3, ...])
) YIELD node, score
RETURN node.text, score
```

## Monitoring and Operations

### Check Job Status
```bash
# View logs
docker logs vector-job

# Check if job is running
docker ps | grep vector-job

# Run manually once
docker exec vector-job python vector_backfill_job.py --once
```

### Performance Tuning
```bash
# For rate-limited APIs
export BATCH_SIZE=25
export SLEEP_INTERVAL=600  # 10 minutes

# For high-throughput scenarios
export BATCH_SIZE=100
export SLEEP_INTERVAL=60   # 1 minute
```

### Error Handling
- **API failures**: Job continues with next batch
- **Database errors**: Logged but don't stop processing
- **Network issues**: Automatic retry on next iteration
- **Invalid data**: Skipped with error logging

## Advanced Features

### Priority Processing
```python
# Modify find_nodes_needing_vectors to prioritize recent content
def find_nodes_needing_vectors(self, graph_name: str) -> List[Dict]:
    graph = self.db.select_graph(graph_name)
    
    # Priority 1: Recent nodes (last hour)
    result = graph.query(f\"\"\"
        MATCH (n) 
        WHERE n.text IS NOT NULL 
          AND n.embedding IS NULL
          AND n.created_at > datetime() - duration('PT1H')
        RETURN n.id as id, n.text as text, labels(n)[0] as label
        LIMIT {BATCH_SIZE}
    \"\"\")
    
    if result.result_set:
        return [{\"id\": row[0], \"text\": row[1], \"label\": row[2]} 
                for row in result.result_set]
    
    # Priority 2: Older nodes
    result = graph.query(f\"\"\"
        MATCH (n) 
        WHERE n.text IS NOT NULL 
          AND n.embedding IS NULL
        RETURN n.id as id, n.text as text, labels(n)[0] as label
        LIMIT {BATCH_SIZE}
    \"\"\")
    
    return [{\"id\": row[0], \"text\": row[1], \"label\": row[2]} 
            for row in result.result_set]
```

### Multi-Tenant Support
```python
# Process each tenant separately
def process_tenant_graphs(self, tenant_prefix: str):
    graphs = [g for g in self.get_all_graphs() if g.startswith(tenant_prefix)]
    for graph_name in graphs:
        self.process_graph(graph_name)
```

### Progress Tracking
```python
# Add progress tracking to database
def track_progress(self, graph_name: str, processed: int):
    graph = self.db.select_graph(graph_name)
    graph.query(f\"\"\"
        MERGE (p:VectorProgress {{graph: '{graph_name}'}})
        SET p.last_run = datetime(),
            p.nodes_processed = COALESCE(p.nodes_processed, 0) + {processed},
            p.last_batch_size = {processed}
    \"\"\")
```

## Benefits

### ✅ Immediate Value
- **Zero architectural changes**: Works with existing setup
- **Fast implementation**: Single file, ~150 lines of code
- **Easy deployment**: Just add one container
- **Immediate automation**: Nodes get vectors within minutes

### ✅ Operational Simplicity
- **Easy to understand**: Single Python file
- **Easy to debug**: Clear logs, can run manually
- **Easy to configure**: Environment variables only
- **Easy to monitor**: Standard Docker logging

### ✅ Cost Effectiveness
- **On-demand processing**: Only runs when needed
- **Batch API calls**: Efficient use of embedding APIs
- **Resource efficient**: Minimal CPU/memory footprint
- **No idle costs**: Unlike always-on GPU instances

### ✅ Flexibility
- **Technology choice**: Python for ML without affecting other services
- **Deployment options**: Docker, cron, systemd
- **Embedding models**: Easy to switch between OpenAI, local models
- **Scheduling**: Configurable intervals and batch sizes

## Limitations

### ❌ Not Real-time
- **Batch processing**: 5-minute delays by default
- **No immediate feedback**: Users don't know when vectorization completes
- **Queue visibility**: No way to see pending work

### ❌ Limited Control
- **No user interaction**: Can't trigger vectorization on demand
- **No prioritization**: Processes all graphs equally
- **No selective processing**: Can't target specific node types

### ❌ Monitoring Gaps
- **Separate process**: Additional monitoring required
- **No metrics endpoint**: Basic logging only
- **No alerting**: Manual log monitoring required

## Future Enhancements

### Phase 2: Enhanced Monitoring
- Add metrics endpoint for Prometheus
- Implement structured logging
- Add health check endpoint

### Phase 3: User Control
- Add MCP tool for job status
- Implement priority queues
- Add selective processing options

### Phase 4: Advanced Features
- Support for multiple embedding models
- Intelligent retry logic
- Performance optimization

## Conclusion

The async vector job solution provides immediate value with minimal complexity. It transforms the existing vector-capable setup into a fully autonomous system while maintaining the KISS principle and requiring no changes to existing services.

This approach is perfect for:
- **MVP implementations**: Quick time-to-value
- **Small to medium deployments**: Optimal complexity/benefit ratio
- **Development environments**: Easy to set up and debug
- **Production systems**: Reliable and maintainable

The solution can evolve over time to add more sophisticated features while maintaining its core simplicity and effectiveness.

---

> **Note**: This document was created with assistance from Claude Sonnet 3.5, an AI assistant by Anthropic.