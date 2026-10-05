import time

import tablero


POSICION_EJE = {"z": 0, "x": 1, "y": 2}


def crear_metricas():
    """
    Crea el diccionario de métricas vacío que devuelven las búsquedas.

    Devuelve:
        Diccionario con comparaciones, tiempo_ms y profundidad_max en 0.
    """
    return {"comparaciones": 0, "tiempo_ms": 0.0, "profundidad_max": 0}


def calcular_tiempo_ms(inicio):
    """
    Calcula cuántos milisegundos pasaron desde un momento de inicio.

    Recibe:
        inicio: valor devuelto por time.perf_counter() al empezar.

    Devuelve:
        Milisegundos transcurridos, redondeados a 4 decimales.
    """
    return round((time.perf_counter() - inicio) * 1000, 4)



def busqueda_lineal(cubo, objetivo=tablero.NAVE_OCULTA):
    """
    Busca la primera celda del cubo que tenga el estado objetivo,
    recorriendo celda por celda con for anidados y sin estructura auxiliar.

    Orden del recorrido: capa z, luego x, luego y.

    Recibe:
        cubo: cubo de juego (lista de listas de listas).
        objetivo: estado a buscar. Por defecto, tablero.NAVE_OCULTA.

    Devuelve:
        Una tupla (punto, metricas):
            punto: (z, x, y) empezando desde 1, o None si no lo encontró.
            metricas: {"comparaciones", "tiempo_ms", "profundidad_max"}.
    """
    metricas = crear_metricas()
    inicio = time.perf_counter()
    n = tablero.tamanio_cubo(cubo)

    for z in range(n):
        for x in range(n):
            for y in range(n):
                metricas["comparaciones"] += 1
                if cubo[z][x][y] == objetivo:
                    metricas["tiempo_ms"] = calcular_tiempo_ms(inicio)
                    return (z + 1, x + 1, y + 1), metricas

    metricas["tiempo_ms"] = calcular_tiempo_ms(inicio)
    return None, metricas
    

def busqueda_optimizada(cubo, objetivo=tablero.NAVE_OCULTA):
    """
    Busca la primera celda con el estado objetivo usando paridad
    (patrón de "tablero de ajedrez" en 3D).

    Justificación:
        Toda nave ocupa al menos 2 celdas contiguas sobre un eje.
        Dos celdas vecinas siempre tienen distinta paridad de (z + x + y),
        así que toda nave tiene por lo menos una celda "par".
        Entonces, revisando solo las celdas pares se encuentra cualquier
        nave mirando como máximo la mitad del cubo (N³/2 celdas en vez de N³).
        Si en las celdas pares no aparece, se revisan las impares, así la
        búsqueda sigue siendo correcta para cualquier otro objetivo.

    Recibe:
        cubo: cubo de juego.
        objetivo: estado a buscar. Por defecto, tablero.NAVE_OCULTA.

    Devuelve:
        Una tupla (punto, metricas), igual que busqueda_lineal.
    """
    metricas = crear_metricas()
    inicio = time.perf_counter()
    n = tablero.tamanio_cubo(cubo)

    for paridad in (0, 1):
        for z in range(n):
            for x in range(n):
                # Arranca en el primer y que cumple la paridad y salta de a 2
                for y in range((z + x + paridad) % 2, n, 2):
                    metricas["comparaciones"] += 1
                    if cubo[z][x][y] == objetivo:
                        metricas["tiempo_ms"] = calcular_tiempo_ms(inicio)
                        return (z + 1, x + 1, y + 1), metricas

    metricas["tiempo_ms"] = calcular_tiempo_ms(inicio)
    return None, metricas


def puntos_del_plano(cubo, eje, valor):
    """
    Genera todos los puntos de un plano del cubo fijando un eje.

    Recibe:
        cubo: cubo de juego.
        eje: "z", "x" o "y".
        valor: valor fijo del eje, desde 1 hasta N.

    Devuelve:
        Lista de puntos (z, x, y), o None si el eje o el valor no son válidos.
    """
    if eje not in POSICION_EJE:
        return None
    n = tablero.tamanio_cubo(cubo)
    if valor < 1 or valor > n:
        return None

    posicion = POSICION_EJE[eje]
    puntos = []
    for a in range(1, n + 1):
        for b in range(1, n + 1):
            punto = [a, b]
            punto.insert(posicion, valor)
            puntos.append(tuple(punto))
    return puntos


def sonar_plano(cubo, eje, valor):
    """
    Revisa un plano entero del cubo y devuelve los contactos detectados.
    No produce daño y no modifica el cubo.

    Recibe:
        cubo: cubo de juego.
        eje: "z", "x" o "y".
        valor: valor fijo del eje, desde 1 hasta N.

    Devuelve:
        Lista de puntos (z, x, y) donde hay una nave oculta.
        Devuelve None si el eje o el valor no son válidos.
    """
    puntos = puntos_del_plano(cubo, eje, valor)
    if puntos is None:
        return None

    contactos = []
    for punto in puntos:
        if tablero.leer_celda(cubo, punto) == tablero.NAVE_OCULTA:
            contactos.append(punto)
    return contactos