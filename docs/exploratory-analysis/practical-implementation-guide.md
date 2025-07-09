# Practical Implementation Guide

## Quick Start: Add Vector Capabilities in 15 Minutes

This guide provides step-by-step instructions for adding automatic vector ingestion to your existing FalkorDB FastMCP Proxy setup.

## Prerequisites

- Existing FalkorDB FastMCP Proxy deployment
- OpenAI API key (or other embedding service)
- Docker and docker-compose

## Step 1: Create Vector Job Directory

```bash
# In your project root
mkdir vector-job
cd vector-job
```

## Step 2: Create Job Script

Create `vector_backfill_job.py`:

```python
#!/usr/bin/env python3
import os
import time
import logging
from typing import List, Dict
import openai
from falkordb import FalkorDB

# Configuration
FALKORDB_HOST = os.getenv('FALKORDB_HOST', 'localhost')
FALKORDB_PORT = int(os.getenv('FALKORDB_PORT', '6379'))
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '50'))
SLEEP_INTERVAL = int(os.getenv('SLEEP_INTERVAL', '300'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleVectorJob:
    def __init__(self):
        self.db = FalkorDB(host=FALKORDB_HOST, port=FALKORDB_PORT)
        self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
    def find_nodes_needing_vectors(self, graph_name: str) -> List[Dict]:
        graph = self.db.select_graph(graph_name)
        result = graph.query(f\"\"\"
            MATCH (n) 
            WHERE n.text IS NOT NULL AND n.embedding IS NULL
            RETURN n.id as id, n.text as text
            LIMIT {BATCH_SIZE}
        \"\"\")
        return [{\"id\": row[0], \"text\": row[1]} for row in result.result_set]
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        response = self.openai_client.embeddings.create(
            model=EMBEDDING_MODEL, input=texts
        )
        return [embedding.embedding for embedding in response.data]
    
    def update_nodes_with_embeddings(self, graph_name: str, nodes: List[Dict], embeddings: List[List[float]]):
        graph = self.db.select_graph(graph_name)
        for node, embedding in zip(nodes, embeddings):
            embedding_str = str(embedding).replace('[', '').replace(']', '')
            graph.query(f\"\"\"
                MATCH (n) WHERE n.id = {node['id']}
                SET n.embedding = vecf32([{embedding_str}])
            \"\"\")
            logger.info(f\"Updated node {node['id']} with embedding\")
    
    def process_graph(self, graph_name: str) -> int:
        nodes = self.find_nodes_needing_vectors(graph_name)
        if not nodes:
            return 0
            
        texts = [node['text'] for node in nodes]
        embeddings = self.generate_embeddings(texts)
        self.update_nodes_with_embeddings(graph_name, nodes, embeddings)
        return len(nodes)
    
    def run_once(self):
        graphs = self.db.list()
        total = sum(self.process_graph(g) for g in graphs)
        logger.info(f\"Processed {total} nodes total\")
        return total
    
    def run_forever(self):
        while True:
            try:
                self.run_once()
            except Exception as e:
                logger.error(f\"Job failed: {e}\")
            time.sleep(SLEEP_INTERVAL)

if __name__ == \"__main__\":
    import sys
    job = SimpleVectorJob()
    if len(sys.argv) > 1 and sys.argv[1] == \"--once\":
        job.run_once()
    else:
        job.run_forever()
```

## Step 3: Create Dependencies File

Create `requirements.txt`:

```txt
falkordb>=1.0.0
openai>=1.0.0
```

