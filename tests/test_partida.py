import pytest

import flota
import partida
import registro
import tablero


# =========================================================
# AYUDAS
# =========================================================

@pytest.fixture(autouse=True)
def carpeta_temporal(tmp_path, monkeypatch):
    """
    Las pruebas que guardan archivos trabajan en una carpeta temporal.
    """
    monkeypatch.chdir(tmp_path)


def cubo_con_fragata(desde, hasta, n=5):
    """
    Devuelve (cubo, flota) con una sola fragata ubicada.
    """
    cubo = tablero.crear_cubo(n)
    resultado = flota.ubicar_nave(cubo, [], "F", desde, hasta)
    assert resultado is not None
    return resultado


def configuracion_1v1():
    cubo1, flota1 = cubo_con_fragata((1, 1, 1), (1, 1, 2))
    cubo2, flota2 = cubo_con_fragata((2, 2, 2), (2, 2, 3))
    return {
        "n": 5,
        "nombre_jugador1": "Ana",
        "cubo_jugador1": cubo1,
        "flota_jugador1": flota1,
        "nombre_jugador2": "Beto",
        "cubo_jugador2": cubo2,
        "flota_jugador2": flota2
    }


def estado_1v1():
    return partida.nueva_partida_1v1(configuracion_1v1())


def configuracion_maquinas():
    cubo1, flota1 = cubo_con_fragata((1, 1, 1), (1, 1, 2))
    cubo2, flota2 = cubo_con_fragata((2, 2, 2), (2, 2, 3))
    return {
        "n": 5,
        "cubo_maquina1": cubo1,
        "flota_maquina1": flota1,
        "cubo_maquina2": cubo2,
        "flota_maquina2": flota2
    }


def entradas(monkeypatch, respuestas):
    """
    Reemplaza input() por una lista de respuestas.
    """
    lista = list(respuestas)

    def falso_input(texto=""):
        return lista.pop(0)

    monkeypatch.setattr("builtins.input", falso_input)


# =========================================================
# validaciones de texto
# =========================================================

def test_leer_tramo_valido():
    assert partida.leer_tramo("3,5,4-3,5,5") == ((3, 5, 4), (3, 5, 5))


def test_leer_tramo_con_espacios():
    assert partida.leer_tramo("3, 5, 4 - 3, 5, 5") == ((3, 5, 4), (3, 5, 5))


@pytest.mark.parametrize("texto", ["", "abc", "1,2,3", "1,2-3,4", "1,2,3-4,5"])
def test_leer_tramo_invalido(texto):
    assert partida.leer_tramo(texto) is None


def test_leer_punto_valido():
    assert partida.leer_punto("1,2,3") == (1, 2, 3)
    assert partida.leer_punto(" 4 , 5 , 6 ") == (4, 5, 6)


@pytest.mark.parametrize("texto", ["", "1,2", "a,b,c", "1,2,3,4", "-1,2,3"])
def test_leer_punto_invalido(texto):
    assert partida.leer_punto(texto) is None


def test_opcion_valida():
    menu = {"1": ("Uno", None), "2": ("Dos", None)}

    assert partida.opcion_valida("1", menu) is True
    assert partida.opcion_valida("3", menu) is False
    assert partida.opcion_valida("a", menu) is False
    assert partida.opcion_valida("", menu) is False


def test_nave_valida():
    pendientes = {"F": 1, "D": 0}

    assert partida.nave_valida("F", pendientes) is True
    assert partida.nave_valida("D", pendientes) is False


def test_nave_valida_letra_inexistente():
    assert partida.nave_valida("X", {"F": 1}) is False


def test_texto_pendientes_omite_los_que_estan_en_cero():
    texto = partida.texto_pendientes({"F": 3, "D": 0, "S": 2})

    assert texto == "Pendientes: F x3  S x2"


def test_pedir_opcion_repite_hasta_que_sea_valida(monkeypatch, capsys):
    entradas(monkeypatch, ["x", "9", "2"])
    menu = {"1": ("Uno", None), "2": ("Dos", None)}

    assert partida.pedir_opcion("Menu", menu) == "2"
    assert "Opcion invalida" in capsys.readouterr().out


