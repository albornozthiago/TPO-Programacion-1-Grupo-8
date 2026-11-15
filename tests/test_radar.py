import radar
import tablero


def cubo_con_nave(n, punto):
    cubo = tablero.crear_cubo(n)
    tablero.escribir_celda(cubo, punto, tablero.NAVE_OCULTA)
    return cubo


def test_busqueda_lineal_encuentra_la_nave():
    cubo = cubo_con_nave(4, (2, 3, 4))
    punto, metricas = radar.busqueda_lineal(cubo)
    assert punto == (2, 3, 4)
    assert metricas["comparaciones"] > 0


def test_busqueda_optimizada_encuentra_la_nave():
    cubo = cubo_con_nave(4, (2, 3, 4))
    punto, metricas = radar.busqueda_optimizada(cubo)
    assert punto == (2, 3, 4)
    assert metricas["comparaciones"] > 0


def test_busquedas_devuelven_tuplas():
    cubo = cubo_con_nave(3, (1, 1, 2))
    assert isinstance(radar.busqueda_lineal(cubo)[0], tuple)
    assert isinstance(radar.busqueda_optimizada(cubo)[0], tuple)


def test_busquedas_sin_nave_devuelven_none():
    cubo = tablero.crear_cubo(3)
    punto_l, metricas_l = radar.busqueda_lineal(cubo)
    punto_o, metricas_o = radar.busqueda_optimizada(cubo)
    assert punto_l is None
    assert punto_o is None
    assert metricas_l["comparaciones"] == 27
    assert metricas_o["comparaciones"] == 27


def test_busqueda_optimizada_no_supera_n_cubo_comparaciones():
    n = 4
    for punto in [(1, 1, 1), (4, 4, 4), (2, 2, 3), (3, 1, 2)]:
        cubo = cubo_con_nave(n, punto)
        _, metricas = radar.busqueda_optimizada(cubo)
        assert metricas["comparaciones"] <= n ** 3


def test_busqueda_optimizada_revisa_primero_la_paridad_cero():
    # (1, 1, 1) -> indices (0, 0, 0): suma par, se encuentra en la primera pasada
    cubo = cubo_con_nave(4, (1, 1, 1))
    punto, metricas = radar.busqueda_optimizada(cubo)
    assert punto == (1, 1, 1)
    assert metricas["comparaciones"] == 1


def test_busquedas_aceptan_objetivo_distinto():
    cubo = tablero.crear_cubo(3)
    tablero.escribir_celda(cubo, (3, 2, 1), tablero.IMPACTO)
    assert radar.busqueda_lineal(cubo, tablero.IMPACTO)[0] == (3, 2, 1)
    assert radar.busqueda_optimizada(cubo, tablero.IMPACTO)[0] == (3, 2, 1)


def test_metricas_tienen_las_tres_claves():
    cubo = cubo_con_nave(3, (2, 2, 2))
    _, metricas = radar.busqueda_lineal(cubo)
    assert set(metricas.keys()) == {"comparaciones", "tiempo_ms", "profundidad_max"}


def test_puntos_del_plano_cantidad_y_formato():
    cubo = tablero.crear_cubo(4)
    puntos = radar.puntos_del_plano(cubo, "z", 3)
    assert puntos is not None
    assert len(puntos) == 16
    assert all(isinstance(p, tuple) for p in puntos)
    assert all(p[0] == 3 for p in puntos)


def test_puntos_del_plano_otros_ejes():
    cubo = tablero.crear_cubo(3)
    plano_x = radar.puntos_del_plano(cubo, "x", 2)
    plano_y = radar.puntos_del_plano(cubo, "y", 1)
    assert plano_x is not None and plano_y is not None
    assert all(p[1] == 2 for p in plano_x)
    assert all(p[2] == 1 for p in plano_y)


def test_puntos_del_plano_invalidos_devuelven_none():
    cubo = tablero.crear_cubo(3)
    assert radar.puntos_del_plano(cubo, "w", 1) is None
    assert radar.puntos_del_plano(cubo, "z", 0) is None
    assert radar.puntos_del_plano(cubo, "z", 4) is None


