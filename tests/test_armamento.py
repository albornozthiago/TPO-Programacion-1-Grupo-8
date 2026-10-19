import tablero
import armamento
import flota


def test_torpedo_agua():
    """
    Comprueba que un torpedo sobre agua devuelva "Agua"
    y marque la celda como agua disparada.
    """
    cubo = tablero.crear_cubo(8)

    resultado = armamento.torpedo(cubo, (1, 1, 1))

    assert resultado == "Agua"
    assert tablero.leer_celda(cubo, (1, 1, 1)) == tablero.AGUA_MARCADA


def test_torpedo_impacto():
    """
    Comprueba que un torpedo sobre una nave devuelva "Impacto"
    y marque la celda como impactada.
    """
    cubo = tablero.crear_cubo(8)
    tablero.escribir_celda(cubo, (2, 2, 2), tablero.NAVE_OCULTA)

    resultado = armamento.torpedo(cubo, (2, 2, 2))

    assert resultado == "Impacto"
    assert tablero.leer_celda(cubo, (2, 2, 2)) == tablero.IMPACTO


def test_torpedo_punto_invalido():
    """
    Comprueba que un punto fuera del cubo sea rechazado.
    """
    cubo = tablero.crear_cubo(8)

    resultado = armamento.torpedo(cubo, (9, 9, 9))

    assert resultado == "Punto invalido"


def test_torpedo_repetido():
    """
    Comprueba que no se pueda volver a disparar
    sobre una celda ya disparada.
    """
    cubo = tablero.crear_cubo(8)

    armamento.torpedo(cubo, (1, 1, 1))
    resultado = armamento.torpedo(cubo, (1, 1, 1))

    assert resultado == "Celda ya disparada"


def test_misil_racimo():
    """
    Comprueba que el misil de racimo afecte las 7 celdas
    correspondientes y registre correctamente los disparos.
    """
    cubo = tablero.crear_cubo(8)

    resultados = armamento.misil_racimo(cubo, (4, 4, 4))

    assert len(resultados) == 7
    assert resultados.count("Agua") == 7


def test_carga_profundidad():
    """
    Comprueba que la carga de profundidad dispare
    a todas las celdas del eje Z.
    """
    cubo = tablero.crear_cubo(5)

    resultados = armamento.carga_profundidad(cubo, (3, 2, 4))

    assert len(resultados) == 5
    assert resultados.count("Agua") == 5


def test_barrido_laser_x():
    """
    Comprueba que el barrido laser sobre el eje X
    afecte todas las celdas de la linea correspondiente.
    """
    cubo = tablero.crear_cubo(5)

    resultados = armamento.barrido_laser(cubo, (3, 2, 4), "x")

    assert len(resultados) == 5
    assert resultados.count("Agua") == 5


def test_barrido_laser_y():
    """
    Comprueba que el barrido laser sobre el eje Y
    afecte todas las celdas de la linea correspondiente.
    """
    cubo = tablero.crear_cubo(5)

    resultados = armamento.barrido_laser(cubo, (3, 2, 4), "y")

    assert len(resultados) == 5
    assert resultados.count("Agua") == 5


def test_consumir_municion():
    """
    Comprueba que la municion se descuente correctamente
    y que no se pueda utilizar un arma sin municion.
    """
    municion = armamento.crear_municion()

    assert armamento.consumir_municion("R", municion) == True
    assert municion["R"] == 2

    assert armamento.consumir_municion("R", municion) == True
    assert armamento.consumir_municion("R", municion) == True

    assert municion["R"] == 0
    assert armamento.consumir_municion("R", municion) == False


def test_ejecutar_disparo():
    """
    Comprueba que ejecutar_disparo utilice el arma elegida
    y descuente correctamente la municion del jugador.
    """
    cubo = tablero.crear_cubo(5)
    municion = armamento.crear_municion()

    resultado = armamento.ejecutar_disparo(
        cubo, "R", (3, 3, 3), municion
    )

    assert len(resultado) == 7
    assert municion["R"] == 2


def test_reiniciar_municion():
    """
    Comprueba que al reiniciar la municion
    las armas recuperen su cantidad inicial.
    """
    armamento.catalogo_armas["R"]["municion"] = 0

    armamento.reiniciar_municion()

    assert armamento.catalogo_armas["R"]["municion"] == 3


def test_racimo_punto_invalido():
    """
    Comprueba que el misil de racimo rechace
    un punto que se encuentra fuera del cubo.
    """
    cubo = tablero.crear_cubo(5)

    resultado = armamento.misil_racimo(cubo, (9, 9, 9))

    assert resultado == []

def test_racimo_esquina():
    """
    Comprueba que el misil de racimo no intente
    disparar fuera del cubo cuando apunta a una esquina.
    """
    cubo = tablero.crear_cubo(5)

    resultados = armamento.misil_racimo(cubo, (1, 1, 1))

    assert len(resultados) == 4


def test_disparo_sin_municion():
    """
    Comprueba que no se pueda disparar un arma
    cuando su municion esta agotada.
    """
    cubo = tablero.crear_cubo(5)
    municion = armamento.crear_municion()

    municion["R"] = 0

    resultado = armamento.ejecutar_disparo(
        cubo, "R", (3, 3, 3), municion
    )

    assert resultado == "Sin municion"

