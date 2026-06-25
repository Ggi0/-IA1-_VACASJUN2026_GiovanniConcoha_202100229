# routes/maze_routes.py
# Blueprint de Flask que registra todas las rutas de la API REST.
# Actúa como tabla de enrutamiento: mapea URL + método HTTP → controlador.
# No contiene lógica; únicamente importa y conecta controladores.

from flask import Blueprint
from controllers.maze_controller import (
    run_bfs,
    run_dfs,
    run_both,
    list_predefined,
    get_predefined,
    generate_maze,
    export_csv,
    export_pdf,
    health_check,
)

# Prefijo base de todas las rutas: /api
maze_bp = Blueprint("maze", __name__, url_prefix="/api")

# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
maze_bp.add_url_rule("/health",          view_func=health_check, methods=["GET"])

# ---------------------------------------------------------------------------
# Algoritmos de búsqueda
# ---------------------------------------------------------------------------
maze_bp.add_url_rule("/search/bfs",      view_func=run_bfs,   methods=["POST"])
maze_bp.add_url_rule("/search/dfs",      view_func=run_dfs,   methods=["POST"])
maze_bp.add_url_rule("/search/both",     view_func=run_both,  methods=["POST"])

# ---------------------------------------------------------------------------
# Laberintos predefinidos y generación
# ---------------------------------------------------------------------------
maze_bp.add_url_rule("/mazes/predefined",         view_func=list_predefined, methods=["GET"])
maze_bp.add_url_rule("/mazes/predefined/<maze_id>", view_func=get_predefined, methods=["GET"])
maze_bp.add_url_rule("/mazes/generate",           view_func=generate_maze,   methods=["POST"])

# ---------------------------------------------------------------------------
# Exportación
# ---------------------------------------------------------------------------
maze_bp.add_url_rule("/export/csv",      view_func=export_csv, methods=["POST"])
maze_bp.add_url_rule("/export/pdf",      view_func=export_pdf, methods=["POST"])