def test_pedir_punto_repite_hasta_que_sea_valido(monkeypatch):
    entradas(monkeypatch, ["hola", "1,2", "3,4,5"])

    assert partida.pedir_punto() == (3, 4, 5)


# =========================================================
# jugadores y nuevas partidas
# =========================================================

def test_crear_jugador_humano():
    jugador = partida.crear_jugador("Ana", tablero.crear_cubo(5), [])

    assert jugador["nombre"] == "Ana"
    assert jugador["maquina"] is False
    assert jugador["detectados"] == []
    assert jugador["municion"]["R"] == 3


def test_crear_jugador_maquina_usa_basica_por_defecto():
    jugador = partida.crear_jugador("Maquina", tablero.crear_cubo(5), [], True)

    assert jugador["maquina"] is True
    assert jugador["dificultad"] == "basica"


def test_crear_jugador_dificultad_invalida():
    with pytest.raises(partida.JugadaInvalidaError):
        partida.crear_jugador("Maquina", tablero.crear_cubo(5), [], True, "experta")


def test_nueva_partida_1v1():
    estado = estado_1v1()

    assert estado["modo"] == "1v1"
    assert estado["turno"] == 0
    assert estado["numero_turno"] == 1
    assert estado["ganador"] is None
    assert estado["historial"] == []
    assert [j["nombre"] for j in estado["jugadores"]] == ["Ana", "Beto"]


def test_nueva_partida_1v1_falta_un_dato():
    configuracion = configuracion_1v1()
    del configuracion["n"]

    with pytest.raises(KeyError):
        partida.nueva_partida_1v1(configuracion)


def test_nueva_partida_vs_maquina():
    cubo1, flota1 = cubo_con_fragata((1, 1, 1), (1, 1, 2))
    cubo2, flota2 = cubo_con_fragata((2, 2, 2), (2, 2, 3))
    configuracion = {
        "n": 5,
        "nombre_jugador": "Ana",
        "cubo_jugador": cubo1,
        "flota_jugador": flota1,
        "cubo_maquina": cubo2,
        "flota_maquina": flota2
    }

    estado = partida.nueva_partida_vs_maquina(configuracion, "avanzada")

    assert estado["modo"] == "vs_maquina"
    assert estado["jugadores"][1]["maquina"] is True
    assert estado["jugadores"][1]["dificultad"] == "avanzada"


def test_nueva_partida_maquina_vs_maquina():
    estado = partida.nueva_partida_maquina_vs_maquina(
        configuracion_maquinas(), ["basica", "avanzada"]
    )

    assert estado["modo"] == "maquina_vs_maquina"
    assert estado["jugadores"][0]["nombre"] == "Maquina 1"
    assert estado["jugadores"][0]["dificultad"] == "basica"
    assert estado["jugadores"][1]["dificultad"] == "avanzada"
    assert estado["jugadores"][0]["maquina"] is True


def test_nueva_partida_maquina_vs_maquina_dificultad_invalida():
    with pytest.raises(partida.JugadaInvalidaError):
        partida.nueva_partida_maquina_vs_maquina(
            configuracion_maquinas(), ["basica", "imposible"]
        )


# =========================================================
# ganador
# =========================================================

def test_hay_ganador_sin_ganador():
    assert partida.hay_ganador(estado_1v1()) is None


def test_hay_ganador_cuando_se_hunde_la_flota_rival():
    estado = estado_1v1()
    for nave in estado["jugadores"][1]["flota"]:
        nave["estado"] = flota.NAVE_HUNDIDA

    assert partida.hay_ganador(estado) == "Ana"


def test_hay_ganador_gana_el_otro_si_se_hunde_mi_flota():
    estado = estado_1v1()
    for nave in estado["jugadores"][0]["flota"]:
        nave["estado"] = flota.NAVE_HUNDIDA

    assert partida.hay_ganador(estado) == "Beto"


# =========================================================
# turnos
# =========================================================

def test_ejecutar_turno_agua_cambia_el_turno_y_registra():
    estado = estado_1v1()

    partida.ejecutar_turno(estado, {"arma": "T", "punto": (5, 5, 5)})

    assert estado["turno"] == 1
    assert estado["numero_turno"] == 2
    assert len(estado["historial"]) == 1
    assert estado["historial"][0]["jugador"] == "Ana"
    assert estado["historial"][0]["arma"] == "T"


