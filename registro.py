RESULTADO_AGUA = "Agua"
RESULTADO_HUNDIDA = "Nave hundida"
RESULTADOS_IMPACTO = ("Impacto", "Nave averiada", "Nave hundida")


def inicio_historial():
    """Objetivo: crea la estructura principal en memoria para almacenar el historial.
    Parametros:
        ninguno
    Retorna:
        list: una lista vacía, lista para recibir acciones con registro_turno."""
    historial = []
    return historial


def registro_turno(historial, turno, jugador, codigo_arma, punto, resultado):
    """Objetivo: guarda los detalles de un disparo en el historial.
    Parametros:
      historial (list): la lista del historial, se modifica en el lugar.
      turno (int): numero de turno en el que ocurrio el disparo.
      jugador (str): nombre o identificador de quien disparo.
      codigo_arma (str): codigo del arma usada, segun el catalogo de armamento.py.
      punto (tup): coordenadas (z, x, y) del disparo, en ese orden.
      resultado (list): lista con el resultado de cada celda afectada, tal como lo
        devuelve armamento.py. Un disparo a una sola celda se guarda como ["Agua"].
    Retorna:
      accion (dict): la accion que se acaba de guardar en el historial."""
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
    """Objetivo: filtra el historial y devuelve solo las acciones de un jugador puntual.
    Parametros:
      historial (list): la lista completa del historial.
      jugador (str): el jugador por el que se quiere filtrar.
    Retorna:
      turno (list): las acciones (diccionarios) cuyo "jugador" coincide con el pedido."""
    turno = [accion for accion in historial if accion["jugador"] == jugador]
    return turno


def mostrar_historial(historial):
    """Objetivo: arma el texto del historial completo, listo para mostrar por pantalla.
    No imprime nada: devuelve el string para que partida.py decida cuando
    y como mostrarlo (por ejemplo, con print()).
    Parametros:
      historial (list): la lista completa del historial.
    Retorna:
      partida_actual (str): una linea de texto por cada disparo registrado, o un mensaje
        indicando que el historial esta vacio si no hubo disparos todavia."""
    partida_actual = ""
    if not historial:
        return "-- No se registraron partidas hasta el momento --"
    for accion in historial:
        z, x, y = accion["punto"]
        resultado = ", ".join(accion["resultado"])
        partida_actual += f"Turno {accion['turno']} | {accion['jugador']} "
        partida_actual += f"| Arma: {accion['arma']} | Coord: ({z},{x},{y}) -- Resultado: {resultado} --\n"
    return partida_actual


def contar_resultados(historial):
    """Objetivo: cuenta cuantas veces aparecio cada resultado en el historial.
    Cada celda afectada por un disparo cuenta por separado.
    Parametros:
      historial (list): la lista completa del historial.
    Retorna:
      conteo (dict): {resultado: cantidad}, por ejemplo {"Agua": 4, "Impacto": 2}."""
    conteo = {}
    for accion in historial:
        for resultado in accion["resultado"]:
            conteo[resultado] = conteo.get(resultado, 0) + 1
    return conteo


def armas_usadas(historial, jugador):
    """Objetivo: cuenta cuantas veces uso cada arma un jugador.
    Parametros:
      historial (list): la lista completa del historial.
      jugador (str): el jugador a consultar.
    Retorna:
      conteo (dict): {codigo_arma: cantidad}, por ejemplo {"T": 5, "R": 1}."""
    conteo = {}
    for accion in turno_jugador(historial, jugador):
        arma = accion["arma"]
        conteo[arma] = conteo.get(arma, 0) + 1
    return conteo


def estadisticas_jugador(historial, jugador):
    """Objetivo: calcula las estadisticas de un jugador a partir del historial.
    Parametros:
      historial (list): la lista completa del historial.
      jugador (str): el jugador a consultar.
    Retorna:
      estadisticas (dict): con las claves
        "disparos": cantidad de acciones del jugador,
        "impactos": celdas con impacto (impacto, nave averiada o nave hundida),
        "agua": celdas con agua,
        "hundidas": naves hundidas,
        "precision": porcentaje entero de impactos sobre (impactos + agua),
          redondeado hacia abajo; vale 0 si todavia no hubo ni impactos ni agua."""
    acciones = turno_jugador(historial, jugador)
    conteo = contar_resultados(acciones)
    impactos = 0
    for resultado in RESULTADOS_IMPACTO:
        impactos += conteo.get(resultado, 0)
    agua = conteo.get(RESULTADO_AGUA, 0)
    try:
        precision = impactos * 100 // (impactos + agua)
    except ZeroDivisionError:
        precision = 0
    estadisticas = {
        "disparos": len(acciones),
        "impactos": impactos,
        "agua": agua,
        "hundidas": conteo.get(RESULTADO_HUNDIDA, 0),
        "precision": precision
    }
    return estadisticas


def estadisticas_partida(historial, jugadores):
    """Objetivo: calcula las estadisticas de todos los jugadores de la partida.
    Parametros:
      historial (list): la lista completa del historial.
      jugadores (list): nombres de los jugadores, por ejemplo ["Jugador 1", "Maquina"].
    Retorna:
      estadisticas (dict): {jugador: estadisticas_jugador(...)} para cada jugador."""
    estadisticas = {jugador: estadisticas_jugador(historial, jugador) for jugador in jugadores}
    return estadisticas


def resumen_final(historial, jugadores, ganador):
    """Objetivo: arma el texto con el resumen de la partida al terminar.
    No imprime nada: devuelve el string para que partida.py lo muestre.
    Parametros:
      historial (list): la lista completa del historial.
      jugadores (list): nombres de los jugadores.
      ganador (str o None): nombre del ganador, o None si la partida no tuvo ganador.
    Retorna:
      resumen (str): texto de varias lineas con el ganador, los disparos totales y
        las estadisticas y armas usadas de cada jugador."""
    estadisticas = estadisticas_partida(historial, jugadores)
    resumen = "===== RESUMEN DE LA PARTIDA =====\n"
    if ganador is None:
        resumen += "Ganador: sin ganador\n"
    else:
        resumen += f"Ganador: {ganador}\n"
    resumen += f"Disparos totales: {len(historial)}\n"
    for jugador in jugadores:
        datos = estadisticas[jugador]
        armas = armas_usadas(historial, jugador)
        armas_texto = "  ".join([f"{arma} x{cantidad}" for arma, cantidad in armas.items()])
        if armas_texto == "":
            armas_texto = "ninguna"
        resumen += f"\n--- {jugador} ---\n"
        resumen += f"Disparos: {datos['disparos']} | Impactos: {datos['impactos']} | Agua: {datos['agua']}\n"
        resumen += f"Naves hundidas: {datos['hundidas']} | Precision: {datos['precision']}%\n"
        resumen += f"Armas usadas: {armas_texto}\n"
    return resumen