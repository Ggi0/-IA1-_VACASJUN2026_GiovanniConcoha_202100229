from pyswip import Prolog
from pathlib import Path
import re


class PrologAdapter:

    def __init__(self):

        self.prolog = Prolog()

        # practica1/
        self.BASE_DIR = Path(__file__).resolve().parents[3]

        # practica1/prolog/
        self.PROLOG_DIR = self.BASE_DIR / "prolog"

        # practica1/prolog/data.pl
        self.DATA_FILE = self.PROLOG_DIR / "data.pl"

        self.prolog.consult(
            str(self.PROLOG_DIR / "knowledge_base.pl")
        )

        self.prolog.consult(
            str(self.PROLOG_DIR / "routes.pl")
        )

        self.prolog.consult(
            str(self.PROLOG_DIR / "city_management.pl")
        )

    def _normalize_atom(self, name: str) -> str:

        atom = (
            str(name)
            .strip()
            .lower()
            .replace(" ", "_")
        )

        atom = re.sub(
            r"[^a-z0-9_]",
            "",
            atom
        )

        if not atom:
            raise ValueError(
                "Nombre inválido"
            )

        return atom

    def _parse_prolog_list(self, term):

        if term is None:
            return []

        if isinstance(term, (list, tuple)):
            return [str(x) for x in term]

        s = str(term).strip()

        if s.startswith("[") and s.endswith("]"):

            contenido = s[1:-1].strip()

            if not contenido:
                return []

            return [
                x.strip()
                for x in contenido.split(",")
            ]

        return [s]

        # CIUDADES
    
    def get_all_cities(self):

        resultados = list(
            self.prolog.query(
                "findall(C, ciudad(C), Cities)"
            )
        )

        if not resultados:
            return []

        return self._parse_prolog_list(
            resultados[0]["Cities"]
        )

    def add_city(self, nombre: str):

        atom = self._normalize_atom(nombre)

        existe = list(
            self.prolog.query(
                f"ciudad({atom})"
            )
        )

        if existe:
            raise ValueError(
                f"La ciudad '{nombre}' ya existe"
            )

        resultado = list(
            self.prolog.query(
                f"agregar_ciudad({atom})"
            )
        )

        if not resultado:
            raise RuntimeError(
                "No se pudo agregar la ciudad"
            )

        with open(
            self.DATA_FILE,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                f"\nciudad({atom})."
            )

        return True

        # CONEXIONES
    
    def add_connection(
        self,
        origen: str,
        destino: str,
        distancia: int
    ):

        o = self._normalize_atom(origen)
        d = self._normalize_atom(destino)

        try:
            distancia = int(distancia)
        except Exception:
            raise ValueError(
                "La distancia debe ser un entero"
            )

        if distancia <= 0:
            raise ValueError(
                "La distancia debe ser mayor que cero"
            )

        existe = list(
            self.prolog.query(
                f"conexion({o},{d},{distancia})"
            )
        )

        if existe:
            raise ValueError(
                "La conexión ya existe"
            )

        resultado = list(
            self.prolog.query(
                f"agregar_conexion({o},{d},{distancia})"
            )
        )

        if not resultado:
            raise RuntimeError(
                "No se pudo agregar la conexión"
            )

        with open(
            self.DATA_FILE,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                f"\nconexion({o},{d},{distancia})."
            )

        return True

        # RUTA MAS CORTA
    
    def find_shortest_route(
        self,
        origen: str,
        destino: str
    ):

        o = self._normalize_atom(origen)
        d = self._normalize_atom(destino)

        consulta = (
            f"ruta_mas_corta("
            f"{o},{d},Ruta,Distancia)"
        )

        resultados = list(
            self.prolog.query(
                consulta
            )
        )

        if not resultados:
            return None

        resultado = resultados[0]

        ruta = self._parse_prolog_list(
            resultado["Ruta"]
        )

        distancia = int(
            resultado["Distancia"]
        )

        return {
            "ruta": ruta,
            "distancia": distancia
        }

        # TODAS LAS RUTAS
    
    def find_all_routes(
        self,
        origen: str,
        destino: str
    ):

        o = self._normalize_atom(origen)
        d = self._normalize_atom(destino)

        resultados = []

        consulta = (
            f"ruta({o},{d},Ruta,Distancia)"
        )

        for r in self.prolog.query(
            consulta
        ):

            resultados.append({
                "ruta": self._parse_prolog_list(
                    r["Ruta"]
                ),
                "distancia": int(
                    r["Distancia"]
                )
            })

        resultados.sort(
            key=lambda x: x["distancia"]
        )

        return resultados

    def get_all_connections(self):

        resultados = list(
            self.prolog.query(
                "findall([O,D,Dist], conexion(O,D,Dist), Connections)"
            )
        )

        if not resultados:
            return []

        conexiones = []

        raw = resultados[0]["Connections"]

        for conexion in raw:

            conexiones.append({
                "origen": str(conexion[0]),
                "destino": str(conexion[1]),
                "distancia": int(conexion[2])
            })

        return conexiones