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
    assert len(puntos) == 16
    assert all(isinstance(p, tuple) for p in puntos)
    assert all(p[0] == 3 for p in puntos)


def test_puntos_del_plano_otros_ejes():
    cubo = tablero.crear_cubo(3)
    assert all(p[1] == 2 for p in radar.puntos_del_plano(cubo, "x", 2))
    assert all(p[2] == 1 for p in radar.puntos_del_plano(cubo, "y", 1))


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
