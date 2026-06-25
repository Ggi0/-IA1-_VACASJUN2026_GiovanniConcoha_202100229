# controllers/maze_controller.py
# Controlador del laberinto (patrón MVC / Controller Layer).
# Recibe las solicitudes HTTP ya parseadas del blueprint de rutas,
# delega la lógica al SearchService y construye las respuestas JSON.
# NO contiene lógica de búsqueda ni de negocio; solo orquesta.

from flask import jsonify, request, Response
from services.search_service import SearchService

# Instancia única del servicio (singleton ligero)
_service = SearchService()


def run_bfs():
    """
    POST /api/search/bfs
    Ejecuta el algoritmo BFS sobre el laberinto recibido en el body.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Body JSON requerido."}), 400

    try:
        result = _service.run_bfs(data)
        return jsonify(result.to_dict()), 200
    except (KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


def run_dfs():
    """
    POST /api/search/dfs
    Ejecuta el algoritmo DFS sobre el laberinto recibido en el body.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Body JSON requerido."}), 400

    try:
        result = _service.run_dfs(data)
        return jsonify(result.to_dict()), 200
    except (KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


def run_both():
    """
    POST /api/search/both
    Ejecuta BFS y DFS sobre el mismo laberinto y retorna comparación.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Body JSON requerido."}), 400

    try:
        results = _service.run_both(data)
        return jsonify(results), 200
    except (KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


def list_predefined():
    """
    GET /api/mazes/predefined
    Retorna la lista de laberintos predefinidos con su metadata.
    """
    try:
        mazes = _service.list_predefined()
        return jsonify({"mazes": mazes, "total": len(mazes)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_predefined(maze_id: str):
    """
    GET /api/mazes/predefined/<maze_id>
    Retorna el laberinto predefinido completo por su ID.
    """
    try:
        maze = _service.get_predefined(maze_id)
        return jsonify(maze), 200
    except KeyError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def generate_maze():
    """
    POST /api/mazes/generate
    Genera un laberinto aleatorio con ruta válida garantizada.
    """
    data = request.get_json(silent=True) or {}
    rows = int(data.get("rows", 10))
    cols = int(data.get("cols", 10))
    density = float(data.get("density", 0.30))

    try:
        maze = _service.generate_maze(rows, cols, density)
        return jsonify(maze), 200
    except (ValueError, RuntimeError) as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


def export_csv():
    """
    POST /api/export/csv
    Recibe los resultados de búsqueda y los exporta como archivo CSV.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Body JSON con resultados requerido."}), 400

    try:
        csv_content = _service.export_csv(data)
        return Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=robomaze_results.csv"},
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def export_pdf():
    """
    POST /api/export/pdf
    Recibe los resultados de búsqueda y los exporta como archivo PDF.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Body JSON con resultados requerido."}), 400

    try:
        pdf_bytes = _service.export_pdf(data)
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={"Content-Disposition": "attachment; filename=robomaze_results.pdf"},
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def health_check():
    """
    GET /api/health
    Endpoint de verificación de estado del servicio.
    """
    return jsonify({"status": "ok", "service": "RoboMaze API"}), 200