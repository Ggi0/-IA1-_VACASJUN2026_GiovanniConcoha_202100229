# models/maze.py
# Representa el laberinto como cuadrícula bidimensional.
# Encapsula la validación de celdas, obstáculos y vecinos.

from __future__ import annotations
from typing import List, Tuple
from models.node import Node


# Celda libre
CELL_FREE = 0
# Celda bloqueada (obstáculo / pared)
CELL_WALL = 1


class Maze:
    """
    Cuadrícula bidimensional del laberinto.

    La cuadrícula se representa como una lista de listas de enteros:
        0 → celda libre
        1 → celda bloqueada

    Atributos:
        rows (int): Número de filas.
        cols (int): Número de columnas.
        grid (List[List[int]]): Matriz del laberinto.
        start (Tuple[int,int]): (fila, columna) del punto de inicio.
        end (Tuple[int,int]): (fila, columna) del punto objetivo.
    """

    # Movimientos posibles: arriba, abajo, izquierda, derecha.
    # No se incluyen diagonales según el enunciado (cuadrícula 4-conectada).
    _DIRECTIONS: List[Tuple[int, int]] = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def __init__(
        self,
        grid: List[List[int]],
        start: Tuple[int, int],
        end: Tuple[int, int],
    ) -> None:
        self.rows: int = len(grid)
        self.cols: int = len(grid[0]) if grid else 0
        self.grid = grid
        self.start = start  # (row, col)
        self.end = end       # (row, col)

    # ------------------------------------------------------------------
    # Consultas sobre el grid
    # ------------------------------------------------------------------

    def is_valid(self, row: int, col: int) -> bool:
        """Devuelve True si (row, col) está dentro de los límites del laberinto."""
        return 0 <= row < self.rows and 0 <= col < self.cols

    def is_free(self, row: int, col: int) -> bool:
        """Devuelve True si la celda es transitable (no es pared)."""
        return self.is_valid(row, col) and self.grid[row][col] == CELL_FREE

    def get_neighbors(self, node: Node) -> List[Node]:
        """
        Retorna los nodos vecinos transitables del nodo dado.
        El orden de exploración es: arriba → abajo → izquierda → derecha.
        """
        neighbors: List[Node] = []
        for dr, dc in self._DIRECTIONS:
            nr, nc = node.row + dr, node.col + dc
            if self.is_free(nr, nc):
                neighbors.append(Node(nr, nc, parent=node))
        return neighbors

    # ------------------------------------------------------------------
    # Validaciones de estado
    # ------------------------------------------------------------------

    def validate(self) -> None:
        """
        Lanza ValueError si el laberinto está en un estado inválido:
        - Grid vacío o con filas de longitud inconsistente.
        - Inicio o destino fuera de límites o sobre una pared.
        """
        if self.rows == 0 or self.cols == 0:
            raise ValueError("El laberinto no puede estar vacío.")

        row_lengths = {len(row) for row in self.grid}
        if len(row_lengths) > 1:
            raise ValueError("Todas las filas del laberinto deben tener la misma longitud.")

        sr, sc = self.start
        er, ec = self.end

        if not self.is_valid(sr, sc):
            raise ValueError(f"El inicio {self.start} está fuera de los límites del laberinto.")
        if not self.is_free(sr, sc):
            raise ValueError(f"El inicio {self.start} está sobre una pared.")

        if not self.is_valid(er, ec):
            raise ValueError(f"El destino {self.end} está fuera de los límites del laberinto.")
        if not self.is_free(er, ec):
            raise ValueError(f"El destino {self.end} está sobre una pared.")

    # ------------------------------------------------------------------
    # Serialización
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "rows": self.rows,
            "cols": self.cols,
            "grid": self.grid,
            "start": {"row": self.start[0], "col": self.start[1]},
            "end": {"row": self.end[0], "col": self.end[1]},
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Maze":
        """
        Construye un Maze desde el payload JSON de la API.

        Esquema esperado:
        {
            "grid": [[0,1,...], ...],
            "start": {"row": 0, "col": 0},
            "end":   {"row": N, "col": M}
        }
        """
        grid = data["grid"]
        start = (data["start"]["row"], data["start"]["col"])
        end = (data["end"]["row"], data["end"]["col"])
        return cls(grid, start, end)