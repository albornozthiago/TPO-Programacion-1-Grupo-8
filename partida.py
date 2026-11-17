import re
import tablero
import flota
import random
import armamento
import radar
import registro


# PATRONES PARA VALIDAR LO QUE SE TIPEA
PATRON_OPCION = r"^\d+$"
PATRON_NAVE = r"^[FDSCPE]$"
PATRON_TRAMO = (
    r"^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*-\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*$"
)
PATRON_PUNTO = r"^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*$"

class OperacionCuboError(Exception):
    pass


class JugadaInvalidaError(OperacionCuboError):
    pass


class SinMunicionError(OperacionCuboError):
    pass


class PartidaFinalizadaError(OperacionCuboError):
    pass


def leer_tramo(texto):
    """
    Convierte un tramo tipeado por el usuario en dos puntos.

    El formato esperado es z,x,y-z,x,y (se permiten espacios).

    Recibe:
        texto: cadena tipeada por el usuario, por ejemplo "3,5,4-3,5,5".
    Devuelve:
        (desde, hasta): dos tuplas (z, x, y) con valores enteros.
        None si el texto no respeta el formato.
    Excepciones:
        No lanza excepciones.
    """

    coincidencia = re.match(PATRON_TRAMO, texto)

    if coincidencia is None:
        return None

    valores = [int(valor) for valor in coincidencia.groups()]

    desde = tuple(valores[0:3])
    hasta = tuple(valores[3:6])

    return desde, hasta


def opcion_valida(texto, opciones):
    """
    Indica si una opcion tipeada existe en un menu.

    Recibe:
        texto: cadena tipeada por el usuario.
        opciones: diccionario del menu {numero: (descripcion, funcion)}.
    Devuelve:
        True si el texto es un numero y esta en el menu.
        False en caso contrario.
    Excepciones:
        No lanza excepciones.
    """

    return re.match(PATRON_OPCION, texto) is not None and texto in opciones


def nave_valida(texto, pendientes):
    """
    Indica si una letra de nave es valida y quedan naves de ese tipo.

    Recibe:
        texto: letra tipeada por el usuario, ya en mayuscula.
        pendientes: diccionario {letra: cantidad pendiente}.
    Devuelve:
        True si la letra es F/D/S/C/P/E y queda al menos una por ubicar.
        False en caso contrario.
    Excepciones:
        No lanza excepciones.
    """

    return re.match(PATRON_NAVE, texto) is not None and pendientes[texto] > 0


def texto_pendientes(pendientes):
    """
    Arma el texto con las naves que faltan ubicar.

    Recibe:
        pendientes: diccionario {letra: cantidad pendiente}.
    Devuelve:
        Cadena del estilo "Pendientes: F x3  D x2  S x2".
        Solo incluye los tipos con cantidad mayor a cero.
    Excepciones:
        No lanza excepciones.
    """

    partes = [
        f"{letra} x{cantidad}" for letra, cantidad in pendientes.items() if cantidad > 0
    ]

    return f"Pendientes: {'  '.join(partes)}"


def pedir_opcion(titulo, opciones):
    """
    Muestra un menu y pide una opcion hasta que sea valida.

    Recibe:
        titulo: titulo del menu.
        opciones: diccionario del menu {numero: (descripcion, funcion)}.
    Devuelve:
        La clave de la opcion elegida.
    """

    print(titulo)

    for clave in opciones:
        print(f"{clave} - {opciones[clave][0]}")

    opcion = input("\n[+] Opcion: ").strip()

    while not opcion_valida(opcion, opciones):
        print("Opcion invalida. Intente de nuevo.")
        opcion = input("Opcion: ").strip()

    return opcion


def mostrar_estado(nombre_jugador, cubo, flota_jugador):
    """
    Muestra el estado de un jugador: sus naves y el cubo capa por capa.

    Recibe:
        nombre_jugador: nombre a mostrar en el encabezado.
        cubo: cubo del jugador.
        flota_jugador: lista de naves ubicadas.
    Devuelve:
        Nada. Solo muestra por pantalla.
    """

    print()
    print(f"===== Estado de {nombre_jugador} =====")

    for nave in flota_jugador:
        puntos = [f"{z},{x},{y}" for z, x, y in nave["puntos"]]
        estado = nave.get("estado", flota.NAVE_INTACTA)
        impactos = nave.get("impactos", [])
        print(
            f"{nave['nombre']} ({estado}; impactos {len(impactos)}/"
            f"{len(nave['puntos'])}): {'  '.join(puntos)}"
        )

    print()

    for z in range(1, tablero.tamanio_cubo(cubo) + 1):
        print(tablero.dibujar_plano_z(cubo, z))
        print()


def opcion_no_disponible():
    """
    Avisa que la opcion todavia no esta implementada.

    Devuelve:
        True, para volver al menu principal.
    """

    print("\n[!] Opcion no disponible en esta entrega.")

    return True


def ubicar_manualmente(n):
    """
    Pide nave por nave hasta completar la flota.

    Recibe:
        n: tamaño del cubo.
    Devuelve:
        (cubo, flota) con toda la flota ubicada.
    """

    cubo = tablero.crear_cubo(n)
    flota_jugador = []

    while not flota.flota_completa(flota_jugador):
        pendientes = flota.naves_pendientes(flota_jugador)

        print()
        print(texto_pendientes(pendientes))

        nave = input("Nave (F/D/S/C/P/E): ").strip().upper()

        if not nave_valida(nave, pendientes):
            print("Nave invalida o ya ubicada. Intente de nuevo.")

        else:
            tramo = leer_tramo(input("Desde-hasta: "))

            if tramo is None:
                print("Formato invalido. Use z,x,y-z,x,y (por ejemplo 3,5,4-3,5,5).")

            elif (
                flota.ubicar_nave(cubo, flota_jugador, nave, tramo[0], tramo[1]) is None
            ):
                print("No se puede ubicar ahi. Intente de nuevo.")

            else:
                print("Ubicada.")

    return cubo, flota_jugador


