# models/node.py
# Representa un nodo individual dentro del laberinto.
# Cada celda del grid es un nodo con coordenadas (fila, columna)
# y una referencia a su nodo padre para reconstruir el camino.

class Node:
    """
    Nodo del espacio de estados del laberinto.

    Atributos:
        row (int): Fila en la cuadrícula (eje Y).
        col (int): Columna en la cuadrícula (eje X).
        parent (Node | None): Nodo del que se llegó a este durante la búsqueda.
                              None cuando es el nodo raíz (inicio).
    """

    def __init__(self, row: int, col: int, parent=None):
        self.row = row
        self.col = col
        self.parent: "Node | None" = parent

    # ------------------------------------------------------------------
    # Igualdad y hash: dos nodos son iguales si tienen las mismas coordenadas,
    # sin importar el padre. Esto permite usar nodos en conjuntos (visited).
    # ------------------------------------------------------------------

    def __eq__(self, other) -> bool:
        if not isinstance(other, Node):
            return False
        return self.row == other.row and self.col == other.col

    def __hash__(self) -> int:
        return hash((self.row, self.col))

    def __repr__(self) -> str:
        return f"Node(row={self.row}, col={self.col})"

    def to_dict(self) -> dict:
        """Serializa el nodo a diccionario para respuestas JSON."""
        return {"row": self.row, "col": self.col}