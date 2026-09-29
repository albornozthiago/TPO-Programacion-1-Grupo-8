import tablero
import armamento


def test_torpedo_agua():
    """
    Comprueba que un torpedo sobre agua devuelva "Agua"
    y marque la celda como agua disparada.
    """
    cubo = tablero.crear_cubo(8)

    resultado = armamento.torpedo(cubo, (1, 1, 1))

    assert resultado == "Agua"
    assert tablero.leer_celda(cubo, (1, 1, 1)) == tablero.aguamarcada


def test_torpedo_impacto():
    """
    Comprueba que un torpedo sobre una nave devuelva "Impacto"
    y marque la celda como impactada.
    """
    cubo = tablero.crear_cubo(8)
    tablero.escribir_celda(cubo, (2, 2, 2), tablero.naveoculta)

    resultado = armamento.torpedo(cubo, (2, 2, 2))

    assert resultado == "Impacto"
    assert tablero.leer_celda(cubo, (2, 2, 2)) == tablero.impacto


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