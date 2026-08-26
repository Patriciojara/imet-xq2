import os
import pandas as pd


def cortar_datos():
    # Buscamos los archivos en la carpeta data y obtenemos el último archivo CSV
    archivo_data = os.listdir('data')
    #print('archivos en carpeta:', archivo_data)
    ultimo_archivo = max(archivo_data)
    #print("Último archivo CSV:", ultimo_archivo)

    path = "data" + '\\' + str(ultimo_archivo)

    df = pd.read_csv(path, sep=",", encoding="utf-8") # Leemos los datos del dataframe

    #print(df.head())
    #print(df.columns)


    df_cortado = df[['temperature_c', 'pressure_hpa', 'relative_humidity_pct']]

    temp = round(df['temperature_c'].iloc[-1], 1) 
    press = round(df['pressure_hpa'].iloc[-1], 1)
    hum = round(df['relative_humidity_pct'].iloc[-1], 1)
    latitude = round(df['latitude_deg'].iloc[-1], 6)
    longitude = round(df['longitude_deg'].iloc[-1], 6)
    

    print(temp, press, hum, latitude, longitude)
    return temp, press, hum, latitude, longitude


cortar_datos()

