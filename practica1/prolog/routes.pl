
% Regla para encontrar una ruta entre dos ciudades
ruta(Origen, Destino, [Origen, Destino], Distancia) :-
    conexion(Origen, Destino, Distancia).

% Regla para encontrar rutas más largas (recursivas)
ruta(Origen, Destino, [Origen|Ruta], DistanciaTotal) :-
    conexion(Origen, Intermedio, Distancia),
    ruta(Intermedio, Destino, Ruta, DistanciaRestante),
    \+ member(Origen, Ruta), % Evitar ciclos
    DistanciaTotal is Distancia + DistanciaRestante.

% Regla para calcular la distancia total de una ruta
distancia_total([_], 0).
distancia_total([Ciudad1, Ciudad2|Resto], DistanciaTotal) :-
    conexion(Ciudad1, Ciudad2, Distancia),
    distancia_total([Ciudad2|Resto], DistanciaRestante),
    DistanciaTotal is Distancia + DistanciaRestante.

% Regla para encontrar la ruta más corta
ruta_mas_corta(Origen, Destino, RutaCorta, DistanciaCorta) :-
    setof([Ruta, Distancia], ruta(Origen, Destino, Ruta, Distancia), Rutas),
    Rutas = [[RutaCorta, DistanciaCorta]|_]. % La primera ruta es la más corta (ordenada por distancia)