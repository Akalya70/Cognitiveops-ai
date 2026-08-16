import { rootCauseLabel, severityColor } from "../utils/formatters";

export default function RootCausePanel({ rootCause, confidence, severity, contributingFactors }) {
  const color = confidence >= 75 ? "#12b76a" : confidence >= 50 ? "#eab308" : "#f79009";
  const factors = Object.entries(contributingFactors || {})
    .filter(([key]) => key !== "UNKNOWN")
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

  return (
    <div className="panel">
      <div className="panel-header">
        <div className="panel-title">AI Root Cause Analysis</div>
        {severity ? (
          <span className="text-mono" style={{ fontSize: 11, color: severityColor(severity) }}>
            {severity}
          </span>
        ) : null}
      </div>
      <div className="panel-body">
        <div className="rootcause-hero">
          <div
            className="confidence-ring"
            style={{
              background: `conic-gradient(${color} ${confidence * 3.6}deg, #1f2b36 0deg)`,
            }}
          >
            <div
              style={{
                position: "absolute",
                inset: 6,
                borderRadius: "50%",
                background: "var(--surface)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              {Math.round(confidence || 0)}%
            </div>
          </div>
          <div>
            <div className="muted" style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: 0.5, marginBottom: 4 }}>
              Probable Root Cause
            </div>
            <div style={{ fontSize: 20, fontWeight: 700, color: "var(--accent)" }}>{rootCauseLabel(rootCause)}</div>
          </div>
        </div>

        {factors.length > 0 ? (
          <div style={{ marginTop: 20 }}>
            <div className="muted" style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: 0.5, marginBottom: 10 }}>
              Contributing Factor Scores
            </div>
            {factors.map(([cause, score]) => (
              <div key={cause} style={{ marginBottom: 8 }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 3 }}>
                  <span className="muted">{rootCauseLabel(cause)}</span>
                  <span className="text-mono">{Math.round(score * 100)}%</span>
                </div>
                <div style={{ height: 5, background: "var(--border)", borderRadius: 3, overflow: "hidden" }}>
                  <div style={{ height: "100%", width: `${score * 100}%`, background: "var(--accent)" }} />
                </div>
              </div>
            ))}
          </div>
        ) : null}
      </div>
    </div>
  );
}
