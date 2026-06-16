import type { MetricsResponse, AgentsResponse, AlertsResponse } from "@/types/metric"

// Backend URL — override with NEXT_PUBLIC_BACKEND_URL env var in production
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://127.0.0.1:8000"

async function get<T>(path: string): Promise<T> {
  const response = await fetch(`${BACKEND_URL}${path}`)
  if (!response.ok) throw new Error(`Request failed: ${response.status}`)
  return response.json()
}

export const fetchMetrics = () => get<MetricsResponse>("/metrics")
export const fetchAgents  = () => get<AgentsResponse>("/agents")
export const fetchAlerts  = () => get<AlertsResponse>("/alerts")
