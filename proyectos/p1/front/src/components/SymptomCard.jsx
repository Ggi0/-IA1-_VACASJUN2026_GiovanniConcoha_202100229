import React from "react";

const SymptomCard = ({ sintoma, selected, onToggle }) => {
  return (
    <label className={`symptom-card ${selected ? "selected" : ""}`}>
      <input
        type="checkbox"
        checked={selected}
        onChange={() => onToggle(sintoma.id)}
      />
      <div className="symptom-content">
        <h4>{sintoma.nombre}</h4>
        <p>{sintoma.descripcion}</p>
        <span className="symptom-id">{sintoma.id}</span>
      </div>
    </label>
  );
};

export default SymptomCard;