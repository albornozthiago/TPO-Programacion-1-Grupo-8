# Batalla Naval 3D - "Operación Cubo" - Trabajo Práctico Integrador · Programación 1

Repositorio del equipo 8, correspondiente al desarrollo del Trabajo Práctico Integrador para la materia Programación 1, UADE 2026.

## Integrantes:

- Albornoz, Thiago Agustin
- Lesme Garcia, Franco Agustin
- Sanchez De Bock, Ignacio Tomas 
- Sarniguette, Valentino
- Trezeguet, Gaston
- Zaccari, Valentin Angel

## Responsables a cargo:

- Rosio, Nicolas
- Guzman, Gustavo Damian Fernando

## Instalación

Requisitos: Python 3.10 o superior.

```bash
git clone https://github.com/albornozthiago/Batalla-Naval-3D
cd Batalla-Naval-3D
pip install -r requirements.txt
```

El único paquete externo es `pytest`, que se usa para las pruebas. El juego en sí usa solo la biblioteca estándar.

## Ejecución

Desde la carpeta del proyecto:

```bash
python partida.py
```

Para correr las pruebas:

```bash
pytest
```

Las rutas son relativas a la carpeta del proyecto, así que hay que ejecutar los comandos desde ahí.

## Menús

Todo se elige de una lista de opciones o se responde a una pregunta. Un dato inválido nunca corta el programa: se avisa y se vuelve a preguntar.

### Menú principal

| Opción | Qué hace |
|---|---|
| 1 - Partida uno contra uno | Dos jugadores humanos. Cada uno ubica su flota y se alternan los turnos. |
| 2 - Partida uno contra la máquina | Un jugador contra la máquina. Se elige el nivel de la máquina. |
| 3 - Partida máquina contra máquina | Dos máquinas juegan solas. Se elige el nivel de cada una. |
| 4 - Continuar una partida guardada | Lista las partidas de `datos/partidas/` y retoma la elegida. |
| 5 - Salir | Termina el programa. |

### Ubicación de la flota

Cada jugador humano elige entre ubicación manual o automática. En la manual se indica la nave por su letra (F, D, S, C, P, E) y el tramo con los dos extremos unidos por un guión, por ejemplo `3,5,4-3,5,5`. La máquina siempre ubica su flota de forma automática.

### Turno

| Opción | Qué hace |
|---|---|
| 1 - Disparar | Pide el arma (T, R, C, S, L, O, G) y el objetivo `z,x,y`. El sonar pide un eje y un valor de plano. |
| 2 - Ver el cubo | Muestra la flota y el cubo propio, capa por capa. |
| 3 - Guardar y salir | Guarda la partida con el nombre elegido y vuelve al menú principal. |
| 4 - Radar | Abre el menú de radar. |

### Armas

| Letra | Arma |
|---|---|
| T | Torpedo |
| R | Misil de racimo |
| C | Carga de profundidad |
| S | Sonar (muestra los contactos de un plano y sus coordenadas) |
| L | Barrido láser |
| O | Onda expansiva |
| G | Torpedo guiado |

### Radar

Trabaja sobre lo que el jugador sabe del cubo rival. Los contactos que detectó el sonar se marcan con `?`.

| Opción | Qué hace |
|---|---|
| 1 - Comparar las tres búsquedas | Busca el primer contacto con la búsqueda lineal, la optimizada y la recursiva, y muestra las métricas de cada una (comparaciones, tiempo y profundidad máxima). |
| 2 - Recorrer el cubo | Recorre el cubo por capas, en espiral, desde un punto o por octantes, e indica en qué orden aparecen los contactos. |
| 3 - Ver lo que sé del cubo rival | Dibuja el cubo rival capa por capa con lo descubierto hasta ahora. |
| 4 - Volver | Vuelve al turno. |

### Niveles de la máquina

- **Básica:** dispara a un punto al azar entre los que no probó.
- **Avanzada:** si hay un impacto sin hundir, dispara a una celda pegada a ese impacto. Si no, dispara a la celda más probable según el mapa de probabilidad de `radar.py`.

### Final de la partida

Al terminar se muestra el ganador, el historial de disparos, el resumen con las estadísticas de cada jugador y el ranking. Después se ofrece exportar el resumen a un archivo de texto.

## Archivos que genera el programa

| Ruta | Contenido |
|---|---|
| `datos/partidas/` | Partidas guardadas, una por archivo `.json`. |
| `datos/ranking.json` | Partidas jugadas y victorias de cada jugador. |
| `datos/exportaciones/` | Resúmenes exportados, uno por archivo `.txt`. |

Los nombres de partida admiten letras, números, guion y guion bajo, hasta 30 caracteres.

## Estructura del proyecto

| Módulo | Responsabilidad |
|---|---|
| `tablero.py` | Cubo, validación de puntos, planos, vecinos y recorridos. |
| `flota.py` | Catálogo de naves, ubicación, impactos, datos para guardar y reponer la flota. |
| `armamento.py` | Catálogo de armas, efecto de cada una y munición. |
| `radar.py` | Búsquedas con métricas, sonar por planos, recorridos recursivos y mapa de probabilidad. |
| `registro.py` | Historial, estadísticas, guardado y carga en JSON, ranking y exportación. |
| `partida.py` | Menús, ciclo de turnos, los tres formatos de partida y excepciones propias. |
| `tests/` | Pruebas con pytest de cada módulo. |
| `docs/bitacora.md` | Registro del trabajo de cada integrante por entrega. |