def test_sonar_plano_detecta_solo_naves_del_plano():
    cubo = tablero.crear_cubo(4)
    tablero.escribir_celda(cubo, (2, 1, 1), tablero.NAVE_OCULTA)
    tablero.escribir_celda(cubo, (2, 4, 3), tablero.NAVE_OCULTA)
    tablero.escribir_celda(cubo, (3, 1, 1), tablero.NAVE_OCULTA)
    contactos = radar.sonar_plano(cubo, "z", 2)
    assert contactos is not None
    assert sorted(contactos) == [(2, 1, 1), (2, 4, 3)]


def test_sonar_plano_no_modifica_el_cubo():
    cubo = cubo_con_nave(3, (1, 2, 3))
    copia = [[fila[:] for fila in plano] for plano in cubo]
    radar.sonar_plano(cubo, "z", 1)
    assert cubo == copia


def test_sonar_plano_invalido_devuelve_none():
    cubo = tablero.crear_cubo(3)
    assert radar.sonar_plano(cubo, "q", 1) is None
    assert radar.sonar_plano(cubo, "z", 9) is None


# --- Entrega 3 ---
# Cada funcion tiene tres tests:
#   valido   -> un caso normal que tiene que funcionar
#   invalido -> un dato que esta mal o un caso donde no hay resultado
#   limite   -> el borde: cubo minimo, ultima capa, esquinas, empates


# busqueda_recursiva

def test_busqueda_recursiva_valido():
    cubo = cubo_con_nave(8, (6, 3, 4))
    punto, metricas = radar.busqueda_recursiva(cubo)
    assert punto == (6, 3, 4)
    assert metricas["comparaciones"] > 0
    assert metricas["profundidad_max"] == 4      # 8 capas: 8 -> 4 -> 2 -> 1


def test_busqueda_recursiva_invalido():
    # sin naves en el cubo: no encuentra nada, pero revisa las 27 celdas
    punto, metricas = radar.busqueda_recursiva(tablero.crear_cubo(3))
    assert punto is None
    assert metricas["comparaciones"] == 27
    # cubo vacio (sin capas): no se cuelga y devuelve None
    punto, metricas = radar.busqueda_recursiva([])
    assert punto is None
    assert metricas["comparaciones"] == 0


def test_busqueda_recursiva_limite():
    # cubo de 1 celda: el caso base se resuelve en la primera llamada
    punto, metricas = radar.busqueda_recursiva(cubo_con_nave(1, (1, 1, 1)))
    assert punto == (1, 1, 1)
    assert metricas["profundidad_max"] == 1
    # nave en la ultima celda del cubo: igual la encuentra
    cubo = cubo_con_nave(8, (8, 8, 8))
    assert radar.busqueda_recursiva(cubo)[0] == (8, 8, 8)
    # coincide con las otras dos busquedas
    assert radar.busqueda_lineal(cubo)[0] == radar.busqueda_recursiva(cubo)[0]


# recorrido_por_octantes

def test_recorrido_por_octantes_valido():
    puntos = radar.recorrido_por_octantes(tablero.crear_cubo(4))
    assert len(puntos) == 64
    assert len(set(puntos)) == 64                 # no repite celdas
    # primero termina el octante de abajo (z 1-2, x 1-2, y 1-2): 8 celdas
    assert set(puntos[:8]) == {(z, x, y) for z in (1, 2) for x in (1, 2) for y in (1, 2)}


def test_recorrido_por_octantes_invalido():
    # cubo sin capas: no hay nada que recorrer
    assert radar.recorrido_por_octantes([]) == []


def test_recorrido_por_octantes_limite():
    # cubo de 1 celda: caso base directo
    assert radar.recorrido_por_octantes(tablero.crear_cubo(1)) == [(1, 1, 1)]
    # N impar: las mitades no son iguales, pero igual cubre todo sin repetir
    puntos = radar.recorrido_por_octantes(tablero.crear_cubo(3))
    assert len(puntos) == 27
    assert len(set(puntos)) == 27
    assert puntos[0] == (1, 1, 1)
    assert puntos[-1] == (3, 3, 3)


# recorrer (despacho con el diccionario RECORRIDOS)

def test_recorrer_valido():
    # los cuatro recorridos cubren el cubo entero sin repetir
    cubo = tablero.crear_cubo(4)
    for nombre in radar.RECORRIDOS:
        puntos = radar.recorrer(cubo, nombre)
        assert puntos is not None
        assert len(puntos) == 64
        assert len(set(puntos)) == 64
        assert all(isinstance(p, tuple) for p in puntos)   # mismo formato


