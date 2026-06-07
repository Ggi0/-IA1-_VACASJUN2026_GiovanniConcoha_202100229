
% CIUDADES


ciudad(guatemala).
ciudad(antigua).
ciudad(peten).
ciudad(escuintla).
ciudad(xela).
ciudad(jalapa).
ciudad(chiquimula).
ciudad(huehuetenango).
ciudad(suchitepequez).
ciudad(san_marcos).


% CONEXIONES


conexion(guatemala, antigua, 45).
conexion(antigua, peten, 300).

conexion(guatemala, escuintla, 60).
conexion(escuintla, xela, 120).

conexion(xela, huehuetenango, 90).
conexion(huehuetenango, san_marcos, 80).

conexion(guatemala, jalapa, 150).
conexion(jalapa, chiquimula, 100).

conexion(chiquimula, peten, 350).

conexion(suchitepequez, escuintla, 70).
ciudad(quiche).
conexion(guatemala,quiche,300).