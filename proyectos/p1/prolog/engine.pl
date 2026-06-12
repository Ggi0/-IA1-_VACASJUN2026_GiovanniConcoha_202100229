:- encoding(utf8).

% Carga de módulos del sistema experto (orden importante)
:- ensure_loaded('knowledge/helpers.pl').    % auxiliares y síntomas activos
:- ensure_loaded('knowledge/diagnoses.pl').  % fallas y recomendaciones
:- ensure_loaded('knowledge/rules.pl').      % reglas de inferencia


% PREDICADO PRINCIPAL: diagnosticar/1

diagnosticar(Resultado) :-
    % 1. Obtener todos los diagnosticos que aplican
    todos_los_diagnosticos(DiagnosticosRaw),

    % 2. Construir resultado enriquecido con datos de diagnoses.pl
    construir_resultado(DiagnosticosRaw, Resultado).



% construir_resultado(+DiagnosticosRaw, -Resultado)
% Transforma la lista de falla(ID, Sintomas) en términos diagnóstico/6 con todos los datos necesarios para el backend Python.

construir_resultado([], []).
construir_resultado([falla(ID, Sintomas)|Resto], [Diag|RestoRes]) :-
    
    % Obtener datos de la falla desde diagnoses.pl
    obtener_falla(ID, Nombre, Tipo, DescFalla),
    
    % Obtener recomendación asociada a la falla
    obtener_recomendacion(ID, Recomendacion),
    
    % Construir el termino de diagnóstico
    Diag = diagnostico(ID, Nombre, Tipo, DescFalla, Recomendacion, Sintomas),
    
    % Continuar con el resto
    construir_resultado(Resto, RestoRes).

% Caso de falla no encontrada en el catálogo (seguridad ante inconsistencias)
construir_resultado([falla(ID, _)|Resto], RestoRes) :-
    \+ falla(ID, _, _, _),       % la falla no existe en el catálogo
    construir_resultado(Resto, RestoRes).



%                                                               CONSULTA DE CATÁLOGOS
% Predicados que permiten al backend obtener los datos maestros del sistema.



% listar_sintomas(-Lista)
% Devuelve todos los síntomas disponibles como lista de terminos:
%   sintoma(ID, Nombre)
%
% Ejemplo de uso desde Python:
%   query listar_sintomas(L)
%   L = [sintoma(s01, 'Pantalla negra al encender'), ...]

listar_sintomas(Lista) :-
    findall(
        sintoma(ID, Nombre),
        sintoma_valido(ID, Nombre),
        Lista
    ).



% listar_fallas(-Lista)
% Devuelve todas las fallas del catálogo como lista de términos:
%   falla_info(ID, Nombre, Tipo, Descripcion)

listar_fallas(Lista) :-
    findall(
        falla_info(ID, Nombre, Tipo, Desc),
        falla(ID, Nombre, Tipo, Desc),
        Lista
    ).



%                                       VALIDACIÓN DE ENTRADA
% Predicados de apoyo para que el backend rechace datos incorrectos.

% validar_sintomas(+Lista, -Invalidos)
% Dada una lista de IDs enviados por el usuario, devuelve los que NO
% existen en el catálogo. Lista vacía = todos válidos.
%
% Ejemplo:
%   validar_sintomas([s01, s99, s02], Invalidos)
%   Invalidos = [s99]

validar_sintomas(Lista, Invalidos) :-
    filtrar_validos(Lista, _, Invalidos).



% PREDICADO COMPLETO: diagnosticar_desde_lista/2
%
% Combina cargar_sintomas + diagnosticar en un solo predicado.
% Permite que Python haga UNA SOLA consulta para todo el proceso.
%
%   diagnosticar_desde_lista(+ListaSintomas, -Resultado)
%
% Ejemplo desde pyswip:
%   list(engine.diagnosticar_desde_lista([s01, s02], R))

