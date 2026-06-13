import React from "react";

const DiagnosisBox = ({ diagnosticos }) => {
  return (
    <div className="panel-box">
      <h3>Diagnóstico</h3>

      {!diagnosticos || diagnosticos.length === 0 ? (
        <p>No hay diagnóstico disponible todavía.</p>
      ) : (
        diagnosticos.map((diag) => (
          <div key={diag.falla_id} className="diagnosis-item">
            <h4>{diag.nombre}</h4>
            <p><strong>ID:</strong> {diag.falla_id}</p>
            <p><strong>Tipo:</strong> {diag.tipo}</p>
            <p>{diag.descripcion}</p>
          </div>
        ))
      )}
    </div>
  );
};

export default DiagnosisBox;