def ubicar_automaticamente(n):
    """
    Ubica toda la flota de forma automatica.

    Si flota.ubicacion_automatica no logra completar la flota,
    se crea un cubo nuevo y se vuelve a intentar.

    Recibe:
        n: tamaño del cubo.
    Devuelve:
        (cubo, flota) con toda la flota ubicada.
    """

    flota_jugador = None

    while flota_jugador is None:
        cubo = tablero.crear_cubo(n)
        flota_jugador = flota.ubicacion_automatica(cubo, flota.CATALOGO_NAVES, None)

    return cubo, flota_jugador


MENU_UBICACION = {
    "1": ("Ubicacion manual", ubicar_manualmente),
    "2": ("Ubicacion automatica", ubicar_automaticamente),
}


def ubicar_flota(nombre_jugador, n):
    """
    Muestra el submenu de ubicacion y ubica la flota de un jugador.

    Recibe:
        nombre_jugador: nombre a mostrar en el encabezado.
        n: tamaño del cubo.
    Devuelve:
        (cubo, flota) con toda la flota ubicada.
    """

    print()
    opcion = pedir_opcion(f"--- Flota de {nombre_jugador} ---", MENU_UBICACION)

    return MENU_UBICACION[opcion][1](n)


def salir():
    """
    Termina el programa.

    Devuelve:
        False, para cortar el ciclo del menu principal.
    """

    print("\nHasta luego.\n")

    return False

def leer_punto(texto):
    """
    Convierte un punto escrito por el usuario en una tupla de coordendas.

    Recibe:
        texto: cadena con formato z,x,y.

    Devuelve:
        Una tupla (z, x, y) con valores enteros.
        None si el texto no respeta el formato esperado.

    Excepciones:
        No lanza excepciones.
    """

    coincidencia = re.match(PATRON_PUNTO, texto)

    if coincidencia is None:
        return None

    valores = []

    for valor in coincidencia.groups():
        valores.append(int(valor))

    return tuple(valores)


def pedir_punto():
    """
    Solicita al usuario un punto hasta que tenga un formato valido.

    Recibe:
        Ningun parametro.

    Devuelve:
        Una tupla (z, x, y) ingresada por el usuario.

    Excepciones:
        No lanza excepciones.
    """

    punto = leer_punto(input("Objetivo: "))

    while punto is None:
        print("Formato invalido. Use z,x,y.")
        punto = leer_punto(input("Objetivo: "))

    return punto

def crear_jugador(nombre, cubo, flota_jugador, maquina=False, dificultad=None):
    """
    Crea la estructura que representa a un jugador.

    Recibe:
        nombre: nombre del jugador.
        cubo: cubo perteneciente al jugador.
        flota_jugador: lista de naves del jugador.
        maquina: True si el jugador es controlado por la maquina.
                 False en caso contrario.
        dificultad: nivel de la maquina ("basica" o "avanzada").
                    Si es una maquina y no se indica, usa "basica".

    Devuelve:
        Diccionario con nombre, cubo, flota, tipo de jugador,
        dificultad, municion disponible y puntos detectados por el sonar.

    Excepciones:
        JugadaInvalidaError si la dificultad no existe.
    """

    if maquina and dificultad is None:
        dificultad = "basica"

    if maquina and dificultad not in ESTRATEGIAS_MAQUINA:
        raise JugadaInvalidaError("Dificultad invalida.")

    return {
        "nombre": nombre,
        "cubo": cubo,
        "flota": flota_jugador,
        "maquina": maquina,
        "dificultad": dificultad,
        "municion": armamento.crear_municion(),
        "detectados": []
    }

def nueva_partida_1v1(configuracion):
    """
    Crea el estado inicial de una partida entre dos jugadores.

    Recibe:
        configuracion: diccionario que contiene tamaño del cubo,
        nombres, cubos y flotas de ambos jugadores.

    Devuelve:
        Diccionario con el estado inicial de la partida.

    Excepciones:
        KeyError si falta algun dato obligatorio en configuracion.
    """

    jugador1 = crear_jugador(
        configuracion["nombre_jugador1"],
        configuracion["cubo_jugador1"],
        configuracion["flota_jugador1"]
    )

    jugador2 = crear_jugador(
        configuracion["nombre_jugador2"],
        configuracion["cubo_jugador2"],
        configuracion["flota_jugador2"]
    )

    estado = {
        "modo": "1v1",
        "n": configuracion["n"],
        "jugadores": [jugador1, jugador2],
        "turno": 0,
        "numero_turno": 1,
        "historial": registro.inicio_historial(),
        "ganador": None,
        "ultimo_resultado": None
    }

    return estado