def test_ejecutar_turno_impacto_marca_la_celda():
    estado = estado_1v1()

    partida.ejecutar_turno(estado, {"arma": "T", "punto": (2, 2, 2)})

    cubo_rival = estado["jugadores"][1]["cubo"]
    assert tablero.leer_celda(cubo_rival, (2, 2, 2)) == tablero.IMPACTO


def test_ejecutar_turno_hunde_la_nave_y_termina_la_partida():
    estado = estado_1v1()

    partida.ejecutar_turno(estado, {"arma": "T", "punto": (2, 2, 2)})
    partida.ejecutar_turno(estado, {"arma": "T", "punto": (5, 5, 5)})
    partida.ejecutar_turno(estado, {"arma": "T", "punto": (2, 2, 3)})

    assert estado["ganador"] == "Ana"
    assert estado["turno"] == 0


def test_ejecutar_turno_con_partida_terminada():
    estado = estado_1v1()
    estado["ganador"] = "Ana"

    with pytest.raises(partida.PartidaFinalizadaError):
        partida.ejecutar_turno(estado, {"arma": "T", "punto": (5, 5, 5)})


def test_ejecutar_turno_arma_inexistente():
    with pytest.raises(partida.JugadaInvalidaError):
        partida.ejecutar_turno(estado_1v1(), {"arma": "Z", "punto": (1, 1, 1)})


def test_ejecutar_turno_punto_fuera_del_cubo():
    with pytest.raises(partida.JugadaInvalidaError):
        partida.ejecutar_turno(estado_1v1(), {"arma": "T", "punto": (9, 9, 9)})


def test_ejecutar_turno_celda_ya_disparada():
    estado = estado_1v1()
    partida.ejecutar_turno(estado, {"arma": "T", "punto": (5, 5, 5)})
    estado["turno"] = 0

    with pytest.raises(partida.JugadaInvalidaError):
        partida.ejecutar_turno(estado, {"arma": "T", "punto": (5, 5, 5)})


def test_ejecutar_turno_sin_municion():
    estado = estado_1v1()
    estado["jugadores"][0]["municion"]["R"] = 0

    with pytest.raises(partida.SinMunicionError):
        partida.ejecutar_turno(estado, {"arma": "R", "punto": (3, 3, 3)})


def test_las_excepciones_heredan_de_operacion_cubo_error():
    assert issubclass(partida.JugadaInvalidaError, partida.OperacionCuboError)
    assert issubclass(partida.SinMunicionError, partida.OperacionCuboError)
    assert issubclass(partida.PartidaFinalizadaError, partida.OperacionCuboError)


# =========================================================
# sonar
# =========================================================

def test_sonar_detecta_naves_y_guarda_los_contactos():
    estado = estado_1v1()

    partida.ejecutar_turno(estado, {"arma": "S", "eje": "z", "valor": 2})

    ana = estado["jugadores"][0]
    assert (2, 2, 2) in ana["detectados"]
    assert (2, 2, 3) in ana["detectados"]
    assert "2 contactos detectados" in estado["ultimo_resultado"]
    assert "(2,2,2)" in estado["ultimo_resultado"]
    assert ana["municion"]["S"] == 3


def test_sonar_en_plano_vacio():
    estado = estado_1v1()

    partida.ejecutar_turno(estado, {"arma": "S", "eje": "z", "valor": 5})

    assert estado["jugadores"][0]["detectados"] == []
    assert "0 contactos detectados" in estado["ultimo_resultado"]


def test_sonar_eje_invalido():
    with pytest.raises(partida.JugadaInvalidaError):
        partida.ejecutar_turno(estado_1v1(), {"arma": "S", "eje": "w", "valor": 1})


def test_sonar_valor_fuera_del_cubo():
    with pytest.raises(partida.JugadaInvalidaError):
        partida.ejecutar_turno(estado_1v1(), {"arma": "S", "eje": "z", "valor": 9})


def test_sonar_sin_municion():
    estado = estado_1v1()
    estado["jugadores"][0]["municion"]["S"] = 0

    with pytest.raises(partida.SinMunicionError):
        partida.ejecutar_turno(estado, {"arma": "S", "eje": "z", "valor": 1})


