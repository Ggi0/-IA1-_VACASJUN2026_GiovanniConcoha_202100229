import axios from "axios";

const BASE_URL = import.meta.env.VITE_RUTA_BASE;

// Instancia Axios
const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor para ver TODAS las requests
api.interceptors.request.use(
  (config) => {
    console.log("========== REQUEST ==========");
    console.log("URL:", `${config.baseURL}${config.url}`);
    console.log("METHOD:", config.method?.toUpperCase());
    console.log("PARAMS:", config.params || null);
    console.log("PAYLOAD:", config.data || null);
    return config;
  },
  (error) => {
    console.error("Error en request interceptor:", error);
    return Promise.reject(error);
  }
);

// Interceptor para ver responses
api.interceptors.response.use(
  (response) => {
    console.log("========== RESPONSE ==========");
    console.log("URL:", response.config?.url);
    console.log("STATUS:", response.status);
    console.log("DATA:", response.data);
    return response;
  },
  (error) => {
    console.error("========== RESPONSE ERROR ==========");
    console.error("URL:", error.config?.url);
    console.error("STATUS:", error.response?.status);
    console.error("DATA:", error.response?.data);
    console.error("MESSAGE:", error.message);
    return Promise.reject(error);
  }
);

// GET /sintomas
export const obtenerSintomas = async () => {
  const response = await api.get("/sintomas");
  return response.data;
};

// POST /diagnosticar
export const diagnosticarEquipo = async (payload) => {
  console.log("Payload enviado a /diagnosticar:", payload);
  const response = await api.post("/diagnosticar", payload);
  return response.data;
};

// GET /historial?limit=20&offset=0
export const obtenerHistorial = async (limit = 20, offset = 0) => {
  const response = await api.get("/historial", {
    params: { limit, offset },
  });
  return response.data;
};

// GET /historial/{id}
export const obtenerHistorialPorId = async (id) => {
  const response = await api.get(`/historial/${id}`);
  return response.data;
};

export default api;