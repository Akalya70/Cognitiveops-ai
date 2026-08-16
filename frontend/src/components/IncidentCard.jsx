import { useNavigate } from "react-router-dom";
import SeverityBadge from "./SeverityBadge";
import ServiceStatus from "./ServiceStatus";
import { formatRelativeTime, rootCauseLabel } from "../utils/formatters";

export default function IncidentCard({ incident }) {
  const navigate = useNavigate();
  return (
    <div
      className="panel"
      style={{ padding: 16, cursor: "pointer", marginBottom: 12 }}
      onClick={() => navigate(`/incidents/${incident.id}`)}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
        <div>
          <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4 }}>{incident.title}</div>
          <div className="muted" style={{ fontSize: 12.5 }}>
            {incident.affected_service} · {formatRelativeTime(incident.created_at)}
          </div>
        </div>
        <div style={{ display: "flex", gap: 8, flexShrink: 0 }}>
          <SeverityBadge severity={incident.severity} />
          <ServiceStatus status={incident.status} />
        </div>
      </div>
      {incident.probable_root_cause ? (
        <div style={{ marginTop: 10, fontSize: 12.5 }} className="text-mono">
          <span className="muted">Root cause: </span>
          <span style={{ color: "var(--accent)" }}>{rootCauseLabel(incident.probable_root_cause)}</span>
          {incident.confidence_score ? <span className="muted"> · {Math.round(incident.confidence_score)}% confidence</span> : null}
        </div>
      ) : null}
    </div>
  );
}
