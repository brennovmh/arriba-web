import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import api from "../services/api";

export default function LoginPage() {
  const [email, setEmail] = useState("admin@lab.local");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const auth = useAuth();

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    try {
      const response = await api.post("/auth/login", { email, password });
      auth.login(response.data.access_token);
      navigate("/");
    } catch {
      setError("Falha no login.");
    }
  }

  return (
    <div className="login-shell">
      <form className="login-card" onSubmit={handleSubmit}>
        <h1>Lab NGS Platform</h1>
        <p className="muted">Login interno do laboratório</p>
        <label>
          E-mail
          <input value={email} onChange={(event) => setEmail(event.target.value)} />
        </label>
        <label>
          Senha
          <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
        </label>
        {error ? <p className="error-text">{error}</p> : null}
        <button type="submit">Entrar</button>
      </form>
    </div>
  );
}
