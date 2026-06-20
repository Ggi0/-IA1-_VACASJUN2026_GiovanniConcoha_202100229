import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import {
  getProviders,
  createProvider,
  updateProvider,
  deleteProvider,
} from "../services/api";
import { styles } from "../styles";

const EMPTY_FORM = { name: "", nit: "", address: "", phone: "" };

export default function ProvidersPage() {
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState(null); // null = creando, número = editando

  useEffect(() => {
    loadProviders();
  }, []);

  const loadProviders = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getProviders();
      setProviders(data);
    } catch (err) {
      setError(err?.response?.data?.detail || "Error al cargar proveedores.");
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const startEdit = (provider) => {
    setEditingId(provider.id);
    setForm({
      name: provider.name || "",
      nit: provider.nit || "",
      address: provider.address || "",
      phone: provider.phone || "",
    });
    setError("");
    setSuccessMsg("");
  };

  const cancelEdit = () => {
    setEditingId(null);
    setForm(EMPTY_FORM);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccessMsg("");

    try {
      if (editingId) {
        await updateProvider(editingId, form);
        setSuccessMsg("Proveedor actualizado correctamente.");
      } else {
        await createProvider(form);
        setSuccessMsg("Proveedor creado correctamente.");
      }
      setForm(EMPTY_FORM);
      setEditingId(null);
      loadProviders();
    } catch (err) {
      setError(err?.response?.data?.detail || "Error al guardar el proveedor.");
    }
  };

  const handleDelete = async (id) => {
    setError("");
    setSuccessMsg("");
    try {
      await deleteProvider(id);
      setSuccessMsg("Proveedor eliminado correctamente.");
      loadProviders();
    } catch (err) {
      setError(err?.response?.data?.detail || "No se pudo eliminar el proveedor.");
    }
  };

  return (
    <div style={styles.page}>
      <Navbar />
      <div style={styles.container}>
        <h1 style={styles.h1}>Proveedores</h1>
        <p style={styles.subtitle}>
          Administración de proveedores asociados a las facturas.
        </p>

        {error && <div style={styles.alertError}>{error}</div>}
        {successMsg && <div style={styles.alertSuccess}>{successMsg}</div>}

        <div style={styles.twoColumns}>
          {/* Formulario crear/editar */}
          <div style={styles.card}>
            <h2 style={styles.h2}>
              {editingId ? `Editar proveedor #${editingId}` : "Nuevo proveedor"}
            </h2>

            <form onSubmit={handleSubmit}>
              <div style={styles.formGroup}>
                <label style={styles.label}>Nombre</label>
                <input
                  type="text"
                  name="name"
                  value={form.name}
                  onChange={handleChange}
                  style={styles.input}
                  required
                />
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>NIT (formato: 1234567-8 o CF)</label>
                <input
                  type="text"
                  name="nit"
                  value={form.nit}
                  onChange={handleChange}
                  style={styles.input}
                  required
                />
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>Dirección (opcional)</label>
                <input
                  type="text"
                  name="address"
                  value={form.address}
                  onChange={handleChange}
                  style={styles.input}
                />
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>Teléfono (opcional)</label>
                <input
                  type="text"
                  name="phone"
                  value={form.phone}
                  onChange={handleChange}
                  style={styles.input}
                />
              </div>

              <div style={{ display: "flex", gap: "10px" }}>
                <button type="submit" style={styles.button}>
                  {editingId ? "Guardar cambios" : "Crear proveedor"}
                </button>
                {editingId && (
                  <button
                    type="button"
                    style={styles.buttonSecondary}
                    onClick={cancelEdit}
                  >
                    Cancelar
                  </button>
                )}
              </div>
            </form>
          </div>

          {/* Lista de proveedores */}
          <div style={styles.card}>
            <h2 style={styles.h2}>Lista de proveedores</h2>
            {loading ? (
              <p style={styles.subtitle}>Cargando...</p>
            ) : providers.length === 0 ? (
              <p style={styles.subtitle}>No hay proveedores registrados.</p>
            ) : (
              <table style={styles.table}>
                <thead>
                  <tr>
                    <th style={styles.th}>Nombre</th>
                    <th style={styles.th}>NIT</th>
                    <th style={styles.th}>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {providers.map((p) => (
                    <tr key={p.id}>
                      <td style={styles.td}>{p.name}</td>
                      <td style={styles.td}>{p.nit}</td>
                      <td style={styles.td}>
                        <div style={{ display: "flex", gap: "8px" }}>
                          <button
                            style={styles.buttonSecondary}
                            onClick={() => startEdit(p)}
                          >
                            Editar
                          </button>
                          <button
                            style={styles.buttonDanger}
                            onClick={() => handleDelete(p.id)}
                          >
                            Eliminar
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}