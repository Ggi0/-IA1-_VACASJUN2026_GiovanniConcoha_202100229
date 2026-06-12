:- encoding(utf8).
% =============================================================================
% helpers.pl
% Predicados auxiliares del sistema experto Doctor Byte.
%
% Responsabilidades:
%   - Gestionar síntomas activos en sesión (assert/retract dinámico)
%   - Validar síntomas válidos contra el catálogo
%   - Operaciones sobre listas (verificación de subconjuntos, pertenencia)
%   - Construcción de resultados estructurados
%   - Manejo de cortes (!) para optimización de búsqueda
%
% NOTA: Este archivo es requerido por rules.pl y engine.pl.
%       No contiene reglas de diagnóstico; solo utilidades.
% =============================================================================

:- use_module(library(lists)).  % Para last/2, nth/3, etc. en SWI-Prolog


% =============================================================================
% SECCIÓN 1: CATÁLOGO DE SÍNTOMAS VÁLIDOS
% Hecho: sintoma_valido(ID, Nombre)
%
% Define todos los síntomas que el sistema reconoce.
% Usado para validar la entrada del usuario antes de diagnosticar.
% =============================================================================

sintoma_valido(s01, 'Pantalla negra al encender').
sintoma_valido(s02, 'Pitidos al arrancar').
sintoma_valido(s03, 'Reinicios inesperados').
sintoma_valido(s04, 'Apagados repentinos').
sintoma_valido(s05, 'Sobrecalentamiento').
sintoma_valido(s06, 'Lentitud general del sistema').
sintoma_valido(s07, 'Congelamientos frecuentes').
sintoma_valido(s08, 'Pantalla azul').
sintoma_valido(s09, 'No detecta el disco duro').
sintoma_valido(s10, 'Error al iniciar el sistema operativo').
sintoma_valido(s11, 'Archivos corruptos').
sintoma_valido(s12, 'Conexión a internet inestable').
sintoma_valido(s13, 'No detecta redes WiFi').
sintoma_valido(s14, 'Puertos USB no funcionan').
sintoma_valido(s15, 'Ruido extraño en el disco').
sintoma_valido(s16, 'Ventilador hace mucho ruido').
sintoma_valido(s17, 'Programas se cierran solos').
sintoma_valido(s18, 'Aparición de ventanas emergentes').
sintoma_valido(s19, 'No enciende').
sintoma_valido(s20, 'Batería se descarga rápidamente').


% =============================================================================
% SECCIÓN 2: SÍNTOMAS ACTIVOS EN SESIÓN (base de datos dinámica)
%
% sintoma_activo/1 se declara dinámico porque se agrega y elimina
% en tiempo de ejecución con assert/retract.
%
% Esto permite que Python cargue los síntomas del usuario antes
% de solicitar el diagnóstico.
% =============================================================================

:- dynamic sintoma_activo/1.
% sintoma_activo(ID). — se agrega vía assert durante una sesión de diagnóstico


% -----------------------------------------------------------------------------
% cargar_sintomas(+Lista)
% Recibe una lista de IDs de síntomas y los registra como activos.
% Primero limpia cualquier sesión anterior (limpiar_sintomas/0).
%
% Ejemplo: cargar_sintomas([s01, s02, s05])
% -----------------------------------------------------------------------------
cargar_sintomas(Lista) :-
    limpiar_sintomas,               % eliminar sesión previa
    cargar_sintomas_aux(Lista).     % cargar los nuevos

cargar_sintomas_aux([]).            % caso base: lista vacía → nada que hacer
cargar_sintomas_aux([H|T]) :-       % caso recursivo: cargar cabeza y resto
    assertz(sintoma_activo(H)),     % registrar síntoma H como activo
    cargar_sintomas_aux(T).         % procesar el resto de la lista


% -----------------------------------------------------------------------------
% limpiar_sintomas/0
% Elimina todos los síntomas activos de la sesión actual.
% Se llama automáticamente al inicio de cargar_sintomas/1.
% -----------------------------------------------------------------------------
limpiar_sintomas :-
    retractall(sintoma_activo(_)).  % retractall no falla si no hay hechos


% =============================================================================
% SECCIÓN 3: VERIFICACIÓN DE SÍNTOMAS
% =============================================================================

% -----------------------------------------------------------------------------
% presente(+ID)
% Verifica si un síntoma está activo en la sesión actual.
% Usado dentro de las reglas de rules.pl.
%
% Ejemplo: presente(s01) → true si s01 fue cargado con cargar_sintomas/1
% -----------------------------------------------------------------------------
presente(ID) :-
    sintoma_activo(ID).


% -----------------------------------------------------------------------------
% al_menos_uno(+Lista)
% Tiene éxito si AL MENOS UNO de los síntomas de la lista está presente.
% Usa CORTE (!) para detenerse al encontrar el primero: no necesita
% verificar el resto si ya encontró uno verdadero → optimización.
%
% Ejemplo: al_menos_uno([s12, s13]) → true si s12 o s13 están activos
% -----------------------------------------------------------------------------
al_menos_uno([H|_]) :-
    presente(H),
    !.                              % CORTE: encontró uno, no sigue buscando
al_menos_uno([_|T]) :-
    al_menos_uno(T).               % prueba con el resto de la lista


