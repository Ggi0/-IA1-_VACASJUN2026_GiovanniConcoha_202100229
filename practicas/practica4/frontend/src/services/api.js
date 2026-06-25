// src/services/api.js
// Capa de comunicación con el backend de RoboMaze.
// Todos los fetch al backend pasan por aquí — nunca llamar a fetch directamente desde componentes.

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

/**
 * Helper interno: fetch + manejo de errores unificado.
 * Lanza un Error con el mensaje del backend si el status no es 2xx.
 */
async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  // Para exportaciones (blob), no parsear JSON
  if (options._blob) {
    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: "Error del servidor" }));
      throw new Error(err.error || "Error desconocido");
    }
    return res.blob();
  }

  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Error desconocido");
  return data;
}

// ─── Health ────────────────────────────────────────────────────────────────

export const checkHealth = () => request("/health");

// ─── Búsqueda ──────────────────────────────────────────────────────────────

/** Ejecuta BFS y retorna SearchResult */
export const runBFS = (mazePayload) =>
  request("/search/bfs", { method: "POST", body: JSON.stringify(mazePayload) });

/** Ejecuta DFS y retorna SearchResult */
export const runDFS = (mazePayload) =>
  request("/search/dfs", { method: "POST", body: JSON.stringify(mazePayload) });

/** Ejecuta BFS + DFS y retorna { bfs, dfs, comparison } */
export const runBoth = (mazePayload) =>
  request("/search/both", { method: "POST", body: JSON.stringify(mazePayload) });

// ─── Laberintos ────────────────────────────────────────────────────────────

/** Lista metadata de los laberintos predefinidos */
export const listPredefined = () => request("/mazes/predefined");

/** Obtiene un laberinto predefinido completo por ID */
export const getPredefined = (mazeId) => request(`/mazes/predefined/${mazeId}`);

/**
 * Genera un laberinto aleatorio
 * @param {number} rows
 * @param {number} cols
 * @param {number} density 0.0–0.6
 */
export const generateMaze = (rows, cols, density) =>
  request("/mazes/generate", {
    method: "POST",
    body: JSON.stringify({ rows, cols, density }),
  });

// ─── Exportación ───────────────────────────────────────────────────────────

/** Descarga el CSV de resultados */
export const exportCSV = async (results) => {
  const blob = await request("/export/csv", {
    method: "POST",
    body: JSON.stringify(results),
    _blob: true,
  });
  downloadBlob(blob, "robomaze_results.csv", "text/csv");
};

/** Descarga el PDF de resultados */
export const exportPDF = async (results) => {
  const blob = await request("/export/pdf", {
    method: "POST",
    body: JSON.stringify(results),
    _blob: true,
  });
  downloadBlob(blob, "robomaze_results.pdf", "application/pdf");
};

/** Helper para disparar descarga desde un Blob */
function downloadBlob(blob, filename, type) {
  const url = URL.createObjectURL(new Blob([blob], { type }));
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}