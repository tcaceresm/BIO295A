from skimage import draw
import numpy as np
import pandas as pd

def obtener_datos():
    frames = int(input("Introduzca el número de frames: "))

    background_x = int(input("Introduzca la coordenada X de la " +
                            "región background: "))
    background_y = int(input("Introduzca la coordenada Y de la " +
                           "región background: "))
    
    background = (background_x, background_y)
    bck_radio = int(input("Introduzca el valor del radio de la zona background: "))
    radio = int(input("Introduzca el valor de radio a utilizar en las regiones de interés: "))

    #Obtengo las coordenadas de las regiones a analizar
    coordenadas = []
    agregar_region = True
    print('Se procederá a solicitar las coordenadas X e Y de las regiones de interés')
    x = int(input("Ingrese la coordenada X de la región 1: "))
    y = int(input("Ingrese la coordenada Y de la región 1: "))
    coordenadas.append((x, y))

    i = 2
    while agregar_region:
        agregar_region = input("¿Desea agregar otra región?: y/n ")
        if agregar_region.lower() == 'n':
            agregar_region = False

        elif agregar_region.lower() == 'y':
            x = int(input(f"Ingrese la coordenada X de la región {i}: "))
            y = int(input(f"Ingrese la coordenada Y de la región {i}: "))
            coordenadas.append((x, y))
            i += 1
        
        else:
            print('Por favor, introduce "y" o "n"') 

    return frames, background, radio, bck_radio, coordenadas

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

def intensidad_region(image, coordenadas, background, radius, bckground_radius, frames=162):
    """
    Calcula el promedio del valor de los pixeles de las regiones de interes.
    Está corregido por el background

Parameters
----------
    
image : numpy.ndarray     (ski.imread()


coordenadas : list of tuples

    Es una lista que contiene las tuplas de coordenadas de interés.

background : tuple

    Tupla que representa las coordenadas de la región background

radius : int

    El radio deseado de las regiones de interés

bckground_radius : int

    El radio deseado de la región background

frames : int

    Numero de frames que posee el archivo de imagen

Returns
-------
Pandas DataFrame

    Retorna un dataframe de dimensiones N° regiones x N° frames. Cada
    fila representa el valor de intensidad (en pixeles). Cada columna
    representa una región.
"""

    all_intensity = [] #Contendrá la intensidad de las regiones en todos los frames
    
    for coordenada in coordenadas: 
        frame_intensity = [] #Intensidad de la region en cada frame
        for frame in range(frames):
            bg_value = (np.mean(image[frame][draw.circle(background[1], background[0], bckground_radius)]))
            valor_1 = (np.mean(image[frame][draw.circle(coordenada[1], coordenada[0], radius)])) - bg_value
            frame_intensity.append(valor_1)
        all_intensity.append(frame_intensity)

    #Se transforma la lista all_intensity a un DataFrame.
    df = pd.DataFrame(all_intensity).T 

    #Para establecer el nombre de las columnas
    columns = ['Region_'+str(i) for i in range(1,len(coordenadas)+1)] 
    df.columns = columns 
    
    return df
