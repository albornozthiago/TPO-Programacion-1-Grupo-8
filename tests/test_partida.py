import flota
import partida


# =========================================================
# leer_tramo
# =========================================================

def test_leer_tramo_valido():
    assert partida.leer_tramo("3,5,4-3,5,5") == ((3, 5, 4), (3, 5, 5))


def test_leer_tramo_con_espacios():
    assert partida.leer_tramo(" 3 , 5 , 4 - 3 , 5 , 5 ") == ((3, 5, 4), (3, 5, 5))


def test_leer_tramo_con_numeros_de_dos_cifras():
    assert partida.leer_tramo("10,1,1-10,1,2") == ((10, 1, 1), (10, 1, 2))


def test_leer_tramo_con_letras_devuelve_none():
    assert partida.leer_tramo("a,5,4-3,5,5") is None
    assert partida.leer_tramo("abc") is None


def test_leer_tramo_incompleto_devuelve_none():
    assert partida.leer_tramo("3,5,4") is None
    assert partida.leer_tramo("3,5-3,5") is None
    assert partida.leer_tramo("3,5,4-") is None
    assert partida.leer_tramo("") is None


def test_leer_tramo_con_negativos_devuelve_none():
    assert partida.leer_tramo("-3,5,4-3,5,5") is None


# =========================================================
# opcion_valida
# =========================================================

def test_opcion_valida_existente():
    assert partida.opcion_valida("1", partida.MENU_PRINCIPAL) is True
    assert partida.opcion_valida("5", partida.MENU_PRINCIPAL) is True


def test_opcion_valida_fuera_del_menu():
    assert partida.opcion_valida("9", partida.MENU_PRINCIPAL) is False
    assert partida.opcion_valida("0", partida.MENU_PRINCIPAL) is False


def test_opcion_valida_texto_no_numerico():
    assert partida.opcion_valida("a", partida.MENU_PRINCIPAL) is False
    assert partida.opcion_valida("", partida.MENU_PRINCIPAL) is False
    assert partida.opcion_valida("1 2", partida.MENU_PRINCIPAL) is False


# =========================================================
# nave_valida
# =========================================================

def test_nave_valida_con_pendientes():
    pendientes = {"F": 3, "D": 2, "S": 2, "C": 1, "P": 1, "E": 1}
    assert partida.nave_valida("F", pendientes) is True
    assert partida.nave_valida("E", pendientes) is True


def test_nave_valida_ya_ubicada():
    pendientes = {"F": 0, "D": 2, "S": 2, "C": 1, "P": 1, "E": 1}
    assert partida.nave_valida("F", pendientes) is False


def test_nave_valida_letra_inexistente():
    pendientes = {"F": 3, "D": 2, "S": 2, "C": 1, "P": 1, "E": 1}
    assert partida.nave_valida("X", pendientes) is False
    assert partida.nave_valida("FF", pendientes) is False
    assert partida.nave_valida("", pendientes) is False


# =========================================================
# texto_pendientes
# =========================================================

def test_texto_pendientes_flota_vacia():
    pendientes = {"F": 3, "D": 2, "S": 2, "C": 1, "P": 1, "E": 1}
    assert partida.texto_pendientes(pendientes) == "Pendientes: F x3  D x2  S x2  C x1  P x1  E x1"


def test_texto_pendientes_omite_los_completos():
    pendientes = {"F": 0, "D": 1, "S": 0, "C": 0, "P": 0, "E": 0}
    assert partida.texto_pendientes(pendientes) == "Pendientes: D x1"


# =========================================================
# ubicar_automaticamente
# =========================================================

def test_ubicar_automaticamente_completa_la_flota():
    cubo, naves = partida.ubicar_automaticamente(8)
    assert flota.flota_completa(naves)
    assert len(cubo) == 8
