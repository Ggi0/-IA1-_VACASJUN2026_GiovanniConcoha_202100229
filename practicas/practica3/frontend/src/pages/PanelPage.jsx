import { useState, useRef } from "react";
import Navbar from "../components/Navbar";
import { uploadInvoice, validateInvoice, triggerRPA, getSession } from "../services/api";
import { styles } from "../styles";

// Campos del formulario de factura (usados tanto para mostrar como para editar)
const FIELD_LABELS = {
  invoice_number: "Número de Factura",
  date: "Fecha (YYYY-MM-DD)",
  provider: "Proveedor",
  nit: "NIT",
  subtotal: "Subtotal",
  taxes: "Impuestos",
  total: "Total",
};

const EMPTY_FORM = {
  invoice_number: "",
  date: "",
  provider: "",
  nit: "",
  subtotal: "",
  taxes: "",
  total: "",
};

export default function PanelPage() {
  const fileInputRef = useRef(null);
  const { user } = getSession();

  // ── Estados del flujo ───────────────────────────────────────────
  // idle           → esperando que el empleado seleccione un archivo
  // uploading      → /invoices/upload en curso
  // needs_review   → el OCR no extrajo todo, mostrar form editable + imagen
  // ready_to_send  → todo OK (del OCR o ya validado manualmente), listo para RPA
  // sending_rpa    → /invoices/trigger-rpa en curso (puede tardar)
  // done           → RPA terminó (éxito o fallo)
  const [stage, setStage] = useState("idle");

  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  const [filePath, setFilePath] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [fieldErrors, setFieldErrors] = useState({});
  const [warnings, setWarnings] = useState([]);
  const [globalMessage, setGlobalMessage] = useState("");

  const [rpaResult, setRpaResult] = useState(null); // { success, invoice_id, rpa_message }

  // ─────────────────────────────────────────────────────────────
  // PASO 1: Selección de archivo
  // ─────────────────────────────────────────────────────────────
  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);
    setGlobalMessage("");
    setFieldErrors({});
    setWarnings([]);

    // Preview solo si es imagen; los PDF no se previsualizan en <img>
    if (file.type.startsWith("image/")) {
      setPreviewUrl(URL.createObjectURL(file));
    } else {
      setPreviewUrl(null);
    }
  };

  const resetFlow = () => {
    setStage("idle");
    setSelectedFile(null);
    setPreviewUrl(null);
    setFilePath(null);
    setForm(EMPTY_FORM);
    setFieldErrors({});
    setWarnings([]);
    setGlobalMessage("");
    setRpaResult(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  // ─────────────────────────────────────────────────────────────
  // PASO 2, 3, 4, 5: Subir y procesar con OCR
  // ─────────────────────────────────────────────────────────────
  const handleUpload = async () => {
    if (!selectedFile) return;

    setStage("uploading");
    setGlobalMessage("");

    try {
      const result = await uploadInvoice(selectedFile);

      setFilePath(result.file_path);

      if (result.status === "ERROR") {
        setGlobalMessage(result.message || "Error procesando el archivo.");
        setStage("idle");
        return;
      }

      // Cargar los datos extraídos en el formulario (READY o NEEDS_REVIEW)
      setForm({
        invoice_number: result.extracted_data?.invoice_number ?? "",
        date: result.extracted_data?.date ?? "",
        provider: result.extracted_data?.provider ?? "",
        nit: result.extracted_data?.nit ?? "",
        subtotal: result.extracted_data?.subtotal ?? "",
        taxes: result.extracted_data?.taxes ?? "",
        total: result.extracted_data?.total ?? "",
      });

      setWarnings(result.validation?.warnings || []);

      if (result.status === "READY") {
        setFieldErrors({});
        setStage("ready_to_send");
      } else {
        // NEEDS_REVIEW — mostrar errores por campo
        const errMap = {};
        (result.validation?.errors || []).forEach((e) => {
          errMap[e.field] = e.message;
        });
        setFieldErrors(errMap);
        setGlobalMessage(result.message || "Revisa los campos marcados.");
        setStage("needs_review");
      }
    } catch (err) {
      setGlobalMessage(
        err?.response?.data?.detail || "Error al subir el archivo."
      );
      setStage("idle");
    }
  };

  // ─────────────────────────────────────────────────────────────
  // PASO 5b: El empleado corrige y vuelve a validar
  // ─────────────────────────────────────────────────────────────
  const handleFieldChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleRevalidate = async () => {
    setGlobalMessage("");
    try {
      const payload = {
        invoice_number: form.invoice_number,
        date: form.date,
        provider: form.provider,
        nit: form.nit,
        subtotal: form.subtotal === "" ? null : Number(form.subtotal),
        taxes: form.taxes === "" ? null : Number(form.taxes),
        total: form.total === "" ? null : Number(form.total),
      };

      const result = await validateInvoice(payload);

      if (result.is_valid) {
        setFieldErrors({});
        setWarnings(result.warnings || []);
        // Usar los datos normalizados que regresa el backend
        setForm({
          invoice_number: result.clean_data.invoice_number,
          date: result.clean_data.date,
          provider: result.clean_data.provider,
          nit: result.clean_data.nit,
          subtotal: result.clean_data.subtotal,
          taxes: result.clean_data.taxes,
          total: result.clean_data.total,
        });
        setStage("ready_to_send");
      } else {
        const errMap = {};
        (result.errors || []).forEach((e) => {
          errMap[e.field] = e.message;
        });
        setFieldErrors(errMap);
        setWarnings(result.warnings || []);
        setGlobalMessage("Aún hay campos con errores.");
      }
    } catch (err) {
      setGlobalMessage(
        err?.response?.data?.detail || "Error al validar los datos."
      );
    }
  };

  // ─────────────────────────────────────────────────────────────
  // PASO 6, 7, 8: Disparar el RPA
  // ─────────────────────────────────────────────────────────────
  const handleTriggerRPA = async () => {
    setStage("sending_rpa");
    setGlobalMessage("");

    try {
      const invoiceData = {
        invoice_number: form.invoice_number,
        date: form.date,
        provider: form.provider,
        nit: form.nit,
        subtotal: Number(form.subtotal),
        taxes: Number(form.taxes),
        total: Number(form.total),
      };

      const result = await triggerRPA(invoiceData, filePath);
      setRpaResult(result);
      setStage("done");
    } catch (err) {
      setRpaResult({
        success: false,
        rpa_message:
          err?.response?.data?.detail || "Error al ejecutar la automatización RPA.",
      });
      setStage("done");
    }
  };

  // ─────────────────────────────────────────────────────────────
  // RENDER
  // ─────────────────────────────────────────────────────────────
  return (
    <div style={styles.page}>
      <Navbar />
      <div style={styles.container}>
        <h1 style={styles.h1}>Subir Factura</h1>
        <p style={styles.subtitle}>
          Bienvenido, {user?.username}. Sube una factura en PDF, JPG o PNG
          para iniciar el procesamiento automático.
        </p>

        {globalMessage && (
          <div style={styles.alertError}>{globalMessage}</div>
        )}

        {/* ── STAGE: idle / uploading — selector de archivo ───────── */}
        {(stage === "idle" || stage === "uploading") && (
          <div style={styles.card}>
            <div
              style={styles.dropzone}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={handleFileSelect}
                style={{ display: "none" }}
              />
              {selectedFile ? (
                <p>Archivo seleccionado: <strong>{selectedFile.name}</strong></p>
              ) : (
                <p>Haz click aquí para seleccionar una factura (PDF, JPG, PNG)</p>
              )}
            </div>

            <div style={{ marginTop: "16px" }}>
              <button
                style={
                  !selectedFile || stage === "uploading"
                    ? styles.buttonDisabled
                    : styles.button
                }
                disabled={!selectedFile || stage === "uploading"}
                onClick={handleUpload}
              >
                {stage === "uploading" ? "Procesando con OCR..." : "Procesar Factura"}
              </button>
            </div>
          </div>
        )}

        {/* ── STAGE: needs_review / ready_to_send — form + imagen ──── */}
        {(stage === "needs_review" ||
          stage === "ready_to_send" ||
          stage === "sending_rpa") && (
          <div style={styles.twoColumns}>
            {/* Columna izquierda: formulario editable */}
            <div style={styles.card}>
              <h2 style={styles.h2}>
                {stage === "needs_review"
                  ? "Revisa y corrige los datos"
                  : "Datos extraídos — listos para registrar"}
              </h2>

              {warnings.length > 0 && (
                <div style={styles.alertWarning}>
                  {warnings.map((w, i) => (
                    <div key={i}>⚠ {w}</div>
                  ))}
                </div>
              )}

              {Object.keys(FIELD_LABELS).map((field) => (
                <div style={styles.formGroup} key={field}>
                  <label style={styles.label}>{FIELD_LABELS[field]}</label>
                  <input
                    type="text"
                    value={form[field] ?? ""}
                    onChange={(e) => handleFieldChange(field, e.target.value)}
                    style={fieldErrors[field] ? styles.inputError : styles.input}
                    disabled={stage === "sending_rpa"}
                  />
                  {fieldErrors[field] && (
                    <div style={styles.errorText}>{fieldErrors[field]}</div>
                  )}
                </div>
              ))}

              <div style={{ display: "flex", gap: "10px", marginTop: "10px" }}>
                {stage === "needs_review" && (
                  <button style={styles.button} onClick={handleRevalidate}>
                    Validar Cambios
                  </button>
                )}

                {stage === "ready_to_send" && (
                  <button style={styles.button} onClick={handleTriggerRPA}>
                    Registrar Factura (Ejecutar RPA)
                  </button>
                )}

                {stage === "sending_rpa" && (
                  <button style={styles.buttonDisabled} disabled>
                    Ejecutando automatización... (puede tardar 5–20s)
                  </button>
                )}

                <button style={styles.buttonSecondary} onClick={resetFlow}>
                  Cancelar
                </button>
              </div>
            </div>

            {/* Columna derecha: vista previa del archivo */}
            <div style={styles.card}>
              <h2 style={styles.h2}>Documento</h2>
              {previewUrl ? (
                <img
                  src={previewUrl}
                  alt="Factura"
                  style={{ width: "100%", borderRadius: "8px", border: "1px solid #334155" }}
                />
              ) : (
                <p style={styles.subtitle}>
                  Vista previa no disponible para este tipo de archivo (PDF).
                  Archivo: {selectedFile?.name}
                </p>
              )}
            </div>
          </div>
        )}

        {/* ── STAGE: done — resultado final del RPA ────────────────── */}
        {stage === "done" && rpaResult && (
          <div style={styles.card}>
            {rpaResult.success ? (
              <div style={styles.alertSuccess}>
                ✅ {rpaResult.rpa_message || "Factura procesada correctamente."}
                {rpaResult.invoice_id && (
                  <div>ID de factura: {rpaResult.invoice_id}</div>
                )}
              </div>
            ) : (
              <div style={styles.alertError}>
                ❌ {rpaResult.rpa_message || "El RPA no pudo completar el registro."}
                {rpaResult.invoice_id && (
                  <div>
                    La factura se guardó con estado ERROR (ID: {rpaResult.invoice_id}).
                  </div>
                )}
              </div>
            )}

            <button style={styles.button} onClick={resetFlow}>
              Subir otra factura
            </button>
          </div>
        )}
      </div>
    </div>
  );
}