diagnosticar_desde_lista(ListaSintomas, Resultado) :-
    % Validación: rechazar si la lista está vacía
    lista_no_vacia(ListaSintomas),
    % Cargar síntomas en la base dinámica
    cargar_sintomas(ListaSintomas),
    % Ejecutar diagnóstico
    diagnosticar(Resultado).

% Caso de lista vacía: devuelve resultado vacío con mensaje de error
diagnosticar_desde_lista([], [error('No se proporcionaron síntomas')]) :-
    !.



% FORMATEO JSON
%
% Si Python ejecuta SWI-Prolog como subprocess y lee stdout,
% este predicado imprime el resultado en formato JSON compatible.
%
% Uso desde línea de comandos:
%   swipl -g "diagnosticar_json_stdout([s01,s02])" -t halt engine.pl



% diagnosticar_json_stdout(+ListaSintomas)
% Ejecuta el diagnóstico y escribe el resultado JSON en stdout.
% Python captura esta salida con subprocess.

diagnosticar_json_stdout(ListaSintomas) :-
    diagnosticar_desde_lista(ListaSintomas, Resultado),
    resultado_a_json(Resultado, JSON),
    write(JSON), nl.

% Caso de error
diagnosticar_json_stdout([]) :-
    write('{"error": "No se proporcionaron sintomas", "diagnosticos": []}'), nl.



% resultado_a_json(+Resultado, -JSON)
% Convierte la lista de diagnóstico a un átomo JSON válido.
% No requiere librería externa: construye el string manualmente.

resultado_a_json(Resultado, JSON) :-
    maplist(diagnostico_a_json, Resultado, JSONDiags),
    atomic_list_concat(JSONDiags, ',', DiagsConcatenados),
    atomic_list_concat(['{"diagnosticos":[', DiagsConcatenados, ']}'], JSON).

% Caso sin diagnósticos
resultado_a_json([], '{"diagnosticos":[]}').


% Convierte un término diagnóstico/6 a objeto JSON
diagnostico_a_json(
    diagnostico(ID, Nombre, Tipo, Desc, Rec, Sintomas),
    JSON
) :-
    term_to_atom(ID, IDAtom),
    term_to_atom(Tipo, TipoAtom),
    % Escapar comillas en strings (básico)
    escape_json_string(Nombre, NombreEsc),
    escape_json_string(Desc, DescEsc),
    escape_json_string(Rec, RecEsc),
    % Construir array de síntomas
    maplist(term_to_atom, Sintomas, SintomaAtoms),
    atomics_to_sintomas_json(SintomaAtoms, SintomasJSON),
    % Ensamblar objeto JSON
    atomic_list_concat([
        '{"id":"', IDAtom, '",',
        '"nombre":"', NombreEsc, '",',
        '"tipo":"', TipoAtom, '",',
        '"descripcion":"', DescEsc, '",',
        '"recomendacion":"', RecEsc, '",',
        '"sintomas_activados":', SintomasJSON,
        '}'
    ], JSON).

% Maneja el caso de error en la lista
diagnostico_a_json(error(Msg), JSON) :-
    escape_json_string(Msg, MsgEsc),
    atomic_list_concat(['{"error":"', MsgEsc, '"}'], JSON).


% Convierte lista de átomos a array JSON: [s01,s02] → '["s01","s02"]'
atomics_to_sintomas_json(Atoms, JSON) :-
    maplist([A, S]>>(atomic_list_concat(['"', A, '"'], S)), Atoms, QuotedAtoms),
    atomic_list_concat(QuotedAtoms, ',', Inner),
    atomic_list_concat(['[', Inner, ']'], JSON).


% Escapa comillas dobles en strings para JSON válido
escape_json_string(Input, Output) :-
    atom_string(Input, Str),
    split_string(Str, "\"", "", Parts),
    atomic_list_concat(Parts, '\\"', Output).



% INICIALIZACIÓN DEL MOTOR
% Se ejecuta automáticamente al cargar engine.pl.
% Limpia cualquier estado residual de sesiones anteriores.

:- initialization(limpiar_sintomas, now).