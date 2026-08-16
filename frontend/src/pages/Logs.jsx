import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import LoadingSpinner from "../components/LoadingSpinner";
import EmptyState from "../components/EmptyState";
import { getLogs } from "../api/api";
import { formatDateTime } from "../utils/formatters";

const LEVEL_COLORS = {
  DEBUG: "#5b6770",
  INFO: "#4dd8c8",
  WARNING: "#eab308",
  ERROR: "#f79009",
  CRITICAL: "#f04438",
};

export default function Logs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [service, setService] = useState("");
  const [level, setLevel] = useState("");
  const [errorCode, setErrorCode] = useState("");

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    getLogs({ service: service || undefined, level: level || undefined, error_code: errorCode || undefined, limit: 150 })
      .then((data) => mounted && setLogs(data))
      .catch((err) => mounted && setError(err.message))
      .finally(() => mounted && setLoading(false));
    return () => {
      mounted = false;
    };
  }, [service, level, errorCode]);

  return (
    <>
      <Navbar title="Logs" subtitle={`${logs.length} SHOWN`} />
      <div className="page-content">
        <div className="filters-row">
          <input className="input" placeholder="Filter by service…" value={service} onChange={(e) => setService(e.target.value)} />
          <select className="select" value={level} onChange={(e) => setLevel(e.target.value)}>
            <option value="">All levels</option>
            <option value="DEBUG">Debug</option>
            <option value="INFO">Info</option>
            <option value="WARNING">Warning</option>
            <option value="ERROR">Error</option>
            <option value="CRITICAL">Critical</option>
          </select>
          <input className="input" placeholder="Error code…" value={errorCode} onChange={(e) => setErrorCode(e.target.value)} />
        </div>

        {error ? (
          <div className="panel" style={{ padding: 14, marginBottom: 16, borderColor: "#f04438", color: "#f04438" }}>
            {error}
          </div>
        ) : null}

        {loading ? (
          <LoadingSpinner label="Loading logs…" />
        ) : logs.length === 0 ? (
          <EmptyState icon="—" title="No logs found" description="Try adjusting filters or run a simulation." />
        ) : (
          <div className="panel">
            <div className="panel-body" style={{ padding: 0 }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Service</th>
                    <th>Level</th>
                    <th>Message</th>
                    <th>Error Code</th>
                    <th>Trace ID</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log) => (
                    <tr key={log.id}>
                      <td className="table-mono">{formatDateTime(log.timestamp)}</td>
                      <td>{log.service_name}</td>
                      <td>
                        <span style={{ color: LEVEL_COLORS[log.level] || "#8b98a5", fontWeight: 600, fontFamily: "var(--font-mono)", fontSize: 11.5 }}>
                          {log.level}
                        </span>
                      </td>
                      <td>{log.message}</td>
                      <td className="table-mono">{log.error_code || "—"}</td>
                      <td className="table-mono">{log.trace_id || "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
