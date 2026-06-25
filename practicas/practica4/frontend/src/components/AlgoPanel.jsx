// src/components/AlgoPanel.jsx
// Panel de ejecución de algoritmos y visualización de estadísticas.

export default function AlgoPanel({ results, loading, onBFS, onDFS, onBoth, hasResults, onExportCSV, onExportPDF }) {
    const { bfs, dfs, comparison } = results;
  
    return (
      <div className="algo-panel">
        {/* ── Botones de ejecución ─────────────────────────── */}
        <div className="algo-section">
          <h3 className="section-title">Ejecutar Algoritmo</h3>
          <div className="algo-buttons">
            <button className="algo-btn bfs-btn" onClick={onBFS} disabled={loading}>
              <span className="btn-tag">BFS</span>
              <span className="btn-sub">Búsqueda en anchura</span>
            </button>
            <button className="algo-btn dfs-btn" onClick={onDFS} disabled={loading}>
              <span className="btn-tag">DFS</span>
              <span className="btn-sub">Búsqueda en profundidad</span>
            </button>
            <button className="algo-btn both-btn" onClick={onBoth} disabled={loading}>
              <span className="btn-tag">BFS + DFS</span>
              <span className="btn-sub">Comparar ambos</span>
            </button>
          </div>
        </div>
  
        {/* ── Loading ──────────────────────────────────────── */}
        {loading && (
          <div className="loading-bar">
            <div className="loading-fill" />
            <span>Ejecutando...</span>
          </div>
        )}
  
        {/* ── Resultados individuales ───────────────────────── */}
        {(bfs || dfs) && (
          <div className="algo-section">
            <h3 className="section-title">Resultados</h3>
            <div className="results-grid">
              {bfs && <ResultCard result={bfs} color="var(--cyan)" />}
              {dfs && <ResultCard result={dfs} color="var(--pink)" />}
            </div>
          </div>
        )}
  
        {/* ── Comparación ───────────────────────────────────── */}
        {comparison && (
          <div className="algo-section">
            <h3 className="section-title">Comparación</h3>
            <ComparisonTable cmp={comparison} />
          </div>
        )}
  
        {/* ── Exportar ──────────────────────────────────────── */}
        {hasResults && (
          <div className="algo-section">
            <h3 className="section-title">Exportar Resultados</h3>
            <div className="export-buttons">
              <button className="export-btn csv-btn" onClick={onExportCSV} disabled={loading}>
                ⬇ Descargar CSV
              </button>
              <button className="export-btn pdf-btn" onClick={onExportPDF} disabled={loading}>
                ⬇ Descargar PDF
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }
  
  function ResultCard({ result, color }) {
    return (
      <div className="result-card" style={{ borderColor: color }}>
        <div className="result-header" style={{ color }}>
          <span className="result-algo">{result.algorithm}</span>
          <span className={`result-badge ${result.found ? "found" : "notfound"}`}>
            {result.found ? "✓ Ruta encontrada" : "✗ Sin ruta"}
          </span>
        </div>
        <div className="result-stats">
          <Stat label="Nodos explorados" value={result.nodes_explored} />
          <Stat label="Longitud ruta" value={result.path_length || "—"} />
          <Stat label="Tiempo" value={`${result.execution_time_ms} ms`} />
        </div>
        {result.message && (
          <p className="result-message">{result.message}</p>
        )}
      </div>
    );
  }
  
  function Stat({ label, value }) {
    return (
      <div className="stat-item">
        <span className="stat-label">{label}</span>
        <span className="stat-value">{value}</span>
      </div>
    );
  }
  
  function ComparisonTable({ cmp }) {
    const rows = [
      { label: "Algoritmo más rápido",    value: cmp.faster_algorithm },
      { label: "Menos nodos explorados",  value: cmp.fewer_nodes_explored },
      { label: "Ruta más corta",          value: cmp.shorter_path },
      { label: "Tiempo BFS (ms)",         value: cmp.bfs_time_ms },
      { label: "Tiempo DFS (ms)",         value: cmp.dfs_time_ms },
      { label: "Nodos BFS",               value: cmp.bfs_nodes },
      { label: "Nodos DFS",               value: cmp.dfs_nodes },
      { label: "Longitud BFS",            value: cmp.bfs_path_length },
      { label: "Longitud DFS",            value: cmp.dfs_path_length },
    ];
  
    return (
      <div className="comparison-table">
        {rows.map((r) => (
          <div key={r.label} className="cmp-row">
            <span className="cmp-label">{r.label}</span>
            <span className="cmp-value">{r.value}</span>
          </div>
        ))}
        {cmp.note && <p className="cmp-note">{cmp.note}</p>}
      </div>
    );
  }
  