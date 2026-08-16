import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import StatCard from "../components/StatCard";
import IncidentCard from "../components/IncidentCard";
import MetricChart from "../components/MetricChart";
import LoadingSpinner from "../components/LoadingSpinner";
import EmptyState from "../components/EmptyState";
import { getDashboardSummary, getIncidents, getMetrics } from "../api/api";
import { formatRelativeTime } from "../utils/formatters";

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const [summaryData, incidentData, metricData] = await Promise.all([
          getDashboardSummary(),
          getIncidents({ limit: 5 }),
          getMetrics({ limit: 60 }),
        ]);
        if (!mounted) return;
        setSummary(summaryData);
        setIncidents(incidentData);
        setMetrics(metricData);
      } catch (err) {
        if (mounted) setError(err.message);
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, []);

  if (loading) {
    return (
      <>
        <Navbar title="Dashboard" />
        <div className="page-content">
          <LoadingSpinner label="Loading dashboard…" />
        </div>
      </>
    );
  }

  return (
    <>
      <Navbar title="Dashboard" subtitle="SYSTEM_OVERVIEW" />
      <div className="page-content">
        {error ? (
          <div className="panel" style={{ padding: 14, marginBottom: 16, borderColor: "#f04438", color: "#f04438" }}>
            {error}
          </div>
        ) : null}

        <div className="grid grid-4" style={{ marginBottom: 20 }}>
          <StatCard label="System Health" value={`${summary?.average_health_score ?? 0}%`} accent="var(--low)" />
          <StatCard label="Active Incidents" value={summary?.active_incidents ?? 0} accent="var(--high)" />
          <StatCard label="Critical Incidents" value={summary?.critical_incidents ?? 0} accent="var(--critical)" />
          <StatCard label="Services Monitored" value={summary?.total_services ?? 0} />
        </div>

        <div className="grid grid-2" style={{ marginBottom: 20 }}>
          <MetricChart title="API Latency (ms)" data={metrics} dataKey="api_latency" color="#4dd8c8" unit="ms" />
          <MetricChart title="Error Rate (%)" data={metrics} dataKey="error_rate" color="#f04438" unit="%" />
          <MetricChart title="CPU Usage (%)" data={metrics} dataKey="cpu_usage" color="#f79009" unit="%" />
          <MetricChart title="Database Connections (%)" data={metrics} dataKey="db_connections" color="#eab308" unit="%" />
        </div>

        <div className="panel">
          <div className="panel-header">
            <div className="panel-title">Recent Incidents</div>
          </div>
          <div className="panel-body">
            {incidents.length === 0 ? (
              <EmptyState icon="—" title="No incidents recorded" description="Run a simulation to generate a demo incident." />
            ) : (
              incidents.map((incident) => <IncidentCard incident={incident} key={incident.id} />)
            )}
          </div>
        </div>

        {summary?.recent_deployments?.length ? (
          <div className="panel" style={{ marginTop: 20 }}>
            <div className="panel-header">
              <div className="panel-title">Recent Deployments</div>
            </div>
            <div className="panel-body" style={{ padding: 0 }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Service</th>
                    <th>Version</th>
                    <th>Status</th>
                    <th>When</th>
                  </tr>
                </thead>
                <tbody>
                  {summary.recent_deployments.map((d) => (
                    <tr key={d.id}>
                      <td>{d.service_name}</td>
                      <td className="table-mono">{d.version}</td>
                      <td>{d.status}</td>
                      <td>{formatRelativeTime(d.timestamp)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : null}
      </div>
    </>
  );
}
