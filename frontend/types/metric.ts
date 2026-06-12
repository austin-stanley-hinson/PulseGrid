// Mirrors the Metric table in backend/models.py.
// If the backend schema changes, update this to match.
export type Metric = {
  id: number
  agent_id: string
  hostname: string
  cpu_percent: number
  memory_percent: number
  memory_used: number
  memory_total: number
  timestamp: string
  created_at: string
}

export type MetricsResponse = {
  count: number
  metrics: Metric[]
}
