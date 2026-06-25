// src/components/Toolbar.jsx
// Barra de herramientas para seleccionar el modo de dibujo del laberinto.

export default function Toolbar({ drawMode, setDrawMode }) {
    const tools = [
      { id: "wall",  label: "Pared",   icon: "⬛", title: "Dibujar paredes" },
      { id: "erase", label: "Borrar",  icon: "⬜", title: "Borrar celdas" },
      { id: "start", label: "Inicio",  icon: "🟢", title: "Mover punto de inicio" },
      { id: "end",   label: "Destino", icon: "🔴", title: "Mover punto destino" },
    ];
  
    return (
      <div className="toolbar">
        <span className="toolbar-label">Herramienta</span>
        <div className="toolbar-tools">
          {tools.map((t) => (
            <button
              key={t.id}
              className={`tool-btn ${drawMode === t.id ? "active" : ""}`}
              onClick={() => setDrawMode(t.id)}
              title={t.title}
            >
              <span className="tool-icon">{t.icon}</span>
              <span className="tool-label">{t.label}</span>
            </button>
          ))}
        </div>
      </div>
    );
  }