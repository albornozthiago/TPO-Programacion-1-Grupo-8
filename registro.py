import json
import os
import re

RESULTADO_AGUA = "Agua"
RESULTADO_HUNDIDA = "Nave hundida"

RESULTADOS_IMPACTO = (
    "Impacto",
    "Nave averiada",
    "Nave hundida"
)


CARPETA_PARTIDAS = "datos/partidas"
CARPETA_EXPORTACIONES = "datos/exportaciones"
ARCHIVO_RANKING = "datos/ranking.json"

PATRON_NOMBRE = r"^[A-Za-z0-9_-]{1,30}$"


class RegistroError(Exception):
    """
    Excepcion base para los errores producidos en registro.py.
    """
    pass


class NombrePartidaInvalido(RegistroError):
    """
    Se produce cuando el nombre de una partida no cumple
    con el formato permitido.
    """
    pass


class PartidaNoEncontrada(RegistroError):
    """
    Se produce cuando se intenta cargar una partida
    que no existe.
    """
    pass


class ErrorArchivoPartida(RegistroError):
    """
    Se produce cuando ocurre un problema al leer
    o escribir un archivo.
    """
    pass

def inicio_historial():
    """
    Objetivo:
        crea la estructura principal en memoria para almacenar
        el historial.

    Parametros:
        ninguno.

    Retorna:
        list: una lista vacia, lista para recibir acciones
        con registro_turno.
    """

    historial = []

    return historial


def registro_turno(historial,turno,jugador,codigo_arma,punto,resultado):
    """
    Objetivo:
        guarda los detalles de un disparo en el historial.

    Parametros:
        historial (list):
            lista del historial. Se modifica en el lugar.

        turno (int):
            numero de turno en el que ocurrio el disparo.

        jugador (str):
            nombre o identificador de quien disparo.

        codigo_arma (str):
            codigo del arma utilizada.

        punto (tuple):
            coordenadas (z, x, y) del disparo.

        resultado (list):
            resultados de las celdas afectadas.

    Retorna:
        dict:
            accion agregada al historial.
    """

    accion = {
        "jugador": jugador,
        "turno": turno,
        "arma": codigo_arma,
        "punto": punto,
        "resultado": resultado
    }

    historial.append(accion)

    return accion


def turno_jugador(historial, jugador):
    """
    Objetivo:
        devuelve solamente las acciones realizadas
        por un jugador.

    Parametros:
        historial (list):
            historial completo de la partida.

        jugador (str):
            jugador que se desea consultar.

    Retorna:
        list:
            acciones correspondientes al jugador.
    """

    turno = []

    for accion in historial:

        if accion["jugador"] == jugador:
            turno.append(accion)

    return turno


def mostrar_historial(historial):
    """
    Objetivo:
        arma el texto correspondiente al historial completo.

    Parametros:
        historial (list):
            historial de la partida.

    Retorna:
        str:
            texto con todas las acciones realizadas.
    """

    partida_actual = ""

    if not historial:
        return "-- No se registraron partidas hasta el momento --"

    for accion in historial:

        z, x, y = accion["punto"]

        resultado = ", ".join(
            accion["resultado"]
        )

        partida_actual += (
            f"Turno {accion['turno']} | "
            f"{accion['jugador']} "
        )

        partida_actual += (
            f"| Arma: {accion['arma']} "
            f"| Coord: ({z},{x},{y}) "
            f"-- Resultado: {resultado} --\n"
        )

    return partida_actual

def contar_resultados(historial):
    """
    Objetivo:
        cuenta cuantas veces aparece cada resultado
        dentro del historial.

    Parametros:
        historial (list):
            historial completo o parcial.

    Retorna:
        dict:
            resultado y cantidad de apariciones.
    """

    conteo = {}

    for accion in historial:

        for resultado in accion["resultado"]:

            if resultado not in conteo:
                conteo[resultado] = 0

            conteo[resultado] += 1

    return conteo


def armas_usadas(historial, jugador):
    """
    Objetivo:
        cuenta cuantas veces utilizo cada arma
        un jugador.

    Parametros:
        historial (list):
            historial completo.

        jugador (str):
            jugador a consultar.

    Retorna:
        dict:
            codigo de arma y cantidad de usos.
    """

    conteo = {}

    acciones = turno_jugador(
        historial,
        jugador
    )

    for accion in acciones:

        arma = accion["arma"]

        if arma not in conteo:
            conteo[arma] = 0

        conteo[arma] += 1

    return conteo


def estadisticas_jugador(historial, jugador):
    """
    Objetivo:
        calcula las estadisticas de un jugador.

    Parametros:
        historial (list):
            historial completo.

        jugador (str):
            jugador que se desea consultar.

    Retorna:
        dict:
            disparos, impactos, agua, naves hundidas
            y precision.
    """

    acciones = turno_jugador(historial,jugador)

    conteo = contar_resultados(acciones)

    impactos = 0

    for resultado in RESULTADOS_IMPACTO:

        impactos += conteo.get(resultado,0)

    agua = conteo.get(RESULTADO_AGUA,0)

    try:

        precision = (
            impactos * 100
            // (impactos + agua)
        )

    except ZeroDivisionError:

        precision = 0

    estadisticas = {
        "disparos": len(acciones),
        "impactos": impactos,
        "agua": agua,
        "hundidas": conteo.get(
            RESULTADO_HUNDIDA,
            0
        ),
        "precision": precision
    }

    return estadisticas


