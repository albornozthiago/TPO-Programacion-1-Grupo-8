def inicioHistorial():
    """Objetivo: crea la estructura principal en memoria para almacenar el historial.
    Parametros:
        ninguno
    Retorna:
        list: una lista vacía, lista para recibir acciones con registroTurno."""
    historial = []
    return historial

def registroTurno(historial, turno, jugador, codigo_arma, punto, resultado):
    """Objetivo: guarda los detalles de un disparo en el historial.
    Parametros:
      historial (list): la lista del historial, se modifica en el lugar.
      turno (int): numero de turno en el que ocurrio el disparo.
      jugador (str): nombre o identificador de quien disparo.
      codigo_arma (str): codigo del arma usada, segun el catalogo de armamento.py.
      punto (tup): coordenadas (z, x, y) del disparo, en ese orden.
      resultado (str): desenlace del disparo tal como lo devuelve armamento.py.
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

def turnoJugador(historial,jugador):
    """Objetivo: filtra el historial y devuelve solo las acciones de un jugador puntual.
    Parametros:
      historial (list): la lista completa del historial.
      jugador (str): el jugador por el que se quiere filtrar.
    Retorna:
      turno (list): las acciones (diccionarios) cuyo "jugador" coincide con el pedido."""
    turno = [accion for accion in historial if accion["jugador"] == jugador]
    return turno

def mostrarHistorial(historial):
    """Objetivo: arma el texto del historial completo, listo para mostrar por pantalla.
    No imprime nada: devuelve el string para que partida.py decida cuando
    y como mostrarlo (por ejemplo, con print()).
    Parametros:
      historial (list): la lista completa del historial.
    Retorna:
      partidaActual (str): una linea de texto por cada disparo registrado, o un mensaje
        indicando que el historial esta vacio si no hubo disparos todavia."""
    partidaActual = ""
    if not historial:
        return "-- No se registraron partidas hasta el momento --"
    for accion in historial:
        z, x, y = accion["punto"]
        partidaActual += f"Turno {accion['turno']} | {accion['jugador']} "
        partidaActual += f"| Arma: {accion['arma']} | Coord: ({z},{x},{y}) -- Resultado: {accion['resultado']} --\n"
    return partidaActual

