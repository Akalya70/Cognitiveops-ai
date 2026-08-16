export default function LoadingSpinner({ label = "Loading…" }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10, padding: 30, color: "var(--text-tertiary)", fontSize: 13 }}>
      <span className="spinner" />
      {label}
    </div>
  );
}