def test_torpedo_con_flota():
    """
    Comprueba que el torpedo pueda impactar una nave
    ubicada mediante el modulo flota.
    """
    cubo = tablero.crear_cubo(8)
    naves = []

    resultado_ubicacion = flota.ubicar_nave(
        cubo, naves, "F", (3, 3, 3), (3, 3, 4)
    )

    assert resultado_ubicacion is not None

    municion = armamento.crear_municion()

    resultado = armamento.ejecutar_disparo(
        cubo, "T", (3, 3, 3), municion, flota_jugador=naves
    )

    assert resultado == "Nave averiada"
    assert tablero.leer_celda(cubo, (3, 3, 3)) == tablero.IMPACTO
    assert naves[0]["impactos"] == [(3, 3, 3)]
    assert naves[0]["estado"] == flota.NAVE_AVERIADA


def test_torpedo_hunde_nave_y_actualiza_todas_sus_celdas():
    cubo = tablero.crear_cubo(8)
    naves = []
    flota.ubicar_nave(cubo, naves, "F", (3, 3, 3), (3, 3, 4))

    assert armamento.torpedo(cubo, (3, 3, 3), naves) == "Nave averiada"
    resultado = armamento.torpedo(cubo, (3, 3, 4), naves)

    assert resultado == "Nave hundida"
    assert naves[0]["estado"] == flota.NAVE_HUNDIDA
    assert naves[0]["impactos"] == [(3, 3, 3), (3, 3, 4)]
    assert tablero.leer_celda(cubo, (3, 3, 3)) == tablero.HUNDIDO
    assert tablero.leer_celda(cubo, (3, 3, 4)) == tablero.HUNDIDO

def test_municion_independiente():
    """
    Comprueba que cada jugador tenga su propia municion
    y que los disparos de uno no afecten al otro.
    """
    jugador1 = armamento.crear_municion()
    jugador2 = armamento.crear_municion()

    armamento.consumir_municion("R", jugador1)

    assert jugador1["R"] == 2
    assert jugador2["R"] == 3

def test_torpedo_celda_detectada():
    """
    Comprueba que un torpedo pueda disparar sobre
    una celda previamente detectada por sonar.
    """
    cubo = tablero.crear_cubo(5)

    tablero.escribir_celda(cubo, (2, 2, 2), tablero.DETECTADO)

    resultado = armamento.torpedo(cubo, (2, 2, 2))

    assert resultado == "Agua"
    assert tablero.leer_celda(cubo, (2, 2, 2)) == tablero.AGUA_MARCADA

def test_laser_no_dana_submarino():
    """
    Comprueba que el barrido laser no produzca
    impactos sobre un submarino.
    """
    cubo = tablero.crear_cubo(8)
    naves = []

    flota.ubicar_nave(
        cubo, naves, "S", (2, 3, 3), (2, 3, 5)
    )

    resultados = armamento.barrido_laser(
        cubo, (2, 3, 3), "y", naves
    )

    assert resultados.count("Submarino inmune") == 3

    assert tablero.leer_celda(cubo, (2, 3, 3)) == tablero.NAVE_OCULTA
    assert tablero.leer_celda(cubo, (2, 3, 4)) == tablero.NAVE_OCULTA
    assert tablero.leer_celda(cubo, (2, 3, 5)) == tablero.NAVE_OCULTA

    assert naves[0]["impactos"] == []
    assert naves[0]["estado"] == flota.NAVE_INTACTA

def test_recompensa_estacion_orbital():
    """
    Comprueba que hundir una estacion orbital
    entregue municion adicional una sola vez.
    """
    cubo = tablero.crear_cubo(8)
    naves = []
    municion = armamento.crear_municion()

    resultado_ubicacion = flota.ubicar_nave(
        cubo, naves, "E", (3, 3, 3), (4, 4, 4)
    )

    assert resultado_ubicacion is not None

    municion_inicial = municion["R"]

    puntos_estacion = naves[0]["puntos"]

    for punto in puntos_estacion[:-1]:
        armamento.ejecutar_disparo(
            cubo, "T", punto, municion, flota_jugador=naves
        )

    assert municion["R"] == municion_inicial

    armamento.ejecutar_disparo(
        cubo, "T", puntos_estacion[-1], municion, flota_jugador=naves
    )

    assert naves[0]["estado"] == flota.NAVE_HUNDIDA
    assert municion["R"] == municion_inicial + 1

    armamento.ejecutar_disparo(
        cubo, "T", puntos_estacion[-1], municion, flota_jugador=naves
    )

    assert municion["R"] == municion_inicial + 1

def test_sonar_integrado():
    """
    Comprueba que el sonar detecte naves,
    no produzca daños y consuma municion.
    """
    cubo = tablero.crear_cubo(8)
    municion = armamento.crear_municion()

    tablero.escribir_celda(
        cubo, (3, 4, 5), tablero.NAVE_OCULTA
    )

    resultado = armamento.ejecutar_disparo(
        cubo, "S", (3, 3, 3), municion, eje="z"
    )

    assert [3, 4, 5] in resultado
    assert municion["S"] == 3

    assert tablero.leer_celda(
        cubo, (3, 4, 5)
    ) == tablero.NAVE_OCULTA