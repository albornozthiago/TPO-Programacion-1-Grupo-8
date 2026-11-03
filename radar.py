import time

import tablero


def armar_metricas(comparaciones, inicio):
    """Objetivo: armar el diccionario de metricas que pide la consigna.
    Parametros:
        comparaciones (int): cantidad de celdas comparadas en la busqueda
        inicio (float): instante de comienzo, tomado con time.time()
    Retorna:
        dict: {"comparaciones": int, "tiempo_ms": float, "profundidad_max": int}.
        profundidad_max vale 0 porque estas busquedas no son recursivas.
    Excepciones: no lanza ninguna."""
    fin = time.time()
    tiempo_ms = round((fin - inicio) * 1000, 4)
    return {
        "comparaciones": comparaciones,
        "tiempo_ms": tiempo_ms,
        "profundidad_max": 0,
    }


def busqueda_lineal(cubo, objetivo=tablero.NAVE_OCULTA):
    """Objetivo: encontrar la primera celda con el estado buscado,
    recorriendo el cubo celda por celda con for anidados.
    Parametros:
        cubo (list): el cubo de juego
        objetivo (str): estado de celda a buscar, por defecto una nave oculta
    Retorna:
        tuple: (punto, metricas). punto es (z, x, y) desde 1, o None si
        el objetivo no esta en el cubo. metricas es el dict de armar_metricas.
    Excepciones: no lanza ninguna."""
    comparaciones = 0
    inicio = time.time()
    n = len(cubo)

    for z in range(n):
        for x in range(n):
            for y in range(n):
                comparaciones = comparaciones + 1
                if cubo[z][x][y] == objetivo:
                    return (z + 1, x + 1, y + 1), armar_metricas(comparaciones, inicio)

    return None, armar_metricas(comparaciones, inicio)


def busqueda_optimizada(cubo, objetivo=tablero.NAVE_OCULTA):
    """Objetivo: encontrar la primera celda con el estado buscado
    revisando primero solo la mitad de las celdas (patron de ajedrez).
    Toda nave mide al menos 2 celdas contiguas, que siempre tienen paridad
    distinta en z + x + y, asi que la primera pasada ya detecta cualquier nave.
    Parametros:
        cubo (list): el cubo de juego
        objetivo (str): estado de celda a buscar, por defecto una nave oculta
    Retorna:
        tuple: (punto, metricas). punto es (z, x, y) desde 1, o None si
        el objetivo no esta en el cubo. metricas es el dict de armar_metricas.
    Excepciones: no lanza ninguna."""
    comparaciones = 0
    inicio = time.time()
    n = len(cubo)

    for paridad in range(2):
        for z in range(n):
            for x in range(n):
                for y in range((z + x + paridad) % 2, n, 2):
                    comparaciones = comparaciones + 1
                    if cubo[z][x][y] == objetivo:
                        return (z + 1, x + 1, y + 1), armar_metricas(
                            comparaciones, inicio
                        )

    return None, armar_metricas(comparaciones, inicio)


def puntos_del_plano(cubo, eje, valor):
    """Objetivo: armar la lista de todos los puntos de un plano del cubo.
    Ejemplo: eje "z" y valor 3 devuelve todos los puntos (3, x, y).
    Parametros:
        cubo (list): el cubo de juego
        eje (str): "z", "x" o "y"
        valor (int): valor fijo del eje, desde 1 hasta N
    Retorna:
        list: lista de puntos (z, x, y), o None si el eje o el valor no son validos
    Excepciones: no lanza ninguna."""
    ejes = ["z", "x", "y"]
    n = len(cubo)
    if eje not in ejes:
        return None
    if valor < 1 or valor > n:
        return None

    posicion = ejes.index(eje)
    puntos = []
    for a in range(1, n + 1):
        for b in range(1, n + 1):
            punto = [a, b]
            punto.insert(posicion, valor)
            puntos.append(tuple(punto))
    return puntos


def sonar_plano(cubo, eje, valor):
    """Objetivo: revisar un plano entero del cubo y devolver donde hay naves.
    No hace dano y no modifica el cubo.
    Parametros:
        cubo (list): el cubo de juego
        eje (str): "z", "x" o "y"
        valor (int): valor fijo del eje, desde 1 hasta N
    Retorna:
        list: puntos (z, x, y) del plano que contienen una nave oculta
        (lista vacia si no hay), o None si el eje o el valor no son validos
    Excepciones: no lanza ninguna."""
    puntos = puntos_del_plano(cubo, eje, valor)
    if puntos is None:
        return None

    contactos = []
    for punto in puntos:
        if tablero.leer_celda(cubo, punto) == tablero.NAVE_OCULTA:
            contactos.append(punto)
    return contactos
