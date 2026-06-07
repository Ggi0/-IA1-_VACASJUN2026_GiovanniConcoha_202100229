
% Regla para agregar una nueva ciudad
agregar_ciudad(Nombre) :-
    \+ ciudad(Nombre), % Verificar que la ciudad no exista
    assertz(ciudad(Nombre)).

% Regla para agregar una nueva conexión entre ciudades
agregar_conexion(Origen, Destino, Distancia) :-
    \+ conexion(Origen, Destino, Distancia), % Verificar que la conexión no exista
    assertz(conexion(Origen, Destino, Distancia)).