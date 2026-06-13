
% AGREGAR CIUDAD


agregar_ciudad(Nombre) :-
    \+ ciudad(Nombre),
    assertz(ciudad(Nombre)).


% AGREGAR CONEXION


agregar_conexion(Origen, Destino, Distancia) :-

    ciudad(Origen),
    ciudad(Destino),

    Distancia > 0,

    \+ conexion(Origen, Destino, Distancia),

    assertz(conexion(Origen, Destino, Distancia)).