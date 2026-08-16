import { NavLink } from "react-router-dom";

const LINKS = [
  { to: "/", label: "Dashboard" },
  { to: "/incidents", label: "Incidents" },
  { to: "/services", label: "Services" },
  { to: "/logs", label: "Logs" },
  { to: "/metrics", label: "Metrics" },
  { to: "/deployments", label: "Deployments" },
  { to: "/simulation", label: "Simulation" },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-brand-mark" />
        <div className="sidebar-brand-text">
          CognitiveOps
          <small>AI Root Cause</small>
        </div>
      </div>
      {LINKS.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          end={link.to === "/"}
          className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
        >
          <span className="dot" />
          {link.label}
        </NavLink>
      ))}
    </aside>
  );
}
