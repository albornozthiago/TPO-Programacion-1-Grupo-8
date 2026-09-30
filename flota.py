import random
import tablero

NAVE_OCULTA = "N"

# Catálogo de naves
CATALOGO_NAVES = {
    "F": {
        "nombre": "Fragata",
        "celdas": 2,
        "cantidad": 3
    },
    "D": {
        "nombre": "Destructor",
        "celdas": 3,
        "cantidad": 2
    },
    "S": {
        "nombre": "Submarino",
        "celdas": 3,
        "cantidad": 2
    },
    "C": {
        "nombre": "Crucero",
        "celdas": 4,
        "cantidad": 1
    },
    "P": {
        "nombre": "Portaaviones",
        "celdas": 5,
        "cantidad": 1
    },
    "E": {
        "nombre": "Estacion orbital",
        "celdas": 8,
        "cantidad": 1
    }
}

def cantidad_ubicada(flota, tipo):
    """
    Verifica la cantidad de naves de un tipo que ya fueron ubicadas.
    Recibe:
        flota: lista de naves ubicadas
        tipo: tipo de nave a contar
    Devuelve:
        cuantas naves de un tipo ya fueron ubicadas.
    """

    cantidad = 0

    for nave in flota:

        if nave["tipo"] == tipo:
            cantidad += 1

    return cantidad

def generar_puntos_lineales(punto_desde, punto_hasta, largo):
    """
    Genera los puntos ocupados por una nave lineal.
    Recibe: 
        punto_desde: (z, x, y) de la primer celda
        punto_hasta: (z, x, y) de la última celda
        largo: longitud de la nave
    Devuelve:
        una lista de puntos si la ubicacion es valida.
        None si no forma una linea valida.
    """
    z1 = punto_desde[0]
    x1 = punto_desde[1]
    y1 = punto_desde[2]
    z2 = punto_hasta[0]
    x2 = punto_hasta[1]
    y2 = punto_hasta[2]
    puntos = []
    #Eje Z
    if x1 == x2 and y1 == y2:
        inicio = min(z1, z2)
        fin = max(z1, z2)
        if fin - inicio + 1 != largo:
            return None
        for z in range(inicio, fin + 1):
            puntos.append((z, x1, y1))
    #Eje X
    elif z1 == z2 and y1 == y2:
        inicio = min(x1, x2)
        fin = max(x1, x2)
        if fin - inicio + 1 != largo:
            return None
        for x in range(inicio, fin + 1):
            puntos.append((z1, x, y1))
    #Eje Y
    elif z1 == z2 and x1 == x2:
        inicio = min(y1, y2)
        fin = max(y1, y2)
        if fin - inicio + 1 != largo:
            return None
        for y in range(inicio, fin + 1):
            puntos.append((z1, x1, y))
    else:
        return None
    return puntos

def generar_puntos_estacion(punto_desde, punto_hasta):
    """
    Genera los puntos de una estacion orbital 2x2x2.

    Los dos puntos representan esquinas opuestas del bloque.

    Recibe:
        punto_desde: (z, x, y) de la primer celda
        punto_hasta: (z, x, y) de la última celda
    Devuelve:
        una lista de puntos si la ubicacion es valida.
        None si no forma un bloque 2x2x2.
    """
    z1 = punto_desde[0]
    x1 = punto_desde[1]
    y1 = punto_desde[2]
    z2 = punto_hasta[0]
    x2 = punto_hasta[1]
    y2 = punto_hasta[2]
    if abs(z1 - z2) != 1:
        return None
    if abs(x1 - x2) != 1:
        return None
    if abs(y1 - y2) != 1:
        return None
    puntos = []
    for z in range(min(z1, z2), max(z1, z2) + 1):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                puntos.append((z, x, y))
    return puntos

def puntos_validos(cubo, puntos):
    """
    Verifica que todos los puntos pertenezcan al cubo y no se repitan.
    """
    repetidos = []

    for punto in puntos:
        if not tablero.punto_valido(cubo, punto):
            return False

        if punto in repetidos:
            return False

        repetidos.append(punto)

    return True


