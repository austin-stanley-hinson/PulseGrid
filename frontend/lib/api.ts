import type { MetricsResponse } from "@/types/metric"

// Backend URL — override with NEXT_PUBLIC_BACKEND_URL env var in production
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://127.0.0.1:8000"

export async function fetchMetrics(): Promise<MetricsResponse> {
  const response = await fetch(`${BACKEND_URL}/metrics`)

  if (!response.ok) {
    throw new Error(`Failed to fetch metrics: ${response.status}`)
  }

  return response.json()
}
