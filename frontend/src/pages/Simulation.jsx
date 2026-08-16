import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import RootCausePanel from "../components/RootCausePanel";
import EvidencePanel from "../components/EvidencePanel";
import RecommendationPanel from "../components/RecommendationPanel";
import LoadingSpinner from "../components/LoadingSpinner";
import {
  simulateNormal,
  simulateDatabaseFailure,
  simulateMemoryOverload,
  simulateBadDeployment,
  simulateNetworkFailure,
  simulateApiTimeout,
} from "../api/api";

const SCENARIOS = [
  {
    key: "normal",
    title: "Normal System",
    desc: "Generate a healthy baseline with no anomalies.",
    action: simulateNormal,
  },
  {
    key: "database-failure",
    title: "Database Failure",
    desc: "Connection pool exhaustion cascading into payment errors.",
    action: simulateDatabaseFailure,
  },
  {
    key: "memory-overload",
    title: "Memory Overload",
    desc: "Gradual memory leak leading to OOM errors.",
    action: simulateMemoryOverload,
  },
  {
    key: "bad-deployment",
    title: "Bad Deployment",
    desc: "A recent release spikes error rates sharply.",
    action: simulateBadDeployment,
  },
  {
    key: "network-failure",
    title: "Network Failure",
    desc: "Connectivity issues affecting multiple services.",
    action: simulateNetworkFailure,
  },
  {
    key: "api-timeout",
    title: "API Timeout",
    desc: "Cascading timeouts calling downstream services.",
    action: simulateApiTimeout,
  },
];

export default function Simulation() {
  const [running, setRunning] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const runScenario = async (scenario) => {
    setRunning(scenario.key);
    setError(null);
    setResult(null);
    try {
      const data = await scenario.action();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setRunning(null);
    }
  };

  return (
    <>
      <Navbar title="Simulation" subtitle="DEMO_SCENARIOS" />
      <div className="page-content">
        <div className="panel" style={{ marginBottom: 20 }}>
          <div className="panel-header">
            <div className="panel-title">Trigger a Scenario</div>
          </div>
          <div className="panel-body">
            <div className="sim-grid">
              {SCENARIOS.map((s) => (
                <button
                  key={s.key}
                  className="sim-card"
                  onClick={() => runScenario(s)}
                  disabled={running !== null}
                >
                  <div className="sim-card-title">{running === s.key ? "Running…" : s.title}</div>
                  <div className="sim-card-desc">{s.desc}</div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {running ? <LoadingSpinner label="Generating scenario data and running AI analysis…" /> : null}

        {error ? (
          <div className="panel" style={{ padding: 14, marginBottom: 16, borderColor: "#f04438", color: "#f04438" }}>
            {error}
          </div>
        ) : null}

        {result && result.analysis ? (
          <>
            <div
              className="panel"
              style={{ padding: 16, marginBottom: 20, borderColor: "var(--accent)", cursor: "pointer" }}
              onClick={() => navigate(`/incidents/${result.incident.id}`)}
            >
              <div style={{ fontWeight: 600, marginBottom: 4 }}>Simulation Complete — view full incident details →</div>
              <div className="muted" style={{ fontSize: 12.5 }}>
                Incident #{result.incident.id}: {result.incident.title}
              </div>
            </div>
            <div className="grid grid-2" style={{ marginBottom: 20 }}>
              <RootCausePanel
                rootCause={result.analysis.root_cause}
                confidence={result.analysis.confidence}
                severity={result.analysis.severity}
                contributingFactors={result.analysis.contributing_factors}
              />
              <EvidencePanel evidence={result.analysis.evidence} />
            </div>
            <RecommendationPanel recommendations={result.analysis.recommendations} />
          </>
        ) : result ? (
          <div className="panel" style={{ padding: 16 }}>
            <div style={{ fontWeight: 600, marginBottom: 4 }}>Baseline generated</div>
            <div className="muted" style={{ fontSize: 12.5 }}>{result.message}</div>
          </div>
        ) : null}
      </div>
    </>
  );
}