def nueva_partida_vs_maquina(configuracion, dificultad):
    """
    Crea el estado inicial de una partida contra la maquina.

    Recibe:
        configuracion: diccionario con los datos del jugador
        y de la maquina.
        dificultad: nivel de dificultad elegido para la maquina.

    Devuelve:
        Diccionario con el estado inicial de la partida.

    Excepciones:
        KeyError si falta algun dato obligatorio en configuracion.
    """

    jugador = crear_jugador(
        configuracion["nombre_jugador"],
        configuracion["cubo_jugador"],
        configuracion["flota_jugador"]
    )

    maquina = crear_jugador(
        "Maquina",
        configuracion["cubo_maquina"],
        configuracion["flota_maquina"],
        True,
        dificultad
    )

    estado = {
        "modo": "vs_maquina",
        "n": configuracion["n"],
        "jugadores": [jugador, maquina],
        "turno": 0,
        "numero_turno": 1,
        "historial": registro.inicio_historial(),
        "ganador": None,
        "ultimo_resultado": None,
        "dificultad": dificultad
    }

    return estado


def nueva_partida_maquina_vs_maquina(configuracion, dificultades):
    """
    Crea el estado inicial de una partida entre dos maquinas.

    Recibe:
        configuracion: diccionario con n y los cubos y flotas de
        "maquina1" y "maquina2".
        dificultades: lista con la dificultad de cada maquina,
        por ejemplo ["basica", "avanzada"].

    Devuelve:
        Diccionario con el estado inicial de la partida.

    Excepciones:
        KeyError si falta algun dato obligatorio en configuracion.
        JugadaInvalidaError si alguna dificultad no existe.
    """

    maquina1 = crear_jugador(
        "Maquina 1",
        configuracion["cubo_maquina1"],
        configuracion["flota_maquina1"],
        True,
        dificultades[0]
    )

    maquina2 = crear_jugador(
        "Maquina 2",
        configuracion["cubo_maquina2"],
        configuracion["flota_maquina2"],
        True,
        dificultades[1]
    )

    estado = {
        "modo": "maquina_vs_maquina",
        "n": configuracion["n"],
        "jugadores": [maquina1, maquina2],
        "turno": 0,
        "numero_turno": 1,
        "historial": registro.inicio_historial(),
        "ganador": None,
        "ultimo_resultado": None,
        "dificultades": dificultades
    }

    return estado


def hay_ganador(estado):
    """
    Verifica si alguna de las flotas fue completamente hundida.

    Recibe:
        estado: diccionario con el estado actual de la partida.

    Devuelve:
        Nombre del jugador ganador si existe.
        None si la partida todavia no tiene ganador.

    Excepciones:
        KeyError si el estado no contiene los datos esperados.
    """

    jugadores = estado["jugadores"]

    for i in range(len(jugadores)):
        todas_hundidas = True

        for nave in jugadores[i]["flota"]:
            if nave.get("estado") != flota.NAVE_HUNDIDA:
                todas_hundidas = False

        if todas_hundidas:
            indice_ganador = 1 - i
            return jugadores[indice_ganador]["nombre"]

    return None


def disparar_sonar(estado, jugador, rival, jugada):
    """
    Ejecuta un sonar sobre un plano del cubo rival.

    Guarda los contactos en jugador["detectados"], para mostrarlos
    como DETECTADO en la vista del rival.

    Recibe:
        estado: diccionario con el estado actual de la partida.
        jugador: jugador que dispara.
        rival: jugador que recibe el disparo.
        jugada: diccionario con "eje" y "valor" del plano.

    Devuelve:
        Tupla (texto con los contactos y sus coordenadas, punto para el historial).

    Excepciones:
        JugadaInvalidaError si el eje o el valor son invalidos.
        SinMunicionError si no queda municion de sonar.
    """

    eje = jugada["eje"]
    valor = jugada["valor"]

    if eje not in ("z", "x", "y"):
        raise JugadaInvalidaError("Eje invalido.")

    if valor < 1 or valor > estado["n"]:
        raise JugadaInvalidaError("Valor invalido.")

    if jugador["municion"]["S"] == 0:
        raise SinMunicionError("No queda municion de sonar.")

    puntos_plano = {
        "z": (valor, 1, 1),
        "x": (1, valor, 1),
        "y": (1, 1, valor)
    }

    contactos = armamento.ejecutar_disparo(
        rival["cubo"],
        "S",
        puntos_plano[eje],
        jugador["municion"],
        eje=eje,
        flota_jugador=rival["flota"]
    )

    coordenadas = []

    for contacto in contactos:
        punto = (contacto[0], contacto[1], contacto[2])
        coordenadas.append(f"({punto[0]},{punto[1]},{punto[2]})")

        if punto not in jugador["detectados"]:
            jugador["detectados"].append(punto)

    texto = (
        f"Sonar sobre el plano {eje} = {valor}. "
        f"{len(contactos)} contactos detectados."
    )

    if len(coordenadas) > 0:
        texto += " Contactos en: " + ", ".join(coordenadas) + "."

    return texto, (0, 0, 0)


def disparar_con_punto(estado, jugador, rival, jugada):
    """
    Ejecuta un arma que se dispara a un punto (todas menos el sonar).

    Recibe:
        estado: diccionario con el estado actual de la partida.
        jugador: jugador que dispara.
        rival: jugador que recibe el disparo.
        jugada: diccionario con "arma", "punto" y, si hace falta, "eje".

    Devuelve:
        Tupla (resultado del disparo, punto para el historial).

    Excepciones:
        JugadaInvalidaError si el punto, el eje o el arma son invalidos
        o la celda ya fue disparada.
        SinMunicionError si el arma no tiene municion.
    """

    punto = jugada["punto"]

    if not tablero.punto_valido(rival["cubo"], punto):
        raise JugadaInvalidaError("Punto invalido.")

    resultado = armamento.ejecutar_disparo(
        rival["cubo"],
        jugada["arma"],
        punto,
        jugador["municion"],
        eje=jugada.get("eje"),
        flota_jugador=rival["flota"]
    )

    if resultado == "Sin municion":
        raise SinMunicionError("No queda municion.")

    if resultado == "Arma no disponible":
        raise JugadaInvalidaError("Arma no disponible.")

    if resultado == "Eje invalido":
        raise JugadaInvalidaError("Eje invalido.")

    if resultado == "Celda ya disparada":
        raise JugadaInvalidaError("La celda ya fue disparada.")

    return resultado, punto


