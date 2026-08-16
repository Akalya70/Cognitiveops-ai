import { severityColor } from "../utils/formatters";

export default function SeverityBadge({ severity }) {
  const color = severityColor(severity);
  return (
    <span className="badge" style={{ color, background: `${color}1a`, border: `1px solid ${color}40` }}>
      <span className="dot" />
      {severity || "UNKNOWN"}
    </span>
  );
}
