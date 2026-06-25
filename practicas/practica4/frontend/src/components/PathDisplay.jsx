// src/components/PathDisplay.jsx
// Muestra la ruta encontrada como lista de coordenadas paso a paso.

export default function PathDisplay({ results }) {
    const { bfs, dfs } = results;
    if (!bfs && !dfs) return null;
  
    return (
      <div className="path-display">
        {bfs?.found && <PathSection result={bfs} color="var(--cyan)" />}
        {dfs?.found && <PathSection result={dfs} color="var(--pink)" />}
      </div>
    );
  }
  
  function PathSection({ result, color }) {
    return (
      <div className="path-section">
        <h4 className="path-title" style={{ color }}>
          Ruta {result.algorithm} — {result.path_length} pasos
        </h4>
        <div className="path-coords">
          {result.path.map((p, i) => (
            <span key={i} className="path-coord" style={{ borderColor: color }}>
              ({p.row},{p.col})
            </span>
          ))}
        </div>
      </div>
    );
  }