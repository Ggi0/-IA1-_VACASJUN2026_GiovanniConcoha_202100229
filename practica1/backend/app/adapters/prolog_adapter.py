from pyswip import Prolog
import re

class PrologAdapter:
    def __init__(self):
        self.prolog = Prolog()
        # Rutas relativas desde: practica1/backend/app/adapters -> subir 3 niveles a practica1 -> prolog
        self.prolog.consult("../../prolog/knowledge_base.pl")
        self.prolog.consult("../../prolog/routes.pl")
        self.prolog.consult("../../prolog/city_management.pl")

    def _normalize_atom(self, name: str) -> str:
        # Normaliza nombres de ciudades a átomos válidos en minúsculas con guiones bajos
        n = str(name).strip().lower().replace(" ", "_")
        n = re.sub(r"[^a-z0-9_]", "", n)
        if not n:
            raise ValueError("Nombre inválido para atomizar")
        return n

    def _parse_prolog_list(self, term):
        # Intenta manejar distintos formatos que pyswip puede devolver
        if term is None:
            return []
        # Si pyswip ya retornó lista/tuple
        try:
            if isinstance(term, (list, tuple)):
                return [str(x) for x in term]
        except Exception:
            pass
        s = str(term).strip()
        # Formato como "[a,b,c]"
        if s.startswith("[") and s.endswith("]"):
            inner = s[1:-1].strip()
            if inner == "":
                return []
            parts = [p.strip() for p in inner.split(",")]
            return parts
        # Si llega como átomo simple
        return [s]

    def find_shortest_route(self, origen: str, destino: str):
        o = self._normalize_atom(origen)
        d = self._normalize_atom(destino)
        consulta = f"ruta_mas_corta({o},{d},Ruta,Distancia)"
        resultados = list(self.prolog.query(consulta))
        if not resultados:
            return None
        res = resultados[0]
        ruta = self._parse_prolog_list(res.get("Ruta"))
        distancia = res.get("Distancia")
        try:
            distancia = int(distancia)
        except Exception:
            distancia = int(str(distancia))
        return {"ruta": ruta, "distancia": distancia}

    def find_all_routes(self, origen: str, destino: str):
        o = self._normalize_atom(origen)
        d = self._normalize_atom(destino)
        # Usamos findall para obtener todas las rutas con sus distancias
        consulta = f"findall([R,D], ruta({o},{d},R,D), Rutas)"
        resultados = list(self.prolog.query(consulta))
        if not resultados:
            return []
        raw = resultados[0].get("Rutas")
        rutas = []
        # raw puede ser lista de listas; cada elemento es [Ruta,Distancia]
        if isinstance(raw, (list, tuple)):
            for pair in raw:
                if not pair:
                    continue
                rterm = pair[0]
                dterm = pair[1] if len(pair) > 1 else None
                ruta = self._parse_prolog_list(rterm)
                try:
                    distancia = int(dterm)
                except Exception:
                    distancia = int(str(dterm))
                rutas.append({"ruta": ruta, "distancia": distancia})
        else:
            # Fallback: intentar parsear string
            rutas.append({"ruta": self._parse_prolog_list(raw), "distancia": None})
        # Ordenar por distancia ascendente
        rutas.sort(key=lambda x: x["distancia"] if x["distancia"] is not None else float("inf"))
        return rutas

    def get_all_cities(self):
        resultados = list(self.prolog.query("findall(C, ciudad(C), Cities)"))
        if not resultados:
            return []
        cities_raw = resultados[0].get("Cities")
        return self._parse_prolog_list(cities_raw)

    def add_city(self, nombre: str):
        atom = self._normalize_atom(nombre)
        # Ejecutar agregar_ciudad/1; si ya existe la consulta falla (no éxito)
        resultados = list(self.prolog.query(f"agregar_ciudad({atom})"))
        if not resultados:
            # Si no se pudo agregar, verificar si ya existe
            exists = list(self.prolog.query(f"ciudad({atom})"))
            if exists:
                raise ValueError(f"La ciudad '{nombre}' ya existe")
            raise RuntimeError("No se pudo agregar la ciudad")
        return True

    def add_connection(self, origen: str, destino: str, distancia: int):
        o = self._normalize_atom(origen)
        d = self._normalize_atom(destino)
        if not isinstance(distancia, int):
            try:
                distancia = int(distancia)
            except Exception:
                raise ValueError("Distancia debe ser un entero")
        resultados = list(self.prolog.query(f"agregar_conexion({o},{d},{distancia})"))
        if not resultados:
            # comprobar si la conexión ya existe
            exists = list(self.prolog.query(f"conexion({o},{d},{distancia})"))
            if exists:
                raise ValueError("La conexión ya existe")
            raise RuntimeError("No se pudo agregar la conexión")
        return True