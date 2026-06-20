import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import { getInvoices, getInvoiceLogs } from "../services/api";
import { styles, statusBadgeStyle } from "../styles";

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [logs, setLogs] = useState([]);
  const [logsLoading, setLogsLoading] = useState(false);

  useEffect(() => {
    loadInvoices();
  }, []);

  const loadInvoices = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getInvoices();
      setInvoices(data);
    } catch (err) {
      setError(err?.response?.data?.detail || "Error al cargar las facturas.");
    } finally {
      setLoading(false);
    }
  };

  const openDetail = async (invoice) => {
    setSelectedInvoice(invoice);
    setLogsLoading(true);
    setLogs([]);
    try {
      const data = await getInvoiceLogs(invoice.id);
      setLogs(data);
    } catch (err) {
      setLogs([]);
    } finally {
      setLogsLoading(false);
    }
  };

  const closeDetail = () => {
    setSelectedInvoice(null);
    setLogs([]);
  };

  return (
    <div style={styles.page}>
      <Navbar />
      <div style={styles.container}>
        <h1 style={styles.h1}>Facturas</h1>
        <p style={styles.subtitle}>
          Listado de todas las facturas procesadas por el sistema.
        </p>

        {error && <div style={styles.alertError}>{error}</div>}

        <div style={styles.card}>
          {loading ? (
            <p style={styles.subtitle}>Cargando...</p>
          ) : invoices.length === 0 ? (
            <p style={styles.subtitle}>No hay facturas registradas todavía.</p>
          ) : (
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>ID</th>
                  <th style={styles.th}>Número</th>
                  <th style={styles.th}>Fecha</th>
                  <th style={styles.th}>NIT</th>
                  <th style={styles.th}>Total</th>
                  <th style={styles.th}>Estado</th>
                  <th style={styles.th}>Duplicado</th>
                  <th style={styles.th}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((inv) => (
                  <tr key={inv.id}>
                    <td style={styles.td}>{inv.id}</td>
                    <td style={styles.td}>{inv.invoice_number}</td>
                    <td style={styles.td}>{inv.date}</td>
                    <td style={styles.td}>{inv.nit}</td>
                    <td style={styles.td}>Q{Number(inv.total).toFixed(2)}</td>
                    <td style={styles.td}>
                      <span style={statusBadgeStyle(inv.status)}>
                        {inv.status}
                      </span>
                    </td>
                    <td style={styles.td}>{inv.is_duplicate ? "Sí" : "No"}</td>
                    <td style={styles.td}>
                      <button
                        style={styles.buttonSecondary}
                        onClick={() => openDetail(inv)}
                      >
                        Ver bitácora
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* ── Modal simple de detalle / bitácora ──────────────────── */}
        {selectedInvoice && (
          <div
            style={{
              position: "fixed",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: "rgba(0,0,0,0.6)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              padding: "20px",
            }}
            onClick={closeDetail}
          >
            <div
              style={{ ...styles.card, maxWidth: "600px", width: "100%" }}
              onClick={(e) => e.stopPropagation()}
            >
              <h2 style={styles.h2}>
                Factura #{selectedInvoice.invoice_number} — Bitácora
              </h2>

              <div style={{ marginBottom: "16px", fontSize: "13px", color: "#94a3b8" }}>
                <div>Proveedor NIT: {selectedInvoice.nit}</div>
                <div>Total: Q{Number(selectedInvoice.total).toFixed(2)}</div>
                <div>Archivo: {selectedInvoice.file_path}</div>
              </div>

              {logsLoading ? (
                <p style={styles.subtitle}>Cargando bitácora...</p>
              ) : logs.length === 0 ? (
                <p style={styles.subtitle}>Sin registros de bitácora.</p>
              ) : (
                <table style={styles.table}>
                  <thead>
                    <tr>
                      <th style={styles.th}>Fecha</th>
                      <th style={styles.th}>Estado</th>
                      <th style={styles.th}>RPA</th>
                      <th style={styles.th}>Mensaje</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logs.map((log) => (
                      <tr key={log.id}>
                        <td style={styles.td}>{log.process_date}</td>
                        <td style={styles.td}>
                          <span style={statusBadgeStyle(log.status)}>
                            {log.status}
                          </span>
                        </td>
                        <td style={styles.td}>{log.rpa_result}</td>
                        <td style={styles.td}>{log.message}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}

              <div style={{ marginTop: "16px" }}>
                <button style={styles.buttonSecondary} onClick={closeDetail}>
                  Cerrar
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}