% -----------------------------------------------------------------------------
% todos_presentes(+Lista)
% Tiene éxito solo si TODOS los síntomas de la lista están presentes.
% Versión explícita (SWI-Prolog también tiene maplist, pero esta es
% más clara pedagógicamente).
%
% Ejemplo: todos_presentes([s01, s02]) → true solo si ambos están activos
% -----------------------------------------------------------------------------
todos_presentes([]).               % caso base: lista vacía → trivialmente true
todos_presentes([H|T]) :-
    presente(H),                   % verificar cabeza
    todos_presentes(T).            % verificar resto (recursión)


% -----------------------------------------------------------------------------
% subconjunto_presente(+Lista, +Min)
% Tiene éxito si al menos Min síntomas de Lista están presentes.
% Útil para reglas que no requieren TODOS los síntomas, sino una mayoría.
%
% Ejemplo: subconjunto_presente([s06, s07, s17, s18], 2)
%          → true si al menos 2 de esos 4 están activos
% -----------------------------------------------------------------------------
subconjunto_presente(Lista, Min) :-
    contar_presentes(Lista, Count),
    Count >= Min.

% Predicado auxiliar: cuenta cuántos elementos de Lista están presentes
contar_presentes([], 0).
contar_presentes([H|T], Count) :-
    contar_presentes(T, SubCount),
    (   presente(H)
    ->  Count is SubCount + 1      % si H está presente, suma 1
    ;   Count is SubCount          % si no, mantiene el conteo
    ).


% =============================================================================
% SECCIÓN 4: VALIDACIÓN DE ENTRADA
% =============================================================================

% -----------------------------------------------------------------------------
% sintoma_existe(+ID)
% Verifica que un ID corresponde a un síntoma del catálogo.
% Usado por engine.pl para rechazar IDs inválidos antes de cargarlos.
%
% Ejemplo: sintoma_existe(s01) → true
%          sintoma_existe(s99) → false
% -----------------------------------------------------------------------------
sintoma_existe(ID) :-
    sintoma_valido(ID, _).


% -----------------------------------------------------------------------------
% filtrar_validos(+Lista, -Validos, -Invalidos)
% Separa una lista de IDs en los que existen en catálogo y los que no.
%
% Ejemplo: filtrar_validos([s01, s99, s02], Validos, Invalidos)
%          Validos = [s01, s02], Invalidos = [s99]
% -----------------------------------------------------------------------------
filtrar_validos([], [], []).
filtrar_validos([H|T], [H|V], I) :-
    sintoma_existe(H),             % H es válido
    !,                             % CORTE: no probar la cláusula alternativa
    filtrar_validos(T, V, I).
filtrar_validos([H|T], V, [H|I]) :-
    filtrar_validos(T, V, I).      % H no es válido → va a Invalidos


% =============================================================================
% SECCIÓN 5: CONSTRUCCIÓN DE RESULTADOS
% =============================================================================

% -----------------------------------------------------------------------------
% obtener_nombre_sintoma(+ID, -Nombre)
% Devuelve el nombre legible de un síntoma por su ID.
%
% Ejemplo: obtener_nombre_sintoma(s01, Nombre)
%          Nombre = 'Pantalla negra al encender'
% -----------------------------------------------------------------------------
obtener_nombre_sintoma(ID, Nombre) :-
    sintoma_valido(ID, Nombre),
    !.                             % CORTE: solo necesitamos la primera coincidencia
obtener_nombre_sintoma(ID, Nombre) :-
    % Si no existe en catálogo, devuelve el ID como texto (fallback seguro)
    term_to_atom(ID, Nombre).


% -----------------------------------------------------------------------------
% nombres_sintomas(+IDs, -Nombres)
% Convierte una lista de IDs en una lista de nombres legibles.
%
% Ejemplo: nombres_sintomas([s01, s02], Nombres)
%          Nombres = ['Pantalla negra al encender', 'Pitidos al arrancar']
% -----------------------------------------------------------------------------
nombres_sintomas([], []).
nombres_sintomas([H|T], [Nombre|Resto]) :-
    obtener_nombre_sintoma(H, Nombre),
    nombres_sintomas(T, Resto).


% -----------------------------------------------------------------------------
% sintomas_activos_lista(-Lista)
% Recolecta todos los síntomas activos en la sesión actual como lista.
% Usado por engine.pl para incluirlos en la respuesta al backend.
%
% Ejemplo: sintomas_activos_lista(L)
%          L = [s01, s02, s05]   (si esos fueron cargados)
% -----------------------------------------------------------------------------
sintomas_activos_lista(Lista) :-
    findall(ID, sintoma_activo(ID), Lista).


% =============================================================================
% SECCIÓN 6: UTILIDADES GENERALES
% =============================================================================

% -----------------------------------------------------------------------------
% lista_no_vacia(+Lista)
% Falla si la lista está vacía. Usado para guardas en engine.pl.
% -----------------------------------------------------------------------------
lista_no_vacia([_|_]).


% -----------------------------------------------------------------------------
% atomos_a_lista(+AtomSeparadoPorComa, -Lista)
% Convierte un átomo como 's01,s02,s03' en lista [s01, s02, s03].
% Útil si Python pasa los síntomas como string separado por comas.
%
% Ejemplo: atomos_a_lista('s01,s02', Lista)
%          Lista = [s01, s02]
% -----------------------------------------------------------------------------
atomos_a_lista(Atom, Lista) :-
    atomic_list_concat(Partes, ',', Atom),   % dividir por coma
    maplist(atom_to_term_safe, Partes, Lista).

% Convierte cada parte string a átomo (trim de espacios)
atom_to_term_safe(Str, Atom) :-
    atom_string(Atom0, Str),
    atom_string(Atom, Atom0).                % normaliza a átomo