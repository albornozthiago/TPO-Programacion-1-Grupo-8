def crear_cubo(n):
    """
    Crea un cubo de dimensiones n x n x n.

    Recibe:
        n: tamaño del cubo. Por defecto vale 8.

    Devuelve:
        Una lista de listas de listas donde todas las celdas
        comienzan como aguasinexplorar.
    """
    cubo = []
    for z in range(n):
        capa = []
        for x in range(n):
            fila = []
            for y in range(n):
                fila.append(aguasinexplorar)
            capa.append(fila)
        cubo.append(capa)
    return cubo

#analizar si hace falta crear una función o no
def tamanio_cubo(cubo):
    """
    Devuelve el tamaño N del cubo.

    Recibe:
        cubo: cubo de juego.

    Devuelve:
        Cantidad de capas del cubo.
    """

    return len(cubo)

def punto_valido(cubo, punto):
    """
    Indica si un punto pertenece al cubo.

    Las coordenadas recibidas usan el formato del usuario:
    (z, x, y), comenzando desde 1.

    Recibe:
        cubo: cubo de juego.
        punto: tres valores (z, x, y).

    Devuelve:
        True si el punto es válido.
        False en caso contrario.
    """

    if len(punto) != 3:
        return False
    z = punto[0]
    x = punto[1]
    y = punto[2]
    n = len(cubo)
    if z < 1 or z > n:
        return False
    if x < 1 or x > n:
        return False
    if y < 1 or y > n:
        return False
    return True


def convertir_indices(punto):
    """
    Las coordenadas del usuario empiezan en 1, las direcciones de las listas en Python empiezan en 0.
    Convierte coordenadas de usuario a índices de Python.

    Esta función comienza con _ porque está pensada
    para uso interno del módulo.
    """

    z = punto[0] - 1
    x = punto[1] - 1
    y = punto[2] - 1

    return z, x, y

def leer_celda(cubo, punto):
    """
    Devuelve el contenido de una celda del cubo.

    Recibe:
        cubo: cubo de juego.
        punto: coordenadas (z, x, y).

    Devuelve:
        El contenido de la celda.

    Si el punto no es válido devuelve None.
    """

    if not punto_valido(cubo, punto):
        return None
    z, x, y = convertir_indices(punto)
    return cubo[z][x][y]

def escribir_celda(cubo, punto, estado):
    """
    Modifica una celda del cubo.

    Recibe:
        cubo: cubo de juego.
        punto: coordenadas (z, x, y).
        estado: nuevo estado de la celda.

    Devuelve:
        True si pudo realizar la modificación.
        False si el punto no es válido.
    """

    if not punto_valido(cubo, punto):
        return False
    z, x, y = convertir_indices(punto)
    cubo[z][x][y] = estado
    return True

def obtener_plano_z(cubo, z):
    """
    Obtiene un plano completo del cubo fijando el eje z.

    Recibe:
        cubo: cubo de juego.
        z: número de capa, comenzando desde 1.

    Devuelve:
        Una matriz con el plano solicitado.

        Devuelve None si z no es válido.
    """

    n = len(cubo)
    if z < 1 or z > n:
        return None
    indice_z = z - 1
    plano = []
    for y in range(n):
        fila = []
        for x in range(n):
            fila.append(cubo[indice_z][x][y])
        plano.append(fila)
    return plano


def dibujar_plano_z(cubo, z):
    """
    Genera una representación en texto de un plano de z.

    No utiliza print porque tablero.py es un módulo de dominio.
    La función devuelve el texto para que partida.py pueda
    mostrarlo.

    Recibe:
        cubo: cubo de juego.
        z: número de capa.

    Devuelve:
        String con la representación del plano.
        Devuelve None si z no es válido.
    """
    plano = obtener_plano_z(cubo, z)
    if plano is None:
        return None
    n = len(cubo)
    texto = ""
    texto += "========= CAPA z = " + str(z) + " =========\n"
    texto += "    "
    for x in range(1, n + 1):
        texto += "x" + str(x) + " "
    texto += "\n"
    for y in range(n):
        texto += "y" + str(y + 1) + "  "
        for x in range(n):
            texto += str(plano[y][x]) + "  "
        texto += "\n"
    texto += "\n"
    texto += "Referencias: "
    texto += "~ sin explorar  "
    texto += "o agua  "
    texto += "X impacto  "
    texto += "# hundido  "
    texto += "? detectado"
    return texto

def copiar_matriz(matriz):
    """
    Realiza una copia independiente de una matriz.

    Recibe:
        matriz: lista de listas.

    Devuelve:
        Una nueva matriz con los mismos valores.
    """

    copia = []
    for fila in matriz:
        nueva_fila = []
        for elemento in fila:
            nueva_fila.append(elemento)
        copia.append(nueva_fila)
    return copia


def fila_minima(matriz):
    """
    Devuelve el índice de la fila cuya suma es menor.

    Recibe:
        matriz: matriz rectangular de números.

    Devuelve:
        Índice de la fila con menor suma.
    """
    sumas = []
    for fila in matriz:
        sumas.append(sum(fila))
    minimo = sumas.index(min(sumas))
    return minimo


def columna_maxima(matriz):
    """
    Devuelve el índice de la columna cuyo promedio es mayor.

    Recibe:
        matriz: matriz rectangular de números.

    Devuelve:
        Índice de la columna con mayor promedio.
    """
    promedios = []
    cantidad_filas = len(matriz)
    cantidad_columnas = len(matriz[0])
    for columna in range(cantidad_columnas):
        suma = 0
        for fila in range(cantidad_filas):
            suma += matriz[fila][columna]
        promedio = suma / cantidad_filas
        promedios.append(promedio)
    maximo = promedios.index(max(promedios))
    return maximo

aguasinexplorar = "~"
naveoculta = "N"
aguamarcada = "o"
impacto = "X"
hundido = "#"
detectado = "?"
rango = 8

#prueba
tablero=crear_cubo(rango)
print(dibujar_plano_z(tablero, 1))