def test_recorrer_invalido():
    cubo = tablero.crear_cubo(3)
    try:
        radar.recorrer(cubo, "zigzag")           # no existe en RECORRIDOS
        assert False
    except KeyError:
        assert True
    # "desde un punto" con un inicio fuera del cubo
    assert radar.recorrer(cubo, "desde un punto", (5, 5, 5)) is None


def test_recorrer_limite():
    cubo = tablero.crear_cubo(3)
    # todos visitan exactamente las mismas celdas, en distinto orden
    conjuntos = []
    for nombre in radar.RECORRIDOS:
        puntos = radar.recorrer(cubo, nombre)
        assert puntos is not None
        conjuntos.append(set(puntos))
    for conjunto in conjuntos:
        assert conjunto == conjuntos[0]
    # "desde un punto" arranca en el punto pedido, aunque sea una esquina
    puntos = radar.recorrer(cubo, "desde un punto", (3, 3, 3))
    assert puntos is not None
    assert puntos[0] == (3, 3, 3)


# mapa_de_probabilidad

def test_mapa_de_probabilidad_valido():
    mapa = radar.mapa_de_probabilidad(tablero.crear_cubo(5), [2])
    # largo 2: el centro entra en 3 ejes x 2 sentidos, la esquina en 3
    assert mapa[2][2][2] == 6
    assert mapa[0][0][0] == 3
    assert mapa[2][2][2] > mapa[0][0][0]


def test_mapa_de_probabilidad_invalido():
    # una nave mas larga que el cubo no entra en ningun lado
    mapa = radar.mapa_de_probabilidad(tablero.crear_cubo(3), [5])
    assert all(v == 0 for capa in mapa for fila in capa for v in fila)
    # el agua marcada queda en 0
    cubo = tablero.crear_cubo(4)
    tablero.escribir_celda(cubo, (1, 1, 2), tablero.AGUA_MARCADA)
    assert radar.mapa_de_probabilidad(cubo, [2])[0][0][1] == 0


def test_mapa_de_probabilidad_limite():
    # agua al lado de la esquina: la esquina pierde la posicion que pasaba por ahi
    cubo = tablero.crear_cubo(4)
    tablero.escribir_celda(cubo, (1, 1, 2), tablero.AGUA_MARCADA)
    assert radar.mapa_de_probabilidad(cubo, [2])[0][0][0] == 2
    # nave del mismo largo que el cubo: entra justo, una posicion por eje
    mapa = radar.mapa_de_probabilidad(tablero.crear_cubo(3), [3])
    assert mapa[0][0][0] == 3
    assert mapa[1][1][1] == 3
    # cubo vacio (sin capas): devuelve un mapa vacio sin romperse
    assert radar.mapa_de_probabilidad([]) == []
    assert radar.celda_mas_probable([], []) is None


# celda_mas_probable

def test_celda_mas_probable_valido():
    cubo = tablero.crear_cubo(5)
    mapa = radar.mapa_de_probabilidad(cubo, [2, 3])
    assert radar.celda_mas_probable(cubo, mapa) == (3, 3, 3)


def test_celda_mas_probable_invalido():
    # el cubo entero ya disparado: no queda celda para elegir
    cubo = tablero.crear_cubo(2)
    puntos = radar.recorrer(cubo, "capas")
    assert puntos is not None
    for punto in puntos:
        tablero.escribir_celda(cubo, punto, tablero.AGUA_MARCADA)
    mapa = radar.mapa_de_probabilidad(cubo)
    assert radar.celda_mas_probable(cubo, mapa) is None


def test_celda_mas_probable_limite():
    # empate en todo el cubo de 2: elige la primera en orden z, x, y
    cubo = tablero.crear_cubo(2)
    mapa = radar.mapa_de_probabilidad(cubo, [2])
    assert radar.celda_mas_probable(cubo, mapa) == (1, 1, 1)
    # si el centro ya tiene un impacto, no lo vuelve a elegir
    cubo = tablero.crear_cubo(5)
    tablero.escribir_celda(cubo, (3, 3, 3), tablero.IMPACTO)
    mapa = radar.mapa_de_probabilidad(cubo, [2, 3])
    assert radar.celda_mas_probable(cubo, mapa) != (3, 3, 3)
