# services/search_service.py
# Capa de servicio (Service Layer pattern).
# Orquesta la ejecución de algoritmos, validación del laberinto,
# medición de tiempo, generación aleatoria y laberintos predefinidos.
# El controlador NUNCA toca los algoritmos directamente; todo pasa por aquí.

from __future__ import annotations

import csv
import io
import random
from typing import Dict, Any, List, Tuple

from models.maze import Maze
from models.search_result import SearchResult
from algorithms.bfs import bfs
from algorithms.dfs import dfs
from utils.timer import Timer


# ---------------------------------------------------------------------------
# Laberintos predefinidos (al menos 5, según requisitos)
# ---------------------------------------------------------------------------
# Formato: grid 0=libre, 1=pared; start y end en (row, col)

PREDEFINED_MAZES: Dict[str, Dict] = {
    "maze_1": {
        "name": "Laberinto Básico 5×5",
        "description": "Laberinto sencillo de 5 filas × 5 columnas.",
        "grid": [
            [0, 1, 0, 0, 0],
            [0, 1, 0, 1, 0],
            [0, 0, 0, 1, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0],
        ],
        "start": {"row": 0, "col": 0},
        "end":   {"row": 4, "col": 4},
    },
    "maze_2": {
        "name": "Laberinto Zigzag 7×7",
        "description": "Camino en zigzag que prueba el orden de exploración.",
        "grid": [
            [0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0],
        ],
        "start": {"row": 0, "col": 0},
        "end":   {"row": 6, "col": 6},
    },
    "maze_3": {
        "name": "Laberinto Sin Solución 5×5",
        "description": "No existe ruta entre inicio y destino. Prueba el manejo de error.",
        "grid": [
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 1, 0, 1, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0],
        ],
        "start": {"row": 0, "col": 0},
        "end":   {"row": 2, "col": 2},
    },
    "maze_4": {
        "name": "Laberinto Complejo 10×10",
        "description": "Laberinto más grande con múltiples caminos alternativos.",
        "grid": [
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 1, 0, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 1, 1, 1, 1, 1, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
            [1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
            [0, 1, 0, 1, 0, 0, 0, 1, 0, 0],
            [0, 1, 0, 1, 1, 1, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0, 1, 1, 1, 1, 0],
        ],
        "start": {"row": 0, "col": 0},
        "end":   {"row": 9, "col": 9},
    },
    "maze_5": {
        "name": "Laberinto Espiral 8×8",
        "description": "Estructura en espiral que favorece a DFS sobre BFS.",
        "grid": [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 0, 0, 0, 0, 1, 0],
            [0, 1, 0, 1, 1, 0, 1, 0],
            [0, 1, 0, 0, 1, 0, 1, 0],
            [0, 1, 1, 0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ],
        "start": {"row": 0, "col": 0},
        "end":   {"row": 4, "col": 3},
    },
    "maze_6": {
        "name": "Laberinto Abierto 6×6",
        "description": "Pocos obstáculos, múltiples rutas posibles.",
        "grid": [
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 0],
            [0, 0, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ],
        "start": {"row": 0, "col": 0},
        "end":   {"row": 5, "col": 5},
    },
}


