import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  getPreguntas,
  createPregunta,
  updatePregunta,
  deletePregunta,
  getChats,
  createChat,
  updateChat,
  deleteChat,
  logoutAdmin,
  getSessionUser,
} from "../API/api_admin";

const styles = {
  page: {
    minHeight: "100vh",
    background: "linear-gradient(135deg, #0b1220 0%, #0f172a 40%, #1e293b 100%)",
    color: "#e2e8f0",
    fontFamily: "Inter, system-ui, sans-serif",
    padding: "24px",
  },
  container: {
    maxWidth: "1300px",
    margin: "0 auto",
  },
  card: {
    background: "rgba(15, 23, 42, 0.92)",
    border: "1px solid rgba(148, 163, 184, 0.16)",
    borderRadius: "18px",
    boxShadow: "0 15px 35px rgba(0,0,0,0.28)",
    padding: "20px",
  },
  sectionTitle: {
    margin: "0 0 14px 0",
    fontSize: "18px",
    fontWeight: 700,
    color: "#f8fafc",
  },
  input: {
    width: "100%",
    padding: "11px 12px",
    borderRadius: "10px",
    border: "1px solid #334155",
    background: "#0f172a",
    color: "#e5e7eb",
    outline: "none",
    fontSize: "14px",
  },
  textarea: {
    width: "100%",
    minHeight: "110px",
    padding: "11px 12px",
    borderRadius: "10px",
    border: "1px solid #334155",
    background: "#0f172a",
    color: "#e5e7eb",
    outline: "none",
    fontSize: "14px",
  },
  buttonPrimary: {
    padding: "11px 16px",
    borderRadius: "10px",
    border: "none",
    background: "linear-gradient(135deg, #2563eb, #1d4ed8)",
    color: "#fff",
    fontWeight: 700,
    cursor: "pointer",
  },
  buttonSecondary: {
    padding: "11px 16px",
    borderRadius: "10px",
    border: "1px solid #475569",
    background: "#1e293b",
    color: "#e2e8f0",
    fontWeight: 600,
    cursor: "pointer",
  },
  buttonDanger: {
    padding: "9px 14px",
    borderRadius: "10px",
    border: "none",
    background: "linear-gradient(135deg, #dc2626, #b91c1c)",
    color: "#fff",
    cursor: "pointer",
    fontWeight: 700,
  },
};

