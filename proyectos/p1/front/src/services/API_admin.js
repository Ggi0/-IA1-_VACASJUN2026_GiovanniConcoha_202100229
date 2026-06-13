import axios from "axios";

const BASE_URL = import.meta.env.VITE_RUTA_BASE;

const apiAdmin = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor request
apiAdmin.interceptors.request.use(
  (config) => {
    console.log("========== ADMIN REQUEST ==========");
    console.log("URL:", `${config.baseURL}${config.url}`);
    console.log("METHOD:", config.method?.toUpperCase());
    console.log("PARAMS:", config.params || null);
    console.log("PAYLOAD:", config.data || null);
    console.log("==================================");
    return config;
  },
  (error) => {
    console.error("Error en request interceptor ADMIN:", error);
    return Promise.reject(error);
  }
);

// Interceptor response
apiAdmin.interceptors.response.use(
  (response) => {
    if (typeof response.data === "string" && response.data.includes("<html")) {
      console.error("🚨 ADMIN ERROR: se recibió HTML en lugar de JSON");
      return Promise.reject(new Error("Respuesta HTML detectada"));
    }

    console.log("========== ADMIN RESPONSE ==========");
    console.log("URL:", response.config?.url);
    console.log("STATUS:", response.status);
    console.log("DATA:", response.data);
    console.log("===================================");
    return response;
  },
  (error) => {
    console.error("========== ADMIN RESPONSE ERROR ==========");
    console.error("URL:", error.config?.url);
    console.error("STATUS:", error.response?.status);
    console.error("DATA:", error.response?.data);
    console.error("MESSAGE:", error.message);
    console.error("=========================================");
    return Promise.reject(error);
  }
);

//
// ==========================
// CRUD SÍNTOMAS
// ==========================
//
export const getAdminSintomas = async () => {
  const response = await apiAdmin.get("/admin/sintomas");
  return response.data;
};

export const postAdminSintoma = async (payload) => {
  console.log("Payload POST /admin/sintomas:", payload);
  const response = await apiAdmin.post("/admin/sintomas", payload);
  return response.data;
};

export const putAdminSintoma = async (id, payload) => {
  console.log(`Payload PUT /admin/sintomas/${id}:`, payload);
  const response = await apiAdmin.put(`/admin/sintomas/${id}`, payload);
  return response.data;
};

export const deleteAdminSintoma = async (id) => {
  console.log(`Payload DELETE /admin/sintomas/${id}:`, { id });
  const response = await apiAdmin.delete(`/admin/sintomas/${id}`);
  return response.data;
};

//
// ==========================
// CRUD FALLAS
// ==========================
//
export const getAdminFallas = async () => {
  const response = await apiAdmin.get("/admin/fallas");
  return response.data;
};

export const postAdminFalla = async (payload) => {
  console.log("Payload POST /admin/fallas:", payload);
  const response = await apiAdmin.post("/admin/fallas", payload);
  return response.data;
};

export const putAdminFalla = async (id, payload) => {
  console.log(`Payload PUT /admin/fallas/${id}:`, payload);
  const response = await apiAdmin.put(`/admin/fallas/${id}`, payload);
  return response.data;
};

export const deleteAdminFalla = async (id) => {
  console.log(`Payload DELETE /admin/fallas/${id}:`, { id });
  const response = await apiAdmin.delete(`/admin/fallas/${id}`);
  return response.data;
};

//
// ==========================
// CRUD RECOMENDACIONES
// ==========================
//
export const getAdminRecomendaciones = async (falla_id = "") => {
  const params = falla_id ? { falla_id } : {};
  console.log("Payload GET /admin/recomendaciones params:", params);
  const response = await apiAdmin.get("/admin/recomendaciones", { params });
  return response.data;
};

export const postAdminRecomendacion = async (payload) => {
  console.log("Payload POST /admin/recomendaciones:", payload);
  const response = await apiAdmin.post("/admin/recomendaciones", payload);
  return response.data;
};

export const putAdminRecomendacion = async (id, payload) => {
  console.log(`Payload PUT /admin/recomendaciones/${id}:`, payload);
  const response = await apiAdmin.put(`/admin/recomendaciones/${id}`, payload);
  return response.data;
};

export const deleteAdminRecomendacion = async (id) => {
  console.log(`Payload DELETE /admin/recomendaciones/${id}:`, { id });
  const response = await apiAdmin.delete(`/admin/recomendaciones/${id}`);
  return response.data;
};

//
// ==========================
// CRUD REGLAS
// ==========================
//
export const getAdminReglas = async () => {
  const response = await apiAdmin.get("/admin/reglas");
  return response.data;
};

export const postAdminRegla = async (payload) => {
  console.log("Payload POST /admin/reglas:", payload);
  const response = await apiAdmin.post("/admin/reglas", payload);
  return response.data;
};

export const deleteAdminRegla = async (payload) => {
  console.log("Payload DELETE /admin/reglas:", payload);

  const response = await apiAdmin.delete("/admin/reglas", {
    data: payload,
  });

  return response.data;
};

export default apiAdmin;