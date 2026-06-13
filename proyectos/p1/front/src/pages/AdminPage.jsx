import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  getAdminSintomas,
  postAdminSintoma,
  putAdminSintoma,
  deleteAdminSintoma,
  getAdminFallas,
  postAdminFalla,
  putAdminFalla,
  deleteAdminFalla,
  getAdminRecomendaciones,
  postAdminRecomendacion,
  putAdminRecomendacion,
  deleteAdminRecomendacion,
  getAdminReglas,
  postAdminRegla,
  deleteAdminRegla,
  postAdminTelegramMensaje,
} from "../services/API_admin";
import "../styles/adminPage.css";

const TABS = ["sintomas", "fallas", "recomendaciones", "reglas"];

const AdminPage = () => {
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState("sintomas");
  const [loading, setLoading] = useState(false);
  const [mensajeGlobal, setMensajeGlobal] = useState("");

  // Data lists
  const [sintomas, setSintomas] = useState([]);
  const [fallas, setFallas] = useState([]);
  const [recomendaciones, setRecomendaciones] = useState([]);
  const [reglas, setReglas] = useState([]);

  // Right message box
  const [mensajeAdmin, setMensajeAdmin] = useState("");
  const [habilitarMensajes, setHabilitarMensajes] = useState(true);

  // Forms - Síntomas
  const [sintomaForm, setSintomaForm] = useState({
    id: "",
    nombre: "",
    descripcion: "",
  });
  const [sintomaEditId, setSintomaEditId] = useState("");
  const [sintomaDeleteId, setSintomaDeleteId] = useState("");

  // Forms - Fallas
  const [fallaForm, setFallaForm] = useState({
    id: "",
    nombre: "",
    tipo: "",
    descripcion: "",
  });
  const [fallaEditId, setFallaEditId] = useState("");
  const [fallaDeleteId, setFallaDeleteId] = useState("");

  // Forms - Recomendaciones
  const [recoFilterFallaId, setRecoFilterFallaId] = useState("");
  const [recomendacionForm, setRecomendacionForm] = useState({
    id: "",
    falla_id: "",
    descripcion: "",
  });
  const [recomendacionEditId, setRecomendacionEditId] = useState("");
  const [recomendacionDeleteId, setRecomendacionDeleteId] = useState("");

  // Forms - Reglas
  const [reglaForm, setReglaForm] = useState({
    falla_id: "",
    sintomas: "",
  });
  const [reglaDeleteForm, setReglaDeleteForm] = useState({
    falla_id: "",
    sintomas: "",
  });

  useEffect(() => {
    cargarTodo();
  }, []);

  const cargarTodo = async () => {
  try {
    setLoading(true);
    setMensajeGlobal("Cargando panel administrativo...");

    const resSintomas = await getAdminSintomas();
    setSintomas(resSintomas.sintomas || []);

    const resFallas = await getAdminFallas();
    setFallas(resFallas.fallas || []);

    const resRecomendaciones = await getAdminRecomendaciones();
    setRecomendaciones(resRecomendaciones.recomendaciones || []);

    const resReglas = await getAdminReglas();
    setReglas(resReglas.reglas || []);

    setMensajeGlobal("Datos administrativos cargados correctamente.");
  } catch (error) {
    console.error("Error carga inicial admin:", error);
    setMensajeGlobal(
      error.response?.data?.error || "Error al cargar datos administrativos."
    );
  } finally {
    setLoading(false);
  }
};

  const parseSintomasArray = (value) => {
    return value
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
  };

  const handleEnviarMensajeAdmin = async () => {
  try {

    if (!habilitarMensajes) {
      setMensajeGlobal(
        "Mensajes deshabilitados. No se envió nada."
      );
      return;
    }

    if (!mensajeAdmin.trim()) {
      setMensajeGlobal(
        "Debes escribir un mensaje en la caja de texto."
      );
      return;
    }

    const payload = {
      mensaje: mensajeAdmin.trim(),
    };

    console.log(
      "Payload Telegram Admin:",
      payload
    );

    const data = await postAdminTelegramMensaje(
      payload
    );

    setMensajeGlobal(
      data.mensaje ||
      "Mensaje enviado correctamente."
    );

    setMensajeAdmin("");

  } catch (error) {

    console.error(
      "Error enviando mensaje Telegram:",
      error
    );

    setMensajeGlobal(
      error.response?.data?.error ||
      "Error al enviar mensaje."
    );
  }
};

  //
  // =========================
  // ACCIONES SÍNTOMAS
  // =========================
  //
  const crearSintoma = async () => {
    try {
      const payload = {
        id: sintomaForm.id.trim(),
        nombre: sintomaForm.nombre.trim(),
        descripcion: sintomaForm.descripcion.trim(),
      };

      console.log("Payload recolectado front - crear síntoma:", payload);

      const data = await postAdminSintoma(payload);
      setMensajeGlobal(data.mensaje || "Síntoma creado correctamente.");
      setSintomaForm({ id: "", nombre: "", descripcion: "" });

      const listado = await getAdminSintomas();
      setSintomas(listado.sintomas || []);
    } catch (error) {
      setMensajeGlobal(
        error.response?.data?.error || "Error al crear síntoma."
      );
    }
  };

  const actualizarSintoma = async () => {
    try {
      const payload = {
        nombre: sintomaForm.nombre.trim(),
        descripcion: sintomaForm.descripcion.trim(),
      };

      console.log("Payload recolectado front - actualizar síntoma:", {
        id: sintomaEditId,
        ...payload,
      });

      const data = await putAdminSintoma(sintomaEditId.trim(), payload);
      setMensajeGlobal(data.mensaje || "Síntoma actualizado correctamente.");

      const listado = await getAdminSintomas();
      setSintomas(listado.sintomas || []);
    } catch (error) {
      setMensajeGlobal(
        error.response?.data?.error || "Error al actualizar síntoma."
      );
    }
  };

  const eliminarSintoma = async () => {
    try {
      console.log("Payload recolectado front - eliminar síntoma:", {
        id: sintomaDeleteId,
      });

      const data = await deleteAdminSintoma(sintomaDeleteId.trim());
      setMensajeGlobal(data.mensaje || "Síntoma eliminado correctamente.");
      setSintomaDeleteId("");

      const listado = await getAdminSintomas();
      setSintomas(listado.sintomas || []);
    } catch (error) {
      setMensajeGlobal(
        error.response?.data?.error || "Error al eliminar síntoma."
      );
    }
  };

  //
  // =========================
  // ACCIONES FALLAS
  // =========================
  //
  const crearFalla = async () => {
    try {
      const payload = {
        id: fallaForm.id.trim(),
        nombre: fallaForm.nombre.trim(),
        tipo: fallaForm.tipo.trim(),
        descripcion: fallaForm.descripcion.trim(),
      };

      console.log("Payload recolectado front - crear falla:", payload);

      const data = await postAdminFalla(payload);
      setMensajeGlobal(data.mensaje || "Falla creada correctamente.");
      setFallaForm({ id: "", nombre: "", tipo: "", descripcion: "" });

      const listado = await getAdminFallas();
      setFallas(listado.fallas || []);
    } catch (error) {
      setMensajeGlobal(error.response?.data?.error || "Error al crear falla.");
    }
  };

  const actualizarFalla = async () => {
    try {
      const payload = {
        nombre: fallaForm.nombre.trim(),
        tipo: fallaForm.tipo.trim(),
        descripcion: fallaForm.descripcion.trim(),
      };

      console.log("Payload recolectado front - actualizar falla:", {
        id: fallaEditId,
        ...payload,
      });

      const data = await putAdminFalla(fallaEditId.trim(), payload);
      setMensajeGlobal(data.mensaje || "Falla actualizada correctamente.");

      const listado = await getAdminFallas();
      setFallas(listado.fallas || []);
    } catch (error) {
      setMensajeGlobal(
        error.response?.data?.error || "Error al actualizar falla."
      );
    }
  };

  const eliminarFalla = async () => {
    try {
      console.log("Payload recolectado front - eliminar falla:", {
        id: fallaDeleteId,
      });

      const data = await deleteAdminFalla(fallaDeleteId.trim());
      setMensajeGlobal(data.mensaje || "Falla eliminada correctamente.");
      setFallaDeleteId("");

      const listado = await getAdminFallas();
      setFallas(listado.fallas || []);
    } catch (error) {
      setMensajeGlobal(
        error.response?.data?.error || "Error al eliminar falla."
      );
    }
  };

  //
  // =========================
  // ACCIONES RECOMENDACIONES
  // =========================
  //
  const cargarRecomendacionesFiltradas = async () => {
    try {
      const data = await getAdminRecomendaciones(recoFilterFallaId.trim());
      setRecomendaciones(data.recomendaciones || []);
      setMensajeGlobal(
        recoFilterFallaId.trim()
          ? `Recomendaciones filtradas por falla ${recoFilterFallaId}.`
          : "Mostrando todas las recomendaciones."
      );
    } catch (error) {
      setMensajeGlobal(
        error.response?.data?.error || "Error al filtrar recomendaciones."
      );
    }
  };

  const crearRecomendacion = async () => {
    try {
      const payload = {
        id: recomendacionForm.id.trim(),
        falla_id: recomendacionForm.falla_id.trim(),
        descripcion: recomendacionForm.descripcion.trim(),
      };

      console.log("Payload recolectado front - crear recomendación:", payload);

      const data = await postAdminRecomendacion(payload);
      setMensajeGlobal(data.mensaje || "Recomendación creada correctamente.");
      setRecomendacionForm({ id: "", falla_id: "", descripcion: "" });

      const listado = await getAdminRecomendaciones();
      setRecomendaciones(listado.recomendaciones || []);
    } catch (error) {
      setMensajeGlobal(
        error.response?.data?.error || "Error al crear recomendación."
      );
    }
  };

  const actualizarRecomendacion = async () => {
    try {
      const payload = {
        falla_id: recomendacionForm.falla_id.trim(),
        descripcion: recomendacionForm.descripcion.trim(),
      };

      console.log("Payload recolectado front - actualizar recomendación:", {
        id: recomendacionEditId,
        ...payload,
      });

      const data = await putAdminRecomendacion(
        recomendacionEditId.trim(),
        payload
      );
      setMensajeGlobal(
        data.mensaje || "Recomendación actualizada correctamente."
      );

      const listado = await getAdminRecomendaciones();
      setRecomendaciones(listado.recomendaciones || []);
    } catch (error) {
      setMensajeGlobal(
        error.response?.data?.error || "Error al actualizar recomendación."
      );
    }
  };

  const eliminarRecomendacion = async () => {
    try {
      console.log("Payload recolectado front - eliminar recomendación:", {
        id: recomendacionDeleteId,
      });

      const data = await deleteAdminRecomendacion(recomendacionDeleteId.trim());
      setMensajeGlobal(data.mensaje || "Recomendación eliminada correctamente.");
      setRecomendacionDeleteId("");

      const listado = await getAdminRecomendaciones();
      setRecomendaciones(listado.recomendaciones || []);
    } catch (error) {
      setMensajeGlobal(
        error.response?.data?.error || "Error al eliminar recomendación."
      );
    }
  };

  //
  // =========================
  // ACCIONES REGLAS
  // =========================
  //
  const crearRegla = async () => {
    try {
      const payload = {
        falla_id: reglaForm.falla_id.trim(),
        sintomas: parseSintomasArray(reglaForm.sintomas),
      };

      console.log("Payload recolectado front - crear regla:", payload);

      const data = await postAdminRegla(payload);
      setMensajeGlobal(data.mensaje || "Regla creada correctamente.");
      setReglaForm({ falla_id: "", sintomas: "" });

      const listado = await getAdminReglas();
      setReglas(listado.reglas || []);
    } catch (error) {
      setMensajeGlobal(error.response?.data?.error || "Error al crear regla.");
    }
  };

  const eliminarRegla = async () => {
    try {
      const payload = {
        falla_id: reglaDeleteForm.falla_id.trim(),
        sintomas: parseSintomasArray(reglaDeleteForm.sintomas),
      };

      console.log("Payload recolectado front - eliminar regla:", payload);

      const data = await deleteAdminRegla(payload);
      setMensajeGlobal(data.mensaje || "Regla eliminada correctamente.");
      setReglaDeleteForm({ falla_id: "", sintomas: "" });

      const listado = await getAdminReglas();
      setReglas(listado.reglas || []);
    } catch (error) {
      setMensajeGlobal(
        error.response?.data?.error || "Error al eliminar regla."
      );
    }
  };

  const resumen = useMemo(() => {
    return {
      sintomas: sintomas.length,
      fallas: fallas.length,
      recomendaciones: recomendaciones.length,
      reglas: reglas.length,
    };
  }, [sintomas, fallas, recomendaciones, reglas]);

  return (
    <div className="admin-page">
      <header className="admin-header">
        <div>
          <h1>Panel Administrador</h1>
          <p>CRUD completo para síntomas, fallas, recomendaciones y reglas.</p>
        </div>

        <div className="header-buttons">
          <button className="reload-btn" onClick={cargarTodo}>
            Recargar datos
          </button>
          <button className="back-btn" onClick={() => navigate("/")}>
            Volver a usuario
          </button>
        </div>
      </header>

      <div className="summary-row">
        <div className="summary-card">Síntomas: {resumen.sintomas}</div>
        <div className="summary-card">Fallas: {resumen.fallas}</div>
        <div className="summary-card">
          Recomendaciones: {resumen.recomendaciones}
        </div>
        <div className="summary-card">Reglas: {resumen.reglas}</div>
      </div>

      {mensajeGlobal && <div className="global-message">{mensajeGlobal}</div>}
      {loading && <div className="global-loading">Cargando...</div>}

      <div className="admin-layout">
        {/* IZQUIERDA */}
        <section className="admin-left">
          <div className="tab-bar">
            {TABS.map((tab) => (
              <button
                key={tab}
                className={`tab-btn ${activeTab === tab ? "active" : ""}`}
                onClick={() => setActiveTab(tab)}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>

          {/* PANEL SINTOMAS */}
          {activeTab === "sintomas" && (
            <div className="crud-panel">
              <h2>Gestión de Síntomas</h2>

              <div className="crud-sections">
                <div className="crud-box">
                  <h3>Crear síntoma</h3>
                  <input
                    type="text"
                    placeholder="ID (ej: S21)"
                    value={sintomaForm.id}
                    onChange={(e) =>
                      setSintomaForm({ ...sintomaForm, id: e.target.value })
                    }
                  />
                  <input
                    type="text"
                    placeholder="Nombre"
                    value={sintomaForm.nombre}
                    onChange={(e) =>
                      setSintomaForm({ ...sintomaForm, nombre: e.target.value })
                    }
                  />
                  <textarea
                    placeholder="Descripción"
                    value={sintomaForm.descripcion}
                    onChange={(e) =>
                      setSintomaForm({
                        ...sintomaForm,
                        descripcion: e.target.value,
                      })
                    }
                  />
                  <button className="save-btn" onClick={crearSintoma}>
                    Crear
                  </button>
                </div>

                <div className="crud-box">
                  <h3>Actualizar síntoma</h3>
                  <input
                    type="text"
                    placeholder="ID a actualizar"
                    value={sintomaEditId}
                    onChange={(e) => setSintomaEditId(e.target.value)}
                  />
                  <input
                    type="text"
                    placeholder="Nuevo nombre"
                    value={sintomaForm.nombre}
                    onChange={(e) =>
                      setSintomaForm({ ...sintomaForm, nombre: e.target.value })
                    }
                  />
                  <textarea
                    placeholder="Nueva descripción"
                    value={sintomaForm.descripcion}
                    onChange={(e) =>
                      setSintomaForm({
                        ...sintomaForm,
                        descripcion: e.target.value,
                      })
                    }
                  />
                  <button className="edit-btn" onClick={actualizarSintoma}>
                    Actualizar
                  </button>
                </div>

                <div className="crud-box">
                  <h3>Eliminar síntoma</h3>
                  <input
                    type="text"
                    placeholder="ID a eliminar"
                    value={sintomaDeleteId}
                    onChange={(e) => setSintomaDeleteId(e.target.value)}
                  />
                  <button className="delete-btn" onClick={eliminarSintoma}>
                    Eliminar
                  </button>
                </div>
              </div>

              <div className="list-box">
                <h3>Listado de síntomas</h3>
                <div className="items-grid">
                  {sintomas.map((item) => (
                    <div key={item.id} className="item-card">
                      <strong>{item.id}</strong>
                      <h4>{item.nombre}</h4>
                      <p>{item.descripcion}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* PANEL FALLAS */}
          {activeTab === "fallas" && (
            <div className="crud-panel">
              <h2>Gestión de Fallas</h2>

              <div className="crud-sections">
                <div className="crud-box">
                  <h3>Crear falla</h3>
                  <input
                    type="text"
                    placeholder="ID (ej: F13)"
                    value={fallaForm.id}
                    onChange={(e) =>
                      setFallaForm({ ...fallaForm, id: e.target.value })
                    }
                  />
                  <input
                    type="text"
                    placeholder="Nombre"
                    value={fallaForm.nombre}
                    onChange={(e) =>
                      setFallaForm({ ...fallaForm, nombre: e.target.value })
                    }
                  />
                  <input
                    type="text"
                    placeholder="Tipo"
                    value={fallaForm.tipo}
                    onChange={(e) =>
                      setFallaForm({ ...fallaForm, tipo: e.target.value })
                    }
                  />
                  <textarea
                    placeholder="Descripción"
                    value={fallaForm.descripcion}
                    onChange={(e) =>
                      setFallaForm({
                        ...fallaForm,
                        descripcion: e.target.value,
                      })
                    }
                  />
                  <button className="save-btn" onClick={crearFalla}>
                    Crear
                  </button>
                </div>

                <div className="crud-box">
                  <h3>Actualizar falla</h3>
                  <input
                    type="text"
                    placeholder="ID a actualizar"
                    value={fallaEditId}
                    onChange={(e) => setFallaEditId(e.target.value)}
                  />
                  <input
                    type="text"
                    placeholder="Nuevo nombre"
                    value={fallaForm.nombre}
                    onChange={(e) =>
                      setFallaForm({ ...fallaForm, nombre: e.target.value })
                    }
                  />
                  <input
                    type="text"
                    placeholder="Nuevo tipo"
                    value={fallaForm.tipo}
                    onChange={(e) =>
                      setFallaForm({ ...fallaForm, tipo: e.target.value })
                    }
                  />
                  <textarea
                    placeholder="Nueva descripción"
                    value={fallaForm.descripcion}
                    onChange={(e) =>
                      setFallaForm({
                        ...fallaForm,
                        descripcion: e.target.value,
                      })
                    }
                  />
                  <button className="edit-btn" onClick={actualizarFalla}>
                    Actualizar
                  </button>
                </div>

                <div className="crud-box">
                  <h3>Eliminar falla</h3>
                  <input
                    type="text"
                    placeholder="ID a eliminar"
                    value={fallaDeleteId}
                    onChange={(e) => setFallaDeleteId(e.target.value)}
                  />
                  <button className="delete-btn" onClick={eliminarFalla}>
                    Eliminar
                  </button>
                </div>
              </div>

              <div className="list-box">
                <h3>Listado de fallas</h3>
                <div className="items-grid">
                  {fallas.map((item) => (
                    <div key={item.id} className="item-card">
                      <strong>{item.id}</strong>
                      <h4>{item.nombre}</h4>
                      <p><b>Tipo:</b> {item.tipo}</p>
                      <p>{item.descripcion}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* PANEL RECOMENDACIONES */}
          {activeTab === "recomendaciones" && (
            <div className="crud-panel">
              <h2>Gestión de Recomendaciones</h2>

              <div className="filter-row">
                <input
                  type="text"
                  placeholder="Filtrar por falla_id (ej: F01)"
                  value={recoFilterFallaId}
                  onChange={(e) => setRecoFilterFallaId(e.target.value)}
                />
                <button className="secondary-btn" onClick={cargarRecomendacionesFiltradas}>
                  Aplicar filtro
                </button>
                <button
                  className="secondary-btn"
                  onClick={async () => {
                    setRecoFilterFallaId("");
                    const data = await getAdminRecomendaciones();
                    setRecomendaciones(data.recomendaciones || []);
                    setMensajeGlobal("Filtro limpiado.");
                  }}
                >
                  Limpiar filtro
                </button>
              </div>

              <div className="crud-sections">
                <div className="crud-box">
                  <h3>Crear recomendación</h3>
                  <input
                    type="text"
                    placeholder="ID (ej: R16)"
                    value={recomendacionForm.id}
                    onChange={(e) =>
                      setRecomendacionForm({
                        ...recomendacionForm,
                        id: e.target.value,
                      })
                    }
                  />
                  <input
                    type="text"
                    placeholder="Falla ID"
                    value={recomendacionForm.falla_id}
                    onChange={(e) =>
                      setRecomendacionForm({
                        ...recomendacionForm,
                        falla_id: e.target.value,
                      })
                    }
                  />
                  <textarea
                    placeholder="Descripción"
                    value={recomendacionForm.descripcion}
                    onChange={(e) =>
                      setRecomendacionForm({
                        ...recomendacionForm,
                        descripcion: e.target.value,
                      })
                    }
                  />
                  <button className="save-btn" onClick={crearRecomendacion}>
                    Crear
                  </button>
                </div>

                <div className="crud-box">
                  <h3>Actualizar recomendación</h3>
                  <input
                    type="text"
                    placeholder="ID a actualizar"
                    value={recomendacionEditId}
                    onChange={(e) => setRecomendacionEditId(e.target.value)}
                  />
                  <input
                    type="text"
                    placeholder="Nuevo falla_id"
                    value={recomendacionForm.falla_id}
                    onChange={(e) =>
                      setRecomendacionForm({
                        ...recomendacionForm,
                        falla_id: e.target.value,
                      })
                    }
                  />
                  <textarea
                    placeholder="Nueva descripción"
                    value={recomendacionForm.descripcion}
                    onChange={(e) =>
                      setRecomendacionForm({
                        ...recomendacionForm,
                        descripcion: e.target.value,
                      })
                    }
                  />
                  <button className="edit-btn" onClick={actualizarRecomendacion}>
                    Actualizar
                  </button>
                </div>

                <div className="crud-box">
                  <h3>Eliminar recomendación</h3>
                  <input
                    type="text"
                    placeholder="ID a eliminar"
                    value={recomendacionDeleteId}
                    onChange={(e) => setRecomendacionDeleteId(e.target.value)}
                  />
                  <button className="delete-btn" onClick={eliminarRecomendacion}>
                    Eliminar
                  </button>
                </div>
              </div>

              <div className="list-box">
                <h3>Listado de recomendaciones</h3>
                <div className="items-grid">
                  {recomendaciones.map((item) => (
                    <div key={item.id} className="item-card">
                      <strong>{item.id}</strong>
                      <p><b>Falla:</b> {item.falla_id}</p>
                      <p>{item.descripcion}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* PANEL REGLAS */}
          {activeTab === "reglas" && (
            <div className="crud-panel">
              <h2>Gestión de Reglas</h2>

              <div className="crud-sections">
                <div className="crud-box">
                  <h3>Crear regla</h3>
                  <input
                    type="text"
                    placeholder="Falla ID (ej: F13)"
                    value={reglaForm.falla_id}
                    onChange={(e) =>
                      setReglaForm({ ...reglaForm, falla_id: e.target.value })
                    }
                  />
                  <input
                    type="text"
                    placeholder="Síntomas separados por coma (ej: S01,S03)"
                    value={reglaForm.sintomas}
                    onChange={(e) =>
                      setReglaForm({ ...reglaForm, sintomas: e.target.value })
                    }
                  />
                  <button className="save-btn" onClick={crearRegla}>
                    Crear regla
                  </button>
                </div>

                <div className="crud-box">
                  <h3>Eliminar regla</h3>
                  <input
                    type="text"
                    placeholder="Falla ID"
                    value={reglaDeleteForm.falla_id}
                    onChange={(e) =>
                      setReglaDeleteForm({
                        ...reglaDeleteForm,
                        falla_id: e.target.value,
                      })
                    }
                  />
                  <input
                    type="text"
                    placeholder="Síntomas separados por coma"
                    value={reglaDeleteForm.sintomas}
                    onChange={(e) =>
                      setReglaDeleteForm({
                        ...reglaDeleteForm,
                        sintomas: e.target.value,
                      })
                    }
                  />
                  <button className="delete-btn" onClick={eliminarRegla}>
                    Eliminar regla
                  </button>
                </div>
              </div>

              <div className="list-box">
                <h3>Listado de reglas</h3>
                <div className="items-grid">
                  {reglas.map((item, index) => (
                    <div key={`${item.falla_id}-${index}`} className="item-card">
                      <strong>Falla: {item.falla_id}</strong>
                      <p>
                        <b>Síntomas:</b>{" "}
                        {Array.isArray(item.sintomas)
                          ? item.sintomas.join(", ")
                          : ""}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </section>

        {/* DERECHA */}
        <aside className="admin-right">
          <div className="side-box">
            <h3>Mensajes / notas</h3>

            <label className="checkbox-row">
              <input
                type="checkbox"
                checked={habilitarMensajes}
                onChange={() => setHabilitarMensajes((prev) => !prev)}
              />
              {habilitarMensajes ? "Habilitar mensajes" : "No habilitar"}
            </label>

            <textarea
              placeholder="Escribe aquí tu mensaje personalizado.."
              value={mensajeAdmin}
              onChange={(e) => setMensajeAdmin(e.target.value)}
            />

            <button className="send-btn" onClick={handleEnviarMensajeAdmin}>
              Enviar
            </button>

          </div>

    
        </aside>
      </div>
    </div>
  );
};

export default AdminPage;