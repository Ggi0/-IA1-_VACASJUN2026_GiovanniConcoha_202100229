// src/components/ConfigPanel.jsx
// Panel de configuración: dimensiones, densidad, laberintos predefinidos y generación.

import { useEffect } from "react";

export default function ConfigPanel({
  rows, cols, density,
  setRows, setCols, setDensity,
  onInit, onGenerate, onClearWalls,
  predefinedList, onLoadPredefined, onLoadPredefinedList,
}) {
  useEffect(() => {
    onLoadPredefinedList();
  }, []);

  return (
    <div className="config-panel">
      {/* ── Dimensiones ──────────────────────────── */}
      <div className="config-section">
        <h3 className="section-title">Configurar Laberinto</h3>

        <label className="config-label">
          Filas <span className="config-val">{rows}</span>
          <input
            type="range" min={3} max={25} value={rows}
            onChange={(e) => setRows(+e.target.value)}
            className="config-slider"
          />
        </label>

        <label className="config-label">
          Columnas <span className="config-val">{cols}</span>
          <input
            type="range" min={3} max={25} value={cols}
            onChange={(e) => setCols(+e.target.value)}
            className="config-slider"
          />
        </label>

        <label className="config-label">
          Densidad de paredes <span className="config-val">{Math.round(density * 100)}%</span>
          <input
            type="range" min={0} max={60} value={Math.round(density * 100)}
            onChange={(e) => setDensity(+e.target.value / 100)}
            className="config-slider"
          />
        </label>

        <div className="config-actions">
          <button className="cfg-btn primary" onClick={() => onInit(rows, cols)}>
            Nuevo grid vacío
          </button>
          <button className="cfg-btn accent" onClick={onGenerate}>
            ⚡ Generar aleatorio
          </button>
          <button className="cfg-btn ghost" onClick={onClearWalls}>
            Limpiar paredes
          </button>
        </div>
      </div>

      {/* ── Predefinidos ─────────────────────────── */}
      {predefinedList.length > 0 && (
        <div className="config-section">
          <h3 className="section-title">Laberintos Predefinidos</h3>
          <div className="predefined-list">
            {predefinedList.map((m) => (
              <button
                key={m.id}
                className="predefined-btn"
                onClick={() => onLoadPredefined(m.id)}
              >
                <span className="predefined-name">{m.name}</span>
                <span className="predefined-size">{m.rows}×{m.cols}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}