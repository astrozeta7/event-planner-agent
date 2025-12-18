# Docker + MCP Architecture for Event Planner Agent

## Overview

This document outlines a production-ready, containerized architecture using Docker and Model Context Protocol (MCP) servers. This approach provides:

- **Portability**: Run anywhere Docker runs
- **Scalability**: Easy horizontal scaling with container orchestration
- **Isolation**: Each service in its own container
- **Reproducibility**: Consistent environments across dev/staging/prod
- **MCP Integration**: Standardized AI-to-service communication

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Docker Network                           │
│                      (event-planner-network)                     │
│                                                                   │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │   FastAPI    │      │  PostgreSQL  │      │    Redis     │  │
│  │  Container   │◄────►│  Container   │      │  Container   │  │
│  │  (Port 8000) │      │  (Port 5432) │      │  (Port 6379) │  │
│  └──────┬───────┘      └──────────────┘      └──────────────┘  │
│         │                                                         │
│         │ MCP Protocol                                           │
│         ▼                                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              MCP Server Layer (Sidecar)                  │   │
│  │                                                           │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │ PostgreSQL   │  │ Google Drive │  │   Slack      │  │   │
│  │  │ MCP Server   │  │ MCP Server   │  │ MCP Server   │  │   │
│  │  │ (stdio/http) │  │ (stdio/http) │  │ (stdio/http) │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  │                                                           │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │  Calendar    │  │   Stripe     │  │   Twilio     │  │   │
│  │  │ MCP Server   │  │ MCP Server   │  │ MCP Server   │  │   │
│  │  │ (stdio/http) │  │ (stdio/http) │  │ (stdio/http) │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────┐      ┌──────────────┐                         │
│  │   Nginx      │      │  Prometheus  │                         │
│  │  (Reverse    │      │  (Metrics)   │                         │
│  │   Proxy)     │      │              │                         │
│  └──────────────┘      └──────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
         │                        │
         ▼                        ▼
    External Users          Monitoring Dashboard
```

---

## Docker Compose Stack

### Services Breakdown

#### 1. **FastAPI Application Container**
- **Image**: Custom Python 3.11 image
- **Purpose**: Main API server
- **Exposes**: Port 8000
- **Environment**: 
  - Database connection strings
  - MCP server endpoints
  - API keys (from secrets)
- **Volumes**: 
  - Application code (for development)
  - MCP config files

#### 2. **PostgreSQL Container**
- **Image**: `postgres:15-alpine`
- **Purpose**: Primary database
- **Exposes**: Port 5432 (internal only)
- **Volumes**: 
  - Persistent data volume
  - Init scripts (schema.sql, seed_data.sql)
- **Health Check**: `pg_isready`

#### 3. **Redis Container**
- **Image**: `redis:7-alpine`
- **Purpose**: Caching, session storage, rate limiting
- **Exposes**: Port 6379 (internal only)
- **Volumes**: Persistent cache data

#### 4. **MCP Sidecar Container**
- **Image**: Custom Node.js image with MCP servers
- **Purpose**: Run all MCP servers in one container
- **Communication**: HTTP endpoints or stdio via shared volumes
- **Environment**: API keys for external services

#### 5. **Nginx Container**
- **Image**: `nginx:alpine`
- **Purpose**: Reverse proxy, SSL termination, load balancing
- **Exposes**: Ports 80, 443
- **Volumes**: SSL certificates, nginx config

#### 6. **Prometheus + Grafana (Optional)**
- **Purpose**: Metrics collection and visualization
- **Exposes**: Prometheus 9090, Grafana 3000

---

## MCP Server Integration Strategies

### Strategy 1: HTTP-Based MCP Servers (Recommended for Docker)

**Pros:**
- Network-native, works perfectly with Docker networking
- Easy to scale horizontally
- Language-agnostic
- Can be deployed as separate microservices

**Implementation:**
```yaml
# docker-compose.yml
services:
  mcp-postgres:
    image: mcp-postgres-server:latest
    environment:
      - DATABASE_URL=postgresql://postgres:5432/event_planner_db
    ports:
      - "3001:3000"
    networks:
      - event-planner-network

  mcp-gdrive:
    image: mcp-gdrive-server:latest
    environment:
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
    ports:
      - "3002:3000"
    networks:
      - event-planner-network
```

**FastAPI Integration:**
```python
import httpx

class MCPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def query(self, tool: str, params: dict):
        response = await self.client.post(
            f"{self.base_url}/mcp/tools/{tool}",
            json=params
        )
        return response.json()

# Usage
postgres_mcp = MCPClient("http://mcp-postgres:3000")
gdrive_mcp = MCPClient("http://mcp-gdrive:3000")
```

### Strategy 2: Stdio-Based MCP Servers (Sidecar Pattern)

**Pros:**
- Official MCP protocol
- Lower latency
- Simpler for single-container deployments

**Implementation:**
```dockerfile
# Dockerfile.mcp-sidecar
FROM node:20-alpine

# Install all MCP servers
RUN npm install -g \
    @modelcontextprotocol/server-postgres \
    @modelcontextprotocol/server-gdrive \
    @modelcontextprotocol/server-slack

# Copy MCP orchestrator script
COPY mcp-orchestrator.js /app/
WORKDIR /app

CMD ["node", "mcp-orchestrator.js"]
```

**Python Integration via Subprocess:**
```python
import asyncio
import json

