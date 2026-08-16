import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import ServiceStatus from "../components/ServiceStatus";
import LoadingSpinner from "../components/LoadingSpinner";
import EmptyState from "../components/EmptyState";
import { getServices } from "../api/api";

export default function Services() {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getServices()
      .then(setServices)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <>
      <Navbar title="Services" subtitle={`${services.length} MONITORED`} />
      <div className="page-content">
        {error ? (
          <div className="panel" style={{ padding: 14, marginBottom: 16, borderColor: "#f04438", color: "#f04438" }}>
            {error}
          </div>
        ) : null}
        {loading ? (
          <LoadingSpinner label="Loading services…" />
        ) : services.length === 0 ? (
          <EmptyState icon="—" title="No services registered" />
        ) : (
          <div className="panel">
            <div className="panel-body" style={{ padding: 0 }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Service</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Health Score</th>
                    <th>CPU</th>
                    <th>Memory</th>
                    <th>Dependencies</th>
                  </tr>
                </thead>
                <tbody>
                  {services.map((s) => (
                    <tr key={s.id}>
                      <td style={{ color: "var(--text-primary)", fontWeight: 500 }}>{s.name}</td>
                      <td className="muted">{s.service_type}</td>
                      <td>
                        <ServiceStatus status={s.status} />
                      </td>
                      <td className="table-mono">{s.health_score?.toFixed(0)}%</td>
                      <td className="table-mono">{s.cpu_usage?.toFixed(0)}%</td>
                      <td className="table-mono">{s.memory_usage?.toFixed(0)}%</td>
                      <td className="table-mono">{s.dependency_count}</td>
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
