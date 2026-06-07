from pyswip import Prolog

class PrologAdapter:

    def __init__(self):
        self.prolog = Prolog()

        self.prolog.consult(
            "../../prolog/knowledge_base.pl"
        )

        self.prolog.consult(
            "../../prolog/routes.pl"
        )

    def shortest_route(self, origen, destino):

        consulta = (
            f"ruta_mas_corta("
            f"{origen},"
            f"{destino},"
            f"Ruta,"
            f"Distancia)"
        )

        return list(
            self.prolog.query(consulta)
        )