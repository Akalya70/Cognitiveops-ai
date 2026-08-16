export function formatDateTime(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatRelativeTime(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  const diffMs = Date.now() - date.getTime();
  const diffMinutes = Math.round(diffMs / 60000);
  if (diffMinutes < 1) return "just now";
  if (diffMinutes < 60) return `${diffMinutes}m ago`;
  const diffHours = Math.round(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.round(diffHours / 24);
  return `${diffDays}d ago`;
}

export function formatPercent(value, decimals = 0) {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return `${Number(value).toFixed(decimals)}%`;
}

export function formatNumber(value, decimals = 0) {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return Number(value).toFixed(decimals);
}

export function formatMs(value) {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return `${Math.round(value)}ms`;
}

export function rootCauseLabel(rootCause) {
  if (!rootCause) return "Unknown";
  return rootCause
    .split("_")
    .map((w) => w.charAt(0) + w.slice(1).toLowerCase())
    .join(" ");
}

export function severityColor(severity) {
  switch ((severity || "").toUpperCase()) {
    case "CRITICAL":
      return "#f04438";
    case "HIGH":
      return "#f79009";
    case "MEDIUM":
      return "#eaaa08";
    case "LOW":
      return "#12b76a";
    default:
      return "#667085";
  }
}

export function statusColor(status) {
  switch ((status || "").toUpperCase()) {
    case "HEALTHY":
      return "#12b76a";
    case "DEGRADED":
      return "#f79009";
    case "CRITICAL":
      return "#f04438";
    case "OPEN":
      return "#f04438";
    case "INVESTIGATING":
      return "#f79009";
    case "MITIGATED":
      return "#eaaa08";
    case "RESOLVED":
      return "#12b76a";
    default:
      return "#667085";
  }
}