export default function AdminPage() {
  const navigate = useNavigate();
  const user = useMemo(() => getSessionUser(), []);
  const [activeTab, setActiveTab] = useState<"preguntas" | "chats">("preguntas");
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  const [preguntas, setPreguntas] = useState([]);
  const [chats, setChats] = useState([]);

  const [preguntaEditId, setPreguntaEditId] = useState<number | null>(null);
  const [chatEditId, setChatEditId] = useState<number | null>(null);

  const [preguntaForm, setPreguntaForm] = useState({
    pregunta: "",
    respuesta: "",
    categoria_id: "",
    palabras_clave: "",
  });

  const [chatForm, setChatForm] = useState({
    chat_id: "",
    nombre_chat: "",
    tipo_chat: "",
    activo: true,
  });

  useEffect(() => {
    const token = localStorage.getItem("smartbot_token");
    if (!token) {
      navigate("/login");
      return;
    }
    cargarDatos();
  }, [navigate]);

  const cargarDatos = async () => {
    setLoading(true);
    setMessage("");
    try {
      const [dataPreguntas, dataChats] = await Promise.all([
        getPreguntas(),
        getChats(),
      ]);

      setPreguntas(dataPreguntas || []);
      setChats(dataChats || []);
    } catch (err) {
      setMessage(
        err?.response?.data?.detail ||
          "No se pudieron cargar los datos del panel"
      );
    } finally {
      setLoading(false);
    }
  };

  const resetPreguntaForm = () => {
    setPreguntaEditId(null);
    setPreguntaForm({
      pregunta: "",
      respuesta: "",
      categoria_id: "",
      palabras_clave: "",
    });
  };

  const resetChatForm = () => {
    setChatEditId(null);
    setChatForm({
      chat_id: "",
      nombre_chat: "",
      tipo_chat: "",
      activo: true,
    });
  };

  const handleLogout = () => {
    logoutAdmin();
    navigate("/login");
  };

  const handlePreguntaChange = (e) => {
    const { name, value } = e.target;
    setPreguntaForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleChatChange = (e) => {
    const { name, value, type, checked } = e.target;
    setChatForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handlePreguntaSubmit = async (e) => {
    e.preventDefault();
    setMessage("");

    const payload = {
      pregunta: preguntaForm.pregunta.trim(),
      respuesta: preguntaForm.respuesta.trim(),
      categoria_id: Number(preguntaForm.categoria_id),
      palabras_clave: preguntaForm.palabras_clave
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
    };

    try {
      if (preguntaEditId) {
        await updatePregunta(preguntaEditId, payload);
        setMessage("Pregunta frecuente actualizada correctamente");
      } else {
        await createPregunta(payload);
        setMessage("Pregunta frecuente creada correctamente");
      }

      resetPreguntaForm();
      await cargarDatos();
    } catch (err) {
      setMessage(
        err?.response?.data?.detail ||
          "No se pudo guardar la pregunta frecuente"
      );
    }
  };

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    setMessage("");

    const payload = {
      chat_id: Number(chatForm.chat_id),
      nombre_chat: chatForm.nombre_chat || null,
      tipo_chat: chatForm.tipo_chat || null,
      activo: !!chatForm.activo,
    };

    try {
      if (chatEditId) {
        await updateChat(chatEditId, payload);
        setMessage("Chat autorizado actualizado correctamente");
      } else {
        await createChat(payload);
        setMessage("Chat autorizado registrado correctamente");
      }

      resetChatForm();
      await cargarDatos();
    } catch (err) {
      setMessage(
        err?.response?.data?.detail ||
          "No se pudo guardar el chat autorizado"
      );
    }
  };

  const handleEditPregunta = (item) => {
    setActiveTab("preguntas");
    setPreguntaEditId(item.id);
    setPreguntaForm({
      pregunta: item.pregunta || "",
      respuesta: item.respuesta || "",
      categoria_id: String(item?.categoria?.id || ""),
      palabras_clave: (item?.palabras_clave || [])
        .map((p) => p.palabra)
        .join(", "),
    });

    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleDeletePregunta = async (id) => {
    const ok = window.confirm("¿Seguro que deseas eliminar esta pregunta frecuente?");
    if (!ok) return;

    try {
      await deletePregunta(id);
      setMessage("Pregunta frecuente eliminada correctamente");
      if (preguntaEditId === id) resetPreguntaForm();
     os();
    } catch (err) {
      setMessage(
        err?.response?.data?.detail ||
          "No se pudo eliminar la pregunta frecuente"
      );
    }
  };

  const handleEditChat = (item) => {
    setActiveTab("chats");
    setChatEditId(item.id);
    setChatForm({
      chat_id: String(item.chat_id || ""),
      nombre_chat: item.nombre_chat || "",
      tipo_chat: item.tipo_chat || "",
      activo: !!item.activo,
    });

    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleDeleteChat = async (id) => {
    const ok = window.confirm("¿Seguro que deseas eliminar este chat autorizado?");
    if (!ok) return;

    try {
      await deleteChat(id);
      setMessage("Chat autorizado eliminado correctamente");
      if (chatEditId === id) resetChatForm();
      await cargarDatos();
    } catch (err) {
      setMessage(
        err?.response?.data?.detail ||
          "No se pudo eliminar el chat autorizado"
      );
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.container}>
        {/* Header */}
        <div
          style={{
            ...styles.card,
            marginBottom: "20px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: "16px",
            flexWrap: "wrap",
          }}
        >
          <div>
            <h1
              style={{
                margin: 0,
                fontSize: "28px",
                fontWeight: 800,
                color: "#f8fafc",
              }}
            >
              SmartBot Admin
            </h1>
            <p style={{ margin: "8px 0 0 0", color: "#94a3b8" }}>
              Gestión de preguntas frecuentes y chats autorizados
            </p>
          </div>

          <div style={{ textAlign: "right" }}>
            <div style={{ color: "#cbd5e1", fontSize: "14px", marginBottom: "10px" }}>
              {user ? (
                <>
                  <strong>{user.nombre}</strong> · {user.usuario} · {user.rol}
                </>
              ) : (
                "Administrador"
              )}
            </div>

            <button onClick={handleLogout} style={styles.buttonSecondary}>
              Cerrar sesión
            </button>
          </div>
        </div>

        {message && (
          <div
            style={{
              ...styles.card,
              marginBottom: "20px",
              background: "rgba(30, 41, 59, 0.96)",
              border: "1px solid rgba(96, 165, 250, 0.35)",
              color: "#bfdbfe",
            }}
          >
            {message}
          </div>
        )}

        {/* Tabs */}
        <div
          style={{
            display: "flex",
            gap: "12px",
            marginBottom: "20px",
            flexWrap: "wrap",
          }}
        >
          <button
            onClick={() => setActiveTab("preguntas")}
            style={{
              ...styles.buttonSecondary,
              background: activeTab === "preguntas" ? "#1d4ed8" : "#1e293b",
              border: activeTab === "preguntas" ? "1px solid #3b82f6" : "1px solid #475569",
              color: "#fff",
            }}
          >
            Preguntas frecuentes
          </button>

          <button
            onClick={() => setActiveTab("chats")}
            style={{
              ...styles.buttonSecondary,
              background: activeTab === "chats" ? "#1d4ed8" : "#1e293b",
              border: activeTab === "chats" ? "1px solid #3b82f6" : "1px solid #475569",
              color: "#fff",
            }}
          >
            Chats autorizados
          </button>
        </div>

        {loading ? (
          <div style={styles.card}>Cargando panel...</div>
        ) : (
          <>
            {activeTab === "preguntas" && (
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "minmax(320px, 420px) 1fr",
                  gap: "20px",
                }}
              >
                {/* Formulario preguntas */}
                <div style={styles.card}>
                  <h2 style={styles.sectionTitle}>
                    {preguntaEditId ? "Editar pregunta frecuente" : "Nueva pregunta frecuente"}
                  </h2>

                  <form onSubmit={handlePreguntaSubmit}>
                    <div style={{ marginBottom: "14px" }}>
                      <label style={{ display: "block", marginBottom: "8px", color: "#cbd5e1" }}>
                        Pregunta
                      </label>
                      <input
                        type="text"
                        name="pregunta"
                        value={preguntaForm.pregunta}
                        onChange={handlePreguntaChange}
                        style={styles.input}
                        placeholder="Ej. ¿Cuál es el horario de atención?"
                        required
                      />
                    </div>

                    <div style={{ marginBottom: "14px" }}>
                      <label style={{ display: "block", marginBottom: "8px", color: "#cbd5e1" }}>
                        Respuesta
                      </label>
                      <textarea
                        name="respuesta"
                        value={preguntaForm.respuesta}
                        onChange={handlePreguntaChange}
                        style={styles.textarea}
                        placeholder="Escribe la respuesta del bot..."
                        required
                      />
                    </div>

                    <div style={{ marginBottom: "14px" }}>
                      <label style={{ display: "block", marginBottom: "8px", color: "#cbd5e1" }}>
                        ID de categoría
                      </label>
                      <input
                        type="number"
                        name="categoria_id"
                        value={preguntaForm.categoria_id}
                        onChange={handlePreguntaChange}
                        style={styles.input}
                        placeholder="Ej. 1"
                        required
                      />
                    </div>

                    <div style={{ marginBottom: "18px" }}>
                      <label style={{ display: "block", marginBottom: "8px", color: "#cbd5e1" }}>
                        Palabras clave
                      </label>
                      <input
                        type="text"
                        name="palabras_clave"
                        value={preguntaForm.palabras_clave}
                        onChange={handlePreguntaChange}
                        style={styles.input}
                        placeholder="Ej. horario, atención, oficina"
                        required
                      />
                      <small style={{ color: "#94a3b8", display: "block", marginTop: "8px" }}>
                        Separa las palabras clave con comas.
                      </small>
                    </div>

                    <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
                      <button type="submit" style={styles.buttonPrimary}>
                        {preguntaEditId ? "Actualizar pregunta" : "Crear pregunta"}
                      </button>

                      <button
                        type="button"
                        style={styles.buttonSecondary}
                        onClick={resetPreguntaForm}
                      >
                        Limpiar
                      </button>
                    </div>
                  </form>
                </div>

                {/* Lista preguntas */}
                <div style={styles.card}>
                  <h2 style={styles.sectionTitle}>Listado de preguntas frecuentes</h2>

                  {preguntas.length === 0 ? (
                    <div style={{ color: "#94a3b8" }}>No hay preguntas registradas.</div>
                  ) : (
                    <div style={{ display: "grid", gap: "14px" }}>
                      {preguntas.map((item) => (
                        <div
                          key={item.id}
                          style={{
                            border: "1px solid #334155",
                            borderRadius: "14px",
                            padding: "16px",
                            background: "#0b1324",
                          }}
                        >
                          <div
                            style={{
                              display: "flex",
                              justifyContent: "space-between",
                              gap: "12px",
                              alignItems: "flex-start",
                              flexWrap: "wrap",
                            }}
                          >
                            <div style={{ flex: 1 }}>
                              <div
                                style={{
                                  fontWeight: 800,
                                  color: "#f8fafc",
                                  fontSize: "16px",
                                  marginBottom: "8px",
                                }}
                              >
                                {item.pregunta}
                              </div>

                              <div
                                style={{
                                  color: "#cbd5e1",
                                  marginBottom: "10px",
                                  whiteSpace: "pre-wrap",
                                  lineHeight: 1.5,
                                }}
                              >
                                {item.respuesta}
                              </div>

                              <div style={{ color: "#93c5fd", fontSize: "13px", marginBottom: "8px" }}>
                                Categoría: {item?.categoria?.nombre || `ID ${item?.categoria?.id || "-"}`}
                              </div>

                              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                                {(item.palabras_clave || []).map((p) => (
                                  <span
                                    key={p.id}
                                    style={{
                                      fontSize: "12px",
                                      background: "#1e3a8a",
                                      color: "#dbeafe",
                                      padding: "6px 10px",
                                      borderRadius: "999px",
                                      border: "1px solid #3b82f6",
                                    }}
                                  >
                                    {p.palabra}
                                  </span>
                                ))}
                              </div>
                            </div>

                            <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                              <button
                                style={styles.buttonSecondary}
                                onClick={() => handleEditPregunta(item)}
                              >
                                Editar
                              </button>
                              <button
                                style={styles.buttonDanger}
                                onClick={() => handleDeletePregunta(item.id)}
                              >
                                Eliminar
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === "chats" && (
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "minmax(320px, 420px) 1fr",
                  gap: "20px",
                }}
              >
                {/* Formulario chats */}
                <div style={styles.card}>
                  <h2 style={styles.sectionTitle}>
                    {chatEditId ? "Editar chat autorizado" : "Nuevo chat autorizado"}
                  </h2>

                  <form onSubmit={handleChatSubmit}>
                    <div style={{ marginBottom: "14px" }}>
                      <label style={{ display: "block", marginBottom: "8px", color: "#cbd5e1" }}>
                        Chat ID
                      </label>
                      <input
                        type="number"
                        name="chat_id"
                        value={chatForm.chat_id}
                        onChange={handleChatChange}
                        style={styles.input}
                        placeholder="Ej. -5168547509"
                        required
                      />
                    </div>

                    <div style={{ marginBottom: "14px" }}>
                      <label style={{ display: "block", marginBottom: "8px", color: "#cbd5e1" }}>
                        Nombre del chat
                      </label>
                      <input
                        type="text"
                        name="nombre_chat"
                        value={chatForm.nombre_chat}
                        onChange={handleChatChange}
                        style={styles.input}
                        placeholder="Ej. Grupo IA"
                      />
                    </div>

                    <div style={{ marginBottom: "14px" }}>
                      <label style={{ display: "block", marginBottom: "8px", color: "#cbd5e1" }}>
                        Tipo de chat
                      </label>
                      <input
                        type="text"
                        name="tipo_chat"
                        value={chatForm.tipo_chat}
                        onChange={handleChatChange}
                        style={styles.input}
                        placeholder="Ej. group, supergroup, private"
                      />
                    </div>

                    <div style={{ marginBottom: "18px" }}>
                      <label
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "10px",
                          color: "#cbd5e1",
                          cursor: "pointer",
                        }}
                      >
                        <input
                          type="checkbox"
                          name="activo"
                          checked={chatForm.activo}
                          onChange={handleChatChange}
                        />
                        Chat activo
                      </label>
                    </div>

                    <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
                      <button type="submit" style={styles.buttonPrimary}>
                        {chatEditId ? "Actualizar chat" : "Registrar chat"}
                      </button>

                      <button
                        type="button"
                        style={styles.buttonSecondary}
                        onClick={resetChatForm}
                      >
                        Limpiar
                      </button>
                    </div>
                  </form>
                </div>

                {/* Lista chats */}
                <div style={styles.card}>
                  <h2 style={styles.sectionTitle}>Listado de chats autorizados</h2>

                  {chats.length === 0 ? (
                    <div style={{ color: "#94a3b8" }}>No hay chats autorizados registrados.</div>
                  ) : (
                    <div style={{ display: "grid", gap: "14px" }}>
                      {chats.map((item) => (
                        <div
                          key={item.id}
                          style={{
                            border: "1px solid #334155",
                            borderRadius: "14px",
                            padding: "16px",
                            background: "#0b1324",
                          }}
                        >
                          <div
                            style={{
                              display: "flex",
                              justifyContent: "space-between",
                              gap: "12px",
                              alignItems: "flex-start",
                              flexWrap: "wrap",
                            }}
                          >
                            <div style={{ flex: 1 }}>
                              <div
                                style={{
                                  fontWeight: 800,
                                  color: "#f8fafc",
                                  fontSize: "16px",
                                  marginBottom: "8px",
                                }}
                              >
                                {item.nombre_chat || "Sin nombre"}
                              </div>

                              <div style={{ color: "#cbd5e1", marginBottom: "6px" }}>
                                <strong>Chat ID:</strong> {item.chat_id}
                              </div>

                              <div style={{ color: "#cbd5e1", marginBottom: "6px" }}>
                                <strong>Tipo:</strong> {item.tipo_chat || "No definido"}
                              </div>

                              <div
                                style={{
                                  display: "inline-block",
                                  marginTop: "8px",
                                  padding: "6px 10px",
                                  borderRadius: "999px",
                                  fontSize: "12px",
                                  fontWeight: 700,
                                  background: item.activo ? "#14532d" : "#7f1d1d",
                                  color: item.activo ? "#dcfce7" : "#fecaca",
                                  border: item.activo
                                    ? "1px solid #16a34a"
                                    : "1px solid #ef4444",
                                }}
                              >
                                {item.activo ? "Activo" : "Inactivo"}
                              </div>
                            </div>

                            <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                              <button
                                style={styles.buttonSecondary}
                                onClick={() => handleEditChat(item)}
                              >
                                Editar
                              </button>
                              <button
                                style={styles.buttonDanger}
                                onClick={() => handleDeleteChat(item.id)}
                              >
                                Eliminar
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}