def estadisticas_partida(historial,jugadores):
    """
    Objetivo:
        calcula las estadisticas de todos los jugadores.

    Parametros:
        historial (list):
            historial completo.

        jugadores (list):
            nombres de los jugadores.

    Retorna:
        dict:
            jugador y sus estadisticas.
    """

    estadisticas = {}

    for jugador in jugadores:

        estadisticas[jugador] = (
            estadisticas_jugador(
                historial,
                jugador
            )
        )

    return estadisticas


def resumen_final(historial,jugadores,ganador):
    """
    Objetivo:
        genera el resumen completo de una partida.

    Parametros:
        historial (list):
            historial completo.

        jugadores (list):
            nombres de los jugadores.

        ganador (str o None):
            nombre del ganador.

    Retorna:
        str:
            resumen de la partida.
    """

    estadisticas = estadisticas_partida(historial,jugadores)

    resumen = ("===== RESUMEN DE LA PARTIDA =====\n")

    if ganador is None:
        resumen += ("Ganador: sin ganador\n")
    else:
        resumen += (f"Ganador: {ganador}\n")

    resumen += (
        f"Disparos totales: "
        f"{len(historial)}\n"
    )

    for jugador in jugadores:
        datos = estadisticas[jugador]
        armas = armas_usadas(historial,jugador)
        armas_texto = ""
        for arma in armas:

            cantidad = armas[arma]

            if armas_texto != "":
                armas_texto += "  "

            armas_texto += (f"{arma} x{cantidad}")

        if armas_texto == "":
            armas_texto = "ninguna"

        resumen += (f"\n--- {jugador} ---\n")

        resumen += (
            f"Disparos: "
            f"{datos['disparos']} | "
            f"Impactos: "
            f"{datos['impactos']} | "
            f"Agua: "
            f"{datos['agua']}\n"
        )

        resumen += (
            f"Naves hundidas: "
            f"{datos['hundidas']} | "
            f"Precision: "
            f"{datos['precision']}%\n"
        )

        resumen += (
            f"Armas usadas: "
            f"{armas_texto}\n"
        )

    return resumen

def validar_nombre_partida(nombre):
    """
    Objetivo:
        valida el nombre utilizado para guardar
        una partida.

    Parametros:
        nombre (str):
            nombre de la partida.

    Retorna:
        bool:
            True si el nombre es valido.

    Excepciones:
        NombrePartidaInvalido:
            si el nombre no cumple el formato.
    """

    if not isinstance(nombre, str):

        raise NombrePartidaInvalido("El nombre debe ser un texto.")

    resultado = re.fullmatch(PATRON_NOMBRE,nombre)

    if resultado is None:

        raise NombrePartidaInvalido(
            "El nombre debe tener entre "
            "1 y 30 caracteres y solo "
            "puede contener letras, "
            "numeros, guion y guion bajo."
        )

    return True

def guardar_partida(estado, nombre):
    """
    Objetivo:
        guarda el estado completo de una partida
        en un archivo JSON.

    Parametros:
        estado (dict):
            estado actual de la partida.

        nombre (str):
            nombre de la partida.

    Retorna:
        str:
            ruta del archivo creado.

    Excepciones:
        NombrePartidaInvalido:
            si el nombre no es valido.

        ErrorArchivoPartida:
            si ocurre un error al guardar.
    """

    validar_nombre_partida(nombre)

    os.makedirs(CARPETA_PARTIDAS,exist_ok=True)

    ruta = os.path.join(CARPETA_PARTIDAS,nombre + ".json")

    try:

        with open(ruta,"w",encoding="utf-8") as archivo:

            json.dump(estado,archivo,indent=4,ensure_ascii=False)

    except (OSError, TypeError) as error:

        raise ErrorArchivoPartida(
            f"No se pudo guardar "
            f"la partida: {error}"
        )

    return ruta

def cargar_partida(nombre):
    """
    Objetivo:
        carga desde JSON una partida guardada.

    Parametros:
        nombre (str):
            nombre de la partida.

    Retorna:
        dict:
            estado de la partida.

    Excepciones:
        NombrePartidaInvalido:
            si el nombre es invalido.

        PartidaNoEncontrada:
            si el archivo no existe.

        ErrorArchivoPartida:
            si el archivo no puede leerse.
    """

    validar_nombre_partida(nombre)

    ruta = os.path.join(CARPETA_PARTIDAS,nombre + ".json")

    if not os.path.exists(ruta):

        raise PartidaNoEncontrada(
            f"No existe una partida "
            f"llamada '{nombre}'."
        )

    try:

        with open(ruta,"r",encoding="utf-8") as archivo:

            estado = json.load(archivo)

    except (OSError,json.JSONDecodeError) as error:

        raise ErrorArchivoPartida(
            f"No se pudo cargar "
            f"la partida: {error}"
        )

    return estado


