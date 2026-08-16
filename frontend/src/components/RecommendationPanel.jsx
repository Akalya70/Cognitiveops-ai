import EmptyState from "./EmptyState";

export default function RecommendationPanel({ recommendations }) {
  return (
    <div className="panel">
      <div className="panel-header">
        <div className="panel-title">Recommended Actions</div>
      </div>
      <div className="panel-body">
        {!recommendations || recommendations.length === 0 ? (
          <EmptyState icon="—" title="No recommendations yet" description="Run analysis to generate recommended actions." />
        ) : (
          recommendations.map((item, idx) => (
            <div className="recommendation-item" key={idx}>
              <span className="recommendation-num">{String(idx + 1).padStart(2, "0")}</span>
              <span>{item}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
