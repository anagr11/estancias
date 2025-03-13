import netCDF4 as nc                                      # libreria para archivos netCDF
import numpy as np                                        # libreria para operaciones matematicas con arreglos
import matplotlib.pyplot as plt                           # libreria para graficar
from matplotlib.colors import LinearSegmentedColormap     # libreria para manejo de colores en la grafica
from pathlib import Path                                  # libreria para manejo de rutas de archivos

def obtener_datos(ruta_archivo):

    try:
        if not Path(ruta_archivo).exists(): # verificar si el archivo existe
            raise FileNotFoundError(f"archivo no encontrado: {ruta_archivo}") # si no existe, mandar mensaje de error
            
        datos = nc.Dataset(ruta_archivo) # abrir el archivo netCDF

        perturbacion_temperatura = datos.variables['T'][:] # perturbación de temperatura potencial
        perturbacion_geopotencial = datos.variables['PH'][:] # perturbación geopotencial
        geopotencial_base = datos.variables['PHB'][:] # geopotencial base
        
        return datos, perturbacion_temperatura, perturbacion_geopotencial, geopotencial_base # regresar los datos extraidos
        
    except Exception as e:
        print(f"error cargando datos WRF: {str(e)}") # si hay un error, mandar mensaje de error
        raise

def procesar_campo_temperatura(perturbacion_temperatura, perturbacion_geopotencial, geopotencial_base):
    try:
        temperatura_base = 100 # temperatura base en Kelvin
        gravedad_titan = 1.352 # gravedad en Titán
        temperatura_potencial = temperatura_base + perturbacion_temperatura # temperatura potencial
        altura = (perturbacion_geopotencial + geopotencial_base) / gravedad_titan # altura en metros
        return temperatura_potencial, altura # regresar los datos procesados

    except Exception as e:
        print(f"error haciendo cálculos: {str(e)}") # si hay un error, mandar mensaje de error
        raise

def graficar_temperatura(temperatura_potencial, altura):
    try:
        plt.figure(figsize=(10, 6)) # crear figura
        plt.contourf(temperatura_potencial, cmap='inferno') # graficar temperatura potencial
        plt.colorbar(label='Temperatura potencial (K)') # agregar barra de color
        plt.contour(altura, colors='black') # agregar contorno de la altura
        plt.xlabel('Longitud') # etiqueta eje x
        plt.ylabel('Altura') # etiqueta eje y
        plt.title('Temperatura potencial en Titán') # titulo de la grafica
        plt.show() # mostrar grafica

    except Exception as e:
        print(f"error graficando datos: {str(e)}") # si hay un error, mandar mensaje de error

def main(file_path, time_idx=0, level_idx=0):
    try:
        # Cargar datos del archivo
        datos, perturbacion_temperatura, perturbacion_geopotencial, geopotencial_base = obtener_datos(file_path)
        
        # Procesar campo de temperatura
        temperatura_potencial, altura = procesar_campo_temperatura(perturbacion_temperatura, perturbacion_geopotencial, geopotencial_base)
        
        # Crear gráfica de temperatura
        graficar_temperatura(
            temperatura_potencial, altura)
        
        # Mostrar la gráfica
        plt.show()
        
        # Cerrar el archivo
        datos.close()
        
    except Exception as e:
        print(f"Error en la ejecución principal: {str(e)}")
        raise

# correr el programa
if __name__ == "__main__":
    file_path = 'C:/Users/anaa_/Downloads/A3'
    main(file_path)