ACCIONES_ARMA = {
    "T": disparar_con_punto,
    "R": disparar_con_punto,
    "C": disparar_con_punto,
    "S": disparar_sonar,
    "L": disparar_con_punto,
    "O": disparar_con_punto,
    "G": disparar_con_punto
}


def ejecutar_turno(estado, jugada):
    """
    Ejecuta una jugada del jugador cuyo turno esta activo.

    El arma se resuelve con el diccionario ACCIONES_ARMA,
    sin cadenas de if / elif.

    Recibe:
        estado: diccionario con el estado actual de la partida.
        jugada: diccionario con el arma y los datos necesarios
        para realizar el ataque.

    Devuelve:
        El estado actualizado de la partida.

    Excepciones:
        PartidaFinalizadaError si la partida ya termino.
        JugadaInvalidaError si los datos de la jugada son invalidos.
        SinMunicionError si el arma elegida no tiene municion.
    """

    if estado["ganador"] is not None:
        raise PartidaFinalizadaError("La partida ya termino.")

    indice_actual = estado["turno"]
    indice_rival = 1 - indice_actual

    jugador = estado["jugadores"][indice_actual]
    rival = estado["jugadores"][indice_rival]

    codigo = jugada["arma"]

    if codigo not in ACCIONES_ARMA:
        raise JugadaInvalidaError("Arma no disponible.")

    resultado, punto_historial = ACCIONES_ARMA[codigo](
        estado,
        jugador,
        rival,
        jugada
    )

    if codigo in ARMAS_RESULTADO_TEXTO:
        resultado_historial = [resultado]
    else:
        resultado_historial = resultado

    registro.registro_turno(
        estado["historial"],
        estado["numero_turno"],
        jugador["nombre"],
        codigo,
        punto_historial,
        resultado_historial
    )

    estado["ultimo_resultado"] = resultado

    ganador = hay_ganador(estado)

    if ganador is not None:
        estado["ganador"] = ganador
    else:
        estado["turno"] = indice_rival
        estado["numero_turno"] += 1

    return estado


def puntos_sin_disparar(cubo, n):
    """
    Lista los puntos del cubo rival donde todavia no se disparo.

    Recibe:
        cubo: cubo del rival.
        n: tamanio del cubo.

    Devuelve:
        Lista de puntos (z, x, y) con agua sin explorar o nave oculta.

    Excepciones:
        No lanza excepciones.
    """

    posibles = []

    for z in range(1, n + 1):
        for x in range(1, n + 1):
            for y in range(1, n + 1):
                celda = tablero.leer_celda(cubo, (z, x, y))

                if (
                    celda == tablero.AGUA_SIN_EXPLORAR
                    or celda == tablero.NAVE_OCULTA
                ):
                    posibles.append((z, x, y))

    return posibles


def elegir_punto_basico(cubo, n):
    """
    Nivel basico de la maquina: dispara a un punto al azar.

    Recibe:
        cubo: cubo del rival.
        n: tamanio del cubo.

    Devuelve:
        Un punto (z, x, y), o None si no queda ninguno.

    Excepciones:
        No lanza excepciones.
    """

    posibles = puntos_sin_disparar(cubo, n)

    if len(posibles) == 0:
        return None

    return random.choice(posibles)


def elegir_punto_avanzado(cubo, n):
    """
    Nivel avanzado de la maquina.

    Primero remata: si hay un impacto sin hundir, dispara a una celda
    pegada a ese impacto que todavia no se probo. Si no hay ninguno,
    dispara a la celda mas probable segun el mapa de probabilidad
    de radar.py.

    Recibe:
        cubo: cubo del rival.
        n: tamanio del cubo.

    Devuelve:
        Un punto (z, x, y), o None si no queda ninguno.

    Excepciones:
        No lanza excepciones.
    """

    for z in range(1, n + 1):
        for x in range(1, n + 1):
            for y in range(1, n + 1):
                if tablero.leer_celda(cubo, (z, x, y)) == tablero.IMPACTO:
                    for vecino in tablero.vecinos_ortogonales(cubo, (z, x, y)):
                        celda = tablero.leer_celda(cubo, vecino)

                        if (
                            celda == tablero.AGUA_SIN_EXPLORAR
                            or celda == tablero.NAVE_OCULTA
                        ):
                            return tuple(vecino)

    mapa = radar.mapa_de_probabilidad(cubo)

    return radar.celda_mas_probable(cubo, mapa)


ESTRATEGIAS_MAQUINA = {
    "basica": elegir_punto_basico,
    "avanzada": elegir_punto_avanzado
}


