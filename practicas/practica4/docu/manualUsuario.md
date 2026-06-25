A continuación se presenta el **Manual de Usuario en formato Markdown (.md)** redactado de manera formal, continua y estructurada en párrafos, incorporando la descripción conceptual de las “imágenes” o vistas de la interfaz según el diseño y el código proporcionado.

***

# RoboMaze — Manual de Usuario

## 1. Introducción

RoboMaze es una aplicación web interactiva orientada a la representación de laberintos y al análisis del comportamiento de algoritmos de búsqueda clásicos, específicamente Breadth-First Search (BFS) y Depth-First Search (DFS). El sistema permite al usuario construir, modificar o generar laberintos y observar visualmente cómo estos algoritmos recorren el espacio hasta encontrar —o no— una ruta entre un punto inicial y un destino.

La aplicación está diseñada para separar claramente la lógica de procesamiento (backend en Python con Flask) de la capa de visualización (frontend), permitiendo que el usuario interactúe exclusivamente con representaciones gráficas mientras los cálculos se ejecutan en el servidor.

***

## 2. Diseño Visual e Identidad de la Interfaz

La interfaz de RoboMaze adopta un estilo visual inspirado en entornos de terminal modernos, con predominio de tonos oscuros que facilitan la concentración en los elementos dinámicos del sistema. El fondo se presenta en negro o gris profundo, sobre el cual destacan acentos en verde eléctrico (#00FF88) y azul neón (#00C8FF).

El color verde eléctrico se utiliza para indicar la ruta final encontrada, mientras que el azul neón representa el proceso de exploración, particularmente asociado al comportamiento de BFS. Las paredes del laberinto se muestran en tonos grises, diferenciándose claramente de las celdas transitables.

![](./images/Captura%20de%20Pantalla%202026-06-24%20a%20la(s)%2023.03.06.png)

En cuanto a tipografía, se emplea una combinación funcional: JetBrains Mono para el grid y los datos técnicos, enfatizando el carácter estructurado y computacional del sistema, y la fuente Inter para los elementos de interfaz, textos explicativos y controles.

El elemento visual principal de la aplicación es el grid del laberinto, conceptualizado como un sistema dinámico que evoluciona en el tiempo. Este grid no es estático; su comportamiento incluye animaciones que representan la exploración celda por celda, simulando el proceso de toma de decisiones del algoritmo.
![](./images/Captura%20de%20Pantalla%202026-06-24%20a%20la(s)%2023.03.39.png)

***

## 3. Estructura General de la Interfaz

La interfaz principal se organiza en tres columnas claramente diferenciadas que estructuran la interacción del usuario:

* Panel izquierdo: configuración del laberinto
* Panel central: visualización del laberinto
* Panel derecho: ejecución de algoritmos y resultados


* Panel izquierdo: configuración del laberinto
![](./images/Captura%20de%20Pantalla%202026-06-24%20a%20la(s)%2023.22.55.png)


* Panel derecho: ejecución de algoritmos y resultados
![](./images/Captura%20de%20Pantalla%202026-06-24%20a%20la(s)%2023.24.02.png)

* Panel central: visualización del laberinto
![](./images/Captura%20de%20Pantalla%202026-06-24%20a%20la(s)%2023.07.25.png)

En la parte superior se encuentra un encabezado que identifica la aplicación y proporciona contexto sobre su funcionalidad. En conjunto, esta disposición permite una separación clara entre entrada de datos, visualización y resultados, facilitando la comprensión del flujo de uso.

***

## 4. Encabezado de la Aplicación

El encabezado presenta la identidad visual del sistema mediante el nombre RoboMaze acompañado de un ícono representativo. Debajo se incluye una breve descripción funcional que indica la capacidad del sistema para visualizar algoritmos BFS y DFS en laberintos.
![](./images/Captura%20de%20Pantalla%202026-06-24%20a%20la(s)%2023.07.45.png)

Además, se muestran indicadores visuales que resaltan las tecnologías principales involucradas, tales como los algoritmos BFS y DFS y la utilización de un backend en Python. Este encabezado cumple una función informativa y contextual, permitiendo al usuario comprender inmediatamente la finalidad de la herramienta.

***

## 5. Panel de Configuración

El panel ubicado en la columna izquierda permite al usuario definir las características del laberinto que se va a analizar. Este panel actúa como el punto de entrada para la creación y manipulación del entorno de búsqueda.

El usuario puede especificar el número de filas y columnas del grid, así como la densidad de paredes, lo cual influye directamente en la complejidad del laberinto. A partir de estos parámetros, el sistema ofrece la posibilidad de inicializar un grid vacío o generar automáticamente un laberinto que garantice la existencia de una ruta válida entre el punto inicial y el destino.
![](./images/Captura%20de%20Pantalla%202026-06-24%20a%20la(s)%2023.07.34.png)

Adicionalmente, el usuario puede eliminar todas las paredes existentes para reiniciar la configuración manual. El sistema también permite cargar laberintos predefinidos, los cuales representan escenarios diseñados para demostrar comportamientos específicos de los algoritmos, como caminos en zigzag, estructuras complejas o casos sin solución.

Visualmente, este panel se presenta como un conjunto de controles agrupados que permiten modificar el estado del sistema antes de la ejecución de los algoritmos.

***

## 6. Panel Central: Visualización del Laberinto

El panel central constituye el componente más importante del sistema, ya que en él se representa gráficamente el laberinto y se visualiza el comportamiento de los algoritmos.

El laberinto se muestra como una cuadrícula bidimensional donde cada celda representa un nodo del grafo. Las celdas libres, paredes, nodos explorados y ruta final se distinguen mediante colores específicos. El punto de inicio y el punto final se identifican mediante indicadores visuales claros que permiten reconocer rápidamente el objetivo del recorrido.

Sobre el grid se encuentra un encabezado que muestra las dimensiones actuales del laberinto. Cuando se ejecutan ambos algoritmos simultáneamente, se indica que la visualización corresponde a BFS, mientras que los resultados de DFS se presentan en el panel lateral.

Debajo del encabezado se encuentra una barra de herramientas que permite interactuar directamente con el grid. A través de esta barra, el usuario puede cambiar el modo de interacción para dibujar paredes, establecer el punto inicial o definir el destino.

El comportamiento dinámico del grid constituye la principal “imagen” funcional del sistema. Durante la ejecución de un algoritmo, las celdas se activan secuencialmente mostrando la exploración. Este proceso permite observar cómo BFS expande su búsqueda en capas, mientras que DFS profundiza en caminos individuales antes de retroceder.

Debajo del grid se presenta una representación textual de la ruta encontrada, expresada como una secuencia de coordenadas que describen el recorrido desde el inicio hasta el destino.

***

## 7. Panel de Algoritmos y Resultados

El panel derecho está dedicado a la ejecución de los algoritmos y la visualización de sus resultados. En este panel, el usuario puede seleccionar entre ejecutar BFS, DFS o ambos algoritmos de forma simultánea.

Cada ejecución produce un conjunto de métricas que incluyen el número de nodos explorados, la longitud de la ruta encontrada y el tiempo de ejecución. Estos valores permiten evaluar el desempeño de cada algoritmo en función del laberinto analizado.

![](./images/Captura%20de%20Pantalla%202026-06-24%20a%20la(s)%2023.09.03.png)

Cuando se ejecutan ambos algoritmos, el sistema presenta una comparación estructurada que indica cuál fue más rápido, cuál exploró menos nodos y cuál produjo la ruta más corta, si aplica. Esta comparación facilita el análisis diferencial entre BFS y DFS.

El panel también incluye opciones para exportar los resultados en formatos CSV y PDF, lo que permite conservar evidencia del análisis realizado o utilizarla en reportes externos.

***

## 8. Sistema de Notificaciones

El sistema incorpora un mecanismo de notificaciones que informa al usuario cuando ocurre un error o una situación excepcional. Estas notificaciones aparecen en la interfaz mediante un componente temporal que muestra mensajes relacionados con problemas de validación, ausencia de rutas o errores en la comunicación con el backend.

![](./images/Captura%20de%20Pantalla%202026-06-24%20a%20la(s)%2023.08.31.png)
![](./images/Captura%20de%20Pantalla%202026-06-24%20a%20la(s)%2023.08.36.png)

Este componente asegura que el usuario reciba retroalimentación inmediata sin interrumpir el flujo principal de interacción.

***

## 9. Flujo de Uso

El uso típico de la aplicación inicia con la configuración del laberinto mediante el panel izquierdo. El usuario puede optar por cargar un laberinto predefinido, generar uno automáticamente o construirlo manualmente.

Una vez definido el entorno, el usuario procede a ejecutar uno o ambos algoritmos desde el panel derecho. El proceso de exploración se visualiza en el panel central, permitiendo observar el comportamiento interno del algoritmo.

Finalmente, el usuario puede analizar los resultados, compararlos y exportarlos si es necesario.

***

## 10. Consideraciones Finales

RoboMaze integra de manera coherente la visualización interactiva con algoritmos clásicos de teoría de grafos. Su diseño centrado en el grid como elemento dinámico permite representar no solo los resultados, sino también el proceso interno de exploración.

La interfaz modular facilita la comprensión del sistema, separando la configuración, la visualización y los resultados en espacios claramente definidos. Esto convierte a RoboMaze en una herramienta adecuada tanto para aprendizaje como para análisis comparativo de algoritmos de búsqueda.

![](./images/Captura%20de%20Pantalla%202026-06-24%20a%20la(s)%2023.21.32.png)
![](./images/Captura%20de%20Pantalla%202026-06-24%20a%20la(s)%2023.21.44.png)
