# app.py
# Punto de entrada de la aplicación Flask (RoboMaze Backend).
# Responsabilidades:
#   1. Crear y configurar la instancia de Flask.
#   2. Habilitar CORS para que el frontend pueda consumir la API.
#   3. Registrar el Blueprint de rutas.
#   4. Arrancar el servidor de desarrollo.
#
# Patrón arquitectónico aplicado: Service Layer
#   app.py  →  routes/  →  controllers/  →  services/  →  algorithms/ + models/

from flask import Flask
from flask_cors import CORS
from routes.maze_routes import maze_bp


def create_app() -> Flask:
    """
    Factory function de la aplicación Flask.
    Permite crear instancias independientes en tests sin arrancar el servidor.
    """
    app = Flask(__name__)

    # Habilitar CORS para todos los orígenes (ajustar en producción)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Registrar el blueprint de rutas
    app.register_blueprint(maze_bp)

    return app


if __name__ == "__main__":
    application = create_app()
    # debug=True habilita el reloader automático y mensajes detallados de error.
    # En producción usar un servidor WSGI como Gunicorn.
    application.run(host="0.0.0.0", port=5000, debug=True)