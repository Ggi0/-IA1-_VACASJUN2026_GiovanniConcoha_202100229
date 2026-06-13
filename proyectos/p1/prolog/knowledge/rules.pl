
% rules.pl
% Reglas de diagnóstico: mapean combinaciones de síntomas
% a fallas. Aquí vive todo el conocimiento experto.
%
% Formato de regla:
%   diagnostico(FallaID, SintomasRequeridos)
%
%   SintomasRequeridos es una lista de IDs de síntomas.
%   Si el usuario selecciona TODOS los síntomas de la lista,
%   la falla se activa.
%
% El corte (!) se usa en diagnosticar_primero/2 del engine
% para detener la búsqueda tras el primer diagnóstico exacto,
% y aquí en reglas con condiciones excluyentes.
%
% IMPORTANTE: El administrador puede agregar nuevas reglas
% a este archivo mediante el CRUD del backend. Las reglas
% nuevas se insertan al final de la sección dinámica.


:- dynamic diagnostico/2.

% ------ F01: Memoria RAM defectuosa -------------------------
% Un solo síntoma fuerte
diagnostico('F01', ['S02']).          % Pitidos al arrancar

% Combinación de 2 síntomas
diagnostico('F01', ['S01', 'S17']).   % Pantalla negra + errores de memoria
diagnostico('F01', ['S06', 'S17']).   % BSOD + errores de memoria
diagnostico('F01', ['S05', 'S17']).   % Lentitud + errores de memoria

% Combinación de 3 síntomas
diagnostico('F01', ['S01', 'S02', 'S17']). % Pantalla negra + pitidos + errores RAM

% ------ F02: Sobrecalentamiento del sistema -----------------
diagnostico('F02', ['S11']).          % Temperatura elevada

diagnostico('F02', ['S03', 'S11']).   % Reinicios + temperatura
diagnostico('F02', ['S04', 'S11']).   % Apagados + temperatura
diagnostico('F02', ['S04', 'S12']).   % Apagados + ventiladores máximo

diagnostico('F02', ['S03', 'S04', 'S12']). % Reinicios + apagados + ventiladores

% ------ F03: Disco duro dañado ------------------------------
diagnostico('F03', ['S08']).          % Ruidos extraños en disco

diagnostico('F03', ['S08', 'S09']).   % Ruidos + archivos corruptos
diagnostico('F03', ['S07', 'S08']).   % No arranca SO + ruidos

diagnostico('F03', ['S07', 'S08', 'S09']). % No arranca + ruidos + archivos corruptos

% ------ F04: Sistema operativo corrupto ---------------------
diagnostico('F04', ['S07']).          % No arranca el SO (sin ruidos de disco)

diagnostico('F04', ['S07', 'S09']).   % No arranca + archivos corruptos
diagnostico('F04', ['S06', 'S09']).   % BSOD + archivos corruptos

diagnostico('F04', ['S06', 'S07', 'S09']). % BSOD + no arranca + archivos corruptos

% ------ F05: Fallo de fuente de alimentación ----------------
diagnostico('F05', ['S03', 'S04']).   % Reinicios + apagados (sin temperatura)
diagnostico('F05', ['S15', 'S04']).   % USB no reconocidos + apagados

% ------ F06: Fallo de tarjeta gráfica ----------------------
diagnostico('F06', ['S16']).          % Sin imagen en el monitor

diagnostico('F06', ['S01', 'S16']).   % Pantalla negra + sin señal monitor
diagnostico('F06', ['S06', 'S16']).   % BSOD + sin señal (driver GPU)

% ------ F07: Infección por malware -------------------------
diagnostico('F07', ['S20']).          % Alertas de virus

diagnostico('F07', ['S05', 'S20']).   % Lentitud + alertas de virus
diagnostico('F07', ['S10', 'S20']).   % Apps se cierran + alertas de virus
diagnostico('F07', ['S19', 'S20']).   % Programas no responden + virus

diagnostico('F07', ['S05', 'S10', 'S20']). % Lentitud + cierres + virus

% ------ F08: Fallo de controladora de red ------------------
diagnostico('F08', ['S13']).          % Sin conexión a internet

diagnostico('F08', ['S13', 'S14']).   % Sin conexión + conexión intermitente
diagnostico('F08', ['S14']).          % Solo intermitencia (driver red)

% ------ F09: Sector de arranque dañado (MBR/GPT) -----------
% Corte (!): si se cumple esta regla NO seguir buscando F04
diagnostico('F09', ['S07', 'S06']) :- !. % No arranca + BSOD = arranque dañado

diagnostico('F09', ['S07']).          % Solo no arranca (regla de fallback)

% ------ F10: Drivers desactualizados/corruptos --------------
diagnostico('F10', ['S15']).          % USB no reconocidos

diagnostico('F10', ['S15', 'S10']).   % USB no reconocidos + apps cierran
diagnostico('F10', ['S06', 'S15']).   % BSOD + USB = driver

% ------ F11: Fallo del sistema de archivos -----------------
diagnostico('F11', ['S09']).          % Archivos corruptos (sin ruidos)

diagnostico('F11', ['S05', 'S09']).   % Lentitud + archivos corruptos
diagnostico('F11', ['S09', 'S19']).   % Archivos corruptos + programas no responden

% ------ F12: Fallo fuente/botón encendido ------------------
diagnostico('F12', ['S18']).          % El equipo no enciende