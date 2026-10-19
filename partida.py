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

def crear_municion():
    """
    Crea la municion inicial de un jugador.

    Recibe:
        Ningun parametro.

    Devuelve:
        Un diccionario cuya clave es el codigo del arma
        y cuyo valor es la municion inicial correspondiente.

    Excepciones:
        No lanza excepciones.
    """

    municion = {}

    for codigo in armamento.catalogo_armas:
        municion[codigo] = armamento.catalogo_armas[codigo]["municion"]

    return municion


def cargar_municion(jugador):
    """
    Copia la municion de un jugador al catalogo de armamento
    antes de ejecutar su turno.

    Recibe:
        jugador: diccionario con los datos del jugador.

    Devuelve:
        Nada. Modifica temporalmente la municion del modulo armamento.

    Excepciones:
        KeyError si el jugador no contiene la clave "municion".
    """

    for codigo in jugador["municion"]:
        armamento.catalogo_armas[codigo]["municion"] = jugador["municion"][codigo]


def guardar_municion(jugador):
    """
    Guarda en el jugador la municion restante despues de su turno.

    Recibe:
        jugador: diccionario con los datos del jugador.

    Devuelve:
        Nada. Modifica el diccionario recibido.

    Excepciones:
        KeyError si el jugador no contiene la clave "municion".
    """

    for codigo in armamento.catalogo_armas:
        jugador["municion"][codigo] = armamento.catalogo_armas[codigo]["municion"]

