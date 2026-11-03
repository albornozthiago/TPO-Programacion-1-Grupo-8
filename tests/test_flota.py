import tablero
import flota
 
 
# =========================================================
# AYUDA: cubo nuevo de 8 x 8 x 8 para cada prueba
# =========================================================
 
def nuevo_cubo():
    return tablero.crear_cubo(8)
 
 
# =========================================================
# cantidad_ubicada
# =========================================================
 
def test_cantidad_ubicada_flota_vacia():
    assert flota.cantidad_ubicada([], "F") == 0
 
 
def test_cantidad_ubicada_cuenta_solo_el_tipo_pedido():
    naves = [
        {"tipo": "F", "puntos": []},
        {"tipo": "F", "puntos": []},
        {"tipo": "D", "puntos": []},
    ]
    assert flota.cantidad_ubicada(naves, "F") == 2
    assert flota.cantidad_ubicada(naves, "D") == 1
    assert flota.cantidad_ubicada(naves, "S") == 0
 
 
# =========================================================
# generar_puntos_lineales
# =========================================================
 
def test_puntos_lineales_eje_z():
    puntos = flota.generar_puntos_lineales((2, 5, 5), (4, 5, 5), 3)
    assert puntos == [(2, 5, 5), (3, 5, 5), (4, 5, 5)]
 
 
def test_puntos_lineales_eje_x():
    puntos = flota.generar_puntos_lineales((3, 1, 4), (3, 2, 4), 2)
    assert puntos == [(3, 1, 4), (3, 2, 4)]
 
 
def test_puntos_lineales_eje_y():
    puntos = flota.generar_puntos_lineales((3, 3, 1), (3, 3, 3), 3)
    assert puntos == [(3, 3, 1), (3, 3, 2), (3, 3, 3)]
 
 
def test_puntos_lineales_acepta_extremos_al_reves():
    puntos = flota.generar_puntos_lineales((4, 5, 5), (2, 5, 5), 3)
    assert puntos == [(2, 5, 5), (3, 5, 5), (4, 5, 5)]
 
 
def test_puntos_lineales_largo_incorrecto_devuelve_none():
    assert flota.generar_puntos_lineales((2, 5, 5), (5, 5, 5), 3) is None
 
 
def test_puntos_lineales_en_diagonal_devuelve_none():
    assert flota.generar_puntos_lineales((1, 1, 1), (2, 2, 1), 2) is None
 
 
# =========================================================
# generar_puntos_estacion
# =========================================================
 
def test_puntos_estacion_son_ocho():
    puntos = flota.generar_puntos_estacion((3, 3, 3), (4, 4, 4))
    assert len(puntos) == 8
    assert (3, 3, 3) in puntos
    assert (4, 4, 4) in puntos
 
 
def test_puntos_estacion_que_no_es_bloque_devuelve_none():
    assert flota.generar_puntos_estacion((3, 3, 3), (3, 4, 4)) is None
    assert flota.generar_puntos_estacion((3, 3, 3), (6, 6, 6)) is None
 
 
# =========================================================
# distancia_valida
# =========================================================
 
def una_fragata():
    return [{"tipo": "F", "puntos": [(3, 3, 3), (3, 3, 4)]}]
 
 
def test_distancia_pegada_es_invalida():
    assert flota.distancia_valida(una_fragata(), [(3, 3, 5), (3, 3, 6)]) is False
 
 
def test_distancia_en_diagonal_es_invalida():
    assert flota.distancia_valida(una_fragata(), [(4, 4, 5), (4, 4, 6)]) is False
 
 
def test_distancia_con_una_celda_libre_es_valida():
    assert flota.distancia_valida(una_fragata(), [(3, 3, 6), (3, 3, 7)]) is True
 
 
def test_distancia_con_flota_vacia_es_valida():
    assert flota.distancia_valida([], [(1, 1, 1)]) is True
 
 
# =========================================================
# ubicar_nave: casos correctos
# =========================================================
 
def test_ubicar_nave_correcta_agrega_a_la_flota_y_marca_el_cubo():
    cubo = nuevo_cubo()
    naves = []
 
    cubo, naves = flota.ubicar_nave(cubo, naves, "F", (3, 3, 3), (3, 3, 4))
 
    assert len(naves) == 1
    assert naves[0]["tipo"] == "F"
    assert naves[0]["puntos"] == [(3, 3, 3), (3, 3, 4)]
    assert tablero.leer_celda(cubo, (3, 3, 3)) == tablero.NAVE_OCULTA
    assert tablero.leer_celda(cubo, (3, 3, 4)) == tablero.NAVE_OCULTA
    assert tablero.leer_celda(cubo, (3, 3, 5)) == tablero.AGUA_SIN_EXPLORAR
 
 
def test_ubicar_nave_acepta_letra_en_minuscula():
    cubo, naves = flota.ubicar_nave(nuevo_cubo(), [], "f", (3, 3, 3), (3, 3, 4))
    assert naves[0]["tipo"] == "F"
 
 
def test_ubicar_cada_tipo_en_un_lugar_valido():
    casos = [
        ("F", (3, 3, 3), (3, 3, 4)),
        ("D", (3, 3, 3), (3, 3, 5)),
        ("S", (2, 2, 2), (2, 2, 4)),
        ("C", (4, 1, 1), (4, 1, 4)),
        ("P", (6, 2, 2), (6, 2, 6)),
        ("E", (3, 3, 3), (4, 4, 4)),
    ]
    for tipo, desde, hasta in casos:
        cubo, naves = flota.ubicar_nave(nuevo_cubo(), [], tipo, desde, hasta)
        assert len(naves) == 1
 
 
