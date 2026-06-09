<p align="center">
  <img src="assets/pulsegrid-logo.png" alt="PulseGrid Logo" width="300"/>
</p>

# PulseGrid

PulseGrid is a distributed event monitoring platform inspired by tools like Datadog. It collects server metrics from lightweight agents, sends them to a backend API, stores historical data, and displays real-time system health on a dashboard.

## Architecture

### Current Phase 2 Architecture

The current Phase 2 implementation uses a Python agent to collect local machine metrics (CPU and memory) and send them as JSON to a FastAPI backend. The backend validates payloads with Pydantic and keeps received metrics in a temporary in-memory store.

```mermaid
flowchart LR
    subgraph Machine["Monitored Machine"]
        Metrics["System Metrics<br/>CPU + Memory"]
        Agent["Python Agent<br/>psutil"]
        Metrics --> Agent
    end

    subgraph Backend["PulseGrid Backend"]
        API["FastAPI App"]
        Validation["Pydantic Validation"]
        MemoryStore["Temporary In-Memory Store<br/>Python List"]
    end

    Agent -->|"HTTP POST /metrics<br/>JSON Payload"| API
    API --> Validation
    Validation --> MemoryStore

    Browser["Browser / Developer"] -->|"GET /"| API
    Browser -->|"GET /metrics"| API
```

### Future Target Architecture

The target architecture expands PulseGrid into a production-ready pipeline where monitored servers send metrics to an ingestion layer, stream through Kafka workers, persist to PostgreSQL and Redis, and power dashboard visualization.

```mermaid
flowchart LR
    subgraph Servers["Monitored Servers"]
        A1["Agent 1<br/>CPU / Memory"]
        A2["Agent 2<br/>Disk / Network"]
        A3["Agent 3<br/>Logs / Health"]
    end

    subgraph Ingestion["Ingestion Layer"]
        API["FastAPI Backend<br/>POST /metrics"]
        Validator["Pydantic Validation"]
    end

    subgraph Stream["Streaming Layer"]
        Kafka["Kafka<br/>Metric Events"]
        Worker["Metric Worker"]
    end

    subgraph Storage["Storage Layer"]
        Postgres["PostgreSQL<br/>Historical Metrics"]
        Redis["Redis<br/>Latest Metrics + Heartbeats"]
    end

    subgraph Visualization["Visualization Layer"]
        Dashboard["Next.js Dashboard"]
        Grafana["Grafana<br/>Optional"]
    end

    A1 -->|"JSON Metrics"| API
    A2 -->|"JSON Metrics"| API
    A3 -->|"JSON Metrics"| API

    API --> Validator
    Validator --> Kafka
    Kafka --> Worker
    Worker --> Postgres
    Worker --> Redis

    Dashboard -->|"REST / WebSocket"| API
    API --> Postgres
    API --> Redis
    Grafana --> Postgres
```

## Planned Features

- Server agents for CPU, memory, disk, and network metrics
- FastAPI backend for metric ingestion
- PostgreSQL for historical metric storage
- Redis for latest metric cache and agent heartbeat tracking
- Kafka for event streaming
- Next.js dashboard for real-time monitoring
- Docker-based local development environment
- Alerting for unhealthy services
## Tech Stack

- **Frontend:** Next.js, TypeScript, Tailwind
- **Backend:** FastAPI, Python
- **Database:** PostgreSQL
- **Cache:** Redis
- **Streaming:** Kafka
- **Infrastructure:** Docker, AWS
- **Monitoring:** Prometheus, Grafana

## Project Structure

- agent/ - Lightweight monitoring agent
- backend/ - API and ingestion service
- frontend/ - Web dashboard
- infra/ - Docker and deployment files
- docs/ - Architecture notes

## Current Goal

Build the first MVP:

1. Create a Python agent that collects CPU and memory usage.
2. Send metrics to a FastAPI backend.
3. Store metrics in PostgreSQL.
4. Display latest metrics in a Next.js dashboard.
