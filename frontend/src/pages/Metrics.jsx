import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import MetricChart from "../components/MetricChart";
import LoadingSpinner from "../components/LoadingSpinner";
import { getServices, getMetricsForService } from "../api/api";

export default function Metrics() {
  const [services, setServices] = useState([]);
  const [selected, setSelected] = useState("");
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getServices().then((data) => {
      setServices(data);
      if (data.length > 0) setSelected(data[0].name);
    });
  }, []);

  useEffect(() => {
    if (!selected) return;
    setLoading(true);
    getMetricsForService(selected, 100)
      .then(setMetrics)
      .finally(() => setLoading(false));
  }, [selected]);

  return (
    <>
      <Navbar title="Metrics" subtitle={selected ? selected.toUpperCase() : ""} />
      <div className="page-content">
        <div className="filters-row">
          <select className="select" value={selected} onChange={(e) => setSelected(e.target.value)}>
            {services.map((s) => (
              <option key={s.id} value={s.name}>
                {s.name}
              </option>
            ))}
          </select>
        </div>

        {loading ? (
          <LoadingSpinner label="Loading metrics…" />
        ) : (
          <div className="grid grid-2">
            <MetricChart title="CPU Usage (%)" data={metrics} dataKey="cpu_usage" color="#f79009" unit="%" />
            <MetricChart title="Memory Usage (%)" data={metrics} dataKey="memory_usage" color="#eab308" unit="%" />
            <MetricChart title="API Latency (ms)" data={metrics} dataKey="api_latency" color="#4dd8c8" unit="ms" />
            <MetricChart title="Error Rate (%)" data={metrics} dataKey="error_rate" color="#f04438" unit="%" />
            <MetricChart title="Database Connections (%)" data={metrics} dataKey="db_connections" color="#12b76a" unit="%" />
            <MetricChart title="Network Usage (%)" data={metrics} dataKey="network_usage" color="#8b98a5" unit="%" />
          </div>
        )}
      </div>
    </>
  );
}
