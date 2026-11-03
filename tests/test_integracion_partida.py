import armamento
import partida
import tablero
import flota


def test_turno_descuenta_municion_solo_al_atacante():
    """
    Comprueba que un turno descuente municion
    solamente al jugador que realiza el disparo.
    """
    jugador1 = partida.crear_jugador(
        "Jugador 1", tablero.crear_cubo(5), []
    )

    jugador2 = partida.crear_jugador(
        "Jugador 2", tablero.crear_cubo(5), []
    )

    estado = {
        "jugadores": [jugador1, jugador2],
        "turno": 0,
        "numero_turno": 1,
        "ganador": None,
        "historial": [],
        "ultimo_resultado": None
    }

    jugada = {
        "arma": "R",
        "punto": (3, 3, 3)
    }

    partida.ejecutar_turno(estado, jugada)

    assert jugador1["municion"]["R"] == 2
    assert jugador2["municion"]["R"] == 3

def test_turno_sonar():
    """
    Comprueba que el sonar funcione durante un turno,
    detecte una nave y descuente municion al atacante.
    """
    jugador1 = partida.crear_jugador(
        "Jugador 1", tablero.crear_cubo(5), []
    )

    jugador2 = partida.crear_jugador(
        "Jugador 2", tablero.crear_cubo(5), []
    )

    tablero.escribir_celda(
        jugador2["cubo"], (3, 4, 4), tablero.NAVE_OCULTA
    )

    estado = {
        "jugadores": [jugador1, jugador2],
        "turno": 0,
        "numero_turno": 1,
        "ganador": None,
        "historial": [],
        "ultimo_resultado": None,
        "n": 5
    }

    jugada = {
        "arma": "S",
        "eje": "z",
        "valor": 3
    }

    partida.ejecutar_turno(estado, jugada)

    assert jugador1["municion"]["S"] == 3
    assert jugador2["municion"]["S"] == 4

    assert tablero.leer_celda(
        jugador2["cubo"], (3, 4, 4)
    ) == tablero.NAVE_OCULTA


def test_turno_recompensa_estacion():
    """
    Comprueba que hundir una estacion orbital durante
    un turno entregue municion al atacante.
    """
    jugador1 = partida.crear_jugador(
        "Jugador 1", tablero.crear_cubo(8), []
    )

    jugador2 = partida.crear_jugador(
        "Jugador 2", tablero.crear_cubo(8), []
    )

    resultado_ubicacion = flota.ubicar_nave(
        jugador2["cubo"],
        jugador2["flota"],
        "E",
        (3, 3, 3),
        (4, 4, 4)
    )

    assert resultado_ubicacion is not None

    puntos = jugador2["flota"][0]["puntos"]

    estado = {
        "jugadores": [jugador1, jugador2],
        "turno": 0,
        "numero_turno": 1,
        "ganador": None,
        "historial": [],
        "ultimo_resultado": None,
        "n": 8
    }

    municion_inicial = jugador1["municion"]["R"]

    # Dañamos siete celdas directamente para preparar el escenario.
    for punto in puntos[:-1]:
        armamento.torpedo(
            jugador2["cubo"],
            punto,
            jugador2["flota"]
        )

    assert jugador2["flota"][0]["estado"] != flota.NAVE_HUNDIDA

    # El ultimo impacto ocurre durante un turno real.
    jugada = {
        "arma": "T",
        "punto": puntos[-1]
    }

    partida.ejecutar_turno(estado, jugada)

    assert jugador2["flota"][0]["estado"] == flota.NAVE_HUNDIDA
    assert jugador1["municion"]["R"] == municion_inicial + 1
    assert jugador2["municion"]["R"] == municion_inicial