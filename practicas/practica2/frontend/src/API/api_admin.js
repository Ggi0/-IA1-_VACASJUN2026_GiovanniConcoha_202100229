import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_HEALTH_URL = import.meta.env.VITE_API_HEALTH_URL || "http://localhost:8000/health";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor para enviar token automáticamente
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("smartbot_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// =========================
// HEALTH
// =========================
export const healthCheck = async () => {
  const response = await axios.get(API_HEALTH_URL);
  return response.data;
};

// =========================
// AUTH
// =========================
export const loginAdmin = async (payload) => {
  const response = await api.post("/auth/login", payload);
  return response.data;
};

// =========================
// PREGUNTAS FRECUENTES
// =========================
export const getPreguntas = async () => {
  const response = await api.get("/admin/preguntas/");
  return response.data;
};

export const getPreguntaById = async (id) => {
  const response = await api.get(`/admin/preguntas/${id}`);
  return response.data;
};

export const createPregunta = async (payload) => {
  const response = await api.post("/admin/preguntas/", payload);
  return response.data;
};

export const updatePregunta = async (id, payload) => {
  const response = await api.put(`/admin/preguntas/${id}`, payload);
  return response.data;
};

export const deletePregunta = async (id) => {
  const response = await api.delete(`/admin/preguntas/${id}`);
  return response.data;
};

// =========================
// CHATS AUTORIZADOS
// =========================
export const getChats = async () => {
  const response = await api.get("/admin/chats/");
  return response.data;
};

export const getChatById = async (id) => {
  const response = await api.get(`/admin/chats/${id}`);
  return response.data;
};

export const createChat = async (payload) => {
  const response = await api.post("/admin/chats/", payload);
  return response.data;
};

export const updateChat = async (id, payload) => {
  const response = await api.put(`/admin/chats/${id}`, payload);
  return response.data;
};

export const deleteChat = async (id) => {
  const response = await api.delete(`/admin/chats/${id}`);
  return response.data;
};

// =========================
// UTILIDADES
// =========================
export const logoutAdmin = () => {
  localStorage.removeItem("smartbot_token");
  localStorage.removeItem("smartbot_user");
};

export const saveSession = (data) => {
  if (data?.access_token) {
    localStorage.setItem("smartbot_token", data.access_token);
  }
  if (data?.usuario) {
    localStorage.setItem("smartbot_user", JSON.stringify(data.usuario));
  }
};

export const getSessionUser = () => {
  const user = localStorage.getItem("smartbot_user");
  return user ? JSON.parse(user) : null;
};

export const isAuthenticated = () => {
  return !!localStorage.getItem("smartbot_token");
};

export default api;