def test_vista_del_rival_oculta_naves_y_marca_detectadas():
    estado = estado_1v1()
    ana, beto = estado["jugadores"]
    ana["detectados"].append((2, 2, 2))

    vista = partida.vista_del_rival(ana, beto)

    assert tablero.leer_celda(vista, (2, 2, 2)) == tablero.DETECTADO
    assert tablero.leer_celda(vista, (2, 2, 3)) == tablero.AGUA_SIN_EXPLORAR
    assert tablero.leer_celda(beto["cubo"], (2, 2, 3)) == tablero.NAVE_OCULTA


def test_disparar_a_un_contacto_del_sonar_da_impacto():
    estado = estado_1v1()
    partida.ejecutar_turno(estado, {"arma": "S", "eje": "z", "valor": 2})
    estado["turno"] = 0

    partida.ejecutar_turno(estado, {"arma": "T", "punto": (2, 2, 2)})

    cubo_rival = estado["jugadores"][1]["cubo"]
    assert tablero.leer_celda(cubo_rival, (2, 2, 2)) == tablero.IMPACTO


# =========================================================
# maquina
# =========================================================

def test_puntos_sin_disparar_cubo_nuevo():
    cubo = tablero.crear_cubo(3)

    assert len(partida.puntos_sin_disparar(cubo, 3)) == 27


def test_puntos_sin_disparar_excluye_los_disparados():
    cubo = tablero.crear_cubo(3)
    tablero.escribir_celda(cubo, (1, 1, 1), tablero.AGUA_MARCADA)
    tablero.escribir_celda(cubo, (2, 2, 2), tablero.IMPACTO)

    puntos = partida.puntos_sin_disparar(cubo, 3)

    assert len(puntos) == 25
    assert (1, 1, 1) not in puntos
    assert (2, 2, 2) not in puntos


def test_elegir_punto_basico_devuelve_un_punto_disponible():
    cubo = tablero.crear_cubo(3)

    punto = partida.elegir_punto_basico(cubo, 3)

    assert punto in partida.puntos_sin_disparar(cubo, 3)


def test_elegir_punto_basico_sin_puntos_devuelve_none():
    cubo = tablero.crear_cubo(1)
    tablero.escribir_celda(cubo, (1, 1, 1), tablero.AGUA_MARCADA)

    assert partida.elegir_punto_basico(cubo, 1) is None


def test_elegir_punto_avanzado_remata_junto_a_un_impacto():
    cubo = tablero.crear_cubo(5)
    tablero.escribir_celda(cubo, (3, 3, 3), tablero.IMPACTO)

    punto = partida.elegir_punto_avanzado(cubo, 5)

    assert list(punto) in tablero.vecinos_ortogonales(cubo, (3, 3, 3))


def test_elegir_punto_avanzado_sin_impactos_devuelve_un_punto_valido():
    cubo = tablero.crear_cubo(5)

    punto = partida.elegir_punto_avanzado(cubo, 5)

    assert tablero.punto_valido(cubo, punto)


def test_estrategias_de_la_maquina():
    assert set(partida.ESTRATEGIAS_MAQUINA.keys()) == {"basica", "avanzada"}


def test_turno_maquina_dispara_y_cambia_el_turno():
    estado = partida.nueva_partida_maquina_vs_maquina(
        configuracion_maquinas(), ["basica", "avanzada"]
    )

    partida.turno_maquina(estado)

    assert estado["turno"] == 1
    assert len(estado["historial"]) == 1
    assert estado["ultima_jugada_maquina"] is not None


def test_turno_maquina_con_jugador_humano():
    with pytest.raises(partida.JugadaInvalidaError):
        partida.turno_maquina(estado_1v1())


@pytest.mark.parametrize("dificultades", [
    ["basica", "basica"],
    ["avanzada", "avanzada"],
    ["basica", "avanzada"],
])
def test_partida_maquina_contra_maquina_termina_con_ganador(dificultades):
    estado = partida.nueva_partida_maquina_vs_maquina(
        configuracion_maquinas(), dificultades
    )

    turnos = 0
    while estado["ganador"] is None and turnos < 1000:
        partida.turno_maquina(estado)
        turnos += 1

    assert estado["ganador"] in ("Maquina 1", "Maquina 2")