def listar_partidas():
    """
    Objetivo:
        obtiene los nombres de las partidas
        guardadas.

    Parametros:
        ninguno.

    Retorna:
        list:
            nombres de las partidas guardadas
            sin la extension .json.
    """

    if not os.path.exists(CARPETA_PARTIDAS):

        return []

    partidas = []

    archivos = os.listdir(CARPETA_PARTIDAS)

    for archivo in archivos:

        if archivo.endswith(".json"):

            nombre = archivo[:-5]

            partidas.append(nombre)

    partidas.sort()

    return partidas


def exportar_resumen(historial,jugadores,ganador,nombre):
    """
    Objetivo:
        exporta el resumen de una partida
        a un archivo de texto.

    Parametros:
        historial (list):
            historial completo.

        jugadores (list):
            participantes.

        ganador (str o None):
            nombre del ganador.

        nombre (str):
            nombre del archivo.

    Retorna:
        str:
            ruta del archivo creado.

    Excepciones:
        NombrePartidaInvalido:
            si el nombre no es valido.

        ErrorArchivoPartida:
            si no se puede escribir.
    """

    validar_nombre_partida(nombre)

    os.makedirs(CARPETA_EXPORTACIONES,exist_ok=True)

    ruta = os.path.join(CARPETA_EXPORTACIONES,nombre + ".txt")

    resumen = resumen_final(historial,jugadores,ganador)

    try:

        with open(ruta,"w",encoding="utf-8") as archivo:

            archivo.write(resumen)

    except OSError as error:

        raise ErrorArchivoPartida(
            f"No se pudo exportar "
            f"el resumen: {error}"
        )

    return ruta


def cargar_ranking():
    """
    Objetivo:
        carga el ranking almacenado en JSON.

    Parametros:
        ninguno.

    Retorna:
        diccionario:
            ranking de jugadores.

    Excepciones:
        ErrorArchivoPartida:
            si existe el archivo pero
            no puede leerse correctamente.
    """

    if not os.path.exists(ARCHIVO_RANKING):

        return {}

    try:

        with open(ARCHIVO_RANKING,"r",encoding="utf-8") as archivo:

            ranking = json.load(archivo)

    except (OSError,json.JSONDecodeError) as error:

        raise ErrorArchivoPartida(
            f"No se pudo cargar "
            f"el ranking: {error}"
        )

    return ranking


def guardar_ranking(ranking):
    """
    Objetivo:
        guarda el ranking actual en JSON.

    Parametros:
        ranking (dict):
            ranking completo.

    Retorna:
        str:
            ruta del archivo de ranking.

    Excepciones:
        ErrorArchivoPartida:
            si no puede escribirse.
    """

    os.makedirs("datos",exist_ok=True)

    try:

        with open(ARCHIVO_RANKING,"w",encoding="utf-8") as archivo:

            json.dump(ranking,archivo,indent=4,ensure_ascii=False)

    except OSError as error:

        raise ErrorArchivoPartida(
            f"No se pudo guardar "
            f"el ranking: {error}"
        )

    return ARCHIVO_RANKING


def actualizar_ranking(jugadores,ganador):
    """
    Objetivo:
        actualiza las partidas jugadas
        y victorias de cada jugador.

    Parametros:
        jugadores (list):
            jugadores participantes.

        ganador (str o None):
            jugador ganador.

    Retorna:
        dict:
            ranking actualizado.
    """

    ranking = cargar_ranking()

    for jugador in jugadores:

        if jugador not in ranking:

            ranking[jugador] = {
                "partidas": 0,
                "victorias": 0
            }

        ranking[jugador]["partidas"] += 1

    if ganador is not None:

        if ganador not in ranking:

            ranking[ganador] = {
                "partidas": 0,
                "victorias": 0
            }

        ranking[ganador]["victorias"] += 1

    guardar_ranking(ranking)

    return ranking


def obtener_victorias(elemento):
    """
    Objetivo:
        funcion auxiliar utilizada para ordenar
        el ranking.

    Parametros:
        elemento (tuple):
            jugador y sus datos.

    Retorna:
        int:
            cantidad de victorias.
    """

    jugador, datos = elemento

    return datos["victorias"]


def obtener_ranking():
    """
    Objetivo:
        devuelve el ranking ordenado
        por cantidad de victorias.

    Parametros:
        ninguno.

    Retorna:
        list:
            lista de tuplas
            (jugador, datos),
            ordenada de mayor a menor.
    """

    ranking = cargar_ranking()

    ranking_ordenado = list(ranking.items())

    ranking_ordenado.sort(key=obtener_victorias,reverse=True)

    return ranking_ordenado