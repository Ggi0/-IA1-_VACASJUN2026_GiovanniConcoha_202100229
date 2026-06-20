import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import { getDashboardMetrics, getRecentInvoices } from "../services/api";
import { styles, statusBadgeStyle } from "../styles";

export default function DashboardPage() {
  const [metrics, setMetrics] = useState(null);
  const [recent, setRecent] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError("");
    try {
      const [metricsData, recentData] = await Promise.all([
        getDashboardMetrics(),
        getRecentInvoices(10),
      ]);
      setMetrics(metricsData);
      setRecent(recentData);
    } catch (err) {
      setError(err?.response?.data?.detail || "Error al cargar el dashboard.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <Navbar />
      <div style={styles.container}>
        <h1 style={styles.h1}>Dashboard</h1>
        <p style={styles.subtitle}>
          Métricas generales del procesamiento de facturas.
        </p>

        {error && <div style={styles.alertError}>{error}</div>}

        {loading ? (
          <p style={styles.subtitle}>Cargando métricas...</p>
        ) : (
          <>
            <div style={styles.grid3}>
              <MetricCard label="Total de facturas" value={metrics.total_invoices} />
              <MetricCard label="Procesadas" value={metrics.processed} />
              <MetricCard label="Pendientes" value={metrics.pending} />
              <MetricCard label="Con errores" value={metrics.with_errors} />
              <MetricCard label="Rechazadas" value={metrics.rejected} />
              <MetricCard label="Duplicadas" value={metrics.duplicates} />
              <MetricCard
                label="Monto total procesado"
                value={`Q${Number(metrics.total_amount).toFixed(2)}`}
              />
              <MetricCard
                label="Tasa de éxito RPA"
                value={`${metrics.rpa_success_rate}%`}
              />
            </div>

            <div style={{ ...styles.card, marginTop: "24px" }}>
              <h2 style={styles.h2}>Últimas facturas procesadas</h2>
              {recent.length === 0 ? (
                <p style={styles.subtitle}>Sin facturas recientes.</p>
              ) : (
                <table style={styles.table}>
                  <thead>
                    <tr>
                      <th style={styles.th}>ID</th>
                      <th style={styles.th}>Número</th>
                      <th style={styles.th}>Total</th>
                      <th style={styles.th}>Estado</th>
                      <th style={styles.th}>Fecha</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recent.map((inv) => (
                      <tr key={inv.id}>
                        <td style={styles.td}>{inv.id}</td>
                        <td style={styles.td}>{inv.invoice_number}</td>
                        <td style={styles.td}>Q{Number(inv.total).toFixed(2)}</td>
                        <td style={styles.td}>
                          <span style={statusBadgeStyle(inv.status)}>
                            {inv.status}
                          </span>
                        </td>
                        <td style={styles.td}>{inv.created_at}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function MetricCard({ label, value }) {
  return (
    <div style={styles.metricCard}>
      <div style={styles.metricValue}>{value}</div>
      <div style={styles.metricLabel}>{label}</div>
    </div>
  );
}