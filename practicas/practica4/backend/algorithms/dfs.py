# algorithms/dfs.py
# Implementación del algoritmo Depth-First Search (DFS) para laberintos.
#
# DFS explora tan profundo como sea posible antes de retroceder.
# Usa una pila LIFO. No garantiza el camino más corto.
# Se implementa de forma iterativa (no recursiva) para evitar
# desbordamiento de pila en laberintos grandes.
#
# Complejidad:
#   Tiempo : O(V + E)
#   Espacio: O(V)

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


def dfs(maze: Maze) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """
    Ejecuta DFS iterativo sobre el laberinto.

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

    # Pila LIFO: estructura central de DFS iterativo
    # Usamos una lista de Python como pila eficiente (append/pop)
    stack: List[Node] = [start_node]

    # Conjunto de nodos visitados para evitar ciclos
    visited: set[Node] = {start_node}

    # Lista que registra el orden de exploración para la visualización
    explored: List[Tuple[int, int]] = []

    while stack:
        # Extraer el nodo del tope de la pila (orden LIFO)
        current = stack.pop()
        explored.append((current.row, current.col))

        # ¿Llegamos al destino?
        if current.row == end_row and current.col == end_col:
            return _reconstruct_path(current), explored

        # Expandir vecinos en orden inverso para que el primero
        # (arriba) sea explorado primero al hacer pop().
        # Orden efectivo de exploración: arriba → abajo → izquierda → derecha
        neighbors = maze.get_neighbors(current)
        for neighbor in reversed(neighbors):
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append(neighbor)

    # No se encontró camino
    return [], explored