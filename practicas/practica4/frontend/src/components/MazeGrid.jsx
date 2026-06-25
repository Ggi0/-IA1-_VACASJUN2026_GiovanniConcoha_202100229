// src/components/MazeGrid.jsx
// Cuadrícula interactiva del laberinto.
// Renderiza cada celda con su estado (libre/pared/inicio/fin/explorado/ruta)
// y maneja eventos de dibujo con mouse (click + drag).

import { useState, useCallback, useRef } from "react";

/** Determina la clase CSS de una celda según su rol */
function getCellClass(row, col, grid, start, end, explored, path) {
  if (start && row === start.row && col === start.col) return "cell-start";
  if (end   && row === end.row   && col === end.col)   return "cell-end";
  if (path.some((p) => p.row === row && p.col === col))     return "cell-path";
  if (explored.some((e) => e.row === row && e.col === col)) return "cell-explored";
  if (grid[row]?.[col] === 1) return "cell-wall";
  return "cell-free";
}

export default function MazeGrid({
  grid, start, end,
  explored = [], path = [],
  drawMode, onCellAction,
}) {
  const isDragging = useRef(false);

  const handleMouseDown = useCallback((row, col) => {
    isDragging.current = true;
    onCellAction(row, col);
  }, [onCellAction]);

  const handleMouseEnter = useCallback((row, col) => {
    if (!isDragging.current) return;
    // En drag solo aplica wall/erase, no start/end
    if (drawMode === "wall" || drawMode === "erase") onCellAction(row, col);
  }, [onCellAction, drawMode]);

  const handleMouseUp = useCallback(() => {
    isDragging.current = false;
  }, []);

  if (!grid || grid.length === 0) {
    return (
      <div className="grid-empty">
        <span>Configura el laberinto para comenzar</span>
      </div>
    );
  }

  const cellSize = Math.min(
    Math.floor(560 / grid[0].length),
    Math.floor(560 / grid.length),
    40
  );

  return (
    <div
      className="maze-grid-wrapper"
      onMouseLeave={() => { isDragging.current = false; }}
      onMouseUp={handleMouseUp}
      style={{ userSelect: "none" }}
    >
      <div
        className="maze-grid"
        style={{
          display: "grid",
          gridTemplateColumns: `repeat(${grid[0].length}, ${cellSize}px)`,
          gridTemplateRows: `repeat(${grid.length}, ${cellSize}px)`,
          gap: "1px",
          background: "#0d1117",
          border: "1px solid #30363d",
          borderRadius: "8px",
          padding: "4px",
          boxShadow: "0 0 40px rgba(0,200,255,0.08)",
        }}
      >
        {grid.map((row, ri) =>
          row.map((_, ci) => {
            const cls = getCellClass(ri, ci, grid, start, end, explored, path);
            return (
              <div
                key={`${ri}-${ci}`}
                className={`maze-cell ${cls}`}
                style={{ width: cellSize, height: cellSize }}
                onMouseDown={() => handleMouseDown(ri, ci)}
                onMouseEnter={() => handleMouseEnter(ri, ci)}
              />
            );
          })
        )}
      </div>
      <div className="grid-legend">
        <LegendItem color="var(--green)" label="Inicio" />
        <LegendItem color="var(--pink)" label="Destino" />
        <LegendItem color="var(--cyan)" label="Ruta" />
        <LegendItem color="rgba(0,200,255,0.25)" label="Explorado" />
        <LegendItem color="#1c2128" label="Pared" border="1px solid #30363d" />
        <LegendItem color="transparent" label="Libre" border="1px solid #30363d" />
      </div>
    </div>
  );
}

function LegendItem({ color, label, border }) {
  return (
    <div className="legend-item">
      <div
        className="legend-dot"
        style={{ background: color, border: border || "none" }}
      />
      <span>{label}</span>
    </div>
  );
}