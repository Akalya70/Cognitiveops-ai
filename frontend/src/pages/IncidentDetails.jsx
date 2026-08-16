import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import SeverityBadge from "../components/SeverityBadge";
import ServiceStatus from "../components/ServiceStatus";
import RootCausePanel from "../components/RootCausePanel";
import EvidencePanel from "../components/EvidencePanel";
import RecommendationPanel from "../components/RecommendationPanel";
import IncidentTimeline from "../components/IncidentTimeline";
import LoadingSpinner from "../components/LoadingSpinner";
import { getIncident, analyzeIncident, resolveIncident } from "../api/api";
import { formatDateTime } from "../utils/formatters";

export default function IncidentDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [incident, setIncident] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  const load = () => {
    setLoading(true);
    getIncident(id)
      .then(setIncident)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setError(null);
    try {
      await analyzeIncident(id);
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleResolve = async () => {
    try {
      await resolveIncident(id);
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) {
    return (
      <>
        <Navbar title="Incident Details" />
        <div className="page-content">
          <LoadingSpinner label="Loading incident…" />
        </div>
      </>
    );
  }

  if (!incident) {
    return (
      <>
        <Navbar title="Incident Details" />
        <div className="page-content">
          <div className="panel" style={{ padding: 20 }}>Incident not found.</div>
        </div>
      </>
    );
  }

  return (
    <>
      <Navbar title={incident.title} subtitle={`INCIDENT #${incident.id}`} />
      <div className="page-content">
        {error ? (
          <div className="panel" style={{ padding: 14, marginBottom: 16, borderColor: "#f04438", color: "#f04438" }}>
            {error}
          </div>
        ) : null}

        <div className="panel" style={{ marginBottom: 20 }}>
          <div className="panel-body">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 14 }}>
              <div>
                <div style={{ display: "flex", gap: 8, marginBottom: 10 }}>
                  <SeverityBadge severity={incident.severity} />
                  <ServiceStatus status={incident.status} />
                </div>
                <div className="muted" style={{ fontSize: 13 }}>
                  Affected service: <strong style={{ color: "var(--text-primary)" }}>{incident.affected_service}</strong>
                </div>
                <div className="muted" style={{ fontSize: 12.5, marginTop: 4 }}>
                  Created {formatDateTime(incident.created_at)}
                </div>
                {incident.description ? (
                  <div style={{ marginTop: 10, fontSize: 13.5 }}>{incident.description}</div>
                ) : null}
              </div>
              <div style={{ display: "flex", gap: 10, flexShrink: 0 }}>
                <button className="btn" onClick={() => navigate(-1)}>
                  Back
                </button>
                <button className="btn btn-accent" onClick={handleAnalyze} disabled={analyzing}>
                  {analyzing ? "Analyzing…" : "Run AI Analysis"}
                </button>
                {incident.status !== "RESOLVED" ? (
                  <button className="btn" onClick={handleResolve}>
                    Mark Resolved
                  </button>
                ) : null}
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-2" style={{ marginBottom: 20 }}>
          <RootCausePanel
            rootCause={incident.probable_root_cause}
            confidence={incident.confidence_score}
            severity={incident.severity}
            contributingFactors={incident.contributing_factors}
          />
          <EvidencePanel evidence={incident.evidence} />
        </div>

        <div className="grid grid-2">
          <div className="panel">
            <div className="panel-header">
              <div className="panel-title">Event Timeline</div>
            </div>
            <div className="panel-body">
              <IncidentTimeline events={incident.timeline} />
            </div>
          </div>
          <RecommendationPanel recommendations={incident.recommendations} />
        </div>
      </div>
    </>
  );
}
