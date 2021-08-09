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
    x = int(input("Ingrese la coordenada X de la región: "))
    y = int(input("Ingrese la coordenada Y de la región: "))
    coordenadas.append((x, y))

    while agregar_region:
        agregar_region = input("¿Desea agregar otra región?: y/n ")
        if agregar_region.lower() == 'n':
            agregar_region = False

        elif agregar_region.lower() == 'y':
            x = int(input("Ingrese la coordenada X de la región: "))
            y = int(input("Ingrese la coordenada Y de la región: "))
            coordenadas.append((x, y))
        
        else:
            print('Por favor, introduce "y" o "n"') 

    return frames, background, radio, bck_radio, coordenadas

def normalize(df):
    '''Normaliza los valores de un dataframe'''

    result = df.copy()
    max_value = max(df.max())
    min_value = max(df.min())
    for feature_name in df.columns:
        result[feature_name] = (df[feature_name] - min_value) / (max_value - min_value)
    return result

def segmentar(imagen, coordenadas, radio):
    '''Muestra la región a analizar'''

    mask = np.ones(shape=imagen[0].shape[0:2], dtype='bool')
    for coordenada in coordenadas:
        x, y = coordenada
        cc, rr = draw.circle(x, y, radius=radio, shape=imagen[0].shape[0:2])
        mask[rr, cc] = False
        imagen[0][rr, cc]
    imagen[0][mask] = 0
    return imagen[0]    

def analisis_region(image, coordenadas, background, radius, bckground_radius, frames=162):
    '''Retorna un dataframe que posee los valores promedios de intensidad de las regiones
       de interés.
       Se itera sobre las coordenadas (regiones) y se obtiene la intensidad promedio de la
       región en cada frame'''

    all_intensity = [] #Contendrá la intensidad de las regiones en todos los frames
    
    for coordenada in coordenadas: 
        frame_intensity = [] #Intensidad de la region en cada frame
        for frame in range(frames):
            bg_value = (np.mean(image[frame][draw.circle(background[1], background[0], bckground_radius)]))
            valor_1 = (np.mean(image[frame][draw.circle(coordenada[1], coordenada[0], radius)])) - bg_value
            frame_intensity.append(valor_1)
        all_intensity.append(frame_intensity)

    #Se transforma la lista all_intensity a un DF.
    df = pd.DataFrame(all_intensity).T 

    #Para nombre de columnas
    columns = ['Region_'+str(i) for i in range(1,len(coordenadas)+1)] 
    df.columns = columns 
    
    return df
