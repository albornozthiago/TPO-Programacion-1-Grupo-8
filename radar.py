import time
import tablero


def armar_metricas(comparaciones, inicio):
    """Objetivo: armar el diccionario de metricas que pide la consigna.
    """
    fin = time.time()
    tiempo_ms = round((fin - inicio) * 1000, 4)
    return {"comparaciones": comparaciones, "tiempo_ms": tiempo_ms, "profundidad_max": 0}



def busqueda_lineal(cubo):
    """Objetivo: encontrar la primera celda con una nave oculta,
    recorriendo el cubo celda por celda con for anidados.
    """
    comparaciones = 0
    inicio = time.time()
    n = len(cubo)

    for z in range(0, n):
        for x in range(0, n):
            for y in range(0, n):
                comparaciones = comparaciones + 1
                if cubo[z][x][y] == tablero.naveoculta:
                    return [z + 1, x + 1, y + 1], armar_metricas(comparaciones, inicio)

    return None, armar_metricas(comparaciones, inicio)




def busqueda_optimizada(cubo):
    """Objetivo: encontrar la primera celda con una nave oculta
    revisando primero solo la mitad de las celdas (patron de ajedrez).
    """
    comparaciones = 0
    inicio = time.time()
    n = len(cubo)

    for paridad in range(0, 2):          
        for z in range(0, n):
            for x in range(0, n):
                for y in range(0, n):
                    if (z + x + y) % 2 == paridad:
                        comparaciones = comparaciones + 1
                        if cubo[z][x][y] == tablero.naveoculta:
                            return [z + 1, x + 1, y + 1], armar_metricas(comparaciones, inicio)

    return None, armar_metricas(comparaciones, inicio)




def puntos_del_plano(cubo, eje, valor):
    """Objetivo: armar la lista de todos los puntos de un plano del cubo.
    Ejemplo: eje "z" y valor 3 devuelve todos los puntos [3, x, y].
    Parametros:
        cubo (list): el cubo de juego
        eje (str): "z", "x" o "y"
        valor (int): valor fijo del eje, desde 1 hasta N
    Retorna:
        list: lista de puntos [z, x, y], o None si el eje o el valor no son validos"""
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
            puntos.append(punto)
    return puntos


def sonar_plano(cubo, eje, valor):
    """Objetivo: revisar un plano entero del cubo y devolver donde hay naves.
    No hace dano y no modifica el cubo.
    """
    puntos = puntos_del_plano(cubo, eje, valor)
    if puntos is None:
        return None

    contactos = []
    for punto in puntos:
        if tablero.leer_celda(cubo, punto) == tablero.naveoculta:
            contactos.append(punto)
    return contactos