export default function EmptyState({ icon = "—", title = "Nothing here yet", description = "" }) {
  return (
    <div className="empty-state">
      <div className="empty-state-icon">{icon}</div>
      <div style={{ color: "var(--text-secondary)", fontWeight: 600, marginBottom: 4 }}>{title}</div>
      {description ? <div style={{ fontSize: 12.5 }}>{description}</div> : null}
    </div>
  );
}
