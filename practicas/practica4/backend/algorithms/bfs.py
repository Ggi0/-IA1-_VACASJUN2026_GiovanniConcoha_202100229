# algorithms/bfs.py
# Implementación del algoritmo Breadth-First Search (BFS) para laberintos.
#
# BFS explora el grafo nivel por nivel usando una cola FIFO.
# Garantiza encontrar el camino MÁS CORTO en número de pasos
# cuando todos los costos de arista son iguales (como en este laberinto).
#
# Complejidad:
#   Tiempo : O(V + E)  donde V = filas*cols, E = aristas de la cuadrícula
#   Espacio: O(V)      para la cola y el conjunto de visitados

from collections import deque
from typing import List, Tuple, Optional

from models.maze import Maze
from models.node import Node


def _reconstruct_path(node: Optional[Node]) -> List[Tuple[int, int]]:
    """
    Reconstruye la ruta desde el nodo destino hasta el inicio
    siguiendo los punteros `parent` y la invierte.

    Returns:
        Lista de coordenadas (row, col) de inicio a destino.
    """
    path: List[Tuple[int, int]] = []
    current = node
    while current is not None:
        path.append((current.row, current.col))
        current = current.parent
    path.reverse()
    return path


def bfs(maze: Maze) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """
    Ejecuta BFS sobre el laberinto.

    Args:
        maze: Instancia validada de Maze con start y end definidos.

    Returns:
        Tupla (path, explored):
            path     → lista ordenada de (row, col) desde inicio a destino,
                        vacía si no hay ruta.
            explored → lista ordenada de (row, col) de nodos visitados
                        durante la búsqueda.
    """
    start_node = Node(maze.start[0], maze.start[1])
    end_row, end_col = maze.end

    # Cola FIFO: estructura central de BFS
    queue: deque[Node] = deque([start_node])

    # Conjunto de nodos visitados para evitar ciclos
    visited: set[Node] = {start_node}

    # Lista que registra el orden de exploración para la visualización
    explored: List[Tuple[int, int]] = []

    while queue:
        # Extraer el nodo del frente de la cola (orden FIFO)
        current = queue.popleft()
        explored.append((current.row, current.col))

        # ¿Llegamos al destino?
        if current.row == end_row and current.col == end_col:
            return _reconstruct_path(current), explored

        # Expandir vecinos en orden: arriba, abajo, izquierda, derecha
        for neighbor in maze.get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    # No se encontró camino
    return [], explored