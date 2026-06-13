"use client"

import { useEffect, useState } from "react"
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts"
import { fetchMetrics, fetchAgents, fetchAlerts } from "@/lib/api"
import type { Metric, Agent, Alert } from "@/types/metric"

function bytesToGB(bytes: number): string {
  return (bytes / 1024 ** 3).toFixed(1) + " GB"
}

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

function AgentCard({ agent }: { agent: Agent }) {
  const isOnline = agent.status === "online" && agent.seconds_since_seen < 30
  return (
    <div className="flex items-center justify-between rounded-xl border border-zinc-200 bg-white p-4 shadow-sm">
      <div>
        <p className="font-medium text-zinc-800">{agent.agent_id}</p>
        <p className="text-xs text-zinc-400">{agent.hostname}</p>
      </div>
      <span className={`rounded-full px-3 py-1 text-xs font-medium ${
        isOnline ? "bg-green-100 text-green-700" : "bg-red-100 text-red-600"
      }`}>
        {isOnline ? "Online" : "Offline"}
      </span>
    </div>
  )
}

function AlertBadge({ severity }: { severity: string }) {
  const styles = severity === "critical"
    ? "bg-red-100 text-red-700"
    : "bg-yellow-100 text-yellow-700"
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${styles}`}>
      {severity}
    </span>
  )
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState<Metric[]>([])
  const [agents, setAgents] = useState<Agent[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  useEffect(() => {
    function load() {
      Promise.all([fetchMetrics(), fetchAgents(), fetchAlerts()])
        .then(([metricsData, agentsData, alertsData]) => {
          setMetrics(metricsData.metrics)
          setAgents(agentsData.agents)
          setAlerts(alertsData.alerts)
          setLastUpdated(new Date())
          setError(null)
        })
        .catch((err) => setError(err.message))
    }

    load()
    const interval = setInterval(load, 5000)
    return () => clearInterval(interval)
  }, [])

  const latest = metrics[0]

  const chartData = [...metrics].reverse().map((m) => ({
    time: new Date(m.timestamp).toLocaleTimeString(),
    cpu: parseFloat(m.cpu_percent.toFixed(1)),
    memory: parseFloat(m.memory_percent.toFixed(1)),
  }))

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
            <p className="text-xs text-zinc-400">Last updated: {lastUpdated.toLocaleTimeString()}</p>
          )}
        </div>

        {/* Error state */}
        {error && (
          <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-600">
            Could not reach backend: {error}
          </div>
        )}

        {/* Stat cards */}
        {latest && (
          <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label="CPU Usage" value={`${latest.cpu_percent.toFixed(1)}%`} color={statusColor(latest.cpu_percent)} />
            <StatCard label="Memory Usage" value={`${latest.memory_percent.toFixed(1)}%`} color={statusColor(latest.memory_percent)} />
            <StatCard label="Memory Used" value={bytesToGB(latest.memory_used)} color="text-zinc-800" />
            <StatCard label="Memory Total" value={bytesToGB(latest.memory_total)} color="text-zinc-800" />
          </div>
        )}

        <div className="mb-8 grid grid-cols-1 gap-6 lg:grid-cols-2">

          {/* Agent health */}
          <div className="rounded-xl border border-zinc-200 bg-white shadow-sm">
            <div className="border-b border-zinc-100 px-6 py-4">
              <h2 className="font-medium text-zinc-800">Active Agents</h2>
            </div>
            <div className="flex flex-col gap-3 p-4">
              {agents.length === 0
                ? <p className="text-sm text-zinc-400">No agents registered yet</p>
                : agents.map((a) => <AgentCard key={a.id} agent={a} />)
              }
            </div>
          </div>

          {/* Alerts */}
          <div className="rounded-xl border border-zinc-200 bg-white shadow-sm">
            <div className="border-b border-zinc-100 px-6 py-4">
              <h2 className="font-medium text-zinc-800">Recent Alerts</h2>
            </div>
            <div className="flex flex-col divide-y divide-zinc-50">
              {alerts.length === 0
                ? <p className="p-4 text-sm text-zinc-400">No alerts — system healthy</p>
                : alerts.slice(0, 5).map((a) => (
                    <div key={a.id} className="flex items-start justify-between px-6 py-3">
                      <div>
                        <p className="text-sm text-zinc-700">{a.message}</p>
                        <p className="text-xs text-zinc-400">{a.agent_id} · {new Date(a.created_at).toLocaleTimeString()}</p>
                      </div>
                      <AlertBadge severity={a.severity} />
                    </div>
                  ))
              }
            </div>
          </div>
        </div>

        {/* Historical trends chart */}
        {chartData.length > 0 && (
          <div className="mb-8 rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 font-medium text-zinc-800">Historical Trends</h2>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={chartData}>
                <XAxis dataKey="time" tick={{ fontSize: 11 }} interval="preserveStartEnd" />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} unit="%" />
                <Tooltip formatter={(value) => `${value}%`} />
                <Legend />
                <Line type="monotone" dataKey="cpu" stroke="#3b82f6" name="CPU" dot={false} strokeWidth={2} />
                <Line type="monotone" dataKey="memory" stroke="#f59e0b" name="Memory" dot={false} strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
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
                      <td className={`px-6 py-3 font-medium ${statusColor(m.cpu_percent)}`}>{m.cpu_percent.toFixed(1)}%</td>
                      <td className={`px-6 py-3 font-medium ${statusColor(m.memory_percent)}`}>{m.memory_percent.toFixed(1)}%</td>
                      <td className="px-6 py-3 text-zinc-400">{new Date(m.timestamp).toLocaleTimeString()}</td>
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
