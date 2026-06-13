okay tenia una parte de logica mal. entonces ayudame a restructurar el proyecto.

este es el proyecto:
"Resumen Ejecutivo
El proyecto Doctor Byte consiste en el desarrollo de un sistema experto orientado al
diagnóstico de fallas comunes en computadoras mediante el uso de técnicas fundamentales
de Inteligencia Artificial. La solución permitirá que un usuario seleccione una serie de
síntomas relacionados con el comportamiento de un equipo de cómputo y reciba un
diagnóstico junto con recomendaciones básicas para la posible solución del problema.
Para la implementación del sistema se utilizará Prolog como motor de inferencia,
aprovechando sus capacidades para representar conocimiento mediante hechos, reglas y
consultas. Adicionalmente, se desarrollará una interfaz web que facilite la interacción con el
usuario y un bot de Telegram que permite notificar los resultados obtenidos de manera
automática.
El proyecto busca que los estudiantes apliquen conceptos de lógica declarativa, sistemas
expertos e integración de tecnologías, fortaleciendo tanto sus conocimientos técnicos como
habilidades de trabajo colaborativo, análisis y resolución de problemas. Como resultado, se
obtendrá una herramienta funcional capaz de automatizar el proceso de diagnóstico
preliminar de fallas informáticas, simulando el comportamiento de un sistema experto
basado en reglas.
4. Enunciado del Proyecto
4.1 Descripción del problema o necesidad a resolver
El diagnóstico de fallas en computadoras suele requerir conocimientos técnicos
especializados para identificar correctamente las posibles causas de un problema. En
muchos casos, usuarios con poca experiencia informática desconocen cómo interpretar
síntomas como pantallas negras, reinicios inesperados, mensajes de error, lentitud del
sistema o problemas de arranque, lo que dificulta la toma de decisiones para resolver la
situación.

Ante esta necesidad, se propone el desarrollo de Doctor Byte, un sistema experto capaz de
analizar síntomas proporcionados por el usuario y generar un diagnóstico preliminar
acompañado de recomendaciones básicas. El sistema utilizará reglas de inferencia
implementadas en Prolog para simular el razonamiento de un experto en soporte técnico,
facilitando la identificación de posibles fallas de hardware o software de forma
automatizada
Alcance del proyecto
Alcance obligatorio:
El proyecto deberá incluir como mínimo los siguientes componentes:
● Desarrollo de una base de conocimiento en Prolog.
● Implementación de al menos 15 síntomas relacionados con fallas comunes
en computadoras.
● Implementación de al menos 10 fallas diagnosticables.
● Implementación de al menos 10 recomendaciones asociadas a las fallas
identificadas.
● Uso de hechos, reglas, variables, listas y al menos un corte (!) dentro de la
solución en Prolog.
● Desarrollo de una interfaz web que permita seleccionar síntomas y solicitar
un diagnóstico.
● Desarrollo de un backend con python que procese las solicitudes y se
comunique con el motor de inferencia en Prolog.
● Generación de diagnósticos basados en las reglas definidas.
● Integración con un bot de Telegram para enviar notificaciones de los
diagnósticos realizados.
● Documentación técnica básica del proyecto.
● Presentación funcional del sistema durante la evaluación.
● Historial de diagnósticos realizados
"




y funciona de la siguiente forma. te explico el flujo

entra un usuario y tiene una consulta de porque esta fallando su dispositivo (pc).


entonces le aparecen los los 20 sintomas en forma de boton puede seleccionar varios sintomas y en base a lo que selecione le dara un diagnostico y una recomendacion.


okay es asi de simple. y eso funcion porque tenemos escrito todos sintomas, recomendaciones y fallos. okay pero vamos a agregar una cosa

en la aplicacion puede existir un admin. 

que va ser el encargado de:
agregar fallos, recomendaciones y sintomas 


entonces funciona asi: viene un usuario y seleciona su sintoma algo como 

"
"id": "S08",
    "nombre": "Pantalla azul",
"descripcion": "El sistema operativo muestra errores críticos y se detiene."
"


entonces despues le da dianosticar y le da una diagnostico y una recomendacion.



puede selecionar varios sintomas pero solo si en la regla esta escrito con 2 o 3. o sea no todas las consultas con 2 o 3 sintomas van a retornar un diganostico seria complicado hacerle convinaciones a todos los sintomas. pero como nimo un sintoma si tiene que tener un diagnostico.

"Gestion de conocimiento 20
CRUD de síntomas 5
CRUD de fallas 5
CRUD de recomendaciones 5
Asociación síntomas ↔ fallas ↔
recomendaciones"

pero yo debo aplicar un CRUD o sea que aparte de poder hacer la parte de user normal tengo que poder crear y leer o borrar sintomas. fallas recomendacioens o sea se van a poder escribir reglas como asociar un fallo a un sintoma.

y todo  eso lo hace prolog 

entonces lo que necesito es que me ayudes a generar los archivos de prolog necesarios para poder completar esto.


o sea deben haber archvios de prolog en donde se ejecute las reglas, hechos y logica y archivos de prolog en donde se escriba la informacion y las reglas que creemos nuevas..


ayudame a generar esta logica en prolog ademas . vamos a utilizar esto pip install pyswip

dame el adapter
proyectos/p1/backend/app/adapter/prolog_adapter.py



```
prolog/
│
├── knowledge/
│   ├── rules.pl
│   ├── diagnoses.pl
│   └── helpers.pl
│
├── data/
│   ├── symptoms.pl
│   ├── failures.pl
│   └── recommendations.pl
│
└── engine.pl

```