def turno_maquina(estado):
    """
    Ejecuta automaticamente un turno de la maquina, segun su dificultad.

    Recibe:
        estado: diccionario con el estado actual de la partida.

    Devuelve:
        Estado actualizado luego del disparo de la maquina.

    Excepciones:
        JugadaInvalidaError si el jugador actual no es una maquina
        o no existen objetivos disponibles.
    """

    maquina = estado["jugadores"][estado["turno"]]
    rival = estado["jugadores"][1 - estado["turno"]]

    if not maquina["maquina"]:
        raise JugadaInvalidaError("No es el turno de la maquina.")

    estrategia = ESTRATEGIAS_MAQUINA[maquina.get("dificultad", "basica")]
    punto = estrategia(rival["cubo"], estado["n"])

    if punto is None:
        raise JugadaInvalidaError(
            "La maquina no tiene objetivos disponibles."
        )

    jugada = {
        "arma": "T",
        "punto": punto
    }

    ejecutar_turno(estado, jugada)

    estado["ultima_jugada_maquina"] = punto

    return estado


ARMAS_RESULTADO_TEXTO = ("T", "S", "G")


ARMAS = {
    "T": "Torpedo",
    "R": "Misil de racimo",
    "C": "Carga de profundidad",
    "S": "Sonar",
    "L": "Barrido laser",
    "O": "Onda expansiva",
    "G": "Torpedo guiado"
}


def pedir_arma():
    """
    Solicita al usuario un arma del catalogo.

    Recibe:
        Ningun parametro.

    Devuelve:
        Codigo del arma seleccionada.

    Excepciones:
        No lanza excepciones.
    """

    for codigo in ARMAS:
        print(codigo, "-", ARMAS[codigo])

    arma = input("Arma (T/R/C/S/L/O/G): ").strip().upper()

    while arma not in ARMAS:
        print("Arma invalida.")
        arma = input("Arma (T/R/C/S/L/O/G): ").strip().upper()

    return arma


def pedir_eje():
    """
    Solicita al usuario un eje valido.

    Recibe:
        Ningun parametro.

    Devuelve:
        Cadena "z", "x" o "y".

    Excepciones:
        No lanza excepciones.
    """

    eje = input("Eje (z/x/y): ").strip().lower()

    while eje not in ("z", "x", "y"):
        print("Eje invalido.")
        eje = input("Eje (z/x/y): ").strip().lower()

    return eje


def pedir_jugada(estado):
    """
    Solicita todos los datos necesarios para realizar una jugada.

    Recibe:
        estado: estado actual de la partida.

    Devuelve:
        Diccionario con arma, punto y, cuando corresponde,
        eje o valor del plano.

    Excepciones:
        No lanza excepciones.
    """

    arma = pedir_arma()

    jugada = {
        "arma": arma
    }

    if arma == "S":
        eje = pedir_eje()

        valor = input(
            "Valor (1-" + str(estado["n"]) + "): "
        ).strip()

        while (
            not valor.isdigit()
            or int(valor) < 1
            or int(valor) > estado["n"]
        ):
            print("Valor invalido.")

            valor = input(
                "Valor (1-" + str(estado["n"]) + "): "
            ).strip()

        jugada["eje"] = eje
        jugada["valor"] = int(valor)

    else:
        jugada["punto"] = pedir_punto()

        if arma == "L":
            eje = pedir_eje()

            while eje not in ("x", "y"):
                print("El laser solo utiliza eje x o y.")
                eje = pedir_eje()

            jugada["eje"] = eje

    return jugada


def estado_para_guardar(estado):
    """
    Arma una copia del estado con la flota en datos compatibles con JSON.

    Recibe:
        estado: diccionario con el estado actual de la partida.

    Devuelve:
        Copia del estado lista para registro.guardar_partida.

    Excepciones:
        KeyError si el estado no contiene los datos esperados.
    """

    copia = dict(estado)
    copia["jugadores"] = []

    for jugador in estado["jugadores"]:
        datos = dict(jugador)
        datos["flota"] = flota.datos_flota(jugador["flota"])
        copia["jugadores"].append(datos)

    return copia


def reponer_estado(estado):
    """
    Deja una partida cargada de JSON lista para seguir jugando.

    JSON guarda las coordenadas como listas, por eso se reconstruye
    la flota con flota.reponer_flota, que las devuelve como tuplas.

    Recibe:
        estado: diccionario cargado con registro.cargar_partida.

    Devuelve:
        El mismo estado, con la flota de cada jugador repuesta.

    Excepciones:
        KeyError si el estado no contiene los datos esperados.
    """

    for jugador in estado["jugadores"]:
        jugador["flota"] = flota.reponer_flota(jugador["flota"])

    return estado


def pedir_nombre_partida():
    """
    Pide el nombre con el que se guarda una partida, hasta que sea valido.

    Recibe:
        Ningun parametro.

    Devuelve:
        Nombre valido segun registro.validar_nombre_partida.

    Excepciones:
        No lanza excepciones: NombrePartidaInvalido se captura aca.
    """

    valido = False
    nombre = ""

    while not valido:
        nombre = input("Nombre de la partida: ").strip()

        try:
            valido = registro.validar_nombre_partida(nombre)
        except registro.NombrePartidaInvalido as error:
            print("Error:", error)

    return nombre


def accion_disparar(estado):
    """
    Pide una jugada y la ejecuta para el jugador del turno.

    Recibe:
        estado: diccionario con el estado actual de la partida.

    Devuelve:
        True, para seguir jugando.

    Excepciones:
        Las excepciones propias se capturan dentro de la funcion.
    """

    jugada = pedir_jugada(estado)

    try:
        ejecutar_turno(estado, jugada)
    except OperacionCuboError as error:
        print("Error:", error)
    else:
        print(estado["ultimo_resultado"])
    finally:
        print()

    return True


def accion_ver_cubo(estado):
    """
    Muestra el cubo y la flota del jugador del turno.

    Recibe:
        estado: diccionario con el estado actual de la partida.

    Devuelve:
        True, para seguir jugando.

    Excepciones:
        No lanza excepciones.
    """

    jugador = estado["jugadores"][estado["turno"]]

    mostrar_estado(jugador["nombre"], jugador["cubo"], jugador["flota"])

    return True


