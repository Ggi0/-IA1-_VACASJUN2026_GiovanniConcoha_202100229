// styles.js
// =========
// Estilos compartidos, minimalistas, sin librerías de CSS.
// Se importan como objeto y se usan inline: style={styles.card}

export const colors = {
  bg: "#0f172a",
  bgLight: "#1e293b",
  border: "#334155",
  text: "#e2e8f0",
  textMuted: "#94a3b8",
  primary: "#2563eb",
  primaryHover: "#1d4ed8",
  success: "#16a34a",
  successBg: "rgba(22, 163, 74, 0.12)",
  error: "#dc2626",
  errorBg: "rgba(220, 38, 38, 0.12)",
  warning: "#d97706",
  warningBg: "rgba(217, 119, 6, 0.12)",
};

export const styles = {
  page: {
    minHeight: "100vh",
    background: colors.bg,
    color: colors.text,
    fontFamily: "Inter, system-ui, -apple-system, sans-serif",
  },
  container: {
    maxWidth: "1100px",
    margin: "0 auto",
    padding: "24px",
  },
  centerPage: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: colors.bg,
    color: colors.text,
    fontFamily: "Inter, system-ui, sans-serif",
    padding: "20px",
  },
  card: {
    background: colors.bgLight,
    border: `1px solid ${colors.border}`,
    borderRadius: "12px",
    padding: "24px",
    marginBottom: "20px",
  },
  navbar: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "16px 24px",
    background: colors.bgLight,
    borderBottom: `1px solid ${colors.border}`,
  },
  navLinks: {
    display: "flex",
    gap: "20px",
    alignItems: "center",
  },
  navLink: {
    color: colors.textMuted,
    textDecoration: "none",
    fontSize: "14px",
    fontWeight: 500,
  },
  navLinkActive: {
    color: colors.text,
    textDecoration: "none",
    fontSize: "14px",
    fontWeight: 700,
  },
  h1: {
    fontSize: "24px",
    fontWeight: 700,
    margin: "0 0 8px 0",
    color: colors.text,
  },
  h2: {
    fontSize: "18px",
    fontWeight: 700,
    margin: "0 0 16px 0",
    color: colors.text,
  },
  subtitle: {
    fontSize: "14px",
    color: colors.textMuted,
    margin: "0 0 20px 0",
  },
  label: {
    display: "block",
    marginBottom: "6px",
    color: colors.textMuted,
    fontSize: "13px",
    fontWeight: 600,
  },
  input: {
    width: "100%",
    padding: "10px 12px",
    borderRadius: "8px",
    border: `1px solid ${colors.border}`,
    background: colors.bg,
    color: colors.text,
    outline: "none",
    fontSize: "14px",
    boxSizing: "border-box",
  },
  inputError: {
    width: "100%",
    padding: "10px 12px",
    borderRadius: "8px",
    border: `1px solid ${colors.error}`,
    background: colors.bg,
    color: colors.text,
    outline: "none",
    fontSize: "14px",
    boxSizing: "border-box",
  },
  formGroup: {
    marginBottom: "14px",
  },
  errorText: {
    color: colors.error,
    fontSize: "12px",
    marginTop: "4px",
  },
  button: {
    padding: "10px 18px",
    borderRadius: "8px",
    border: "none",
    background: colors.primary,
    color: "#fff",
    fontWeight: 600,
    cursor: "pointer",
    fontSize: "14px",
  },
  buttonSecondary: {
    padding: "10px 18px",
    borderRadius: "8px",
    border: `1px solid ${colors.border}`,
    background: "transparent",
    color: colors.text,
    fontWeight: 600,
    cursor: "pointer",
    fontSize: "14px",
  },
  buttonDisabled: {
    padding: "10px 18px",
    borderRadius: "8px",
    border: "none",
    background: colors.border,
    color: colors.textMuted,
    fontWeight: 600,
    cursor: "not-allowed",
    fontSize: "14px",
  },
  buttonDanger: {
    padding: "8px 14px",
    borderRadius: "8px",
    border: "none",
    background: colors.error,
    color: "#fff",
    fontWeight: 600,
    cursor: "pointer",
    fontSize: "13px",
  },
  alertSuccess: {
    padding: "12px 14px",
    borderRadius: "8px",
    background: colors.successBg,
    border: `1px solid ${colors.success}`,
    color: "#86efac",
    fontSize: "13px",
    marginBottom: "16px",
  },
  alertError: {
    padding: "12px 14px",
    borderRadius: "8px",
    background: colors.errorBg,
    border: `1px solid ${colors.error}`,
    color: "#fca5a5",
    fontSize: "13px",
    marginBottom: "16px",
  },
  alertWarning: {
    padding: "12px 14px",
    borderRadius: "8px",
    background: colors.warningBg,
    border: `1px solid ${colors.warning}`,
    color: "#fcd34d",
    fontSize: "13px",
    marginBottom: "16px",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    fontSize: "13px",
  },
  th: {
    textAlign: "left",
    padding: "10px 12px",
    borderBottom: `1px solid ${colors.border}`,
    color: colors.textMuted,
    fontWeight: 600,
  },
  td: {
    padding: "10px 12px",
    borderBottom: `1px solid ${colors.border}`,
    color: colors.text,
  },
  badge: (bgColor, textColor) => ({
    display: "inline-block",
    padding: "3px 10px",
    borderRadius: "999px",
    fontSize: "11px",
    fontWeight: 700,
    background: bgColor,
    color: textColor,
  }),
  grid3: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
    gap: "16px",
  },
  metricCard: {
    background: colors.bgLight,
    border: `1px solid ${colors.border}`,
    borderRadius: "12px",
    padding: "18px",
  },
  metricValue: {
    fontSize: "26px",
    fontWeight: 800,
    color: colors.text,
  },
  metricLabel: {
    fontSize: "12px",
    color: colors.textMuted,
    marginTop: "4px",
  },
  dropzone: {
    border: `2px dashed ${colors.border}`,
    borderRadius: "12px",
    padding: "40px 20px",
    textAlign: "center",
    cursor: "pointer",
    background: colors.bg,
  },
  twoColumns: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "24px",
  },
};

export const statusBadgeStyle = (status) => {
  switch (status) {
    case "PROCESSED":
      return styles.badge(colors.successBg, "#86efac");
    case "PENDING":
      return styles.badge(colors.warningBg, "#fcd34d");
    case "ERROR":
      return styles.badge(colors.errorBg, "#fca5a5");
    case "REJECTED":
      return styles.badge(colors.errorBg, "#fca5a5");
    default:
      return styles.badge(colors.border, colors.text);
  }
};