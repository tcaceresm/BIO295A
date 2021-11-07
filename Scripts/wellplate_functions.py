from skimage import draw
import numpy as np
import pandas as pd



def obtener_datos():
    ''' Obtiene los valores introducidos por el usuario
        Retorna estos valores en forma de tuplas
    '''
    x0 = int(input('Introduce la coordenada X del pocillo del vertice superior izquierdo: '))
    y0 = int(input('Introduce la coordenada Y del pocillo del vertice superior izquierdo: '))
    x1 = int(input('\nIntroduce la coordenada X del pocillo del vertice superior derecho: '))
    y1 = int(input('Introduce la coordenada Y del pocillo del vertice superior derecho: '))
    x2 = int(input('\nIntroduce la coordenada X del pocillo del vertice inferior derecho: '))
    y2 = int(input('Introduce la coordenada Y del pocillo del vertice inferior derecho: '))
    x3 = int(input('\nIntroduce la coordenada X del pocillo del vertice inferior izquierdo: '))
    y3 = int(input('Introduce la coordenada Y del pocillo del vertice inferior izquierdo: '))
    tupla_coordenadas = (x0, y0, x1, y1, x2, y2, x3, y3)

    radio_pocillos = int(input('\nIntroduce el radio de los pocillos: '))

    coordX_background = int(input('\nIntroduce la coordenada X de la region background: '))
    coordY_background = int(input('Introduce la coordenada Y de la región background: '))
    tupla_bckground = (coordX_background, coordY_background)
    
    n_frames = int(input('\nIntroduce el número de frames: '))
    largo_imagen = int(input('Introduce el largo de la imagen, en pixeles: '))
    ancho_imagen = int(input('Introduce el ancho de la imagen, en pixeles: '))
    dimension = (n_frames, largo_imagen, ancho_imagen)

    return tupla_coordenadas, radio_pocillos, tupla_bckground, dimension

def coordenadas_pocillos(coordenadas, columns=12, rows=8):
    """
    Calcula las coordenadas de todos los pocillos de la placa.

Parameters
----------
    
coordinadas : tuple

    Coordenadas del centro de los pocillos de los vértices de la placa

columns : int

    Número de columnas en la placa. Por default, columns=12. Requiere de revisión
    en caso de más columnas.

rows : int

    Numero de filas en la placa. Por default, rows=8. Requiere de revisión
    en caso de más filas.

Returns
-------
Tuple

    Retorna una lista de tuplas con los valores de las coordenadas de todos los pocillos
"""
    # Asigno las coordenadas entregadas a una variable separada (tuple unpacking)
    x0, y0, x1, y1, x2, y2, x3, y3 = coordenadas

    #Distancia entre pocillos de cada columna
    x_dist = (np.abs(x1-x0)*(np.sqrt((y1-y0)**2 + (x1 - x0)**2) / (columns - 1)))/np.sqrt((y1-y0)**2 + (x1 - x0)**2)
    y_dist = (np.abs(y1-y0)*(np.sqrt((y1-y0)**2 + (x1 - x0)**2) / (columns - 1)))/np.sqrt((y1-y0)**2 + (x1 - x0)**2)
        
    #Distancia entre pocillos de cada fila
    x_dist2 = (np.abs(x0 - x3)*(np.sqrt((y3-y0)**2 + (x0 - x3)**2) / (rows - 1)))/np.sqrt((y3-y0)**2 + (x0 - x3)**2)
    y_dist2 = (np.abs(y3 - y0)*(np.sqrt((y3-y0)**2 + (x0 - x3)**2) / (rows - 1)))/np.sqrt((y3-y0)**2 + (x0 - x3)**2)

    #Obtención de las coordenadas de cada pocillo
    all_coordinates = []
    x = x0
    y = y0
    #se itera por cada fila
    for row in range(rows):
        #Al terminar de las coordenadas de todas las columnas de una fila...
        #...se reestablece la posicion al pocillo de más a la izquierda de la siguiente fila

        y = y0 + y_dist2*row
        x = x0 - x_dist2*row

        #Se itera por cada columna
        for col in range(columns):    
            # luego de calcular la coordenada de un pocillo de una columna, voy al siguiente pocillo
            # en la siguiente columna.
            all_coordinates.append((x, y))
            x += x_dist 
            y += y_dist

    return all_coordinates

