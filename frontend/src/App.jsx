import { Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import Incidents from "./pages/Incidents";
import IncidentDetails from "./pages/IncidentDetails";
import Services from "./pages/Services";
import Logs from "./pages/Logs";
import Metrics from "./pages/Metrics";
import Deployments from "./pages/Deployments";
import Simulation from "./pages/Simulation";

export default function App() {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-area">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/incidents" element={<Incidents />} />
          <Route path="/incidents/:id" element={<IncidentDetails />} />
          <Route path="/services" element={<Services />} />
          <Route path="/logs" element={<Logs />} />
          <Route path="/metrics" element={<Metrics />} />
          <Route path="/deployments" element={<Deployments />} />
          <Route path="/simulation" element={<Simulation />} />
        </Routes>
      </div>
    </div>
  );
}
