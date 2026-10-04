import tablero

# Catálogo de armas
catalogo_armas = {
    "T": {"nombre": "Torpedo", "municion": None},
    "R": {"nombre": "Misil de racimo", "municion": 3},
    "C": {"nombre": "Carga de profundidad", "municion": 2},
    "S": {"nombre": "Sonar", "municion": 4},
    "L": {"nombre": "Barrido laser", "municion": 2},
    "O": {"nombre": "Onda expansiva", "municion": 1},
    "G": {"nombre": "Torpedo guiado", "municion": 1}
}


def obtener_arma(codigo):
    """
    Recibe el código de un arma y devuelve su información.
    Si el código no existe, devuelve None.
    """
    return catalogo_armas.get(codigo)


def torpedo(cubo, punto):
    """
    Recibe el cubo y el punto al que se dispara.
    Devuelve el resultado del disparo y modifica la celda correspondiente.
    """

    if not tablero.punto_valido(cubo, punto):
        return "Punto invalido"

    celda = tablero.leer_celda(cubo, punto)

    if celda == tablero.AGUA_SIN_EXPLORAR:
        tablero.escribir_celda(cubo, punto, tablero.AGUA_MARCADA)
        return "Agua"

    if celda == tablero.NAVE_OCULTA:
        tablero.escribir_celda(cubo, punto, tablero.IMPACTO)
        return "Impacto"

    if celda == tablero.AGUA_MARCADA:
        return "Celda ya disparada"

    if celda == tablero.IMPACTO:
        return "Celda ya disparada"

    if celda == tablero.HUNDIDO:
        return "Celda ya disparada"