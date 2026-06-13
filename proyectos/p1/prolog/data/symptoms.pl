
% symptoms.pl
% Hechos que representan los síntomas conocidos del sistema.
% Formato: sintoma(ID, Nombre, Descripcion).
%
% Este archivo es gestionado dinámicamente por el backend.
% El administrador puede agregar/eliminar síntomas a través
% del CRUD, lo que modifica este archivo directamente.


:- dynamic sintoma/3.

sintoma('S01', 'Pantalla negra al encender',
    'La computadora enciende pero no muestra imagen.').

sintoma('S02', 'Pitidos al arrancar',
    'Se escuchan sonidos o códigos de pitidos durante el arranque.').

sintoma('S03', 'Reinicios inesperados',
    'El sistema se reinicia sin intervención del usuario.').

sintoma('S04', 'Apagados repentinos',
    'La computadora se apaga de forma inesperada.').

sintoma('S05', 'Sistema muy lento',
    'El equipo tarda demasiado en responder o ejecutar tareas básicas.').

sintoma('S06', 'Pantalla azul de la muerte (BSOD)',
    'Aparece una pantalla azul con un mensaje de error crítico.').

sintoma('S07', 'No arranca el sistema operativo',
    'El equipo enciende pero el sistema operativo no carga.').

sintoma('S08', 'Ruidos extraños en el disco',
    'Se escuchan clics, chirridos o golpes provenientes del disco.').

sintoma('S09', 'Archivos corruptos o desaparecidos',
    'Archivos del sistema o del usuario aparecen dañados o no se encuentran.').

sintoma('S10', 'Aplicaciones que se cierran solas',
    'Los programas se cierran inesperadamente sin mensaje de error.').

sintoma('S11', 'Temperatura elevada del equipo',
    'El chasis o los componentes presentan calor excesivo al tacto.').

sintoma('S12', 'Ventiladores a máxima velocidad',
    'Los ventiladores trabajan constantemente a alta velocidad.').

sintoma('S13', 'Sin conexión a internet',
    'El equipo no puede conectarse a redes o a internet.').

sintoma('S14', 'Conexión a internet intermitente',
    'La conexión se pierde y recupera de manera irregular.').

sintoma('S15', 'Dispositivos USB no reconocidos',
    'Los puertos USB no detectan los dispositivos conectados.').

sintoma('S16', 'Sin imagen en el monitor',
    'El monitor está encendido pero no recibe señal del equipo.').

sintoma('S17', 'Errores de memoria al ejecutar programas',
    'Aparecen mensajes del tipo "memory access violation" o similares.').

sintoma('S18', 'El equipo no enciende',
    'Al presionar el botón de encendido no hay respuesta alguna.').

sintoma('S19', 'Programas que no responden',
    'Las aplicaciones se congelan y no reaccionan a ninguna acción.').

sintoma('S20', 'Alertas de virus o malware',
    'El antivirus detecta amenazas o el comportamiento del sistema es sospechoso.').
