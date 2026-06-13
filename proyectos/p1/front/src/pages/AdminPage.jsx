import React from "react";
import { useNavigate } from "react-router-dom";

const AdminPage = () => {
  const navigate = useNavigate();

  return (
    <div style={{ padding: "30px" }}>
      <h1>Vista de Administrador</h1>
      <p>Aquí luego irán los módulos administrativos.</p>

      <button
        onClick={() => navigate("/")}
        style={{
          marginTop: "20px",
          padding: "10px 16px",
          border: "none",
          borderRadius: "8px",
          background: "#2563eb",
          color: "#fff",
          cursor: "pointer",
        }}
      >
        Volver a usuario
      </button>
    </div>
  );
};

export default AdminPage;