class StdioMCPClient:
    def __init__(self, command: list):
        self.process = None
        self.command = command
    
    async def start(self):
        self.process = await asyncio.create_subprocess_exec(
            *self.command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    
    async def call_tool(self, tool: str, params: dict):
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": tool, "arguments": params},
            "id": 1
        }
        self.process.stdin.write(json.dumps(request).encode() + b'\n')
        await self.process.stdin.drain()
        
        response = await self.process.stdout.readline()
        return json.loads(response)
```

### Strategy 3: Hybrid Approach (Best for Production)

- **Critical services** (PostgreSQL, Redis): Direct connection
- **External integrations** (Google Drive, Slack, Stripe): MCP servers
- **AI/LLM operations**: MCP protocol

---

## Docker Compose Configuration

### Complete `docker-compose.yml`

```yaml
version: '3.9'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: event-planner-db
    environment:
      POSTGRES_DB: event_planner_db
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-postgres}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql
      - ./database/seed_data.sql:/docker-entrypoint-initdb.d/02-seed.sql
    ports:
      - "5432:5432"
    networks:
      - event-planner-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: event-planner-redis
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - event-planner-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # FastAPI Application
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: event-planner-api
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD:-postgres}@postgres:5432/event_planner_db
      - REDIS_URL=redis://redis:6379
      - MCP_POSTGRES_URL=http://mcp-postgres:3000
      - MCP_GDRIVE_URL=http://mcp-gdrive:3000
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - event-planner-network
    volumes:
      - ./app:/app/app:ro
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # MCP PostgreSQL Server
  mcp-postgres:
    build:
      context: ./mcp-servers/postgres
      dockerfile: Dockerfile
    container_name: mcp-postgres-server
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD:-postgres}@postgres:5432/event_planner_db
    ports:
      - "3001:3000"
    depends_on:
      - postgres
    networks:
      - event-planner-network

  # MCP Google Drive Server
  mcp-gdrive:
    build:
      context: ./mcp-servers/gdrive
      dockerfile: Dockerfile
    container_name: mcp-gdrive-server
    environment:
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
      - GOOGLE_REDIRECT_URI=${GOOGLE_REDIRECT_URI}
    ports:
      - "3002:3000"
    networks:
      - event-planner-network
    volumes:
      - gdrive_tokens:/app/tokens

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: event-planner-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    networks:
      - event-planner-network

  # Prometheus (Monitoring)
  prometheus:
    image: prom/prometheus:latest
    container_name: event-planner-prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - event-planner-network

  # Grafana (Visualization)
  grafana:
    image: grafana/grafana:latest
    container_name: event-planner-grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    networks:
      - event-planner-network

networks:
  event-planner-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  gdrive_tokens:
  prometheus_data:
  grafana_data:
```

---

## Dockerfile for FastAPI Application

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY database/ ./database/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## MCP Server Dockerfiles

### PostgreSQL MCP Server

```dockerfile
# mcp-servers/postgres/Dockerfile
FROM node:20-alpine

WORKDIR /app

# Install MCP PostgreSQL server
RUN npm install -g @modelcontextprotocol/server-postgres express

# Copy HTTP wrapper
COPY server.js .

EXPOSE 3000

CMD ["node", "server.js"]
```

```javascript
// mcp-servers/postgres/server.js
const express = require('express');
const { spawn } = require('child_process');

const app = express();
app.use(express.json());

const DATABASE_URL = process.env.DATABASE_URL;

app.post('/mcp/tools/:tool', async (req, res) => {
  const { tool } = req.params;
  const params = req.body;

  const mcp = spawn('npx', [
    '@modelcontextprotocol/server-postgres',
    DATABASE_URL
  ]);

  const request = {
    jsonrpc: '2.0',
    method: 'tools/call',
    params: { name: tool, arguments: params },
    id: 1
  };

  mcp.stdin.write(JSON.stringify(request) + '\n');
  mcp.stdin.end();

  let output = '';
  mcp.stdout.on('data', (data) => {
    output += data.toString();
  });

  mcp.on('close', () => {
    try {
      const response = JSON.parse(output);
      res.json(response);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });
});

app.listen(3000, () => {
  console.log('MCP PostgreSQL server listening on port 3000');
});
```

---

## Development vs Production

### Development Setup
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Run migrations
docker-compose exec api python -m alembic upgrade head

# Access database
docker-compose exec postgres psql -U postgres -d event_planner_db
```

### Production Setup
```yaml
# docker-compose.prod.yml
version: '3.9'

services:
  api:
    image: ghcr.io/astrozeta7/event-planner-api:latest
    restart: always
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 1G
    environment:
      - ENV=production
      - LOG_LEVEL=info
    # ... rest of config
```

---

## Key Benefits of This Architecture

1. **Scalability**: Scale API containers independently
2. **Isolation**: Each service in its own container
3. **Portability**: Deploy to any Docker-compatible platform (AWS ECS, GCP Cloud Run, Kubernetes)
4. **MCP Integration**: Standardized AI-service communication
5. **Observability**: Built-in monitoring with Prometheus/Grafana
6. **Security**: Network isolation, secrets management
7. **Development Parity**: Same environment dev to prod

---

## Next Steps

1. Create Dockerfiles for each service
2. Build MCP HTTP wrapper servers
3. Set up docker-compose.yml
4. Configure environment variables and secrets
5. Add health checks and monitoring
6. Set up CI/CD pipeline for container builds
7. Deploy to cloud container platform

---

## Deployment Targets

- **AWS**: ECS Fargate, EKS
- **GCP**: Cloud Run, GKE
- **Azure**: Container Instances, AKS
- **Self-hosted**: Docker Swarm, Kubernetes
- **Platform**: Railway, Render, Fly.io
