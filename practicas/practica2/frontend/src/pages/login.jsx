import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { healthCheck, loginAdmin, saveSession, isAuthenticated } from "../API/api_admin";

const pageStyle = {
  minHeight: "100vh",
  margin: 0,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  background:
    "linear-gradient(135deg, #0b1220 0%, #111827 45%, #1e293b 100%)",
  fontFamily: "Inter, system-ui, sans-serif",
  color: "#e5e7eb",
  padding: "20px",
};

const cardStyle = {
  width: "100%",
  maxWidth: "420px",
  background: "rgba(15, 23, 42, 0.95)",
  border: "1px solid rgba(148, 163, 184, 0.15)",
  borderRadius: "18px",
  boxShadow: "0 20px 40px rgba(0,0,0,0.35)",
  padding: "28px",
  backdropFilter: "blur(6px)",
};

const inputStyle = {
  width: "100%",
  padding: "12px 14px",
  borderRadius: "10px",
  border: "1px solid #334155",
  background: "#0f172a",
  color: "#e5e7eb",
  outline: "none",
  fontSize: "14px",
};

const labelStyle = {
  display: "block",
  marginBottom: "8px",
  color: "#cbd5e1",
  fontSize: "14px",
  fontWeight: 600,
};

const buttonStyle = {
  width: "100%",
  padding: "12px 16px",
  borderRadius: "10px",
  border: "none",
  background: "linear-gradient(135deg, #2563eb, #1d4ed8)",
  color: "#fff",
  fontWeight: 700,
  cursor: "pointer",
  fontSize: "14px",
};

export default function LoginPage() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    usuario: "",
    password: "",
  });

  const [loading, setLoading] = useState(false);
  const [serverStatus, setServerStatus] = useState("Comprobando servidor...");
  const [error, setError] = useState("");

  useEffect(() => {
    if (isAuthenticated()) {
      navigate("/admin");
      return;
    }

    const checkServer = async () => {
      try {
        const data = await healthCheck();
        setServerStatus(`Servidor activo: ${data.status || "ok"}`);
      } catch (err) {
        setServerStatus("No se pudo conectar con el backend");
      }
    };

    checkServer();
  }, [navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const data = await loginAdmin(form);
      saveSession(data);
      navigate("/admin");
    } catch (err) {
      const message =
        err?.response?.data?.detail || "No se pudo iniciar sesión";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={pageStyle}>
      <div style={cardStyle}>
        <div style={{ marginBottom: "22px", textAlign: "center" }}>
          <h1
            style={{
              margin: 0,
              fontSize: "28px",
              fontWeight: 800,
              color: "#f8fafc",
              letterSpacing: "-0.02em",
            }}
          >
            SmartBot Admin
          </h1>
          <p style={{ marginTop: "10px", color: "#94a3b8", fontSize: "14px" }}>
            Panel administrativo del sistema de preguntas frecuentes
          </p>
        </div>

        <div
          style={{
            marginBottom: "18px",
            padding: "10px 12px",
            borderRadius: "10px",
            background: "#0b1324",
            border: "1px solid #1e293b",
            color: "#93c5fd",
            fontSize: "13px",
          }}
        >
          {serverStatus}
        </div>

        {error && (
          <div
            style={{
              marginBottom: "16px",
              padding: "10px 12px",
              borderRadius: "10px",
              background: "rgba(127, 29, 29, 0.25)",
              border: "1px solid rgba(239, 68, 68, 0.35)",
              color: "#fecaca",
              fontSize: "13px",
            }}
          >
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: "16px" }}>
            <label style={labelStyle}>Usuario</label>
            <input
              type="text"
              name="usuario"
              value={form.usuario}
              onChange={handleChange}
              placeholder="IA1-User"
              style={inputStyle}
              required
            />
          </div>

          <div style={{ marginBottom: "20px" }}>
            <label style={labelStyle}>Contraseña</label>
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              placeholder="••••••••••••"
              style={inputStyle}
              required
            />
          </div>

          <button type="submit" style={buttonStyle} disabled={loading}>
            {loading ? "Iniciando sesión..." : "Entrar al panel"}
          </button>
        </form>

        <div
          style={{
            marginTop: "18px",
            fontSize: "12px",
            color: "#64748b",
            textAlign: "center",
          }}
        >
          Recomendado para pruebas: usuario administrador preconfigurado
        </div>
      </div>
    </div>
  );
}