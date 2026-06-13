
% recommendations.pl
% Hechos que representan recomendaciones asociadas a fallas.
% Formato: recomendacion(ID, FallaID, Descripcion).
%
% Una falla puede tener múltiples recomendaciones.
% Este archivo es gestionado dinámicamente por el backend.


:- dynamic recomendacion/3.

recomendacion('R01', 'F01',
    'Apagar el equipo, retirar los módulos RAM, limpiar los contactos con borrador y volver a instalarlos correctamente.').

recomendacion('R02', 'F01',
    'Probar con un solo módulo RAM a la vez para identificar cuál está defectuoso.').

recomendacion('R03', 'F02',
    'Limpiar ventiladores internos y verificar que las salidas de aire no estén obstruidas por polvo.').

recomendacion('R04', 'F02',
    'Revisar que el pasta térmica del procesador no esté seca y reemplazarla si es necesario.').

recomendacion('R05', 'F03',
    'Realizar una copia de seguridad inmediata de los datos y ejecutar herramientas de diagnóstico como chkdsk o CrystalDiskInfo.').

recomendacion('R06', 'F03',
    'Considerar reemplazar el disco duro si la herramienta reporta sectores defectuosos graves.').

recomendacion('R07', 'F04',
    'Ejecutar la herramienta de reparación de inicio de Windows (sfc /scannow) o reinstalar el sistema operativo.').

recomendacion('R08', 'F05',
    'Verificar que el cable de alimentación esté correctamente conectado y probar con otra fuente de poder si es posible.').

recomendacion('R09', 'F06',
    'Actualizar o reinstalar los drivers de la tarjeta gráfica desde el sitio oficial del fabricante.').

recomendacion('R10', 'F07',
    'Ejecutar un análisis completo con el antivirus actualizado y considerar formatear el equipo si la infección es severa.').

recomendacion('R11', 'F08',
    'Actualizar los drivers de la tarjeta de red y verificar la configuración TCP/IP del sistema.').

recomendacion('R12', 'F09',
    'Usar un medio de instalación del sistema operativo para reparar el sector de arranque con bootrec /fixmbr.').

recomendacion('R13', 'F10',
    'Identificar el driver problemático en el Administrador de Dispositivos y actualizarlo o reinstalarlo.').

recomendacion('R14', 'F11',
    'Ejecutar chkdsk /f /r desde la consola de recuperación para corregir errores del sistema de archivos.').

recomendacion('R15', 'F12',
    'Verificar que el tomacorriente funcione, revisar el fusible de la fuente de poder y comprobar el cable de alimentación.').