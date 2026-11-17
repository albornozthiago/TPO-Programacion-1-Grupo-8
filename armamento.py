import tablero
import flota as modulo_flota
import radar

# Catálogo de armas
catalogo_armas = {
    "T": {"nombre": "Torpedo", "municion": None},
    "R": {"nombre": "Misil de racimo", "municion": 3},
    "C": {"nombre": "Carga de profundidad", "municion": 2},
    "S": {"nombre": "Sonar", "municion": 4},
    "L": {"nombre": "Barrido laser", "municion": 2},
    "O": {"nombre": "Onda expansiva", "municion": 1},
    "G": {"nombre": "Torpedo guiado", "municion": 1}
}

def obtener_arma(codigo):
    """
    Recibe el código de un arma y devuelve su información.
    Si el código no existe, devuelve None.
    """
    return catalogo_armas.get(codigo)

def crear_municion():
    """
    Crea un diccionario con la municion inicial
    de todas las armas para un jugador.
    """
    municion = {}

    for codigo, datos in catalogo_armas.items():
        municion[codigo] = datos["municion"]

    return municion

def torpedo(cubo, punto, flota_jugador=None):
    """
    Recibe el cubo y el punto al que se dispara.
    Devuelve el resultado del disparo y modifica la celda correspondiente.
    """

    if not tablero.punto_valido(cubo, punto):
        return "Punto invalido"

    celda = tablero.leer_celda(cubo, punto)

    if celda == tablero.AGUA_SIN_EXPLORAR or celda == tablero.DETECTADO:
        tablero.escribir_celda(cubo, punto, tablero.AGUA_MARCADA)
        return "Agua"
    
    if celda == tablero.NAVE_OCULTA:
        tablero.escribir_celda(cubo, punto, tablero.IMPACTO)
        if flota_jugador is not None:
            return modulo_flota.registrar_impacto(cubo, flota_jugador, punto)
        return "Impacto"

    if celda == tablero.AGUA_MARCADA:
        return "Celda ya disparada"

    if celda == tablero.IMPACTO:
        return "Celda ya disparada"

    if celda == tablero.HUNDIDO:
        return "Celda ya disparada"
    
def misil_racimo(cubo, punto, flota_jugador=None):
    """
    Recibe el cubo y el punto del disparo.
    Dispara a la celda elegida y sus 6 vecinas ortogonales.
    Devuelve una lista con los resultados.
    """
    if not tablero.punto_valido(cubo, punto):

        return []

    z, x, y = punto

    puntos = [
        (z, x, y),
        (z + 1, x, y),
        (z - 1, x, y),
        (z, x + 1, y),
        (z, x - 1, y),
        (z, x, y + 1),
        (z, x, y - 1)
    ]

    resultados = []

    for objetivo in puntos:
        if tablero.punto_valido(cubo, objetivo):
            resultado = torpedo(cubo, objetivo, flota_jugador)
            resultados.append(resultado)

    return resultados

def carga_profundidad(cubo, punto, flota_jugador=None):
    """
    Dispara a todas las celdas del eje Z
    que tienen las mismas coordenadas X e Y.
    Devuelve una lista con los resultados.
    """

    if not tablero.punto_valido(cubo, punto):
        return []

    z, x, y = punto
    resultados = []

    for nivel in range(1, len(cubo) + 1):
        objetivo = (nivel, x, y)
        resultado = torpedo(cubo, objetivo, flota_jugador)
        resultados.append(resultado)

    return resultados

def barrido_laser(cubo, punto, eje, flota_jugador=None):
    """
    Dispara a toda una línea sobre el eje X o Y.
    Devuelve una lista con los resultados.
    """

    if not tablero.punto_valido(cubo, punto):
        return []

    if eje not in ("x", "y"):
        return []

    z, x, y = punto
    resultados = []

    for posicion in range(1, len(cubo) + 1):

        if eje == "x":
            objetivo = (z, posicion, y)
        else:
            objetivo = (z, x, posicion)

        es_submarino = False

        if flota_jugador is not None:
            for nave in flota_jugador:
                if nave["tipo"] == "S" and objetivo in nave["puntos"]:
                    es_submarino = True
                    break

        if es_submarino:
            resultados.append("Submarino inmune")
        else:
            resultado = torpedo(cubo, objetivo, flota_jugador)
            resultados.append(resultado)

    return resultados

def sonar(cubo, punto, eje, flota_jugador=None):
    """
    Explora un plano del cubo utilizando el sonar.
    Devuelve las coordenadas de las naves detectadas
    sin producir daños.
    """
    z, x, y = punto

    if eje == "z":
        valor = z
    elif eje == "x":
        valor = x
    elif eje == "y":
        valor = y
    else:
        return None

    return radar.sonar_plano(cubo, eje, valor)

