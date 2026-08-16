export default function Navbar({ title, subtitle }) {
  return (
    <header className="topbar">
      <div>
        <div className="topbar-title">{title}</div>
      </div>
      {subtitle ? <div className="topbar-sub">{subtitle}</div> : null}
    </header>
  );
}
