
% helpers.pl
% Predicados utilitarios reutilizados por rules.pl y engine.pl.
% Aquí viven: intersección de listas, verificación de subsets,
% recolección de recomendaciones y validaciones de existencia.


% ---- subset/2 -----------------------------------------------
% Verifica que todos los elementos de Lista estén en Conjunto.
% Usado para confirmar que los síntomas requeridos por una regla
% están TODOS presentes en los síntomas enviados por el usuario.
%
% subset(+Lista, +Conjunto)
subset([], _).
subset([H|T], Conjunto) :-
    member(H, Conjunto),
    subset(T, Conjunto).

% ---- interseccion/3 -----------------------------------------
% Calcula la intersección entre dos listas.
% Usado para determinar cuántos síntomas relevantes seleccionó
% el usuario, aunque no sean exactamente los requeridos.
%
% interseccion(+Lista1, +Lista2, -Comunes)
interseccion([], _, []).
interseccion([H|T], Lista2, [H|Resto]) :-
    member(H, Lista2), !,
    interseccion(T, Lista2, Resto).
interseccion([_|T], Lista2, Resto) :-
    interseccion(T, Lista2, Resto).

% ---- obtener_recomendaciones/2 ------------------------------
% Recolecta todas las recomendaciones asociadas a una FallaID.
% Retorna una lista de descripciones de texto.
%
% obtener_recomendaciones(+FallaID, -ListaDescripciones)
obtener_recomendaciones(FallaID, Descripciones) :-
    findall(Desc, recomendacion(_, FallaID, Desc), Descripciones).

% ---- obtener_info_falla/4 -----------------------------------
% Conveniencia: dado un FallaID, retorna sus campos.
%
% obtener_info_falla(+FallaID, -Nombre, -Tipo, -Descripcion)
obtener_info_falla(FallaID, Nombre, Tipo, Descripcion) :-
    falla(FallaID, Nombre, Tipo, Descripcion).

% ---- sintoma_existe/1 ---------------------------------------
% Verifica que un ID de síntoma esté registrado en la base.
%
% sintoma_existe(+ID)
sintoma_existe(ID) :-
    sintoma(ID, _, _).

% ---- falla_existe/1 -----------------------------------------
% Verifica que un ID de falla esté registrado en la base.
%
% falla_existe(+ID)
falla_existe(ID) :-
    falla(ID, _, _, _).

% ---- listar_sintomas/1 --------------------------------------
% Retorna todos los síntomas como lista de términos
% sintoma(ID, Nombre, Descripcion).
%
% listar_sintomas(-Lista)
listar_sintomas(Lista) :-
    findall(sintoma(ID, Nombre, Desc),
            sintoma(ID, Nombre, Desc),
            Lista).

% ---- listar_fallas/1 ----------------------------------------
% Retorna todas las fallas como lista de términos
% falla(ID, Nombre, Tipo, Descripcion).
%
% listar_fallas(-Lista)
listar_fallas(Lista) :-
    findall(falla(ID, Nombre, Tipo, Desc),
            falla(ID, Nombre, Tipo, Desc),
            Lista).

% ---- listar_recomendaciones/1 -------------------------------
% Retorna todas las recomendaciones.
%
% listar_recomendaciones(-Lista)
listar_recomendaciones(Lista) :-
    findall(recomendacion(ID, FallaID, Desc),
            recomendacion(ID, FallaID, Desc),
            Lista).