def crear_jugador(nombre, cubo, flota_jugador, maquina=False):
    """
    Crea la estructura que representa a un jugador.

    Recibe:
        nombre: nombre del jugador.
        cubo: cubo perteneciente al jugador.
        flota_jugador: lista de naves del jugador.
        maquina: True si el jugador es controlado por la maquina.
                 False en caso contrario.

    Devuelve:
        Diccionario con nombre, cubo, flota, tipo de jugador
        y municion disponible.

    Excepciones:
        No lanza excepciones.
    """

    return {
        "nombre": nombre,
        "cubo": cubo,
        "flota": flota_jugador,
        "maquina": maquina,
        "municion": crear_municion()
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
        "historial": registro.inicioHistorial(),
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
        True
    )

    estado = {
        "modo": "vs_maquina",
        "n": configuracion["n"],
        "jugadores": [jugador, maquina],
        "turno": 0,
        "numero_turno": 1,
        "historial": registro.inicioHistorial(),
        "ganador": None,
        "ultimo_resultado": None,
        "dificultad": dificultad
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


def ejecutar_turno(estado, jugada):
    """
    Ejecuta una jugada del jugador cuyo turno esta activo.

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

    cargar_municion(jugador)

    if codigo == "S":
        eje = jugada["eje"]
        valor = jugada["valor"]

        if eje not in ("z", "x", "y"):
            raise JugadaInvalidaError("Eje invalido.")

        if valor < 1 or valor > estado["n"]:
            raise JugadaInvalidaError("Valor invalido.")

        if armamento.catalogo_armas["S"]["municion"] == 0:
            raise SinMunicionError("No queda municion de sonar.")

        contactos = radar.sonar_plano(
            rival["cubo"],
            eje,
            valor
        )

        armamento.consumir_municion("S")

        resultado = (
            "Sonar sobre "
            + eje
            + " = "
            + str(valor)
            + ". "
            + str(len(contactos))
            + " contactos detectados."
        )

        punto_historial = (0, 0, 0)

    else:
        punto = jugada["punto"]

        if not tablero.punto_valido(rival["cubo"], punto):
            raise JugadaInvalidaError("Punto invalido.")

        eje = jugada.get("eje")

        resultado = armamento.ejecutar_disparo(
            rival["cubo"],
            codigo,
            punto,
            eje,
            rival["flota"]
        )

        if resultado == "Sin municion":
            raise SinMunicionError("No queda municion.")

        if resultado == "Arma no disponible":
            raise JugadaInvalidaError("Arma no disponible.")

        if resultado == "Eje invalido":
            raise JugadaInvalidaError("Eje invalido.")

        if resultado == "Celda ya disparada":
            raise JugadaInvalidaError("La celda ya fue disparada.")

        punto_historial = punto

    guardar_municion(jugador)

    registro.registroTurno(
        estado["historial"],
        estado["numero_turno"],
        jugador["nombre"],
        codigo,
        punto_historial,
        resultado
    )

    estado["ultimo_resultado"] = resultado

    ganador = hay_ganador(estado)

    if ganador is not None:
        estado["ganador"] = ganador

    else:
        estado["turno"] = indice_rival
        estado["numero_turno"] += 1

    return estado


def turno_maquina(estado):
    """
    Ejecuta automaticamente un turno de la maquina.

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

    posibles = []

    for z in range(1, estado["n"] + 1):
        for x in range(1, estado["n"] + 1):
            for y in range(1, estado["n"] + 1):

                punto = (z, x, y)

                celda = tablero.leer_celda(
                    rival["cubo"],
                    punto
                )

                if (
                    celda == tablero.AGUA_SIN_EXPLORAR
                    or celda == tablero.NAVE_OCULTA
                ):
                    posibles.append(punto)

    if len(posibles) == 0:
        raise JugadaInvalidaError(
            "La maquina no tiene objetivos disponibles."
        )

    punto = random.choice(posibles)

    jugada = {
        "arma": "T",
        "punto": punto
    }

    ejecutar_turno(estado, jugada)

    estado["ultima_jugada_maquina"] = punto

    return estado

ARMAS_ENTREGA_2 = {
    "T": "Torpedo",
    "R": "Misil de racimo",
    "C": "Carga de profundidad",
    "S": "Sonar",
    "L": "Barrido laser"
}


def pedir_arma():
    """
    Solicita al usuario un arma disponible para la Entrega 2.

    Recibe:
        Ningun parametro.

    Devuelve:
        Codigo del arma seleccionada.

    Excepciones:
        No lanza excepciones.
    """

    for codigo in ARMAS_ENTREGA_2:
        print(codigo, "-", ARMAS_ENTREGA_2[codigo])

    arma = input("Arma (T/R/C/S/L): ").strip().upper()

    while arma not in ARMAS_ENTREGA_2:
        print("Arma invalida.")
        arma = input("Arma (T/R/C/S/L): ").strip().upper()

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


def jugar_partida(estado):
    """
    Ejecuta el ciclo principal de una partida.

    Alterna los turnos de los jugadores hasta que haya
    un ganador o se decida salir de la partida.

    Recibe:
        estado: diccionario con el estado actual de la partida.

    Devuelve:
        Estado final o actualizado de la partida.

    Excepciones:
        Las excepciones propias producidas durante una jugada
        son capturadas dentro de la funcion.
    """

    jugando = True

    while jugando and estado["ganador"] is None:

        jugador = estado["jugadores"][estado["turno"]]

        print()
        print("--- Turno de", jugador["nombre"], "---")

        if jugador["maquina"]:
            turno_maquina(estado)

            punto = estado["ultima_jugada_maquina"]

            print(
                "La maquina dispara a",
                punto
            )

            print(
                estado["ultimo_resultado"]
            )

        else:
            MENU_TURNO = {
                "1": "Disparar",
                "2": "Ver el cubo",
                "3": "Salir"
            }

            print("1 - Disparar")
            print("2 - Ver el cubo")
            print("3 - Salir")

            opcion = input("Opcion: ").strip()

            while opcion not in MENU_TURNO:
                print("Opcion invalida.")
                opcion = input("Opcion: ").strip()

            if opcion == "1":
                jugada = pedir_jugada(estado)

                try:
                    ejecutar_turno(
                        estado,
                        jugada
                    )

                except OperacionCuboError as error:
                    print("Error:", error)

                else:
                    print(
                        estado["ultimo_resultado"]
                    )

                finally:
                    print()

            elif opcion == "2":
                mostrar_estado(
                    jugador["nombre"],
                    jugador["cubo"],
                    jugador["flota"]
                )

            elif opcion == "3":
                jugando = False

    if estado["ganador"] is not None:
        print()
        print(
            "GANADOR:",
            estado["ganador"]
        )

        print()
        print(
            registro.mostrarHistorial(
                estado["historial"]
            )
        )

    return estado

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

    estado = nueva_partida_vs_maquina(
        configuracion,
        "basica"
    )

    jugar_partida(estado)

    return True

MENU_PRINCIPAL = {
    "1": ("Partida uno contra uno",iniciar_partida_1v1),
    "2": ("Partida uno contra la maquina",iniciar_partida_vs_maquina),
    "3": ("Partida maquina contra maquina",opcion_no_disponible),
    "4": ("Continuar una partida guardada",opcion_no_disponible),
    "5": ("Salir",salir)
}


def menu_principal():
    """
    Muestra el menu principal hasta que se elija salir.

    La opcion elegida se resuelve con el diccionario MENU_PRINCIPAL,
    sin cadenas de if / elif.
    """ 

    seguir = True

    while seguir:
        opcion = pedir_opcion("\n===== OPERACION CUBO =====", MENU_PRINCIPAL)
        seguir = MENU_PRINCIPAL[opcion][1]()

if __name__ == "__main__":
    menu_principal()