class SearchService:
    """
    Servicio principal de búsqueda y gestión de laberintos.

    Patrón aplicado: Service Layer
    - Separa la lógica de negocio (orquestación de algoritmos,
      generación de laberintos, exportación) de la capa HTTP (controladores).
    """

    # ------------------------------------------------------------------
    # Ejecución de algoritmos
    # ------------------------------------------------------------------

    def run_bfs(self, maze_data: dict) -> SearchResult:
        """Valida el laberinto y ejecuta BFS."""
        maze = Maze.from_dict(maze_data)
        maze.validate()
        elapsed_ms, (path, explored) = Timer.measure(bfs, maze)
        found = len(path) > 0
        msg = "Ruta encontrada." if found else "No existe ruta entre el inicio y el destino."
        return SearchResult("BFS", found, path, explored, elapsed_ms, msg)

    def run_dfs(self, maze_data: dict) -> SearchResult:
        """Valida el laberinto y ejecuta DFS."""
        maze = Maze.from_dict(maze_data)
        maze.validate()
        elapsed_ms, (path, explored) = Timer.measure(dfs, maze)
        found = len(path) > 0
        msg = "Ruta encontrada." if found else "No existe ruta entre el inicio y el destino."
        return SearchResult("DFS", found, path, explored, elapsed_ms, msg)

    def run_both(self, maze_data: dict) -> Dict[str, Any]:
        """
        Ejecuta BFS y DFS sobre el mismo laberinto y retorna
        los resultados con estadísticas comparativas.
        """
        bfs_result = self.run_bfs(maze_data)
        dfs_result = self.run_dfs(maze_data)

        comparison = self._build_comparison(bfs_result, dfs_result)

        return {
            "bfs": bfs_result.to_dict(),
            "dfs": dfs_result.to_dict(),
            "comparison": comparison,
        }

    # ------------------------------------------------------------------
    # Comparación estadística
    # ------------------------------------------------------------------

    def _build_comparison(
        self, bfs_res: SearchResult, dfs_res: SearchResult
    ) -> Dict[str, Any]:
        """Construye el bloque de comparación entre BFS y DFS."""

        def winner(bfs_val, dfs_val, lower_is_better=True):
            if bfs_val == dfs_val:
                return "empate"
            if lower_is_better:
                return "BFS" if bfs_val < dfs_val else "DFS"
            return "BFS" if bfs_val > dfs_val else "DFS"

        return {
            "faster_algorithm": winner(
                bfs_res.execution_time_ms, dfs_res.execution_time_ms
            ),
            "fewer_nodes_explored": winner(
                bfs_res.nodes_explored, dfs_res.nodes_explored
            ),
            "shorter_path": winner(
                bfs_res.path_length if bfs_res.found else float("inf"),
                dfs_res.path_length if dfs_res.found else float("inf"),
            ),
            "bfs_time_ms": bfs_res.execution_time_ms,
            "dfs_time_ms": dfs_res.execution_time_ms,
            "bfs_nodes": bfs_res.nodes_explored,
            "dfs_nodes": dfs_res.nodes_explored,
            "bfs_path_length": bfs_res.path_length,
            "dfs_path_length": dfs_res.path_length,
            "note": (
                "BFS garantiza el camino más corto; "
                "DFS puede explorar menos nodos pero no garantiza optimalidad."
            ),
        }

    # ------------------------------------------------------------------
    # Laberintos predefinidos
    # ------------------------------------------------------------------

    def list_predefined(self) -> List[Dict[str, Any]]:
        """Retorna la lista de laberintos predefinidos con metadata."""
        result = []
        for key, maze in PREDEFINED_MAZES.items():
            result.append({
                "id": key,
                "name": maze["name"],
                "description": maze["description"],
                "rows": len(maze["grid"]),
                "cols": len(maze["grid"][0]),
            })
        return result

    def get_predefined(self, maze_id: str) -> Dict[str, Any]:
        """
        Retorna el laberinto predefinido completo por su ID.

        Raises:
            KeyError: Si el ID no existe.
        """
        if maze_id not in PREDEFINED_MAZES:
            raise KeyError(f"Laberinto '{maze_id}' no encontrado.")
        return PREDEFINED_MAZES[maze_id]

    # ------------------------------------------------------------------
    # Generación aleatoria (Recursive Division simplificado)
    # ------------------------------------------------------------------

    def generate_maze(self, rows: int, cols: int, density: float = 0.3) -> Dict[str, Any]:
        """
        Genera un laberinto aleatorio garantizando que exista al menos
        una ruta entre el inicio (0,0) y el destino (rows-1, cols-1).

        Estrategia:
          1. Crear grid libre.
          2. Agregar paredes aleatorias respetando la densidad.
          3. Verificar conectividad con BFS; si no hay ruta, regenerar
             hasta 10 intentos antes de lanzar error.

        Args:
            rows: Filas del laberinto (mínimo 3, máximo 30).
            cols: Columnas del laberinto (mínimo 3, máximo 30).
            density: Proporción de celdas que serán paredes [0.0, 0.6].

        Returns:
            Diccionario con grid, start y end listos para usar en la API.
        """
        rows = max(3, min(rows, 30))
        cols = max(3, min(cols, 30))
        density = max(0.0, min(density, 0.6))

        for _ in range(15):  # máximo 15 intentos
            grid = self._random_grid(rows, cols, density)
            start = (0, 0)
            end = (rows - 1, cols - 1)

            # Asegurar que inicio y fin sean libres
            grid[start[0]][start[1]] = 0
            grid[end[0]][end[1]] = 0

            # Verificar conectividad
            maze = Maze(grid, start, end)
            path, _ = bfs(maze)
            if path:
                return {
                    "grid": grid,
                    "start": {"row": start[0], "col": start[1]},
                    "end":   {"row": end[0], "col": end[1]},
                    "rows": rows,
                    "cols": cols,
                }

        raise RuntimeError(
            "No se pudo generar un laberinto con ruta válida. "
            "Prueba con menor densidad de paredes."
        )

    def _random_grid(self, rows: int, cols: int, density: float) -> List[List[int]]:
        """Genera la matriz aleatoria cruda."""
        return [
            [1 if random.random() < density else 0 for _ in range(cols)]
            for _ in range(rows)
        ]

    # ------------------------------------------------------------------
    # Exportación CSV
    # ------------------------------------------------------------------

    def export_csv(self, results: Dict[str, Any]) -> str:
        """
        Convierte los resultados de búsqueda a formato CSV en memoria.

        Args:
            results: Diccionario retornado por run_both() o un SearchResult.to_dict().

        Returns:
            String CSV listo para enviar como archivo.
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # --- Encabezado general ---
        writer.writerow(["RoboMaze - Resultados de Búsqueda"])
        writer.writerow([])

        def write_result_section(res: dict, title: str):
            writer.writerow([f"=== {title} ==="])
            writer.writerow(["Algoritmo", res.get("algorithm", "")])
            writer.writerow(["Ruta encontrada", res.get("found", "")])
            writer.writerow(["Nodos explorados", res.get("nodes_explored", "")])
            writer.writerow(["Longitud de ruta", res.get("path_length", "")])
            writer.writerow(["Tiempo de ejecución (ms)", res.get("execution_time_ms", "")])
            writer.writerow(["Mensaje", res.get("message", "")])
            writer.writerow([])

            # Ruta encontrada
            writer.writerow(["Ruta (row, col)"])
            for p in res.get("path", []):
                writer.writerow([p["row"], p["col"]])
            writer.writerow([])

            # Nodos explorados
            writer.writerow(["Explorados (row, col)"])
            for e in res.get("explored", []):
                writer.writerow([e["row"], e["col"]])
            writer.writerow([])

        # Detectar si viene de run_both o de resultado individual
        if "bfs" in results and "dfs" in results:
            write_result_section(results["bfs"], "BFS")
            write_result_section(results["dfs"], "DFS")

            if "comparison" in results:
                cmp = results["comparison"]
                writer.writerow(["=== Comparación ==="])
                for k, v in cmp.items():
                    writer.writerow([k, v])
        else:
            write_result_section(results, results.get("algorithm", "Resultado"))

        return output.getvalue()

    # ------------------------------------------------------------------
    # Exportación PDF
    # ------------------------------------------------------------------

    def export_pdf(self, results: Dict[str, Any]) -> bytes:
        """
        Genera un PDF con los resultados de búsqueda usando ReportLab.

        Returns:
            Bytes del PDF generado.
        """
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        )

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                                leftMargin=inch, rightMargin=inch,
                                topMargin=inch, bottomMargin=inch)

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "Title", parent=styles["Heading1"],
            textColor=colors.HexColor("#1a237e"), fontSize=18, spaceAfter=10
        )
        h2_style = ParagraphStyle(
            "H2", parent=styles["Heading2"],
            textColor=colors.HexColor("#283593"), fontSize=13, spaceAfter=6
        )
        normal = styles["Normal"]

        story = []
        story.append(Paragraph("RoboMaze — Resultados de Búsqueda", title_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
        story.append(Spacer(1, 12))

        def add_result(res: dict, label: str):
            story.append(Paragraph(label, h2_style))

            data = [
                ["Algoritmo", res.get("algorithm", "")],
                ["Ruta encontrada", "Sí" if res.get("found") else "No"],
                ["Nodos explorados", str(res.get("nodes_explored", ""))],
                ["Longitud de ruta", str(res.get("path_length", ""))],
                ["Tiempo de ejecución (ms)", str(res.get("execution_time_ms", ""))],
                ["Mensaje", res.get("message", "")],
            ]

            tbl = Table(data, colWidths=[2.5 * inch, 4 * inch])
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8eaf6")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 10))

            # Ruta
            if res.get("path"):
                path_str = " → ".join(f"({p['row']},{p['col']})" for p in res["path"])
                story.append(Paragraph(f"<b>Ruta:</b> {path_str}", normal))
            story.append(Spacer(1, 14))

        if "bfs" in results and "dfs" in results:
            add_result(results["bfs"], "Resultados BFS")
            add_result(results["dfs"], "Resultados DFS")

            if "comparison" in results:
                cmp = results["comparison"]
                story.append(Paragraph("Comparación BFS vs DFS", h2_style))
                cmp_data = [[k, str(v)] for k, v in cmp.items()]
                tbl2 = Table(cmp_data, colWidths=[3 * inch, 3.5 * inch])
                tbl2.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#fce4ec")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("PADDING", (0, 0), (-1, -1), 4),
                ]))
                story.append(tbl2)
        else:
            add_result(results, results.get("algorithm", "Resultado"))

        doc.build(story)
        buffer.seek(0)
        return buffer.read()