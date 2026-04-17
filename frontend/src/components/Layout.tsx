import { Link, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function Layout() {
  const auth = useAuth();
  const navigate = useNavigate();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <h1>Lab NGS</h1>
          <p className="muted">Plataforma interna de análises</p>
        </div>
        <nav className="nav-links">
          <Link to="/">Dashboard</Link>
          <Link to="/analyses/new">Nova análise</Link>
        </nav>
        <button
          className="secondary-button"
          onClick={() => {
            auth.logout();
            navigate("/login");
          }}
        >
          Sair
        </button>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
