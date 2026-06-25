// src/App.jsx
// Componente raíz de la aplicación RoboMaze.
// En este proyecto la app es de una sola página; App monta directamente HomePage.
// Si en el futuro se agregan rutas (react-router-dom), el Router va aquí.

import HomePage from "./pages/HomePage";
import "./index.css";

export default function App() {
  return <HomePage />;
}