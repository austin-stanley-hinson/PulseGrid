# PulseGrid Architecture

## MVP Architecture

Agent -> FastAPI Backend -> PostgreSQL -> Next.js Dashboard

## Future Architecture

Agent -> FastAPI Ingestion API -> Kafka -> Worker -> PostgreSQL/Redis -> Dashboard

## Main Components

### Agent

Runs on a machine and collects system metrics such as CPU usage and memory usage.

### Backend

Receives metrics from agents, validates the data, and stores it.

### Database

Stores historical metrics for later analysis and dashboard charts.

### Dashboard

Displays live and historical system metrics.