def puntos_ocupados(flota):
    """
    Verifica los puntos ocupados por las naves de la flota.
    Recibe: 
        flota: lista de naves ubicadas
    Devuelve:
        una lista con todos los puntos ocupados por las naves de la flota.
    """

    ocupados = []
    for nave in flota:
        for punto in nave["puntos"]:
            ocupados.append(punto)
    return ocupados

def distancia_valida(flota, puntos_nuevos):
    """
    Verifica que la nave nueva no toque a otra nave.
    Recibe:
        flota: lista de naves ubicadas
        puntos_nuevos: lista de puntos de la nave a ubicar
    Devuelve:
        True si la nave nueva no toca a otra nave.
        False si la nave nueva toca a otra nave.
    """

    ocupados = puntos_ocupados(flota)
    for punto_nuevo in puntos_nuevos:
        z1 = punto_nuevo[0]
        x1 = punto_nuevo[1]
        y1 = punto_nuevo[2]
        for punto_ocupado in ocupados:

            z2 = punto_ocupado[0]
            x2 = punto_ocupado[1]
            y2 = punto_ocupado[2]

            diferencia_z = abs(z1 - z2)
            diferencia_x = abs(x1 - x2)
            diferencia_y = abs(y1 - y2)

            if (diferencia_z <= 1 and
                    diferencia_x <= 1 and
                    diferencia_y <= 1):

                return False

    return True


# =========================================================
# RESTRICCIONES DE CADA TIPO DE NAVE
# =========================================================

def restriccion_nave(cubo, tipo, puntos):
    """
    Verifica las restricciones particulares
    del tipo de nave.
    """

    n = len(cubo)

    # -----------------------------------------------------
    # SUBMARINO
    # Solo mitad inferior de Z
    # -----------------------------------------------------

    if tipo == "S":

        limite = n // 2

        for punto in puntos:

            z = punto[0]

            if z > limite:
                return False

    # -----------------------------------------------------
    # CRUCERO
    # No puede ocupar z = 1 ni z = N
    # -----------------------------------------------------

    elif tipo == "C":

        for punto in puntos:

            z = punto[0]

            if z == 1 or z == n:
                return False

    # -----------------------------------------------------
    # PORTAAVIONES
    # Solo mitad superior de Z
    # -----------------------------------------------------

    elif tipo == "P":

        limite = n // 2

        for punto in puntos:

            z = punto[0]

            if z <= limite:
                return False

    # -----------------------------------------------------
    # ESTACION ORBITAL
    # No puede tocar ninguna cara exterior
    # -----------------------------------------------------

    elif tipo == "E":

        for punto in puntos:

            z = punto[0]
            x = punto[1]
            y = punto[2]

            if z == 1 or z == n:
                return False

            if x == 1 or x == n:
                return False

            if y == 1 or y == n:
                return False

    return True


# =========================================================
# MARCAR LA NAVE EN EL CUBO
# =========================================================

def marcar_nave(cubo, puntos):
    """
    Marca como NAVE_OCULTA todos los puntos de una nave.
    """

    for punto in puntos:

        z = punto[0] - 1
        x = punto[1] - 1
        y = punto[2] - 1

        cubo[z][x][y] = NAVE_OCULTA


# =========================================================
# UBICAR NAVE
# =========================================================

def ubicar_nave(cubo, flota, nave, punto_desde, punto_hasta):
    """
    Intenta ubicar una nave.

    Recibe:
        cubo
        flota
        nave
        punto_desde
        punto_hasta

    Devuelve:
        cubo y flota actualizados si la ubicacion es valida.

        Devuelve None si no se puede ubicar.
    """

    nave = nave.upper()

    # Verificar que el tipo exista

    if nave not in CATALOGO_NAVES:
        return None

    datos = CATALOGO_NAVES[nave]

    # Verificar que no se haya alcanzado
    # la cantidad maxima de ese tipo.

    ubicadas = cantidad_ubicada(flota, nave)

    if ubicadas >= datos["cantidad"]:
        return None

    # -----------------------------------------------------
    # GENERAR LOS PUNTOS
    # -----------------------------------------------------

    if nave == "E":

        puntos = generar_puntos_estacion(
            punto_desde,
            punto_hasta
        )

    else:

        puntos = generar_puntos_lineales(
            punto_desde,
            punto_hasta,
            datos["celdas"]
        )

    if puntos is None:
        return None

    # -----------------------------------------------------
    # VALIDACIONES
    # -----------------------------------------------------

    if not puntos_validos(cubo, puntos):
        return None

    if not restriccion_nave(cubo, nave, puntos):
        return None

    if not distancia_valida(flota, puntos):
        return None

    # -----------------------------------------------------
    # GUARDAR LA NAVE
    # -----------------------------------------------------

    nueva_nave = {
        "tipo": nave,
        "nombre": datos["nombre"],
        "puntos": puntos
    }

    flota.append(nueva_nave)

    marcar_nave(cubo, puntos)

    return cubo, flota


