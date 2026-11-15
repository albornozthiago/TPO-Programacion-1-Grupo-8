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


"""ENTREGA 3: recorridos alternativos"""

def sin_repetidos(puntos):
    """Devuelve True si ningún punto aparece dos veces en la lista."""
    for i in range(0, len(puntos)):
        if puntos[i] in puntos[i + 1:]:
            return False
    return True


def test_recorrido_por_capas_completo():
    cubo = tablero.crear_cubo(3)
    puntos = tablero.recorrido_por_capas(cubo)
    assert len(puntos) == 27
    assert sin_repetidos(puntos)


def test_recorrido_por_capas_orden():
    cubo = tablero.crear_cubo(3)
    puntos = tablero.recorrido_por_capas(cubo)
    assert puntos[0] == [1, 1, 1]
    assert puntos[1] == [1, 2, 1]      
    assert puntos[3] == [1, 1, 2]      
    assert puntos[9] == [2, 1, 1]     
    assert puntos[-1] == [3, 3, 3]


def test_recorrido_espiral_completo():
    cubo = tablero.crear_cubo(4)
    puntos = tablero.recorrido_espiral(cubo)
    assert len(puntos) == 64
    assert sin_repetidos(puntos)


def test_recorrido_espiral_orden_de_una_capa():
    cubo = tablero.crear_cubo(3)
    puntos = tablero.recorrido_espiral(cubo)
    primera_capa = puntos[0:9]
    assert primera_capa == [[1, 1, 1], [1, 2, 1], [1, 3, 1],
                            [1, 3, 2], [1, 3, 3], [1, 2, 3],
                            [1, 1, 3], [1, 1, 2], [1, 2, 2]]


def test_recorrido_espiral_cubo_de_uno():
    cubo = tablero.crear_cubo(1)
    assert tablero.recorrido_espiral(cubo) == [[1, 1, 1]]


def test_recorrido_desde_punto_completo():
    cubo = tablero.crear_cubo(4)
    puntos = tablero.recorrido_desde_punto(cubo, [2, 2, 2])
    assert len(puntos) == 64
    assert sin_repetidos(puntos)


def test_recorrido_desde_punto_empieza_por_el_punto_y_sus_vecinos():
    cubo = tablero.crear_cubo(4)
    puntos = tablero.recorrido_desde_punto(cubo, [2, 2, 2])
    assert puntos[0] == [2, 2, 2]
    vecinos = tablero.vecinos_ortogonales(cubo, [2, 2, 2])
    for vecino in vecinos:
        assert vecino in puntos[1:7]


def test_recorrido_desde_punto_se_aleja_de_a_poco():
    cubo = tablero.crear_cubo(4)
    puntos = tablero.recorrido_desde_punto(cubo, [1, 1, 1])
    distancias = []
    for p in puntos:
        distancias.append((p[0] - 1) + (p[1] - 1) + (p[2] - 1))
    assert distancias == sorted(distancias)


def test_recorrido_desde_punto_invalido():
    cubo = tablero.crear_cubo(4)
    assert tablero.recorrido_desde_punto(cubo, [0, 1, 1]) is None