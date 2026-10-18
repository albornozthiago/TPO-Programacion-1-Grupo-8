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
    Comprueba que el misil de racimo consuma una municion
    por uso y no permita consumir cuando se agota.
    """
    armamento.catalogo_armas["R"]["municion"] = 3

    assert armamento.consumir_municion("R") == True
    assert armamento.catalogo_armas["R"]["municion"] == 2

    assert armamento.consumir_municion("R") == True
    assert armamento.consumir_municion("R") == True

    assert armamento.catalogo_armas["R"]["municion"] == 0
    assert armamento.consumir_municion("R") == False

    # Restauramos la munición para no afectar otras pruebas.
    armamento.catalogo_armas["R"]["municion"] = 3


def test_ejecutar_disparo():
    """
    Comprueba que ejecutar_disparo utilice el arma elegida
    y descuente correctamente su municion.
    """
    cubo = tablero.crear_cubo(5)

    armamento.catalogo_armas["R"]["municion"] = 3

    resultado = armamento.ejecutar_disparo(cubo, "R", (3, 3, 3))

    assert len(resultado) == 7
    assert armamento.catalogo_armas["R"]["municion"] == 2

    armamento.catalogo_armas["R"]["municion"] = 3


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
    cuando su municion se encuentra agotada.
    """
    cubo = tablero.crear_cubo(5)

    armamento.catalogo_armas["R"]["municion"] = 0

    resultado = armamento.ejecutar_disparo(cubo, "R", (3, 3, 3))

    assert resultado == "Sin municion"

    armamento.reiniciar_municion()

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

    resultado = armamento.ejecutar_disparo(
        cubo, "T", (3, 3, 3), flota_jugador=naves
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