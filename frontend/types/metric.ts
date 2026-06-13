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

// Mirrors the Agent table in backend/models.py.
export type Agent = {
  id: number
  agent_id: string
  hostname: string
  status: string
  registered_at: string
  last_seen_at: string
  seconds_since_seen: number
}

export type AgentsResponse = {
  count: number
  agents: Agent[]
}

// Mirrors the Alert table in backend/models.py.
export type Alert = {
  id: number
  agent_id: string
  hostname: string
  alert_type: string
  severity: string
  message: string
  value: number
  threshold: number
  created_at: string
}

export type AlertsResponse = {
  count: number
  alerts: Alert[]
}
