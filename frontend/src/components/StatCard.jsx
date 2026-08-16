export default function StatCard({ label, value, trend, accent }) {
  return (
    <div className="stat-card">
      <div className="stat-label">{label}</div>
      <div className="stat-value" style={accent ? { color: accent } : undefined}>
        {value}
      </div>
      {trend ? <div className="stat-trend">{trend}</div> : null}
    </div>
  );
}