def accion_guardar_y_salir(estado):
    """
    Guarda la partida en datos/partidas/ y sale al menu principal.

    Recibe:
        estado: diccionario con el estado actual de la partida.

    Devuelve:
        False si se guardo (corta la partida).
        True si hubo un error al guardar (se sigue jugando).

    Excepciones:
        RegistroError se captura dentro de la funcion.
    """

    nombre = pedir_nombre_partida()

    try:
        ruta = registro.guardar_partida(estado_para_guardar(estado), nombre)
    except registro.RegistroError as error:
        print("Error:", error)
        return True
    else:
        print("Partida guardada en", ruta)
        return False


def vista_del_rival(jugador, rival):
    """
    Arma lo que el jugador sabe del cubo del rival.

    Las naves ocultas se muestran como agua sin explorar, salvo las que
    detecto el sonar, que se marcan con tablero.DETECTADO. Los disparos
    ya hechos (agua, impacto, hundido) se muestran tal cual.

    Recibe:
        jugador: jugador que mira (usa jugador["detectados"]).
        rival: jugador cuyo cubo se consulta.

    Devuelve:
        Un cubo nuevo con la vista del rival. No modifica el cubo real.

    Excepciones:
        KeyError si el jugador no contiene los datos esperados.
    """

    n = tablero.tamanio_cubo(rival["cubo"])
    vista = tablero.crear_cubo(n)

    detectados = []

    for punto in jugador.get("detectados", []):
        detectados.append((punto[0], punto[1], punto[2]))

    for z in range(1, n + 1):
        for x in range(1, n + 1):
            for y in range(1, n + 1):
                celda = tablero.leer_celda(rival["cubo"], (z, x, y))

                if celda == tablero.NAVE_OCULTA:
                    if (z, x, y) in detectados:
                        celda = tablero.DETECTADO
                    else:
                        celda = tablero.AGUA_SIN_EXPLORAR

                tablero.escribir_celda(vista, (z, x, y), celda)

    return vista


BUSQUEDAS = {
    "Lineal": radar.busqueda_lineal,
    "Optimizada": radar.busqueda_optimizada,
    "Recursiva": radar.busqueda_recursiva
}


def accion_comparar_busquedas(vista):
    """
    Busca el primer contacto del sonar con los tres metodos de busqueda
    de radar.py y muestra las metricas de cada uno.

    Recibe:
        vista: cubo con lo que el jugador sabe del rival.

    Devuelve:
        True, para seguir en el menu de radar.

    Excepciones:
        No lanza excepciones.
    """

    print()
    print("Busqueda del primer contacto del sonar (?):")

    for nombre in BUSQUEDAS:
        punto, metricas = BUSQUEDAS[nombre](vista, tablero.DETECTADO)

        if punto is None:
            resultado = "sin contactos"
        else:
            resultado = f"contacto en {punto}"

        print(
            f"- {nombre}: {resultado} | "
            f"comparaciones: {metricas['comparaciones']} | "
            f"tiempo: {metricas['tiempo_ms']} ms | "
            f"profundidad maxima: {metricas['profundidad_max']}"
        )

    if len(contactos_en_vista(vista)) == 0:
        print("Todavia no hay contactos: usa el sonar primero.")

    return True


def contactos_en_vista(vista):
    """
    Lista los puntos marcados como DETECTADO en una vista, en orden z, x, y.

    Recibe:
        vista: cubo con lo que el jugador sabe del rival.

    Devuelve:
        Lista de puntos (z, x, y).

    Excepciones:
        No lanza excepciones.
    """

    puntos = []

    for punto in radar.recorrer(vista, "capas"):
        if tablero.leer_celda(vista, punto) == tablero.DETECTADO:
            puntos.append(punto)

    return puntos


MENU_RECORRIDOS = {
    "1": ("Por capas de z", "capas"),
    "2": ("En espiral", "espiral"),
    "3": ("Desde un punto", "desde un punto"),
    "4": ("Por octantes", "octantes"),
    "5": ("Volver", None)
}


def accion_recorrido(vista):
    """
    Recorre el cubo con el recorrido elegido y muestra en que orden
    aparecen los contactos del sonar.

    Recibe:
        vista: cubo con lo que el jugador sabe del rival.

    Devuelve:
        True, para seguir en el menu de radar.

    Excepciones:
        No lanza excepciones.
    """

    opcion = pedir_opcion("\n--- Recorridos del cubo ---", MENU_RECORRIDOS)
    nombre = MENU_RECORRIDOS[opcion][1]

    if nombre is None:
        return True

    inicio = (1, 1, 1)

    if nombre == "desde un punto":
        print("Punto de inicio del recorrido:")
        inicio = pedir_punto()

    puntos = radar.recorrer(vista, nombre, inicio)

    if puntos is None:
        print("No se pudo hacer el recorrido: punto de inicio invalido.")
        return True

    primeras = []

    for punto in puntos[:8]:
        primeras.append(f"({punto[0]},{punto[1]},{punto[2]})")

    contactos = []

    for punto in puntos:
        if tablero.leer_celda(vista, punto) == tablero.DETECTADO:
            contactos.append(f"({punto[0]},{punto[1]},{punto[2]})")

    print()
    print(f"Recorrido {nombre}: {len(puntos)} celdas.")
    print("Primeras celdas:", ", ".join(primeras), "...")

    if len(contactos) == 0:
        print("Contactos del sonar: ninguno.")
    else:
        print("Contactos del sonar, en orden de recorrido:", ", ".join(contactos))

    return True


