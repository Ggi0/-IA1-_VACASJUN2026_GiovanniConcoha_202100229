import { Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./pages/login";
import AdminPage from "./pages/admin";
import { isAuthenticated } from "./API/api_admin";

function PrivateRoute({ children }) {
  return isAuthenticated() ? children : <Navigate to="/login" replace />;
}

function PublicRoute({ children }) {
  return isAuthenticated() ? <Navigate to="/admin" replace /> : children;
}

function App() {
  return (
    <Routes>
      <Route
        path="/login"
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        }
      />

      <Route
        path="/admin"
        element={
          <PrivateRoute>
            <AdminPage />
          </PrivateRoute>
        }
      />

      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

export default App;