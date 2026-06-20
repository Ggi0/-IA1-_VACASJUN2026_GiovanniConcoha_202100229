import { Routes, Route, Navigate } from "react-router-dom";

import LoginPage from "./pages/LoginPage";
import PanelPage from "./pages/PanelPage";
import InvoicesPage from "./pages/InvoicesPage";
import DashboardPage from "./pages/DashboardPage";
import ProvidersPage from "./pages/ProvidersPage";
import RpaForm from "./pages/RpaForm";

// NOTA: Por indicación del proyecto, las rutas NO están protegidas
// (no hay redirect automático si no hay token). Cada página asume
// que el usuario ya inició sesión; si no, las llamadas a la API
// devolverán 401 y axios lo propagará como error normal.

export default function App() {
  return (
    <Routes>
      {/* Redirección raíz → login */}
      <Route path="/" element={<Navigate to="/login" replace />} />

      {/* Auth */}
      <Route path="/login" element={<LoginPage />} />

      {/* Vista del empleado: subir factura, OCR, revisión, RPA */}
      <Route path="/panel" element={<PanelPage />} />

      {/* Listado de facturas + bitácora */}
      <Route path="/facturas" element={<InvoicesPage />} />

      {/* Métricas */}
      <Route path="/dashboard" element={<DashboardPage />} />

      {/* CRUD de proveedores */}
      <Route path="/proveedores" element={<ProvidersPage />} />

      {/* Formulario target del bot Selenium — sin Navbar, vista aislada */}
      <Route path="/rpa-form" element={<RpaForm />} />

      {/* Cualquier ruta desconocida → login */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}