# =========================================================
# NAVES PENDIENTES
# =========================================================

def naves_pendientes(flota):
    """
    Devuelve un diccionario con la cantidad pendiente
    de cada tipo de nave.
    """

    pendientes = {}

    for tipo in CATALOGO_NAVES:

        total = CATALOGO_NAVES[tipo]["cantidad"]

        ubicadas = cantidad_ubicada(
            flota,
            tipo
        )

        pendientes[tipo] = total - ubicadas

    return pendientes


# =========================================================
# FLOTA COMPLETA
# =========================================================

def flota_completa(flota):
    """
    Devuelve True si toda la flota fue ubicada.
    """

    for tipo in CATALOGO_NAVES:

        necesarias = CATALOGO_NAVES[tipo]["cantidad"]

        ubicadas = cantidad_ubicada(
            flota,
            tipo
        )

        if ubicadas < necesarias:
            return False

    return True


# =========================================================
# GENERAR UBICACION ALEATORIA
# =========================================================

def generar_ubicacion_aleatoria(n, tipo):
    """
    Genera dos puntos aleatorios para intentar
    ubicar una nave.
    """

    # -----------------------------------------------------
    # ESTACION ORBITAL
    # -----------------------------------------------------

    if tipo == "E":

        z = random.randint(1, n - 1)
        x = random.randint(1, n - 1)
        y = random.randint(1, n - 1)

        desde = (z, x, y)
        hasta = (z + 1, x + 1, y + 1)

        return desde, hasta

    # -----------------------------------------------------
    # NAVES LINEALES
    # -----------------------------------------------------

    largo = CATALOGO_NAVES[tipo]["celdas"]

    eje = random.choice(["z", "x", "y"])

    if eje == "z":

        z = random.randint(1, n - largo + 1)
        x = random.randint(1, n)
        y = random.randint(1, n)

        desde = (z, x, y)
        hasta = (z + largo - 1, x, y)

    elif eje == "x":

        z = random.randint(1, n)
        x = random.randint(1, n - largo + 1)
        y = random.randint(1, n)

        desde = (z, x, y)
        hasta = (z, x + largo - 1, y)

    else:

        z = random.randint(1, n)
        x = random.randint(1, n)
        y = random.randint(1, n - largo + 1)

        desde = (z, x, y)
        hasta = (z, x, y + largo - 1)

    return desde, hasta


# =========================================================
# UBICACION AUTOMATICA
# =========================================================

def ubicacion_automatica(cubo, catalogo, semilla):
    """
    Intenta ubicar automaticamente toda la flota.

    Recibe:
        cubo
        catalogo
        semilla

    Devuelve:
        flota ubicada.

    Devuelve None si no logra completar la flota.
    """

    random.seed(semilla)

    flota = []

    for tipo in catalogo:

        cantidad = catalogo[tipo]["cantidad"]

        for i in range(cantidad):

            ubicada = False
            intentos = 0

            while ubicada == False and intentos < 5000:

                desde, hasta = generar_ubicacion_aleatoria(
                    len(cubo),
                    tipo
                )

                resultado = ubicar_nave(
                    cubo,
                    flota,
                    tipo,
                    desde,
                    hasta
                )

                if resultado is not None:
                    ubicada = True

                else:
                    intentos += 1

            if ubicada == False:
                return None

    return flota