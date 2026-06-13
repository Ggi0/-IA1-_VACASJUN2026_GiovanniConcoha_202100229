import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import SymptomCard from "../components/SymptomCard";
import DiagnosisBox from "../components/DiagnosisBox";
import HistoryCard from "../components/HistoryCard";

import {
  obtenerSintomas,
  diagnosticarEquipo,
  obtenerHistorial,
  obtenerHistorialPorId,
} from "../services/API_user";

import "../styles/userPage.css";

const UserPage = () => {
  const navigate = useNavigate();

  const [usuario, setUsuario] = useState("");
  const [sintomas, setSintomas] = useState([]);
  const [seleccionados, setSeleccionados] = useState([]);
  const [diagnosticos, setDiagnosticos] = useState([]);
  const [recomendaciones, setRecomendaciones] = useState([]);
  const [historial, setHistorial] = useState([]);
  const [mensaje, setMensaje] = useState("");
  const [cargando, setCargando] = useState(false);

  useEffect(() => {
    cargarDatosIniciales();
  }, []);

  const cargarDatosIniciales = async () => {
    try {
      const [sintomasData, historialData] = await Promise.all([
        obtenerSintomas(),
        obtenerHistorial(20, 0),
      ]);

      setSintomas(sintomasData.sintomas || []);
      setHistorial(historialData.historial || []);
    } catch (error) {
      console.error("Error cargando datos iniciales:", error);
      setMensaje("Error al cargar síntomas o historial.");
    }
  };

  const toggleSintoma = (id) => {
    setSeleccionados((prev) => {
      const nuevo = prev.includes(id)
        ? prev.filter((item) => item !== id)
        : [...prev, id];

      console.log("Síntomas seleccionados:", nuevo);
      return nuevo;
    });
  };

  const handleDiagnosticar = async () => {
    setMensaje("");

    if (seleccionados.length === 0) {
      setMensaje("Debe seleccionar al menos un síntoma.");
      console.log("Payload inválido: no hay síntomas seleccionados");
      return;
    }

    const payload = {
      sintomas: seleccionados,
      usuario: usuario.trim() || "Usuario Anónimo",
    };

    console.log("Payload final recolectado por el front:", payload);

    try {
      setCargando(true);

      const data = await diagnosticarEquipo(payload);

      setDiagnosticos(data.diagnosticos || []);

      const todasRecomendaciones =
        data.diagnosticos?.flatMap((d) => d.recomendaciones || []) || [];
      setRecomendaciones(todasRecomendaciones);

      if (data.mensaje) {
        setMensaje(data.mensaje);
      } else {
        setMensaje("Diagnóstico realizado correctamente.");
      }

      // Recargar historial después de diagnosticar
      const historialData = await obtenerHistorial(20, 0);
      setHistorial(historialData.historial || []);
    } catch (error) {
      console.error("Error en diagnóstico:", error);
      setMensaje(
        error.response?.data?.error || "Error al realizar el diagnóstico."
      );
    } finally {
      setCargando(false);
    }
  };

  const handleVerDetalleHistorial = async (id) => {
    try {
      const data = await obtenerHistorialPorId(id);

      console.log("Detalle del historial:", data);

      setDiagnosticos(data.diagnosticos || []);

      const todasRecomendaciones =
        data.diagnosticos?.flatMap((d) => d.recomendaciones || []) || [];
      setRecomendaciones(todasRecomendaciones);

      setMensaje(`Mostrando detalle del historial ID: ${id}`);
    } catch (error) {
      console.error("Error obteniendo historial por ID:", error);
      setMensaje(
        error.response?.data?.error || "No se pudo obtener el detalle."
      );
    }
  };

  return (
    <div className="user-page">
      <header className="top-header">
        <h1>Diagnóstico de Equipos - Usuario</h1>
        <button className="admin-btn" onClick={() => navigate("/admin")}>
          Administrar
        </button>
      </header>

      <div className="main-layout">
        {/* COLUMNA IZQUIERDA */}
        <section className="left-section">
          <div className="user-form-box">
            <label>Nombre de usuario (opcional)</label>
            <input
              type="text"
              placeholder="Ej: Juan Pérez"
              value={usuario}
              onChange={(e) => setUsuario(e.target.value)}
            />
          </div>

          <div className="symptoms-section">
            <h2>Selecciona los síntomas</h2>
            <div className="symptoms-grid">
              {sintomas.map((sintoma) => (
                <SymptomCard
                  key={sintoma.id}
                  sintoma={sintoma}
                  selected={seleccionados.includes(sintoma.id)}
                  onToggle={toggleSintoma}
                />
              ))}
            </div>
          </div>

          <div className="action-row">
            <button
              className="diagnose-btn"
              onClick={handleDiagnosticar}
              disabled={cargando}
            >
              {cargando ? "Diagnosticando..." : "Consultar diagnóstico"}
            </button>
          </div>

          {mensaje && <div className="message-box">{mensaje}</div>}

          <div className="result-panels">
            <DiagnosisBox diagnosticos={diagnosticos} />

            <div className="panel-box">
              <h3>Recomendaciones</h3>
              {recomendaciones.length === 0 ? (
                <p>No hay recomendaciones todavía.</p>
              ) : (
                <ul className="recommendation-list">
                  {recomendaciones.map((rec, index) => (
                    <li key={index}>{rec}</li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </section>

        {/* COLUMNA DERECHA */}
        <aside className="right-section">
          <h2>Historial</h2>
          <div className="history-list">
            {historial.length === 0 ? (
              <p>No hay historial disponible.</p>
            ) : (
              historial.map((item) => (
                <HistoryCard
                  key={item.id}
                  item={item}
                  onVerDetalle={handleVerDetalleHistorial}
                />
              ))
            )}
          </div>
        </aside>
      </div>
    </div>
  );
};

export default UserPage;