# =========================================================
# ubicar_nave: casos que deben fallar
# =========================================================
 
def test_ubicar_tipo_inexistente_falla():
    assert flota.ubicar_nave(nuevo_cubo(), [], "X", (1, 1, 1), (1, 1, 2)) is None
 
 
def test_ubicar_nave_fuera_del_cubo_falla():
    assert flota.ubicar_nave(nuevo_cubo(), [], "F", (8, 8, 8), (8, 8, 9)) is None
 
 
def test_ubicar_nave_con_largo_incorrecto_falla():
    assert flota.ubicar_nave(nuevo_cubo(), [], "F", (3, 3, 3), (3, 3, 5)) is None
 
 
def test_ubicar_nave_que_toca_a_otra_falla():
    cubo, naves = flota.ubicar_nave(nuevo_cubo(), [], "F", (3, 3, 3), (3, 3, 4))
    assert flota.ubicar_nave(cubo, naves, "F", (4, 4, 5), (4, 4, 6)) is None
 
 
def test_ubicar_mas_naves_que_la_cantidad_permitida_falla():
    cubo = nuevo_cubo()
    naves = []
    cubo, naves = flota.ubicar_nave(cubo, naves, "F", (1, 1, 1), (1, 1, 2))
    cubo, naves = flota.ubicar_nave(cubo, naves, "F", (1, 4, 1), (1, 4, 2))
    cubo, naves = flota.ubicar_nave(cubo, naves, "F", (1, 7, 1), (1, 7, 2))
    assert flota.ubicar_nave(cubo, naves, "F", (5, 5, 5), (5, 5, 6)) is None
 
 
def test_submarino_en_mitad_superior_falla():
    assert flota.ubicar_nave(nuevo_cubo(), [], "S", (6, 2, 2), (6, 2, 4)) is None
 
 
def test_portaaviones_en_mitad_inferior_falla():
    assert flota.ubicar_nave(nuevo_cubo(), [], "P", (2, 2, 2), (2, 2, 6)) is None
 
 
def test_crucero_en_z_1_falla():
    assert flota.ubicar_nave(nuevo_cubo(), [], "C", (1, 1, 1), (1, 1, 4)) is None
 
 
def test_crucero_en_z_n_falla():
    assert flota.ubicar_nave(nuevo_cubo(), [], "C", (8, 1, 1), (8, 1, 4)) is None
 
 
def test_estacion_tocando_una_cara_exterior_falla():
    assert flota.ubicar_nave(nuevo_cubo(), [], "E", (1, 3, 3), (2, 4, 4)) is None
 
 
def test_ubicacion_fallida_no_modifica_cubo_ni_flota():
    cubo = nuevo_cubo()
    naves = []
    assert flota.ubicar_nave(cubo, naves, "C", (1, 1, 1), (1, 1, 4)) is None
    assert naves == []
    assert tablero.leer_celda(cubo, (1, 1, 1)) == tablero.AGUA_SIN_EXPLORAR
 
 
# =========================================================
# naves_pendientes y flota_completa
# =========================================================
 
def test_naves_pendientes_con_flota_vacia():
    pendientes = flota.naves_pendientes([])
    assert pendientes == {"F": 3, "D": 2, "S": 2, "C": 1, "P": 1, "E": 1}
 
 
def test_naves_pendientes_descuenta_las_ubicadas():
    cubo, naves = flota.ubicar_nave(nuevo_cubo(), [], "F", (3, 3, 3), (3, 3, 4))
    assert flota.naves_pendientes(naves)["F"] == 2
 
 
def test_flota_completa_false_si_falta_alguna():
    assert flota.flota_completa([]) is False
 
 
# =========================================================
# ubicacion_automatica
# =========================================================
 
def test_ubicacion_automatica_ubica_toda_la_flota():
    for semilla in range(30):
        cubo = nuevo_cubo()
        naves = flota.ubicacion_automatica(cubo, flota.CATALOGO_NAVES, semilla)
        assert naves is not None, "no pudo ubicar la flota con la semilla " + str(semilla)
        assert flota.flota_completa(naves)
        assert len(naves) == 10
 
 
def test_ubicacion_automatica_misma_semilla_misma_flota():
    flota_1 = flota.ubicacion_automatica(nuevo_cubo(), flota.CATALOGO_NAVES, 7)
    flota_2 = flota.ubicacion_automatica(nuevo_cubo(), flota.CATALOGO_NAVES, 7)
    assert flota_1 == flota_2
 
 
def test_ubicacion_automatica_respeta_las_restricciones():
    cubo = nuevo_cubo()
    naves = flota.ubicacion_automatica(cubo, flota.CATALOGO_NAVES, 3)
    for nave in naves:
        assert flota.restriccion_nave(cubo, nave["tipo"], nave["puntos"])
 
 
def test_ubicacion_automatica_ninguna_nave_toca_a_otra():
    cubo = nuevo_cubo()
    naves = flota.ubicacion_automatica(cubo, flota.CATALOGO_NAVES, 3)
    for i in range(len(naves)):
        otras = naves[:i] + naves[i + 1:]
        assert flota.distancia_valida(otras, naves[i]["puntos"])
 
