def onda_expansiva(cubo, punto, flota_jugador=None):
    """
    Dispara desde un punto y se expande de forma recursiva.
    Afecta las celdas que estan hasta dos pasos ortogonales
    del punto inicial, sin repetir celdas.
    Devuelve una lista con los resultados.
    """

    if not tablero.punto_valido(cubo, punto):
        return []

    visitados = set()
    resultados = []

    def propagar(puntos, radio):
        siguientes = []

        for actual in puntos:
            actual = tuple(actual)

            if actual not in visitados:
                visitados.add(actual)

                resultado = torpedo(cubo, actual, flota_jugador)
                resultados.append(resultado)

                if radio > 0:
                    vecinos = tablero.vecinos_ortogonales(cubo, actual)

                    for vecino in vecinos:
                        vecino = tuple(vecino)

                        if vecino not in visitados:
                            siguientes.append(vecino)

        if radio > 0 and siguientes:
            propagar(siguientes, radio - 1)

    propagar([punto], 2)

    return resultados

def buscar_objetivo_guiado(cubo, actual, puntos_nave, impactos, visitados):
    """
    Busca recursivamente una celda de la nave que todavia
    no haya recibido un impacto.
    """

    actual = tuple(actual)

    if actual in visitados:
        return None

    visitados.add(actual)

    if actual in puntos_nave and actual not in impactos:
        return actual

    vecinos = tablero.vecinos_ortogonales(cubo, actual)

    for vecino in vecinos:
        vecino = tuple(vecino)

        if vecino in puntos_nave and vecino not in visitados:
            encontrado = buscar_objetivo_guiado(
                cubo, vecino, puntos_nave, impactos, visitados
            )

            if encontrado is not None:
                return encontrado

    return None


def torpedo_guiado(cubo, punto, flota_jugador=None):
    """
    Busca una celda sin impactar de una nave averiada.
    Parte de una celda impactada y utiliza una busqueda
    recursiva para encontrar el siguiente objetivo.
    """

    if not tablero.punto_valido(cubo, punto):
        return "Punto invalido"

    if flota_jugador is None:
        return "Sin objetivo guiado"

    for nave in flota_jugador:

        if nave["estado"] == modulo_flota.NAVE_AVERIADA:

            impactos = set()

            for impacto in nave["impactos"]:
                impactos.add(tuple(impacto))

            if tuple(punto) not in impactos:
                continue

            puntos_nave = set()

            for posicion in nave["puntos"]:
                puntos_nave.add(tuple(posicion))

            visitados = set()

            objetivo = buscar_objetivo_guiado(
                cubo, punto, puntos_nave, impactos, visitados
            )

            if objetivo is not None:
                return torpedo(cubo, objetivo, flota_jugador)

    return "Sin objetivo guiado"

def consumir_municion(codigo, municion_jugador):
    """
    Recibe el codigo del arma y la municion de un jugador.
    Descuenta una unidad si hay municion disponible.
    Devuelve True si puede utilizar el arma y False si no.
    """
    if codigo not in municion_jugador:
        return False

    cantidad = municion_jugador[codigo]

    if cantidad is None:
        return True

    if cantidad <= 0:
        return False

    municion_jugador[codigo] -= 1
    return True

def recompensar_estacion(flota_jugador, municion_jugador, estado_anterior):
    """
    Otorga municion adicional si una estacion orbital
    acaba de ser hundida.
    """

    if flota_jugador is None:
        return

    for nave in flota_jugador:
        if nave["tipo"] == "E":
            if estado_anterior != modulo_flota.NAVE_HUNDIDA:
                if nave["estado"] == modulo_flota.NAVE_HUNDIDA:
                    municion_jugador["R"] += 1

funciones_armas = {
    "T": torpedo,
    "R": misil_racimo,
    "C": carga_profundidad,
    "L": barrido_laser,
    "S": sonar,
    "O": onda_expansiva,
    "G": torpedo_guiado
}

def ejecutar_disparo(cubo, codigo, punto, municion_jugador, eje=None, flota_jugador=None):
    """
    Ejecuta un disparo con el arma elegida.
    Comprueba y descuenta la municion del jugador.
    Devuelve el resultado del disparo.
    """

    if codigo not in funciones_armas:
        return "Arma no disponible"

    if not tablero.punto_valido(cubo, punto):
        return "Punto invalido"

    if codigo == "L" and eje not in ("x", "y"):
        return "Eje invalido"

    if codigo == "S" and eje not in ("z", "x", "y"):
        return "Eje invalido"

    if codigo not in municion_jugador:
        return "Arma no disponible"

    if municion_jugador[codigo] is not None:
        if municion_jugador[codigo] <= 0:
            return "Sin municion"

    estado_anterior = None

    if flota_jugador is not None:
        for nave in flota_jugador:
            if nave["tipo"] == "E":
                estado_anterior = nave["estado"]

    if codigo in ("L", "S"):
        resultado = funciones_armas[codigo](cubo, punto, eje, flota_jugador)
    else:
        resultado = funciones_armas[codigo](cubo, punto, flota_jugador)

    recompensar_estacion(flota_jugador, municion_jugador, estado_anterior)

    consumir_municion(codigo, municion_jugador)

    return resultado

def reiniciar_municion():
    """
    Restablece la municion inicial de todas las armas.
    """

    catalogo_armas["T"]["municion"] = None
    catalogo_armas["R"]["municion"] = 3
    catalogo_armas["C"]["municion"] = 2
    catalogo_armas["S"]["municion"] = 4
    catalogo_armas["L"]["municion"] = 2
    catalogo_armas["O"]["municion"] = 1
    catalogo_armas["G"]["municion"] = 1