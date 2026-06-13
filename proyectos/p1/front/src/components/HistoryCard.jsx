import React from "react";

const HistoryCard = ({ item, onVerDetalle }) => {
  return (
    <div className="history-card" onClick={() => onVerDetalle(item.id)}>
      <h4>{item.usuario || "Usuario sin nombre"}</h4>
      <p><strong>Fecha:</strong> {new Date(item.fecha).toLocaleString()}</p>
      <p>
        <strong>Síntomas:</strong>{" "}
        {item.sintomas_seleccionados?.join(", ") || "Sin síntomas"}
      </p>
      <p>
        <strong>Diagnósticos:</strong>{" "}
        {item.diagnosticos?.length > 0
          ? item.diagnosticos.map((d) => d.nombre).join(", ")
          : "Sin diagnóstico"}
      </p>
    </div>
  );
};

export default HistoryCard;