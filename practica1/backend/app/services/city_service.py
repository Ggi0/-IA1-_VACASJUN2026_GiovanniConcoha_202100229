from adapters.prolog_adapter import PrologAdapter
from typing import List

class CityService:
    def __init__(self, adapter: PrologAdapter = None):
        self.adapter = adapter or PrologAdapter()

    def get_all_cities(self) -> List[str]:
        return self.adapter.get_all_cities()

    def add_city(self, nombre: str) -> bool:
        return self.adapter.add_city(nombre)

    def add_connection(self, origen: str, destino: str, distancia: int) -> bool:
        return self.adapter.add_connection(origen, destino, distancia)