def accion_ver_vista(vista):
    """
    Muestra, capa por capa, lo que el jugador sabe del cubo del rival.

    Recibe:
        vista: cubo con lo que el jugador sabe del rival.

    Devuelve:
        True, para seguir en el menu de radar.

    Excepciones:
        No lanza excepciones.
    """

    print()
    print("===== Lo que sabes del cubo rival (? = contacto del sonar) =====")

    for z in range(1, tablero.tamanio_cubo(vista) + 1):
        print(tablero.dibujar_plano_z(vista, z))
        print()

    return True


def accion_volver_radar(vista):
    """
    Sale del menu de radar.

    Recibe:
        vista: cubo con lo que el jugador sabe del rival (no se usa).

    Devuelve:
        False, para cortar el ciclo del menu de radar.

    Excepciones:
        No lanza excepciones.
    """

    return False


MENU_RADAR = {
    "1": ("Comparar las tres busquedas", accion_comparar_busquedas),
    "2": ("Recorrer el cubo", accion_recorrido),
    "3": ("Ver lo que se del cubo rival", accion_ver_vista),
    "4": ("Volver", accion_volver_radar)
}


def accion_radar(estado):
    """
    Abre el menu de radar: busquedas con metricas, recorridos del cubo
    y vista del cubo rival.

    Recibe:
        estado: diccionario con el estado actual de la partida.

    Devuelve:
        True, para seguir jugando.

    Excepciones:
        No lanza excepciones.
    """

    jugador = estado["jugadores"][estado["turno"]]
    rival = estado["jugadores"][1 - estado["turno"]]

    vista = vista_del_rival(jugador, rival)

    seguir = True

    while seguir:
        opcion = pedir_opcion("\n--- Radar ---", MENU_RADAR)
        seguir = MENU_RADAR[opcion][1](vista)

    return True


MENU_EXPORTAR = {
    "1": ("Exportar el resumen a un archivo", True),
    "2": ("No exportar", False)
}


def cerrar_partida(estado):
    """
    Muestra el final de la partida: ganador, historial, resumen,
    ranking, y ofrece exportar el resumen.

    Recibe:
        estado: diccionario de una partida con ganador.

    Devuelve:
        Nada. Los errores de archivo se informan por pantalla.

    Excepciones:
        RegistroError se captura dentro de la funcion.
    """

    nombres = []

    for jugador in estado["jugadores"]:
        nombres.append(jugador["nombre"])

    print()
    print("GANADOR:", estado["ganador"])
    print()
    print(registro.mostrar_historial(estado["historial"]))
    print(registro.resumen_final(
        estado["historial"],
        nombres,
        estado["ganador"]
    ))

    try:
        registro.actualizar_ranking(nombres, estado["ganador"])

        print("===== RANKING =====")

        for jugador, datos in registro.obtener_ranking():
            print(
                f"{jugador}: {datos['victorias']} victorias "
                f"en {datos['partidas']} partidas"
            )

        opcion = pedir_opcion("\nExportar el resumen?", MENU_EXPORTAR)

        if MENU_EXPORTAR[opcion][1]:
            nombre = pedir_nombre_partida()
            ruta = registro.exportar_resumen(
                estado["historial"],
                nombres,
                estado["ganador"],
                nombre
            )
            print("Resumen exportado en", ruta)
    except registro.RegistroError as error:
        print("Error:", error)


MENU_TURNO = {
    "1": ("Disparar", accion_disparar),
    "2": ("Ver el cubo", accion_ver_cubo),
    "3": ("Guardar y salir", accion_guardar_y_salir),
    "4": ("Radar", accion_radar)
}


def jugar_partida(estado):
    """
    Ejecuta el ciclo principal de una partida.

    Alterna los turnos de los jugadores hasta que haya un ganador
    o el jugador elija guardar y salir. Sirve para las tres modalidades
    y para las partidas cargadas.

    Recibe:
        estado: diccionario con el estado actual de la partida.

    Devuelve:
        Estado final o actualizado de la partida.

    Excepciones:
        Las excepciones propias producidas durante una jugada
        son capturadas dentro de la funcion.
    """

    seguir = True

    while seguir and estado["ganador"] is None:
        jugador = estado["jugadores"][estado["turno"]]

        print()
        print("--- Turno de", jugador["nombre"], "---")

        if jugador["maquina"]:
            turno_maquina(estado)

            print("Dispara a", estado["ultima_jugada_maquina"])
            print(estado["ultimo_resultado"])
        else:
            opcion = pedir_opcion("", MENU_TURNO)
            seguir = MENU_TURNO[opcion][1](estado)

    if estado["ganador"] is not None:
        cerrar_partida(estado)

    return estado


MENU_DIFICULTAD = {
    "1": ("Basica", "basica"),
    "2": ("Avanzada", "avanzada")
}


def pedir_dificultad(titulo):
    """
    Pide el nivel de dificultad de una maquina.

    Recibe:
        titulo: texto que se muestra arriba del menu.

    Devuelve:
        "basica" o "avanzada".

    Excepciones:
        No lanza excepciones.
    """

    opcion = pedir_opcion(titulo, MENU_DIFICULTAD)

    return MENU_DIFICULTAD[opcion][1]


