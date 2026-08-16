import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import LoadingSpinner from "../components/LoadingSpinner";
import EmptyState from "../components/EmptyState";
import { getDeployments } from "../api/api";
import { formatDateTime } from "../utils/formatters";

export default function Deployments() {
  const [deployments, setDeployments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getDeployments({ limit: 100 })
      .then(setDeployments)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <>
      <Navbar title="Deployments" subtitle={`${deployments.length} RECORDED`} />
      <div className="page-content">
        {error ? (
          <div className="panel" style={{ padding: 14, marginBottom: 16, borderColor: "#f04438", color: "#f04438" }}>
            {error}
          </div>
        ) : null}
        {loading ? (
          <LoadingSpinner label="Loading deployments…" />
        ) : deployments.length === 0 ? (
          <EmptyState icon="—" title="No deployments recorded" />
        ) : (
          <div className="panel">
            <div className="panel-body" style={{ padding: 0 }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Service</th>
                    <th>Version</th>
                    <th>Environment</th>
                    <th>Status</th>
                    <th>Deployed By</th>
                    <th>Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {deployments.map((d) => (
                    <tr key={d.id}>
                      <td style={{ color: "var(--text-primary)" }}>{d.service_name}</td>
                      <td className="table-mono">{d.version}</td>
                      <td className="muted">{d.environment}</td>
                      <td>{d.status}</td>
                      <td className="muted">{d.deployed_by}</td>
                      <td className="table-mono">{formatDateTime(d.timestamp)}</td>
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
