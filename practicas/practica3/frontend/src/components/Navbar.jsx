import { useNavigate, useLocation } from "react-router-dom";
import { getSession, clearSession } from "../services/api";
import { styles } from "../styles";

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = getSession();

  const handleLogout = () => {
    clearSession();
    navigate("/login");
  };

  const linkStyle = (path) =>
    location.pathname === path ? styles.navLinkActive : styles.navLink;

  return (
    <div style={styles.navbar}>
      <div style={{ display: "flex", alignItems: "center", gap: "28px" }}>
        <strong style={{ fontSize: "16px" }}>SmartInvoice</strong>
        <div style={styles.navLinks}>
          <a href="/panel" style={linkStyle("/panel")}>
            Subir Factura
          </a>
          <a href="/facturas" style={linkStyle("/facturas")}>
            Facturas
          </a>
          <a href="/dashboard" style={linkStyle("/dashboard")}>
            Dashboard
          </a>
          <a href="/proveedores" style={linkStyle("/proveedores")}>
            Proveedores
          </a>
        </div>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
        <span style={{ fontSize: "13px", color: "#94a3b8" }}>
          {user?.username} ({user?.role})
        </span>
        <button onClick={handleLogout} style={styles.buttonSecondary}>
          Cerrar sesión
        </button>
      </div>
    </div>
  );
}