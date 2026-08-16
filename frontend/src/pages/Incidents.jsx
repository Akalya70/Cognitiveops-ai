import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import IncidentCard from "../components/IncidentCard";
import LoadingSpinner from "../components/LoadingSpinner";
import EmptyState from "../components/EmptyState";
import { getIncidents } from "../api/api";

export default function Incidents() {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusFilter, setStatusFilter] = useState("");
  const [severityFilter, setSeverityFilter] = useState("");

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    getIncidents({ status: statusFilter || undefined, severity: severityFilter || undefined })
      .then((data) => mounted && setIncidents(data))
      .catch((err) => mounted && setError(err.message))
      .finally(() => mounted && setLoading(false));
    return () => {
      mounted = false;
    };
  }, [statusFilter, severityFilter]);

  return (
    <>
      <Navbar title="Incidents" subtitle={`${incidents.length} SHOWN`} />
      <div className="page-content">
        <div className="filters-row">
          <select className="select" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">All statuses</option>
            <option value="OPEN">Open</option>
            <option value="INVESTIGATING">Investigating</option>
            <option value="MITIGATED">Mitigated</option>
            <option value="RESOLVED">Resolved</option>
          </select>
          <select className="select" value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)}>
            <option value="">All severities</option>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
            <option value="CRITICAL">Critical</option>
          </select>
        </div>

        {error ? (
          <div className="panel" style={{ padding: 14, marginBottom: 16, borderColor: "#f04438", color: "#f04438" }}>
            {error}
          </div>
        ) : null}

        {loading ? (
          <LoadingSpinner label="Loading incidents…" />
        ) : incidents.length === 0 ? (
          <EmptyState icon="—" title="No incidents found" description="Try adjusting filters or run a simulation." />
        ) : (
          incidents.map((incident) => <IncidentCard incident={incident} key={incident.id} />)
        )}
      </div>
    </>
  );
}
