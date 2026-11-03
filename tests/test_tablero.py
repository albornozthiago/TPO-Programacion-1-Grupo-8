"""Pruebas de tablero.py (Entrega 2)"""

import tablero


def test_plano_x_toma_las_celdas_correctas():
    cubo = tablero.crear_cubo(4)
    tablero.escribir_celda(cubo, [3, 2, 4], tablero.IMPACTO)
    plano = tablero.obtener_plano_x(cubo, 2)
    assert plano[2][3] == tablero.IMPACTO      # fila z=3, columna y=4
    assert len(plano) == 4
    assert len(plano[0]) == 4


def test_plano_x_invalido():
    cubo = tablero.crear_cubo(4)
    assert tablero.obtener_plano_x(cubo, 0) is None
    assert tablero.obtener_plano_x(cubo, 5) is None


def test_plano_y_toma_las_celdas_correctas():
    cubo = tablero.crear_cubo(4)
    tablero.escribir_celda(cubo, [1, 3, 2], tablero.IMPACTO)
    plano = tablero.obtener_plano_y(cubo, 2)
    assert plano[0][2] == tablero.IMPACTO      # fila z=1, columna x=3


def test_plano_y_invalido():
    cubo = tablero.crear_cubo(4)
    assert tablero.obtener_plano_y(cubo, 9) is None


def test_dibujar_plano_x():
    cubo = tablero.crear_cubo(4)
    texto = tablero.dibujar_plano_x(cubo, 2)
    assert "CORTE x = 2" in texto
    assert "y1" in texto
    assert "z4" in texto


def test_dibujar_plano_y():
    cubo = tablero.crear_cubo(4)
    texto = tablero.dibujar_plano_y(cubo, 3)
    assert "CORTE y = 3" in texto
    assert "x1" in texto


def test_dibujar_plano_invalido():
    cubo = tablero.crear_cubo(4)
    assert tablero.dibujar_plano_x(cubo, 7) is None
    assert tablero.dibujar_plano_y(cubo, 0) is None


def test_vecinos_ortogonales_en_el_medio():
    cubo = tablero.crear_cubo(4)
    vecinos = tablero.vecinos_ortogonales(cubo, [2, 2, 2])
    assert len(vecinos) == 6
    assert [3, 2, 2] in vecinos
    assert [2, 2, 1] in vecinos


def test_vecinos_ortogonales_en_una_esquina():
    cubo = tablero.crear_cubo(4)
    vecinos = tablero.vecinos_ortogonales(cubo, [1, 1, 1])
    assert len(vecinos) == 3       


def test_vecinos_todos_en_el_medio():
    cubo = tablero.crear_cubo(4)
    vecinos = tablero.vecinos_todos(cubo, [2, 2, 2])
    assert len(vecinos) == 26
    assert [2, 2, 2] not in vecinos
    assert [3, 3, 3] in vecinos    


def test_vecinos_todos_en_una_esquina():
    cubo = tablero.crear_cubo(4)
    vecinos = tablero.vecinos_todos(cubo, [4, 4, 4])
    assert len(vecinos) == 7


def test_vecinos_punto_invalido():
    cubo = tablero.crear_cubo(4)
    assert tablero.vecinos_ortogonales(cubo, [0, 1, 1]) is None
    assert tablero.vecinos_todos(cubo, [5, 1, 1]) is None