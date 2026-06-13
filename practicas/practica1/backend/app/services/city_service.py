from adapters.prolog_adapter import PrologAdapter
from typing import List


class CityService:

    def __init__(
        self,
        adapter: PrologAdapter = None
    ):
        self.adapter = adapter or PrologAdapter()

    def get_all_cities(self):
        return self.adapter.get_all_cities()

    def get_all_connections(self):
        return self.adapter.get_all_connections()

    def add_city(self, nombre: str):
        return self.adapter.add_city(nombre)

    def add_connection(
        self,
        origen: str,
        destino: str,
        distancia: int
    ):
        return self.adapter.add_connection(
            origen,
            destino,
            distancia
        )