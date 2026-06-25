
// src/components/Toast.jsx
// Notificación de error flotante que se auto-descarta.

import { useEffect } from "react";

export default function Toast({ message, onClose }) {
  useEffect(() => {
    if (!message) return;
    const t = setTimeout(onClose, 5000);
    return () => clearTimeout(t);
  }, [message, onClose]);

  if (!message) return null;

  return (
    <div className="toast">
      <span className="toast-icon">⚠</span>
      <span className="toast-msg">{message}</span>
      <button className="toast-close" onClick={onClose}>✕</button>
    </div>
  );
}