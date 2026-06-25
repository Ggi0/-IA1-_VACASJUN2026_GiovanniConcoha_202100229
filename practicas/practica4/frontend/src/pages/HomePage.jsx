// src/pages/HomePage.jsx
// Página principal de RoboMaze.
// Orquesta todos los paneles: configuración, grid, algoritmos y resultados.

import { useEffect } from "react";
import { useMaze } from "../hooks/useMaze";
import MazeGrid from "../components/MazeGrid";
import Toolbar from "../components/Toolbar";
import ConfigPanel from "../components/ConfigPanel";
import AlgoPanel from "../components/AlgoPanel";
import PathDisplay from "../components/PathDisplay";
import Toast from "../components/Toast";

export default function HomePage() {
  const maze = useMaze();

  // Inicializar con un grid vacío por defecto
  useEffect(() => {
    maze.initGrid(10, 10);
  }, []);

  // Determinar qué explorado/path mostrar en el grid
  // Si hay ambos (both), mostrar BFS sobre el grid; DFS requiere toggle (simplificado: BFS primero)
  const activeResult =
    maze.activeAlgo === "dfs" ? maze.results.dfs : maze.results.bfs;
  const explored = activeResult?.explored || [];
  const path = activeResult?.path || [];

  return (
    <div className="home-page">
      {/* ── Header ─────────────────────────────────────────────── */}
      <header className="site-header">
        <div className="header-brand">
          <span className="brand-icon">⬡</span>
          <span className="brand-name">RoboMaze</span>
        </div>
        <p className="header-tagline">
          Visualiza BFS &amp; DFS encontrando rutas en laberintos
        </p>
        <div className="header-badges">
          <span className="badge bfs-badge">BFS</span>
          <span className="badge dfs-badge">DFS</span>
          <span className="badge">Python Backend</span>
        </div>
      </header>

      {/* ── Main layout ────────────────────────────────────────── */}
      <main className="main-layout">

        {/* Columna izquierda: configuración */}
        <aside className="sidebar-left">
          <ConfigPanel
            rows={maze.rows}
            cols={maze.cols}
            density={maze.density}
            setRows={maze.setRows}
            setCols={maze.setCols}
            setDensity={maze.setDensity}
            onInit={maze.initGrid}
            onGenerate={maze.generate}
            onClearWalls={maze.clearWalls}
            predefinedList={maze.predefinedList}
            onLoadPredefined={maze.loadPredefined}
            onLoadPredefinedList={maze.loadPredefinedList}
          />
        </aside>

        {/* Columna central: grid */}
        <section className="grid-section">
          <div className="grid-header">
            <h2 className="grid-title">
              Laberinto{" "}
              <span className="grid-dims">
                {maze.rows}×{maze.cols}
              </span>
            </h2>
            {maze.activeAlgo === "both" && (
              <div className="algo-tabs">
                <span className="algo-tab active-cyan">BFS visualizado</span>
                <span className="algo-tab-note">/ DFS en panel →</span>
              </div>
            )}
          </div>

          <Toolbar drawMode={maze.drawMode} setDrawMode={maze.setDrawMode} />

          <MazeGrid
            grid={maze.grid}
            start={maze.start}
            end={maze.end}
            explored={explored}
            path={path}
            drawMode={maze.drawMode}
            onCellAction={maze.toggleCell}
          />

          {/* Ruta completa en texto */}
          <PathDisplay results={maze.results} />
        </section>

        {/* Columna derecha: algoritmos */}
        <aside className="sidebar-right">
          <AlgoPanel
            results={maze.results}
            loading={maze.loading}
            hasResults={maze.hasResults}
            onBFS={maze.runBFS}
            onDFS={maze.runDFS}
            onBoth={maze.runBoth}
            onExportCSV={maze.doExportCSV}
            onExportPDF={maze.doExportPDF}
          />
        </aside>
      </main>

      {/* ── Toast de errores ──────────────────────────────────── */}
      <Toast message={maze.error} onClose={() => maze.setError(null)} />
    </div>
  );
}