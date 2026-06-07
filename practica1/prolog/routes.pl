
% CONEXION BIDIRECCIONAL


camino(A, B, D) :-
    conexion(A, B, D).

camino(A, B, D) :-
    conexion(B, A, D).


% BUSQUEDA DE RUTAS


ruta(Origen, Destino, Ruta, Distancia) :-
    ruta_aux(
        Origen,
        Destino,
        [Origen],
        RutaInvertida,
        0,
        Distancia
    ),
    reverse(RutaInvertida, Ruta).


% AUXILIAR RECURSIVO


ruta_aux(
    Destino,
    Destino,
    Visitadas,
    Visitadas,
    Distancia,
    Distancia
).

ruta_aux(
    Actual,
    Destino,
    Visitadas,
    Ruta,
    DistanciaActual,
    DistanciaTotal
) :-

    camino(
        Actual,
        Siguiente,
        DistanciaTramo
    ),

    \+ member(
        Siguiente,
        Visitadas
    ),

    NuevaDistancia is
        DistanciaActual +
        DistanciaTramo,

    ruta_aux(
        Siguiente,
        Destino,
        [Siguiente|Visitadas],
        Ruta,
        NuevaDistancia,
        DistanciaTotal
    ).


% RUTA MAS CORTA


ruta_mas_corta(
    Origen,
    Destino,
    RutaCorta,
    DistanciaCorta
) :-

    setof(
        Distancia-Ruta,
        ruta(
            Origen,
            Destino,
            Ruta,
            Distancia
        ),
        [
            DistanciaCorta-RutaCorta
            | _
        ]
    ).


% TODAS LAS RUTAS ORDENADAS


todas_las_rutas(
    Origen,
    Destino,
    Rutas
) :-

    setof(
        Distancia-Ruta,
        ruta(
            Origen,
            Destino,
            Ruta,
            Distancia
        ),
        Rutas
    ).