"use client"

import { useEffect, useState } from "react"
import { fetchMetrics } from "@/lib/api"
import type { Metric } from "@/types/metric"

// Converts bytes to a readable GB string
function bytesToGB(bytes: number): string {
  return (bytes / 1024 ** 3).toFixed(1) + " GB"
}

// Returns a Tailwind color class based on the percentage value
function statusColor(percent: number): string {
  if (percent >= 90) return "text-red-500"
  if (percent >= 75) return "text-yellow-500"
  return "text-green-500"
}

function StatCard({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
      <p className="text-sm text-zinc-500">{label}</p>
      <p className={`mt-1 text-4xl font-semibold ${color}`}>{value}</p>
    </div>
  )
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState<Metric[]>([])
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  useEffect(() => {
    // Fetch immediately on mount, then every 5 seconds to match the agent interval
    function load() {
      fetchMetrics()
        .then((data) => {
          setMetrics(data.metrics)
          setLastUpdated(new Date())
          setError(null)
        })
        .catch((err) => setError(err.message))
    }

    load()
    const interval = setInterval(load, 5000)

    // Cleanup: stop the interval when the component unmounts
    return () => clearInterval(interval)
  }, [])

  const latest = metrics[0]

  return (
    <main className="min-h-screen bg-zinc-50 p-8">
      <div className="mx-auto max-w-5xl">

        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-zinc-900">PulseGrid</h1>
            <p className="text-sm text-zinc-500">Distributed Monitoring Dashboard</p>
          </div>
          {lastUpdated && (
            <p className="text-xs text-zinc-400">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </p>
          )}
        </div>

        {/* Error state */}
        {error && (
          <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-600">
            Could not reach backend: {error}
          </div>
        )}

        {/* Stat cards — shows latest snapshot from the most recent agent report */}
        {latest ? (
          <>
            <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <StatCard
                label="CPU Usage"
                value={`${latest.cpu_percent.toFixed(1)}%`}
                color={statusColor(latest.cpu_percent)}
              />
              <StatCard
                label="Memory Usage"
                value={`${latest.memory_percent.toFixed(1)}%`}
                color={statusColor(latest.memory_percent)}
              />
              <StatCard
                label="Memory Used"
                value={bytesToGB(latest.memory_used)}
                color="text-zinc-800"
              />
              <StatCard
                label="Memory Total"
                value={bytesToGB(latest.memory_total)}
                color="text-zinc-800"
              />
            </div>

            {/* Agent info */}
            <div className="mb-8 rounded-xl border border-zinc-200 bg-white p-4 shadow-sm">
              <p className="text-xs text-zinc-500">Active Agent</p>
              <p className="mt-1 font-medium text-zinc-800">
                {latest.agent_id}{" "}
                <span className="text-zinc-400">({latest.hostname})</span>
              </p>
            </div>
          </>
        ) : (
          !error && (
            <p className="mb-8 text-sm text-zinc-400">Waiting for agent data...</p>
          )
        )}

        {/* Recent metrics table */}
        {metrics.length > 0 && (
          <div className="rounded-xl border border-zinc-200 bg-white shadow-sm">
            <div className="border-b border-zinc-100 px-6 py-4">
              <h2 className="font-medium text-zinc-800">Recent Metrics</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-zinc-100 text-left text-xs text-zinc-400">
                    <th className="px-6 py-3">Agent</th>
                    <th className="px-6 py-3">CPU %</th>
                    <th className="px-6 py-3">Memory %</th>
                    <th className="px-6 py-3">Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {metrics.map((m) => (
                    <tr key={m.id} className="border-b border-zinc-50 hover:bg-zinc-50">
                      <td className="px-6 py-3 text-zinc-700">{m.agent_id}</td>
                      <td className={`px-6 py-3 font-medium ${statusColor(m.cpu_percent)}`}>
                        {m.cpu_percent.toFixed(1)}%
                      </td>
                      <td className={`px-6 py-3 font-medium ${statusColor(m.memory_percent)}`}>
                        {m.memory_percent.toFixed(1)}%
                      </td>
                      <td className="px-6 py-3 text-zinc-400">
                        {new Date(m.timestamp).toLocaleTimeString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </main>
  )
}
