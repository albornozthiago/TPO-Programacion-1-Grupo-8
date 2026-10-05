import re
import tablero
import flota


# =========================================================
# PATRONES PARA VALIDAR LO QUE SE TIPEA
# =========================================================
PATRON_OPCION = r"^\d+$"
PATRON_NAVE = r"^[FDSCPE]$"
PATRON_TRAMO = (
    r"^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*-\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*$"
)


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
        print(f"{nave['nombre']}: {'  '.join(puntos)}")

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


MENU_PRINCIPAL = {
    "1": ("Partida uno contra uno", opcion_no_disponible),
    "2": ("Partida uno contra la maquina", opcion_no_disponible),
    "3": ("Partida maquina contra maquina", opcion_no_disponible),
    "4": ("Continuar una partida guardada", opcion_no_disponible),
    "5": ("Salir", salir),
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
