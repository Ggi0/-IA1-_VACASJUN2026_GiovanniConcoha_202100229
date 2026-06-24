# models/search_result.py
# Encapsula los resultados de una ejecución de algoritmo de búsqueda.
# Contiene la ruta encontrada, nodos explorados, tiempo y metadatos.

from __future__ import annotations
from typing import List, Optional, Tuple


class SearchResult:
    """
    Resultado de la ejecución de un algoritmo de búsqueda (BFS o DFS).

    Atributos:
        algorithm (str): Nombre del algoritmo ejecutado ("BFS" | "DFS").
        found (bool): True si se encontró una ruta válida.
        path (List[Tuple[int,int]]): Coordenadas (row, col) de la ruta encontrada,
                                     en orden desde inicio hasta destino.
                                     Lista vacía si no hay ruta.
        explored (List[Tuple[int,int]]): Coordenadas de todos los nodos visitados
                                          durante la búsqueda, en orden de visita.
        nodes_explored (int): Cantidad total de nodos explorados.
        path_length (int): Longitud de la ruta encontrada (número de celdas).
        execution_time_ms (float): Tiempo de ejecución en milisegundos.
        message (str): Mensaje descriptivo del resultado.
    """

    def __init__(
        self,
        algorithm: str,
        found: bool,
        path: List[Tuple[int, int]],
        explored: List[Tuple[int, int]],
        execution_time_ms: float,
        message: str = "",
    ) -> None:
        self.algorithm = algorithm
        self.found = found
        self.path = path
        self.explored = explored
        self.nodes_explored = len(explored)
        self.path_length = len(path)
        self.execution_time_ms = round(execution_time_ms, 4)
        self.message = message

    def to_dict(self) -> dict:
        """Serializa el resultado completo a diccionario para respuestas JSON."""
        return {
            "algorithm": self.algorithm,
            "found": self.found,
            "path": [{"row": r, "col": c} for r, c in self.path],
            "explored": [{"row": r, "col": c} for r, c in self.explored],
            "nodes_explored": self.nodes_explored,
            "path_length": self.path_length,
            "execution_time_ms": self.execution_time_ms,
            "message": self.message,
        }