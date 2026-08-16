import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { formatDateTime } from "../utils/formatters";
import EmptyState from "./EmptyState";

export default function MetricChart({ title, data, dataKey, color = "#4dd8c8", unit = "" }) {
  if (!data || data.length === 0) {
    return (
      <div className="panel">
        <div className="panel-header">
          <div className="panel-title">{title}</div>
        </div>
        <div className="panel-body">
          <EmptyState icon="—" title="No data yet" description="Metrics will appear here once collected." />
        </div>
      </div>
    );
  }

  const chartData = [...data]
    .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
    .map((d) => ({ ...d, label: formatDateTime(d.timestamp) }));

  return (
    <div className="panel">
      <div className="panel-header">
        <div className="panel-title">{title}</div>
      </div>
      <div className="panel-body" style={{ height: 220 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 12, left: -12, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2b36" />
            <XAxis dataKey="label" stroke="#5b6770" fontSize={11} tick={{ fill: "#5b6770" }} />
            <YAxis stroke="#5b6770" fontSize={11} tick={{ fill: "#5b6770" }} />
            <Tooltip
              contentStyle={{ background: "#121a22", border: "1px solid #1f2b36", borderRadius: 6, fontSize: 12 }}
              labelStyle={{ color: "#8b98a5" }}
              formatter={(value) => [`${Number(value).toFixed(1)}${unit}`, title]}
            />
            <Line type="monotone" dataKey={dataKey} stroke={color} strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
