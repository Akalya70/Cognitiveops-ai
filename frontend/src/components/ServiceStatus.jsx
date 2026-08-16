import { statusColor } from "../utils/formatters";

export default function ServiceStatus({ status }) {
  const color = statusColor(status);
  return (
    <span className="badge" style={{ color, background: `${color}1a`, border: `1px solid ${color}40` }}>
      <span className="dot" />
      {status || "UNKNOWN"}
    </span>
  );
}