def intensidad_pocillos(imagen, coordinate, radius, background,
                    dimension=(360, 1024, 1024), rows= 8, columns=12):
    """
    Calcula la intensidad promedio (en pixeles) de todos los pocillos.

Parameters
----------
imagen : numpy.ndarray

    Variable que contiene la imagen en forma de un numpy array.
    Recordar que al leer la imagen con el módulo io del paquete
    skimage, la imagen se lee como un numpy array.
    (imagen = io.imread("nombre_imagen.tif))
    
coordinate : tuple

    Coordenadas del centro de los pocillos

radius : int

    Radio en pixeles de los pocillos

background : tuple

    Coordenadas de la zona del background

dimension : tuple

    Contiene las dimensiones de la imagen. (N° de frames, largo  imagen en pixeles,
    ancho imagen en pixeles). Por default, (360, 1024, 1024)

rows : int
    Es la cantidad de filas que contiene la placa. Por default, 8. No se ha
    testeado con mas filas, aunque probablemente cause un bug.

columns: int
    Es la cantidad de columnas que contiene la placa. Por default, 12. Un número
    diferente de columnas es posible que cause bugs.

Returns
-------
Pandas Dataframe

    Retorna un dataframe con los valores de intensidad (en pixeles)
    de los 96 pocillos de la placa.
"""
    image = np.reshape(imagen, dimension)
    #n_frames = dimension[0]

    coordenadas = coordenadas_pocillos(coordinate)
    all_intensities = []

    #Itero por cada frame en la imagen
    for frames in image:

        frame_intensities = []
        
        #calculo el valor de intensidad del background
        bck1, bck2 = background
        bg_value = np.mean(frames[draw.circle(bck1, bck2, radius=radius, shape=frames.shape[0:2])])

        for pocillo in coordenadas:
            #Calculo la intensidad del pocillo
            x, y = pocillo
            mean = np.mean(frames[draw.circle(y, x, radius=radius, shape=frames.shape[0:2])]) - bg_value
            frame_intensities.append(mean)
            
        all_intensities.append(frame_intensities) 

    #Aca genero el dataframe, ademas de generar el nombre de cada columna y fila
    row = ['Frame ' + str(x) for x in range(1, len(all_intensities)+1)] 
    column = ['Well ' + str(k) for k in range(1, rows*columns+1)]
    df = pd.DataFrame(all_intensities, index=row, columns=column)

    return df

def normalize(df):
    """
    Normaliza los valores entre 0 y 1 de todos los valores entregados
    en el dataframe

Parameters
----------
    
df : Pandas Dataframe

Returns
-------
Pandas DataFrame

    Retorna una dataframe con los valores normalizados entre 0 y 1
"""
    result = df.copy()
    max_value = max(df.max())
    min_value = max(df.min())
    for feature_name in df.columns:
        result[feature_name] = (df[feature_name] - min_value) / (max_value - min_value)
    return result

def segmentar(imagen, coordenadas, radio):
    """
    Se realiza un "masking" de la imagen a analizar. Es decir, seleccionamos
    sólo las regiones que nos interesan, e ignoramos el resto.

Parameters
----------
    
imagen : numpy.ndarray     (ski.imread())

Returns
-------
Pandas numpy.ndarray

    Retorna un numpy array sólo con los valores (en pixel, que representa
    luminiscencia) de interés

"""

    mask = np.ones(shape=imagen[0].shape[0:2], dtype='bool')
    for coordenada in coordenadas:
        x, y = coordenada
        cc, rr = draw.circle(x, y, radius=radio, shape=imagen[0].shape[0:2])
        mask[rr, cc] = False
        imagen[0][rr, cc]
    imagen[0][mask] = 0
    return imagen[0]  
