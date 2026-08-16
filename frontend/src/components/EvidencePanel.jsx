import EmptyState from "./EmptyState";

export default function EvidencePanel({ evidence }) {
  return (
    <div className="panel">
      <div className="panel-header">
        <div className="panel-title">Evidence</div>
      </div>
      <div className="panel-body">
        {!evidence || evidence.length === 0 ? (
          <EmptyState icon="—" title="No evidence yet" description="Run analysis to gather supporting evidence." />
        ) : (
          evidence.map((item, idx) => (
            <div className="evidence-item" key={idx}>
              <span className="evidence-check">✓</span>
              <span>{item}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
