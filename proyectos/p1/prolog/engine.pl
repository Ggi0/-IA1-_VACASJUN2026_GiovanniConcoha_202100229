
% engine.pl
% Punto de entrada del motor de inferencia Doctor Byte.
% Carga todos los módulos y expone los predicados públicos
% que el adapter de Python (pyswip) va a consultar.
%
% Uso desde Python:
%   prolog = Prolog()
%   prolog.consult('engine.pl')
%   list(prolog.query("diagnosticar([...], FallaID, Nombre, Tipo, Desc, Recs)"))


:- set_prolog_flag(encoding, utf8).

% Carga de datos persistentes
:- consult('data/symptoms.pl').
:- consult('data/failures.pl').
:- consult('data/recommendations.pl').

% Carga de conocimiento
:- consult('knowledge/helpers.pl').
:- consult('knowledge/rules.pl').


% diagnosticar/6
% Predicado principal. Dado una lista de IDs de síntomas
% seleccionados por el usuario, busca la primera falla cuyas
% reglas sean satisfechas y retorna toda la información.
%
% diagnosticar(+SintomasSeleccionados,
%              -FallaID, -Nombre, -Tipo, -Descripcion,
%              -Recomendaciones)
%
% Estrategia: busca reglas donde TODOS los síntomas requeridos
% estén dentro de los seleccionados. Si hay varias reglas que
% aplican para la misma falla, solo se reporta una vez (via
% la prioridad de findall + primer match).

diagnosticar(SintomasSeleccionados, FallaID, Nombre, Tipo, Descripcion, Recomendaciones) :-
    diagnostico(FallaID, SintomasRequeridos),
    subset(SintomasRequeridos, SintomasSeleccionados),
    falla(FallaID, Nombre, Tipo, Descripcion),
    obtener_recomendaciones(FallaID, Recomendaciones),
    Recomendaciones \= [].  % Solo reportar fallas que tengan recomendaciones


% diagnosticar_todos/2
% Retorna TODAS las fallas diagnosticadas (sin duplicados)
% a partir de la lista de síntomas seleccionados.
%
% diagnosticar_todos(+SintomasSeleccionados, -ListaDiagnosticos)
%
% Cada elemento de ListaDiagnosticos es un término:
%   diagnostico(FallaID, Nombre, Tipo, Descripcion, Recomendaciones)

diagnosticar_todos(SintomasSeleccionados, ListaDiagnosticos) :-
    findall(
        diagnostico(FallaID, Nombre, Tipo, Descripcion, Recomendaciones),
        diagnosticar(SintomasSeleccionados, FallaID, Nombre, Tipo, Descripcion, Recomendaciones),
        ListaConDuplicados
    ),
    % Eliminar duplicados por FallaID
    eliminar_duplicados_falla(ListaConDuplicados, ListaDiagnosticos).


% eliminar_duplicados_falla/2
% Elimina entradas duplicadas basándose en el FallaID.
% Usa acumulador interno.

eliminar_duplicados_falla(Lista, SinDuplicados) :-
    eliminar_duplicados_falla(Lista, [], SinDuplicados).

eliminar_duplicados_falla([], _, []).
eliminar_duplicados_falla(
    [diagnostico(FallaID, N, T, D, R)|Resto],
    Vistos,
    Resultado
) :-
    member(FallaID, Vistos), !,
    eliminar_duplicados_falla(Resto, Vistos, Resultado).
eliminar_duplicados_falla(
    [diagnostico(FallaID, N, T, D, R)|Resto],
    Vistos,
    [diagnostico(FallaID, N, T, D, R)|Resultado]
) :-
    eliminar_duplicados_falla(Resto, [FallaID|Vistos], Resultado).


% CRUD: Agregar hechos dinámicamente
% Estos predicados son llamados por el adapter cuando el
% administrador agrega datos nuevos. Los assert/retract
% operan en memoria; la persistencia la maneja Python
% reescribiendo los archivos .pl correspondientes.


% agregar_sintoma(+ID, +Nombre, +Descripcion)
agregar_sintoma(ID, Nombre, Descripcion) :-
    \+ sintoma(ID, _, _),  % No duplicar
    assertz(sintoma(ID, Nombre, Descripcion)).

% eliminar_sintoma(+ID)
eliminar_sintoma(ID) :-
    retract(sintoma(ID, _, _)).

% agregar_falla(+ID, +Nombre, +Tipo, +Descripcion)
agregar_falla(ID, Nombre, Tipo, Descripcion) :-
    \+ falla(ID, _, _, _),
    assertz(falla(ID, Nombre, Tipo, Descripcion)).

% eliminar_falla(+ID)
eliminar_falla(ID) :-
    retract(falla(ID, _, _, _)).

% agregar_recomendacion(+ID, +FallaID, +Descripcion)
agregar_recomendacion(ID, FallaID, Descripcion) :-
    \+ recomendacion(ID, _, _),
    assertz(recomendacion(ID, FallaID, Descripcion)).

% eliminar_recomendacion(+ID)
eliminar_recomendacion(ID) :-
    retract(recomendacion(ID, _, _)).

% agregar_regla(+FallaID, +ListaSintomas)
agregar_regla(FallaID, ListaSintomas) :-
    \+ diagnostico(FallaID, ListaSintomas),
    assertz(diagnostico(FallaID, ListaSintomas)).

% eliminar_regla(+FallaID, +ListaSintomas)
eliminar_regla(FallaID, ListaSintomas) :-
    retract(diagnostico(FallaID, ListaSintomas)).


% Predicados de consulta para el CRUD (listas completas)


% todos_sintomas(-Lista) — lista de sintoma(ID, Nombre, Desc)
todos_sintomas(Lista) :- listar_sintomas(Lista).

% todas_fallas(-Lista) — lista de falla(ID, Nombre, Tipo, Desc)
todas_fallas(Lista) :- listar_fallas(Lista).

% todas_recomendaciones(-Lista)
todas_recomendaciones(Lista) :- listar_recomendaciones(Lista).

% todas_reglas(-Lista) — lista de regla(FallaID, Sintomas)
todas_reglas(Lista) :-
    findall(regla(FallaID, Sintomas), diagnostico(FallaID, Sintomas), Lista).