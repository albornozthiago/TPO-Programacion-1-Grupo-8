import json

import pytest

import registro


# =========================================================
# AYUDAS
# =========================================================

@pytest.fixture(autouse=True)
def carpeta_temporal(tmp_path, monkeypatch):
    """
    Cada prueba trabaja en una carpeta temporal, para no tocar
    los archivos reales de datos/.
    """
    monkeypatch.chdir(tmp_path)


def historial_de_ejemplo():
    historial = registro.inicio_historial()
    registro.registro_turno(historial, 1, "Ana", "T", (1, 1, 1), ["Agua"])
    registro.registro_turno(historial, 2, "Beto", "T", (2, 2, 2), ["Impacto"])
    registro.registro_turno(historial, 3, "Ana", "R", (3, 3, 3), ["Impacto", "Agua"])
    registro.registro_turno(historial, 4, "Beto", "T", (1, 2, 3), ["Nave hundida"])
    return historial


# =========================================================
# historial
# =========================================================

def test_inicio_historial_es_lista_vacia():
    assert registro.inicio_historial() == []


def test_registro_turno_agrega_la_accion():
    historial = registro.inicio_historial()

    accion = registro.registro_turno(historial, 1, "Ana", "T", (1, 2, 3), ["Agua"])

    assert historial == [accion]
    assert accion["jugador"] == "Ana"
    assert accion["turno"] == 1
    assert accion["arma"] == "T"
    assert accion["punto"] == (1, 2, 3)
    assert accion["resultado"] == ["Agua"]


def test_turno_jugador_filtra_por_jugador():
    historial = historial_de_ejemplo()

    acciones = registro.turno_jugador(historial, "Ana")

    assert len(acciones) == 2
    assert acciones[0]["turno"] == 1
    assert acciones[1]["turno"] == 3


def test_turno_jugador_inexistente_devuelve_lista_vacia():
    assert registro.turno_jugador(historial_de_ejemplo(), "Zoe") == []


def test_mostrar_historial_vacio():
    texto = registro.mostrar_historial([])

    assert "No se registraron" in texto


def test_mostrar_historial_incluye_los_datos_del_disparo():
    historial = registro.inicio_historial()
    registro.registro_turno(historial, 1, "Ana", "R", (1, 2, 3), ["Impacto", "Agua"])

    texto = registro.mostrar_historial(historial)

    assert "Turno 1" in texto
    assert "Ana" in texto
    assert "Arma: R" in texto
    assert "(1,2,3)" in texto
    assert "Impacto, Agua" in texto


# =========================================================
# estadisticas
# =========================================================

def test_contar_resultados():
    conteo = registro.contar_resultados(historial_de_ejemplo())

    assert conteo == {"Agua": 2, "Impacto": 2, "Nave hundida": 1}


def test_contar_resultados_historial_vacio():
    assert registro.contar_resultados([]) == {}


def test_armas_usadas():
    historial = historial_de_ejemplo()

    assert registro.armas_usadas(historial, "Ana") == {"T": 1, "R": 1}
    assert registro.armas_usadas(historial, "Beto") == {"T": 2}


def test_estadisticas_jugador():
    historial = historial_de_ejemplo()

    datos = registro.estadisticas_jugador(historial, "Ana")

    assert datos["disparos"] == 2
    assert datos["impactos"] == 1
    assert datos["agua"] == 2
    assert datos["hundidas"] == 0
    assert datos["precision"] == 33


def test_estadisticas_jugador_con_hundida():
    datos = registro.estadisticas_jugador(historial_de_ejemplo(), "Beto")

    assert datos["disparos"] == 2
    assert datos["impactos"] == 2
    assert datos["hundidas"] == 1
    assert datos["precision"] == 100


def test_estadisticas_jugador_sin_disparos_tiene_precision_cero():
    datos = registro.estadisticas_jugador([], "Ana")

    assert datos["disparos"] == 0
    assert datos["precision"] == 0


def test_estadisticas_partida_incluye_a_todos():
    datos = registro.estadisticas_partida(historial_de_ejemplo(), ["Ana", "Beto"])

    assert set(datos.keys()) == {"Ana", "Beto"}
    assert datos["Ana"]["disparos"] == 2


def test_resumen_final_con_ganador():
    resumen = registro.resumen_final(historial_de_ejemplo(), ["Ana", "Beto"], "Beto")

    assert "RESUMEN DE LA PARTIDA" in resumen
    assert "Ganador: Beto" in resumen
    assert "Disparos totales: 4" in resumen
    assert "--- Ana ---" in resumen
    assert "T x1  R x1" in resumen


def test_resumen_final_sin_ganador_ni_armas():
    resumen = registro.resumen_final([], ["Ana"], None)

    assert "Ganador: sin ganador" in resumen
    assert "Armas usadas: ninguna" in resumen


# =========================================================
# nombre de partida
# =========================================================

@pytest.mark.parametrize("nombre", ["partida1", "mi_partida", "mi-partida", "A", "x" * 30])
def test_validar_nombre_partida_valido(nombre):
    assert registro.validar_nombre_partida(nombre) is True


@pytest.mark.parametrize("nombre", ["", "con espacio", "a/b", "../x", "ñandu", "x" * 31])
def test_validar_nombre_partida_invalido(nombre):
    with pytest.raises(registro.NombrePartidaInvalido):
        registro.validar_nombre_partida(nombre)


