import random
import tablero

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

ORDEN_AUTOMATICO = ["E", "P", "C", "D", "S", "F"]

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

    Recibe:
        cubo: cubo de juego
        puntos: lista de puntos (z, x, y)
    Devuelve:
        True si todos los puntos estan dentro del cubo y ninguno se repite.
        False en caso contrario.
    Excepciones:
        No lanza excepciones.
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

def marcar_nave(cubo, puntos):
    """
    Marca como NAVE_OCULTA todos los puntos de una nave.

    Recibe:
        cubo: cubo de juego (se modifica)
        puntos: lista de puntos (z, x, y) de la nave, con ejes de 1 a N
    Devuelve:
        Nada. Modifica el cubo recibido.
    Excepciones:
        IndexError si algun punto esta fuera del cubo
        (ubicar_nave lo valida antes de llamarla).
    """

    for punto in puntos:

        z = punto[0] - 1
        x = punto[1] - 1
        y = punto[2] - 1

        cubo[z][x][y] = tablero.NAVE_OCULTA


def ubicar_nave(cubo, flota, nave, punto_desde, punto_hasta):
    """
    Intenta ubicar una nave.

    Recibe:
        cubo: cubo de juego
        flota: lista de naves ya ubicadas
        nave: letra del tipo de nave (F/D/S/C/P/E)
        punto_desde: (z, x, y) del primer extremo
        punto_hasta: (z, x, y) del otro extremo
    Devuelve:
        (cubo, flota) actualizados si la ubicacion es valida.
        None si no se puede ubicar (tipo inexistente, cantidad maxima
        alcanzada, puntos que no forman la nave, nave fuera del cubo,
        restriccion del tipo incumplida o nave que toca a otra).
        Si devuelve None, el cubo y la flota quedan sin modificar.
    Excepciones:
        AttributeError si nave no es una cadena.
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

def naves_pendientes(flota):
    """
    Calcula cuantas naves de cada tipo faltan ubicar.

    Recibe:
        flota: lista de naves ubicadas
    Devuelve:
        Un diccionario {letra: cantidad pendiente}, por ejemplo
        {"F": 3, "D": 2, "S": 2, "C": 1, "P": 1, "E": 1}.
    Excepciones:
        No lanza excepciones.
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

def flota_completa(flota):
    """
    Indica si toda la flota ya fue ubicada.

    Recibe:
        flota: lista de naves ubicadas
    Devuelve:
        True si estan ubicadas todas las naves del catalogo.
        False si falta alguna.
    Excepciones:
        No lanza excepciones.
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

def generar_ubicacion_aleatoria(n, tipo):
    """
    Genera dos puntos aleatorios para intentar ubicar una nave.
    No garantiza que la ubicacion sea valida: eso lo decide ubicar_nave.

    Recibe:
        n: tamaño del cubo
        tipo: letra del tipo de nave
    Devuelve:
        (desde, hasta): dos puntos (z, x, y) que forman la nave.
    Excepciones:
        KeyError si tipo no esta en CATALOGO_NAVES.
        ValueError si n es demasiado chico para la nave.
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

    for tipo in ORDEN_AUTOMATICO:

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