## Step 4: Create Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY vector_backfill_job.py .
CMD [\"python\", \"vector_backfill_job.py\"]
```

## Step 5: Update Docker Compose

Add to your existing `docker-compose.yml`:

```yaml
services:
  # ... your existing services ...
  
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

## Step 6: Set Environment Variable

Create `.env` file or export:

```bash
export OPENAI_API_KEY=\"sk-your-openai-api-key-here\"
```

## Step 7: Deploy

```bash
# Build and start the vector job
docker-compose up -d vector-job

# Check logs
docker-compose logs -f vector-job
```

## Step 8: Test the System

### Add Test Data
Use your existing `falkordb_query` tool:

```cypher
CREATE (d:Document {
  id: 1,
  text: \"FalkorDB is a graph database with vector search capabilities\",
  created_at: datetime()
})
```

### Create Vector Index
```cypher
CREATE VECTOR INDEX FOR (d:Document) ON (d.embedding) 
OPTIONS {dimension:1536, similarityFunction:'cosine'}
```

### Wait and Check
After 5 minutes, check if the vector was added:

```cypher
MATCH (d:Document {id: 1}) 
RETURN d.text, d.embedding IS NOT NULL as has_embedding
```

### Test Vector Search
```cypher
CALL db.idx.vector.queryNodes(
  'Document', 'embedding', 5, 
  vecf32([0.1, 0.2, 0.3])  -- dummy query vector
) YIELD node, score
RETURN node.text, score
```

## Monitoring and Troubleshooting

### Check Job Status
```bash
# View recent logs
docker-compose logs --tail=50 vector-job

# Check if container is running
docker-compose ps vector-job

# Run job manually once
docker-compose exec vector-job python vector_backfill_job.py --once
```

### Common Issues

**Issue: \"OPENAI_API_KEY environment variable required\"**
```bash
# Solution: Set the API key
echo \"OPENAI_API_KEY=sk-your-key\" >> .env
docker-compose up -d vector-job
```

**Issue: \"Failed to connect to FalkorDB\"**
```bash
# Solution: Check FalkorDB is running
docker-compose ps falkordb
docker-compose logs falkordb
```

**Issue: \"No nodes need vectors\"**
```bash
# Solution: Add test data with text property
# Use falkordb_query tool to create nodes with 'text' property
```

**Issue: Rate limiting from OpenAI**
```bash
# Solution: Reduce batch size and increase interval
docker-compose exec vector-job sh -c \"
export BATCH_SIZE=25
export SLEEP_INTERVAL=600
python vector_backfill_job.py --once
\"
```

## Configuration Options

### Embedding Models

```yaml
# Fast and cost-effective
- EMBEDDING_MODEL=text-embedding-3-small

# Higher quality, more expensive  
- EMBEDDING_MODEL=text-embedding-3-large
```

### Performance Tuning

```yaml
# For high-volume processing
- BATCH_SIZE=100
- SLEEP_INTERVAL=60

# For rate-limited APIs
- BATCH_SIZE=25
- SLEEP_INTERVAL=600

# For development/testing
- BATCH_SIZE=10
- SLEEP_INTERVAL=30
```

### Resource Limits

```yaml
vector-job:
  # ... other config ...
  deploy:
    resources:
      limits:
        cpus: '1'
        memory: 1G
      reservations:
        cpus: '0.5'
        memory: 512M
```

## Advanced Usage

### Priority Processing

Modify the job to prioritize recent content:

```python
def find_nodes_needing_vectors(self, graph_name: str) -> List[Dict]:
    graph = self.db.select_graph(graph_name)
    
    # Try recent nodes first
    result = graph.query(f\"\"\"
        MATCH (n) 
        WHERE n.text IS NOT NULL 
          AND n.embedding IS NULL
          AND n.created_at > datetime() - duration('PT1H')
        RETURN n.id as id, n.text as text
        LIMIT {BATCH_SIZE}
    \"\"\")
    
    if result.result_set:
        return [{\"id\": row[0], \"text\": row[1]} for row in result.result_set]
    
    # Fall back to any nodes
    result = graph.query(f\"\"\"
        MATCH (n) 
        WHERE n.text IS NOT NULL AND n.embedding IS NULL
        RETURN n.id as id, n.text as text
        LIMIT {BATCH_SIZE}
    \"\"\")
    
    return [{\"id\": row[0], \"text\": row[1]} for row in result.result_set]
```

### Multi-Tenant Support

For tenant-isolated processing:

```python
def process_tenant_graphs(self, tenant_prefix: str):
    \"\"\"Process only graphs for a specific tenant\"\"\"
    all_graphs = self.db.list()
    tenant_graphs = [g for g in all_graphs if g.startswith(f\"{tenant_prefix}_\")]
    
    for graph_name in tenant_graphs:
        self.process_graph(graph_name)
```

### Progress Tracking

Add progress tracking to the database:

```python
def track_progress(self, graph_name: str, processed: int):
    graph = self.db.select_graph(graph_name)
    graph.query(f\"\"\"
        MERGE (p:VectorProgress {{graph: '{graph_name}'}})
        SET p.last_run = datetime(),
            p.total_processed = COALESCE(p.total_processed, 0) + {processed},
            p.last_batch_size = {processed}
    \"\"\")
```

## Production Considerations

### Security

```yaml
# Use secrets for API keys
secrets:
  openai_api_key:
    external: true

services:
  vector-job:
    secrets:
      - openai_api_key
    environment:
      - OPENAI_API_KEY_FILE=/run/secrets/openai_api_key
```

### Monitoring

```yaml
# Add health check
vector-job:
  healthcheck:
    test: [\"CMD\", \"python\", \"-c\", \"import requests; requests.get('http://localhost:8080/health')\"]
    interval: 30s
    timeout: 10s
    retries: 3
```

### Logging

```yaml
# Structured logging
vector-job:
  logging:
    driver: \"json-file\"
    options:
      max-size: \"10m\"
      max-file: \"3\"
```

### Resource Management

```yaml
# Prevent resource exhaustion
vector-job:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
    restart_policy:
      condition: on-failure
      delay: 30s
      max_attempts: 3
```

## Integration with Existing Workflows

### Manual Triggering

```bash
# Trigger immediate processing
docker-compose exec vector-job python vector_backfill_job.py --once

# Process specific graph
docker-compose exec vector-job python -c \"
from vector_backfill_job import SimpleVectorJob
job = SimpleVectorJob()
job.process_graph('your_graph_name')
\"
```

### Scheduled Processing

```bash
# Add to crontab for additional control
0 */6 * * * docker-compose -f /path/to/docker-compose.yml exec vector-job python vector_backfill_job.py --once
```

### CI/CD Integration

```yaml
# In your deployment pipeline
- name: Deploy vector job
  run: |
    docker-compose up -d vector-job
    docker-compose exec vector-job python vector_backfill_job.py --once
    docker-compose logs vector-job
```

## Next Steps

### Phase 2: Enhanced Monitoring
- Add metrics endpoint
- Implement structured logging  
- Add health checks

### Phase 3: User Control
- Add MCP tools for job control
- Implement job status reporting
- Add selective processing

### Phase 4: Scale Optimization
- Implement hardware-optimized architecture
- Add dedicated vector MCP service
- Optimize for production workloads

## Summary

You now have a fully functional automatic vector ingestion system that:

✅ **Works with existing setup** - No changes to current services  
✅ **Processes automatically** - Nodes get vectors within 5 minutes  
✅ **Easy to deploy** - Single Docker container  
✅ **Easy to monitor** - Standard Docker logging  
✅ **Cost effective** - Only runs when needed  
✅ **Configurable** - Environment variables for all settings  

The system transforms your existing vector-capable FalkorDB setup into a fully autonomous vector search platform while maintaining simplicity and reliability.