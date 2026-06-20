import axios from "axios";

// ─────────────────────────────────────────────────────────────────
// CONFIGURACIÓN BASE
// Usa 0.0.0.0/127.0.0.1 indistintamente — ambos apuntan al mismo backend.
// Para producción solo cambia la variable de entorno VITE_API_BASE_URL.
// ─────────────────────────────────────────────────────────────────
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const API_HEALTH_URL =
  import.meta.env.VITE_API_HEALTH_URL || "http://127.0.0.1:8000/health";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor: agrega el token JWT a cada request automáticamente
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("smartinvoice_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// =====================================================================
// HEALTH
// =====================================================================
export const healthCheck = async () => {
  const response = await axios.get(API_HEALTH_URL);
  return response.data;
};

// =====================================================================
// AUTH
// =====================================================================

// POST /auth/login
// Body: { username, password }
// Respuesta: { access_token, token_type, user: { id, username, email, role } }
export const loginUser = async (payload) => {
  const response = await api.post("/auth/login", payload);
  return response.data;
};

// GET /auth/me
// Respuesta: { id, username, email, role, is_active }
export const getCurrentUser = async () => {
  const response = await api.get("/auth/me");
  return response.data;
};

// ── Helpers de sesión (localStorage) ────────────────────────────────
export const saveSession = (data) => {
  localStorage.setItem("smartinvoice_token", data.access_token);
  localStorage.setItem("smartinvoice_user", JSON.stringify(data.user));
};

export const getSession = () => {
  const token = localStorage.getItem("smartinvoice_token");
  const userRaw = localStorage.getItem("smartinvoice_user");
  const user = userRaw ? JSON.parse(userRaw) : null;
  return { token, user };
};

export const clearSession = () => {
  localStorage.removeItem("smartinvoice_token");
  localStorage.removeItem("smartinvoice_user");
};

export const isAuthenticated = () => {
  return !!localStorage.getItem("smartinvoice_token");
};

// =====================================================================
// INVOICES — Flujo principal
// =====================================================================

// POST /invoices/upload
// Body: FormData con el campo "file"
// Respuesta: { status: READY|NEEDS_REVIEW|ERROR, extracted_data, validation, file_path, ... }
export const uploadInvoice = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post("/invoices/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

// POST /invoices/validate
// Body: { invoice_number, date, provider, nit, subtotal, taxes, total }
// Respuesta: { is_valid, errors: [{field, message}], warnings, clean_data }
export const validateInvoice = async (data) => {
  const response = await api.post("/invoices/validate", data);
  return response.data;
};

// POST /invoices/trigger-rpa
// Body: { invoice_data: {...}, file_path: "..." }
// Respuesta: { success, invoice_id, rpa_status, rpa_message, duration_ms }
export const triggerRPA = async (invoiceData, filePath) => {
  const response = await api.post("/invoices/trigger-rpa", {
    invoice_data: invoiceData,
    file_path: filePath,
  });
  return response.data;
};

// GET /invoices
// Respuesta: lista de facturas
export const getInvoices = async () => {
  const response = await api.get("/invoices/");
  return response.data;
};

// GET /invoices/{id}
// Respuesta: objeto factura
export const getInvoiceById = async (id) => {
  const response = await api.get(`/invoices/${id}`);
  return response.data;
};

// GET /invoices/{id}/logs
// Respuesta: lista de entradas de bitácora de esa factura
export const getInvoiceLogs = async (id) => {
  const response = await api.get(`/invoices/${id}/logs`);
  return response.data;
};

// =====================================================================
// PROVIDERS — CRUD
// =====================================================================

// GET /providers
export const getProviders = async () => {
  const response = await api.get("/providers/");
  return response.data;
};

// GET /providers/{id}
export const getProviderById = async (id) => {
  const response = await api.get(`/providers/${id}`);
  return response.data;
};

// POST /providers
// Body: { name, nit, address?, phone? }
export const createProvider = async (data) => {
  const response = await api.post("/providers/", data);
  return response.data;
};

// PUT /providers/{id}
// Body: campos a actualizar (parcial)
export const updateProvider = async (id, data) => {
  const response = await api.put(`/providers/${id}`, data);
  return response.data;
};

// DELETE /providers/{id}
export const deleteProvider = async (id) => {
  const response = await api.delete(`/providers/${id}`);
  return response.data;
};

// =====================================================================
// LOGS — Bitácora
// =====================================================================

// GET /logs  (solo ADMIN en backend)
export const getAllLogs = async () => {
  const response = await api.get("/logs/");
  return response.data;
};

// =====================================================================
// DASHBOARD
// =====================================================================

// GET /dashboard/metrics
export const getDashboardMetrics = async () => {
  const response = await api.get("/dashboard/metrics");
  return response.data;
};

// GET /dashboard/recent?limit=10
export const getRecentInvoices = async (limit = 10) => {
  const response = await api.get("/dashboard/recent", {
    params: { limit },
  });
  return response.data;
};

export default api;