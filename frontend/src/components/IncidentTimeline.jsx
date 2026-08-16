import { formatDateTime } from "../utils/formatters";
import EmptyState from "./EmptyState";

export default function IncidentTimeline({ events }) {
  if (!events || events.length === 0) {
    return <EmptyState icon="⋯" title="No timeline events" description="Run analysis to build a contextual timeline." />;
  }
  return (
    <div className="timeline">
      {events.map((event, idx) => (
        <div className="timeline-item" key={idx}>
          <div className="timeline-time">{formatDateTime(event.timestamp)}</div>
          <div className="timeline-desc">{event.description}</div>
        </div>
      ))}
    </div>
  );
}