# =========================================================
# guardar y continuar
# =========================================================

def test_estado_para_guardar_se_puede_serializar():
    estado = estado_1v1()
    partida.ejecutar_turno(estado, {"arma": "T", "punto": (2, 2, 2)})

    datos = partida.estado_para_guardar(estado)

    registro.guardar_partida(datos, "serializable")
    assert datos["jugadores"][1]["flota"][0]["puntos"][0] == [2, 2, 2]


def test_estado_para_guardar_no_modifica_el_estado_original():
    estado = estado_1v1()

    partida.estado_para_guardar(estado)

    assert estado["jugadores"][0]["flota"][0]["puntos"][0] == (1, 1, 1)


def test_guardar_y_continuar_conserva_la_partida():
    estado = estado_1v1()
    partida.ejecutar_turno(estado, {"arma": "T", "punto": (2, 2, 2)})

    registro.guardar_partida(partida.estado_para_guardar(estado), "continuar")
    cargado = partida.reponer_estado(registro.cargar_partida("continuar"))

    assert cargado["turno"] == 1
    assert cargado["numero_turno"] == 2
    assert len(cargado["historial"]) == 1
    assert cargado["jugadores"][1]["flota"][0]["puntos"][0] == (2, 2, 2)
    assert cargado["jugadores"][1]["flota"][0]["estado"] == flota.NAVE_AVERIADA


def test_se_puede_seguir_jugando_despues_de_cargar():
    estado = estado_1v1()
    partida.ejecutar_turno(estado, {"arma": "T", "punto": (2, 2, 2)})
    registro.guardar_partida(partida.estado_para_guardar(estado), "seguir")
    cargado = partida.reponer_estado(registro.cargar_partida("seguir"))

    partida.ejecutar_turno(cargado, {"arma": "T", "punto": (5, 5, 5)})
    partida.ejecutar_turno(cargado, {"arma": "T", "punto": (2, 2, 3)})

    assert cargado["ganador"] == "Ana"


# =========================================================
# menus con entrada simulada
# =========================================================

def test_pedir_nombre_partida_repite_si_es_invalido(monkeypatch):
    entradas(monkeypatch, ["nombre malo", "../x", "buena_1"])

    assert partida.pedir_nombre_partida() == "buena_1"


def test_accion_guardar_y_salir_guarda_y_corta_el_ciclo(monkeypatch):
    entradas(monkeypatch, ["mi_partida"])
    estado = estado_1v1()

    seguir = partida.accion_guardar_y_salir(estado)

    assert seguir is False
    assert registro.listar_partidas() == ["mi_partida"]


def test_jugar_partida_guardar_y_salir_desde_el_menu(monkeypatch):
    entradas(monkeypatch, ["3", "salida"])
    estado = estado_1v1()

    partida.jugar_partida(estado)

    assert estado["ganador"] is None
    assert registro.listar_partidas() == ["salida"]


def test_jugar_partida_maquina_contra_maquina_cierra_con_ranking(monkeypatch):
    entradas(monkeypatch, ["2"])
    estado = partida.nueva_partida_maquina_vs_maquina(
        configuracion_maquinas(), ["avanzada", "basica"]
    )

    partida.jugar_partida(estado)

    assert estado["ganador"] is not None
    ranking = dict(registro.obtener_ranking())
    assert ranking[estado["ganador"]]["victorias"] == 1


def test_cerrar_partida_exporta_el_resumen(monkeypatch, capsys):
    entradas(monkeypatch, ["1", "exportado"])
    estado = estado_1v1()
    partida.ejecutar_turno(estado, {"arma": "T", "punto": (2, 2, 2)})
    partida.ejecutar_turno(estado, {"arma": "T", "punto": (5, 5, 5)})
    partida.ejecutar_turno(estado, {"arma": "T", "punto": (2, 2, 3)})

    partida.cerrar_partida(estado)

    assert "GANADOR: Ana" in capsys.readouterr().out
    with open("datos/exportaciones/exportado.txt", "r", encoding="utf-8") as archivo:
        assert "Ganador: Ana" in archivo.read()


def test_armas_disponibles_en_el_menu():
    assert set(partida.ACCIONES_ARMA.keys()) == {"T", "R", "C", "S", "L", "O", "G"}
