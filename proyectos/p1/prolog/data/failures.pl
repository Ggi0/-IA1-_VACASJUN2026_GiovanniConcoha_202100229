
% failures.pl
% Hechos que representan las fallas diagnosticables.
% Formato: falla(ID, Nombre, Tipo, Descripcion).
%
% Tipos posibles: 'Hardware', 'Software', 'Red', 'Seguridad'
% Este archivo es gestionado dinámicamente por el backend.


:- dynamic falla/4.

falla('F01', 'Memoria RAM defectuosa', 'Hardware',
    'Posible fallo físico o mala conexión de los módulos de memoria RAM.').

falla('F02', 'Sobrecalentamiento del sistema', 'Hardware',
    'El equipo presenta temperaturas excesivas que afectan su funcionamiento.').

falla('F03', 'Disco duro dañado', 'Hardware',
    'La unidad de almacenamiento presenta sectores defectuosos o fallas mecánicas.').

falla('F04', 'Sistema operativo corrupto', 'Software',
    'Archivos críticos del sistema operativo están dañados o ausentes.').

falla('F05', 'Fallo de fuente de alimentación', 'Hardware',
    'La fuente de poder no suministra voltaje estable o suficiente.').

falla('F06', 'Fallo de tarjeta gráfica', 'Hardware',
    'La GPU presenta daño físico o sus drivers están corruptos.').

falla('F07', 'Infección por malware', 'Seguridad',
    'El sistema ha sido comprometido por software malicioso.').

falla('F08', 'Fallo de controladora de red', 'Red',
    'La tarjeta de red o sus drivers presentan problemas.').

falla('F09', 'Sector de arranque dañado (MBR/GPT)', 'Software',
    'El registro de arranque está corrupto e impide cargar el sistema operativo.').

falla('F10', 'Controladores (drivers) desactualizados o corruptos', 'Software',
    'Los drivers de uno o más dispositivos están dañados o son incompatibles.').

falla('F11', 'Fallo del sistema de archivos', 'Software',
    'El sistema de archivos presenta inconsistencias o errores estructurales.').

falla('F12', 'Fallo de fuente de alimentación o botón de encendido', 'Hardware',
    'El equipo no recibe energía eléctrica o el circuito de encendido falla.').
falla('F14', 'falla test', 'Harward',
    'test').
