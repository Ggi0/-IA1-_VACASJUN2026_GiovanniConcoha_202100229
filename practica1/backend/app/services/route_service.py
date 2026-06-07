from adapters.prolog_adapter import PrologAdapter
from typing import Optional, List, Dict

class RouteService:
    def __init__(self, adapter: Optional[PrologAdapter] = None):
        self.adapter = adapter or PrologAdapter()

    def find_shortest_route(self, origen: str, destino: str) -> Dict:
        result = self.adapter.find_shortest_route(origen, destino)
        if not result:
            raise ValueError(f"No existe ruta entre '{origen}' y '{destino}'")
        return result

    def find_all_routes(self, origen: str, destino: str) -> List[Dict]:
        return self.adapter.find_all_routes(origen, destino)