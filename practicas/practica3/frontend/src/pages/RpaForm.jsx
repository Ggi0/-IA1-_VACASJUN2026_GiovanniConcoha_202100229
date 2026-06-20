/**
 * RpaForm.jsx
 * ============
 * Formulario en la ruta /rpa-form.
 * Este es el TARGET del bot Selenium: el RPA abre esta página,
 * llena los campos por su "id" y hace submit. El backend recibe
 * el POST en /invoices/rpa-submit y completa el guardado en la DB.
 *
 * IMPORTANTE: NO requiere login. El bot no tiene sesión de usuario;
 * la seguridad la da el campo oculto "rpa_token" que el backend valida.
 *
 * Los IDs de cada input (field-invoice_number, rpa-submit-btn, etc.)
 * deben mantenerse exactamente así: el bot Selenium los busca por ID.
 */

import { useState, useEffect } from "react";
import api from "../services/api";

const EMPTY_FORM = {
  invoice_number: "",
  date: "",
  provider: "",
  nit: "",
  subtotal: "",
  taxes: "",
  total: "",
  file_path: "",
  user_id: "",
  rpa_token: "",
};

export default function RpaForm() {
  const [formData, setFormData] = useState(EMPTY_FORM);
  const [status, setStatus] = useState("idle"); // idle | submitting | success | error
  const [message, setMessage] = useState("");

  // El bot pasa los valores como query params en la URL al navegar:
  // /rpa-form?invoice_number=001-2024&date=2024-01-15&...
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const fromUrl = {};

    Object.keys(formData).forEach((key) => {
      const val = params.get(key);
      if (val) fromUrl[key] = val;
    });

    if (Object.keys(fromUrl).length > 0) {
      setFormData((prev) => ({ ...prev, ...fromUrl }));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
  e.preventDefault();
  setStatus("submitting");
  setMessage("");

  try {
    const payload = {
      ...formData,

      // 🔥 FORZAR TOKEN AQUÍ
      rpa_token:
        document.getElementById("field-rpa_token")?.value ||
        "smartinvoice-rpa-secret-2024",
    };

    const response = await api.post("/invoices/rpa-submit", payload);

    setStatus("success");
    setMessage(
      response.data.message ||
        `Factura procesada correctamente. ID: ${response.data.invoice_id}`
    );
  } catch (err) {
    setStatus("error");
    setMessage(
      err?.response?.data?.detail || "Error al procesar la factura."
    );
  }
};

  return (
    <div style={{ maxWidth: 600, margin: "40px auto", fontFamily: "monospace" }}>
      <h2>SmartInvoice — RPA Form</h2>
      <p style={{ color: "#888", fontSize: 12 }}>
        Este formulario es llenado automáticamente por el bot RPA (Selenium).
        No requiere inicio de sesión.
      </p>

      <form onSubmit={handleSubmit} id="rpa-invoice-form">
        <div>
          <label>Número de Factura</label>
          <br />
          <input
            id="field-invoice_number"
            name="invoice_number"
            value={formData.invoice_number}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label>Fecha</label>
          <br />
          <input
            id="field-date"
            name="date"
            value={formData.date}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label>Proveedor</label>
          <br />
          <input
            id="field-provider"
            name="provider"
            value={formData.provider}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label>NIT</label>
          <br />
          <input
            id="field-nit"
            name="nit"
            value={formData.nit}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label>Subtotal</label>
          <br />
          <input
            id="field-subtotal"
            name="subtotal"
            value={formData.subtotal}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label>Impuestos</label>
          <br />
          <input
            id="field-taxes"
            name="taxes"
            value={formData.taxes}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label>Total</label>
          <br />
          <input
            id="field-total"
            name="total"
            value={formData.total}
            onChange={handleChange}
            required
          />
        </div>

        {/* Campos ocultos — el bot los llena vía JavaScript */}
        <input
          type="hidden"
          id="field-file_path"
          name="file_path"
          value={formData.file_path}
          onChange={handleChange}
        />
        <input
          type="hidden"
          id="field-user_id"
          name="user_id"
          value={formData.user_id}
          onChange={handleChange}
        />
        <input
          type="hidden"
          id="field-rpa_token"
          name="rpa_token"
          value={formData.rpa_token}
          onChange={handleChange}
        />

        <button
          type="submit"
          id="rpa-submit-btn"
          disabled={status === "submitting"}
          style={{ marginTop: 16, padding: "8px 24px" }}
        >
          {status === "submitting" ? "Procesando..." : "Registrar Factura"}
        </button>
      </form>

      {/* El bot Selenium busca estos divs por ID para leer el resultado */}
      {status === "success" && (
        <div id="rpa-result-success" style={{ color: "green", marginTop: 12 }}>
          ✅ {message}
        </div>
      )}

      {status === "error" && (
        <div id="rpa-result-error" style={{ color: "red", marginTop: 12 }}>
          ❌ {message}
        </div>
      )}
    </div>
  );
}