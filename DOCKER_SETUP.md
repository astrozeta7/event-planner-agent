# Event Planner Agent - Docker Setup

## Quick Start

### Prerequisites
- Docker Desktop installed
- Docker Compose v2.0+
- 4GB+ RAM available

### 1. Clone and Setup
```bash
cd event-planner-agent
cp .env.example .env
# Edit .env with your credentials (optional for local dev)
```

### 2. Build and Start All Services
```bash
docker-compose up --build
```

This will start:
- **PostgreSQL** (port 5432) - Database with schema and seed data
- **Redis** (port 6379) - Caching layer
- **MCP PostgreSQL Server** (port 3001) - Database MCP interface
- **MCP Google Drive Server** (port 3002) - Google Drive MCP interface
- **FastAPI Application** (port 8000) - Main API
- **Nginx** (port 80) - Reverse proxy

### 3. Verify Services

**Check all services are healthy:**
```bash
docker-compose ps
```

**Test API health:**
```bash
curl http://localhost/health
# or
curl http://localhost:8000/health
```

**Test MCP PostgreSQL server:**
```bash
curl http://localhost:3001/health
```

**Test MCP Google Drive server:**
```bash
curl http://localhost:3002/health
```

### 4. Test Event Planning Endpoint

```bash
curl -X POST http://localhost/plan-event \
  -H "Content-Type: application/json" \
  -d '{
    "event_date": "2025-06-15",
    "location": "San Francisco",
    "number_of_guests": 100,
    "cuisine_preferences": ["Italian", "Indian"],
    "needs_event_room": true,
    "budget_per_guest": 100
  }'
```

### 5. Access API Documentation
- Swagger UI: http://localhost/docs
- ReDoc: http://localhost/redoc

---

## Docker Commands

### Start services in background
```bash
docker-compose up -d
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f postgres
docker-compose logs -f mcp-postgres
```

### Stop services
```bash
docker-compose down
```

### Stop and remove volumes (clean slate)
```bash
docker-compose down -v
```

### Rebuild specific service
```bash
docker-compose up --build api
```

### Execute commands in containers
```bash
# Access PostgreSQL
docker-compose exec postgres psql -U postgres -d event_planner_db

# Access API container
docker-compose exec api bash

# Run migrations
docker-compose exec api python -m alembic upgrade head
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                                                           │
│  ┌─────────┐    ┌──────────┐    ┌──────────┐           │
│  │  Nginx  │───►│   API    │───►│PostgreSQL│           │
│  │  :80    │    │  :8000   │    │  :5432   │           │
│  └────┬────┘    └────┬─────┘    └──────────┘           │
│       │              │                                    │
│       │              │         ┌──────────┐             │
│       │              └────────►│  Redis   │             │
│       │                        │  :6379   │             │
│       │                        └──────────┘             │
│       │                                                  │
│       │         ┌──────────────┐  ┌──────────────┐     │
│       ├────────►│ MCP Postgres │  │ MCP GDrive   │     │
│       │         │    :3001     │  │    :3002     │     │
│       │         └──────────────┘  └──────────────┘     │
└───────┴──────────────────────────────────────────────────┘
```

---

## Environment Variables

Create `.env` file from `.env.example`:

```bash
# Database
DB_USER=postgres
DB_PASSWORD=your_secure_password

# Google Drive (optional)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
```

---

## Development Workflow

### Hot Reload (Development Mode)
The API container is configured with `--reload` flag. Changes to Python files will automatically restart the server.

### Database Migrations
```bash
# Create new migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec api alembic upgrade head

# Rollback
docker-compose exec api alembic downgrade -1
```

### Reset Database
```bash
docker-compose down -v
docker-compose up -d postgres
# Wait for postgres to be ready
docker-compose up -d
```

---

## Production Deployment

### Build for Production
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

### Environment Variables for Production
- Set strong `DB_PASSWORD`
- Configure SSL certificates in `nginx/ssl/`
- Set `DEBUG=false`
- Use secrets management (AWS Secrets Manager, HashiCorp Vault)

### Health Checks
All services have health checks configured:
- PostgreSQL: `pg_isready`
- Redis: `redis-cli ping`
- API: `curl /health`
- MCP servers: `wget /health`

---

## Troubleshooting

### Port conflicts
If ports are already in use, modify `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change host port
```

### Database connection issues
```bash
# Check if postgres is healthy
docker-compose ps postgres

# View postgres logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres pg_isready -U postgres
```

### MCP server issues
```bash
# Check MCP server logs
docker-compose logs mcp-postgres
docker-compose logs mcp-gdrive

# Test MCP endpoints
curl http://localhost:3001/health
curl http://localhost:3002/health
```

### Container won't start
```bash
# Remove all containers and volumes
docker-compose down -v

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up
```

---

## Monitoring

### View resource usage
```bash
docker stats
```

### Container health status
```bash
docker-compose ps
```

---

## Next Steps

1. **Add Monitoring**: Uncomment Prometheus/Grafana in `docker-compose.yml`
2. **Configure SSL**: Add certificates to `nginx/ssl/`
3. **Set up CI/CD**: Build and push images to registry
4. **Deploy to Cloud**: AWS ECS, GCP Cloud Run, or Kubernetes
5. **Add More MCP Servers**: Slack, Stripe, Calendar integrations

---

## Support

For issues or questions:
- GitHub: https://github.com/astrozeta7/event-planner-agent
- Documentation: See `DOCKER_MCP_ARCHITECTURE.md`