def test_validar_nombre_partida_no_texto():
    with pytest.raises(registro.NombrePartidaInvalido):
        registro.validar_nombre_partida(123)


def test_las_excepciones_heredan_de_registro_error():
    assert issubclass(registro.NombrePartidaInvalido, registro.RegistroError)
    assert issubclass(registro.PartidaNoEncontrada, registro.RegistroError)
    assert issubclass(registro.ErrorArchivoPartida, registro.RegistroError)


# =========================================================
# guardar y cargar partidas
# =========================================================

def test_guardar_y_cargar_partida():
    estado = {"turno": 1, "jugadores": ["Ana", "Beto"], "ganador": None}

    ruta = registro.guardar_partida(estado, "prueba")
    cargado = registro.cargar_partida("prueba")

    assert ruta.endswith("prueba.json")
    assert cargado == estado


def test_guardar_partida_nombre_invalido():
    with pytest.raises(registro.NombrePartidaInvalido):
        registro.guardar_partida({}, "nombre invalido")


def test_guardar_partida_con_datos_no_serializables():
    with pytest.raises(registro.ErrorArchivoPartida):
        registro.guardar_partida({"dato": {1, 2, 3}}, "prueba")


def test_cargar_partida_inexistente():
    with pytest.raises(registro.PartidaNoEncontrada):
        registro.cargar_partida("no_existe")


def test_cargar_partida_nombre_invalido():
    with pytest.raises(registro.NombrePartidaInvalido):
        registro.cargar_partida("../fuera")


def test_cargar_partida_con_archivo_danado():
    registro.guardar_partida({"a": 1}, "danada")
    with open("datos/partidas/danada.json", "w", encoding="utf-8") as archivo:
        archivo.write("{ esto no es json")

    with pytest.raises(registro.ErrorArchivoPartida):
        registro.cargar_partida("danada")


def test_listar_partidas_sin_carpeta():
    assert registro.listar_partidas() == []


def test_listar_partidas_ordenadas_y_sin_extension():
    registro.guardar_partida({}, "b_partida")
    registro.guardar_partida({}, "a_partida")
    with open("datos/partidas/otro.txt", "w", encoding="utf-8") as archivo:
        archivo.write("no es una partida")

    assert registro.listar_partidas() == ["a_partida", "b_partida"]


# =========================================================
# exportar resumen
# =========================================================

def test_exportar_resumen_crea_el_archivo():
    historial = historial_de_ejemplo()

    ruta = registro.exportar_resumen(historial, ["Ana", "Beto"], "Beto", "resumen1")

    assert ruta.endswith("resumen1.txt")
    with open(ruta, "r", encoding="utf-8") as archivo:
        contenido = archivo.read()
    assert contenido == registro.resumen_final(historial, ["Ana", "Beto"], "Beto")


def test_exportar_resumen_nombre_invalido():
    with pytest.raises(registro.NombrePartidaInvalido):
        registro.exportar_resumen([], ["Ana"], None, "nombre malo")


# =========================================================
# ranking
# =========================================================

def test_cargar_ranking_sin_archivo():
    assert registro.cargar_ranking() == {}


def test_guardar_y_cargar_ranking():
    ranking = {"Ana": {"partidas": 2, "victorias": 1}}

    registro.guardar_ranking(ranking)

    assert registro.cargar_ranking() == ranking


def test_cargar_ranking_danado():
    registro.guardar_ranking({})
    with open(registro.ARCHIVO_RANKING, "w", encoding="utf-8") as archivo:
        archivo.write("[[")

    with pytest.raises(registro.ErrorArchivoPartida):
        registro.cargar_ranking()


def test_actualizar_ranking_suma_partidas_y_victorias():
    ranking = registro.actualizar_ranking(["Ana", "Beto"], "Ana")

    assert ranking["Ana"] == {"partidas": 1, "victorias": 1}
    assert ranking["Beto"] == {"partidas": 1, "victorias": 0}


def test_actualizar_ranking_acumula_entre_partidas():
    registro.actualizar_ranking(["Ana", "Beto"], "Ana")
    ranking = registro.actualizar_ranking(["Ana", "Beto"], "Beto")

    assert ranking["Ana"] == {"partidas": 2, "victorias": 1}
    assert ranking["Beto"] == {"partidas": 2, "victorias": 1}


def test_actualizar_ranking_sin_ganador():
    ranking = registro.actualizar_ranking(["Ana", "Beto"], None)

    assert ranking["Ana"]["victorias"] == 0
    assert ranking["Beto"]["victorias"] == 0


def test_actualizar_ranking_persiste_en_el_archivo():
    registro.actualizar_ranking(["Ana", "Beto"], "Ana")

    with open(registro.ARCHIVO_RANKING, "r", encoding="utf-8") as archivo:
        guardado = json.load(archivo)

    assert guardado["Ana"]["victorias"] == 1


def test_obtener_victorias():
    assert registro.obtener_victorias(("Ana", {"partidas": 3, "victorias": 2})) == 2


def test_obtener_ranking_ordenado_por_victorias():
    registro.guardar_ranking({
        "Ana": {"partidas": 3, "victorias": 1},
        "Beto": {"partidas": 3, "victorias": 3},
        "Cami": {"partidas": 3, "victorias": 2}
    })

    ranking = registro.obtener_ranking()

    assert [jugador for jugador, datos in ranking] == ["Beto", "Cami", "Ana"]
