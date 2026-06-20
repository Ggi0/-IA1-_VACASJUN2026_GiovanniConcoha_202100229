import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { healthCheck, loginUser, saveSession, isAuthenticated } from "../services/api";
import { styles } from "../styles";

export default function LoginPage() {
  const navigate = useNavigate();

  const [form, setForm] = useState({ username: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [serverStatus, setServerStatus] = useState("Comprobando servidor...");
  const [error, setError] = useState("");

  useEffect(() => {
    // Si ya hay sesión, saltar directo al panel
    if (isAuthenticated()) {
      navigate("/panel");
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
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const data = await loginUser(form);
      saveSession(data);
      navigate("/panel");
    } catch (err) {
      const message =
        err?.response?.data?.detail || "No se pudo iniciar sesión.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.centerPage}>
      <div style={{ ...styles.card, width: "100%", maxWidth: "400px" }}>
        <div style={{ marginBottom: "20px", textAlign: "center" }}>
          <h1 style={{ ...styles.h1, fontSize: "26px" }}>SmartInvoice</h1>
          <p style={styles.subtitle}>
            Panel de procesamiento de facturas (OCR + RPA)
          </p>
        </div>

        <div
          style={{
            marginBottom: "16px",
            padding: "10px 12px",
            borderRadius: "8px",
            background: "#0b1324",
            border: "1px solid #1e293b",
            color: "#93c5fd",
            fontSize: "12px",
          }}
        >
          {serverStatus}
        </div>

        {error && <div style={styles.alertError}>{error}</div>}

        <form onSubmit={handleSubmit}>
          <div style={styles.formGroup}>
            <label style={styles.label}>Usuario</label>
            <input
              type="text"
              name="username"
              value={form.username}
              onChange={handleChange}
              placeholder="admin"
              style={styles.input}
              required
            />
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>Contraseña</label>
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              placeholder="••••••••"
              style={styles.input}
              required
            />
          </div>

          <button
            type="submit"
            style={loading ? styles.buttonDisabled : styles.button}
            disabled={loading}
            onMouseDown={(e) => e.preventDefault()}
          >
            {loading ? "Iniciando sesión..." : "Entrar"}
          </button>
        </form>
      </div>
    </div>
  );
}