def iniciar_partida_1v1():
    """
    Configura e inicia una partida entre dos jugadores humanos.

    Recibe:
        Ningun parametro.

    Devuelve:
        True al finalizar para volver al menu principal.

    Excepciones:
        No lanza excepciones propias directamente.
    """

    n = tablero.RANGO_DEFECTO

    nombre1 = input("Nombre Jugador 1: ").strip()
    nombre2 = input("Nombre Jugador 2: ").strip()

    if nombre1 == "":
        nombre1 = "Jugador 1"

    if nombre2 == "":
        nombre2 = "Jugador 2"

    cubo1, flota1 = ubicar_flota(
        nombre1,
        n
    )

    cubo2, flota2 = ubicar_flota(
        nombre2,
        n
    )

    configuracion = {
        "n": n,
        "nombre_jugador1": nombre1,
        "nombre_jugador2": nombre2,
        "cubo_jugador1": cubo1,
        "flota_jugador1": flota1,
        "cubo_jugador2": cubo2,
        "flota_jugador2": flota2
    }

    estado = nueva_partida_1v1(
        configuracion
    )

    jugar_partida(estado)

    return True

def iniciar_partida_vs_maquina():
    """
    Configura e inicia una partida entre un jugador
    humano y la maquina.

    Recibe:
        Ningun parametro.

    Devuelve:
        True al finalizar para volver al menu principal.

    Excepciones:
        No lanza excepciones propias directamente.
    """

    n = tablero.RANGO_DEFECTO

    nombre = input(
        "Nombre del jugador: "
    ).strip()

    if nombre == "":
        nombre = "Jugador 1"

    cubo_jugador, flota_jugador = ubicar_flota(
        nombre,
        n
    )

    cubo_maquina, flota_maquina = ubicar_automaticamente(
        n
    )

    configuracion = {
        "n": n,
        "nombre_jugador": nombre,
        "cubo_jugador": cubo_jugador,
        "flota_jugador": flota_jugador,
        "cubo_maquina": cubo_maquina,
        "flota_maquina": flota_maquina
    }

    dificultad = pedir_dificultad("\nDificultad de la maquina:")

    estado = nueva_partida_vs_maquina(
        configuracion,
        dificultad
    )

    jugar_partida(estado)

    return True

def iniciar_partida_maquina_vs_maquina():
    """
    Configura e inicia una partida entre dos maquinas.

    Recibe:
        Ningun parametro.

    Devuelve:
        True al finalizar para volver al menu principal.

    Excepciones:
        No lanza excepciones propias directamente.
    """

    n = tablero.RANGO_DEFECTO

    dificultad1 = pedir_dificultad("\nDificultad de la Maquina 1:")
    dificultad2 = pedir_dificultad("\nDificultad de la Maquina 2:")

    cubo1, flota1 = ubicar_automaticamente(n)
    cubo2, flota2 = ubicar_automaticamente(n)

    configuracion = {
        "n": n,
        "cubo_maquina1": cubo1,
        "flota_maquina1": flota1,
        "cubo_maquina2": cubo2,
        "flota_maquina2": flota2
    }

    estado = nueva_partida_maquina_vs_maquina(
        configuracion,
        [dificultad1, dificultad2]
    )

    jugar_partida(estado)

    return True


def continuar_partida():
    """
    Lista las partidas guardadas y retoma la elegida.

    Recibe:
        Ningun parametro.

    Devuelve:
        True al finalizar para volver al menu principal.

    Excepciones:
        RegistroError se captura dentro de la funcion.
    """

    nombres = registro.listar_partidas()

    if len(nombres) == 0:
        print("\n[!] No hay partidas guardadas.")
        return True

    opciones = {}
    numero = 1

    for nombre in nombres:
        opciones[str(numero)] = (nombre, nombre)
        numero += 1

    opciones[str(numero)] = ("Volver al menu", None)

    clave = pedir_opcion("\n--- Partidas guardadas ---", opciones)
    elegida = opciones[clave][1]

    if elegida is None:
        return True

    try:
        estado = registro.cargar_partida(elegida)
        estado = reponer_estado(estado)
    except (registro.RegistroError, KeyError) as error:
        print("Error: no se pudo cargar la partida:", error)
        return True

    jugar_partida(estado)

    return True


MENU_PRINCIPAL = {
    "1": ("Partida uno contra uno",iniciar_partida_1v1),
    "2": ("Partida uno contra la maquina",iniciar_partida_vs_maquina),
    "3": ("Partida maquina contra maquina",iniciar_partida_maquina_vs_maquina),
    "4": ("Continuar una partida guardada",continuar_partida),
    "5": ("Salir",salir)
}


def menu_principal():
    """
    Muestra el menu principal hasta que se elija salir.

    La opcion elegida se resuelve con el diccionario MENU_PRINCIPAL,
    sin cadenas de if / elif. Si ocurre un error, se informa y el
    menu se vuelve a mostrar: el programa no se corta por una
    excepcion no capturada.

    Recibe:
        Ningun parametro.

    Devuelve:
        Nada. Termina cuando el usuario elige Salir.

    Excepciones:
        No lanza excepciones: las propias y las inesperadas se
        capturan y se informa por pantalla.
    """

    seguir = True

    while seguir:
        try:
            opcion = pedir_opcion("\n===== OPERACION CUBO =====", MENU_PRINCIPAL)
            seguir = MENU_PRINCIPAL[opcion][1]()
        except (OperacionCuboError, registro.RegistroError) as error:
            print("Error:", error)
        except (KeyboardInterrupt, EOFError):
            print("\nPrograma interrumpido.")
            seguir = False
        except Exception as error:
            print("Error inesperado:", error)


if __name__ == "__main__":
    menu_principal()

