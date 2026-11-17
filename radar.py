import time

import tablero


def armar_metricas(comparaciones, inicio, profundidad_max=0):
    """Objetivo: armar el diccionario de metricas que pide la consigna.
    Parametros:
        comparaciones (int): cantidad de celdas comparadas en la busqueda
        inicio (float): instante de comienzo, tomado con time.time()
        profundidad_max (int): profundidad maxima de recursion alcanzada.
            Vale 0 (por defecto) en las busquedas que no son recursivas.
    Retorna:
        dict: {"comparaciones": int, "tiempo_ms": float, "profundidad_max": int}.
    Excepciones: no lanza ninguna."""
    fin = time.time()
    tiempo_ms = round((fin - inicio) * 1000, 4)
    return {
        "comparaciones": comparaciones,
        "tiempo_ms": tiempo_ms,
        "profundidad_max": profundidad_max,
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


# ---------------------------------------------------------------------------
# Entrega 3: busqueda recursiva, recorridos recursivos y mapa de probabilidad
# ---------------------------------------------------------------------------

DESCARTADAS = [tablero.AGUA_MARCADA, tablero.HUNDIDO]
LARGOS_DEFECTO = [2, 3, 4, 5]


def _buscar_en_capa(cubo, objetivo, z, contador):
    """Objetivo: revisar una sola capa z del cubo, celda por celda.
    Es el caso base de la busqueda recursiva.
    Parametros:
        cubo (list): el cubo de juego
        objetivo (str): estado de celda a buscar
        z (int): indice de la capa, desde 0
        contador (dict): {"comparaciones": int}, se actualiza en el lugar
    Retorna:
        tuple: punto (z, x, y) desde 1, o None si no esta en la capa.
    Excepciones: no lanza ninguna."""
    n = len(cubo)
    for x in range(n):
        for y in range(n):
            contador["comparaciones"] = contador["comparaciones"] + 1
            if cubo[z][x][y] == objetivo:
                return (z + 1, x + 1, y + 1)
    return None


def _buscar_rango(cubo, objetivo, z_desde, z_hasta, profundidad, contador):
    """Objetivo: buscar el objetivo entre las capas z_desde y z_hasta
    (incluidas) partiendo el rango a la mitad en cada llamada
    (divide y conquista).
    Caso base: el rango tiene una sola capa, y se revisa con _buscar_en_capa
    (o el rango esta vacio, por ejemplo con un cubo sin capas, y devuelve None).
    Caso recursivo: se busca en la mitad de abajo y, si no aparece,
    en la mitad de arriba.
    Parametros:
        cubo (list): el cubo de juego
        objetivo (str): estado de celda a buscar
        z_desde (int): primera capa del rango, desde 0
        z_hasta (int): ultima capa del rango, desde 0
        profundidad (int): profundidad de esta llamada (la primera es 1)
        contador (dict): {"comparaciones": int, "profundidad_max": int},
            se actualiza en el lugar
    Retorna:
        tuple: punto (z, x, y) desde 1, o None si no esta en el rango.
    Excepciones: no lanza ninguna."""
    if z_desde > z_hasta:
        return None

    contador["profundidad_max"] = max(contador["profundidad_max"], profundidad)

    if z_desde == z_hasta:
        return _buscar_en_capa(cubo, objetivo, z_desde, contador)

    medio = (z_desde + z_hasta) // 2
    encontrado = _buscar_rango(cubo, objetivo, z_desde, medio, profundidad + 1, contador)
    if encontrado is not None:
        return encontrado
    return _buscar_rango(cubo, objetivo, medio + 1, z_hasta, profundidad + 1, contador)


def busqueda_recursiva(cubo, objetivo=tablero.NAVE_OCULTA):
    """Objetivo: encontrar la primera celda con el estado buscado usando
    recursion: parte el cubo por capas de z a la mitad hasta llegar a una
    sola capa, que revisa celda por celda.
    Parametros:
        cubo (list): el cubo de juego
        objetivo (str): estado de celda a buscar, por defecto una nave oculta
    Retorna:
        tuple: (punto, metricas). punto es (z, x, y) desde 1, o None si
        el objetivo no esta en el cubo. metricas es el dict de armar_metricas,
        con la profundidad maxima real de la recursion.
    Excepciones: no lanza ninguna."""
    inicio = time.time()
    contador = {"comparaciones": 0, "profundidad_max": 0}
    punto = _buscar_rango(cubo, objetivo, 0, len(cubo) - 1, 1, contador)
    metricas = armar_metricas(
        contador["comparaciones"], inicio, contador["profundidad_max"]
    )
    return punto, metricas


def _todos_los_puntos(cubo):
    """Objetivo: listar todas las celdas del cubo en orden z, x, y.
    Es una ayuda interna para el mapa de probabilidad (no es un recorrido
    del menu: los recorridos de tablero.py ya cubren el orden por capas).
    Parametros:
        cubo (list): el cubo de juego
    Retorna:
        list: puntos (z, x, y) desde 1. Lista vacia si el cubo no tiene capas.
    Excepciones: no lanza ninguna."""
    n = len(cubo)
    puntos = []
    for z in range(1, n + 1):
        for x in range(1, n + 1):
            for y in range(1, n + 1):
                puntos.append((z, x, y))
    return puntos


def _mitades(desde, hasta):
    """Objetivo: partir un rango de coordenadas en dos mitades.
    Parametros:
        desde (int): primer valor del rango
        hasta (int): ultimo valor del rango
    Retorna:
        list: lista de rangos (desde, hasta). Si el rango tiene un solo
        valor, devuelve solo ese rango.
    Excepciones: no lanza ninguna."""
    if desde == hasta:
        return [(desde, hasta)]
    medio = (desde + hasta) // 2
    return [(desde, medio), (medio + 1, hasta)]


def _octantes(rango_z, rango_x, rango_y):
    """Objetivo: recorrer recursivamente un bloque del cubo partiendolo en
    octantes (hasta 8 bloques mas chicos: mitad en z, en x y en y).
    Caso base: el bloque esta vacio (devuelve []) o es una sola celda
    (devuelve esa celda).
    Caso recursivo: recorre cada octante, uno despues del otro.
    Parametros:
        rango_z, rango_x, rango_y (tuple): (desde, hasta) de cada eje, desde 1
    Retorna:
        list: puntos (z, x, y) del bloque en el orden del recorrido.
    Excepciones: no lanza ninguna."""
    if rango_z[0] > rango_z[1] or rango_x[0] > rango_x[1] or rango_y[0] > rango_y[1]:
        return []
    if rango_z[0] == rango_z[1] and rango_x[0] == rango_x[1] and rango_y[0] == rango_y[1]:
        return [(rango_z[0], rango_x[0], rango_y[0])]
    puntos = []
    for sub_z in _mitades(rango_z[0], rango_z[1]):
        for sub_x in _mitades(rango_x[0], rango_x[1]):
            for sub_y in _mitades(rango_y[0], rango_y[1]):
                puntos = puntos + _octantes(sub_z, sub_x, sub_y)
    return puntos


def recorrido_por_octantes(cubo):
    """Objetivo: recorrer el cubo por octantes, en forma recursiva.
    Parte el cubo en 8 cubos mas chicos (mitad de abajo y de arriba en cada
    eje), cada uno en 8 mas, y asi hasta llegar a celdas sueltas. Termina de
    recorrer un octante entero antes de pasar al siguiente.
    Parametros:
        cubo (list): el cubo de juego
    Retorna:
        list: puntos (z, x, y) desde 1 en el orden del recorrido. Lista vacia
        si el cubo no tiene capas.
    Excepciones: no lanza ninguna."""
    n = len(cubo)
    return _octantes((1, n), (1, n), (1, n))


# Adaptadores: todos los recorridos del diccionario reciben (cubo, inicio).
# Los de tablero.py son de Nacho y se usan tal como estan.

def _recorrido_capas(cubo, _inicio):
    """Adaptador de tablero.recorrido_por_capas (no usa el punto de inicio)."""
    return tablero.recorrido_por_capas(cubo)


def _recorrido_espiral(cubo, _inicio):
    """Adaptador de tablero.recorrido_espiral (no usa el punto de inicio)."""
    return tablero.recorrido_espiral(cubo)


def _recorrido_desde_punto(cubo, inicio):
    """Adaptador de tablero.recorrido_desde_punto (arranca en inicio)."""
    return tablero.recorrido_desde_punto(cubo, inicio)


def _recorrido_octantes(cubo, _inicio):
    """Adaptador de recorrido_por_octantes (no usa el punto de inicio)."""
    return recorrido_por_octantes(cubo)


RECORRIDOS = {
    "capas": _recorrido_capas,
    "espiral": _recorrido_espiral,
    "desde un punto": _recorrido_desde_punto,
    "octantes": _recorrido_octantes,
}


def recorrer(cubo, nombre, inicio=(1, 1, 1)):
    """Objetivo: ejecutar un recorrido elegido por nombre, usando el
    diccionario RECORRIDOS (sin cadenas de if / elif). Reune los recorridos
    de tablero.py (capas, espiral y desde un punto) y el de radar.py
    (octantes), y los devuelve todos con el mismo formato.
    Parametros:
        cubo (list): el cubo de juego
        nombre (str): "capas", "espiral", "desde un punto" u "octantes"
        inicio (tuple): punto (z, x, y) desde 1; solo lo usa "desde un punto"
    Retorna:
        list: puntos como tuplas (z, x, y) en el orden del recorrido, o None
        si el recorrido no pudo hacerse (punto de inicio invalido).
    Excepciones:
        KeyError si el nombre no esta en RECORRIDOS."""
    puntos = RECORRIDOS[nombre](cubo, inicio)
    if puntos is None:
        return None
    resultado = []
    for punto in puntos:
        resultado.append(tuple(punto))
    return resultado


def _tramo_posible(cubo, punto, eje, largo):
    """Objetivo: decidir si una nave recta de cierto largo puede ocupar el
    tramo que empieza en punto y avanza por un eje.
    Parametros:
        cubo (list): el cubo de juego, visto por quien dispara
        punto (tuple): punto (z, x, y) desde 1 donde empieza el tramo
        eje (int): 0 para z, 1 para x, 2 para y
        largo (int): cantidad de celdas de la nave
    Retorna:
        list: los puntos del tramo si la nave entra, o None si se sale del
        cubo o pasa por una celda descartada (agua marcada o hundido).
    Excepciones: no lanza ninguna."""
    tramo = []
    for paso in range(largo):
        actual = list(punto)
        actual[eje] = actual[eje] + paso
        actual = tuple(actual)
        if not tablero.punto_valido(cubo, actual):
            return None
        if tablero.leer_celda(cubo, actual) in DESCARTADAS:
            return None
        tramo.append(actual)
    return tramo


def mapa_de_probabilidad(cubo, largos=None):
    """Objetivo: estimar en que celdas es mas probable que haya una nave.
    Para cada largo de nave y cada eje, prueba todas las posiciones rectas
    posibles; cada posicion que entra suma 1 a cada celda que ocupa.
    Una celda con mas puntos es una celda por donde pueden pasar mas naves.
    Parametros:
        cubo (list): el cubo de juego, visto por quien dispara
        largos (list): largos de nave a considerar. Si es None (por defecto)
            usa LARGOS_DEFECTO: 2, 3, 4 y 5
    Retorna:
        list: matriz N x N x N de enteros (mismos indices que el cubo).
            Las celdas descartadas quedan en 0.
    Excepciones: no lanza ninguna."""
    if largos is None:
        largos = LARGOS_DEFECTO
    puntos = _todos_los_puntos(cubo)
    n = len(cubo)
    mapa = tablero.crear_cubo(n)
    for z in range(n):
        for x in range(n):
            for y in range(n):
                mapa[z][x][y] = 0

    for largo in largos:
        for eje in range(3):
            for punto in puntos:
                tramo = _tramo_posible(cubo, punto, eje, largo)
                if tramo is not None:
                    for celda in tramo:
                        z, x, y = celda[0] - 1, celda[1] - 1, celda[2] - 1
                        mapa[z][x][y] = mapa[z][x][y] + 1
    return mapa


def celda_mas_probable(cubo, mapa):
    """Objetivo: elegir la celda sin explorar con mas puntos en el mapa de
    probabilidad (sirve, por ejemplo, para el nivel dificil de la maquina).
    Parametros:
        cubo (list): el cubo de juego, visto por quien dispara
        mapa (list): matriz devuelta por mapa_de_probabilidad
    Retorna:
        tuple: punto (z, x, y) desde 1 con mas puntos, o None si no queda
        ninguna celda sin explorar. Si hay empate, la primera en orden z, x, y.
    Excepciones: no lanza ninguna."""
    sin_disparar = [tablero.AGUA_SIN_EXPLORAR, tablero.NAVE_OCULTA, tablero.DETECTADO]
    puntos = _todos_los_puntos(cubo)
    mejor = None
    mejor_valor = -1
    for punto in puntos:
        z, x, y = punto[0] - 1, punto[1] - 1, punto[2] - 1
        if cubo[z][x][y] in sin_disparar and mapa[z][x][y] > mejor_valor:
            mejor = punto
            mejor_valor = mapa[z][x][y]
    return mejor
