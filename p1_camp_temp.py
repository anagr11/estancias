import netCDF4 as nc                                      # importa libreria para archivos netCDF
import numpy as np                                        # importa libreria para operaciones matematicas con arreglos
import matplotlib.pyplot as plt                           # importa libreria para graficar
from matplotlib.colors import LinearSegmentedColormap     # importa libreria para manejo de colores en la grafica
from pathlib import Path                                  # importa libreria para manejo de rutas de archivos

def load_wrf_data(file_path):

    try:
        if not Path(file_path).exists(): # verificar si el archivo existe
            raise FileNotFoundError(f"File not found: {file_path}") # si no existe, mandar mensaje de error
            
        datos = nc.Dataset(file_path) # abrir el archivo netCDF

        times = datos.variables['Times'][:] # extraer datos de tiempo
        t = datos.variables['T'][:] # extraer datos de perturbacion de temperatura potencial
        p = datos.variables['P'][:] # extraer datos de presion
        pb = datos.variables['PB'][:] # extraer datos de presion base
        
        return datos, times, t, p, pb # regresar los datos extraidos
        
    except Exception as e:
        print(f"Error loading WRF data: {str(e)}") # si hay un error, mandar mensaje de error
        raise

def process_temperature_field(t, p, pb, time_idx=0, level_idx=0):

    try:
        # calcular presion total sumando la presion base y la presion
        pressure_total = p + pb
        
        # extraer datos de temperatura y presion para el tiempo y nivel especificado
        # reestructurar los datos para que tengan la forma de un arreglo de 2 dimensiones

        temp = t[time_idx, level_idx, 0, :].squeeze()

    
        # calcular las dimensiones del arreglo
        length = len(temp)
        width = int(np.sqrt(length))
        height = length // width

        if width * height != length:
            height += 1
            # ajustar el tamaño del arreglo
            padding_needed = width * height - length
            temp = np.pad(temp, (0, padding_needed), mode='edge')
            
        temp = temp.reshape(height, width)
        
        # ajustar la presion para que tenga la misma forma que la temperatura
        pressure_level = pressure_total[time_idx, level_idx, 0, :].squeeze()
        if len(pressure_level) != width * height:
            pressure_level = np.pad(pressure_level, (0, padding_needed), mode='edge')
        pressure_level = pressure_level.reshape(height, width)
        
        # convertir la temperatura potencial a temperatura real
        R = 290.0  # constante para aire (J/kg·K)
        cp = 1044.0  # calor especifico a una presion constante (J/kg·K)
        P0 = 1*10^5  # presion de referencia (Pa)
        
        temp_actual = (temp + 94) * (pressure_level/P0)**(R/cp) # formula para convertir temperatura potencial a temperatura real
        
        return temp_actual # regresar la temperatura real
        
    except Exception as e:
        print(f"Error processing temperature field: {str(e)}") # si hay un error, mandar mensaje de error
        raise

def create_temperature_plot(temp_field, title='Temperature Field', cmap='RdYlBu_r'):
    
    try:
        # crear una malla de puntos para la grafica
        ny, nx = temp_field.shape
        x = np.arange(nx)
        y = np.arange(ny)
        X, Y = np.meshgrid(x, y)
        
        # crear figura
        plt.figure(figsize=(12, 8))
        
        # crear mapa de colores
        levels = np.linspace(np.min(temp_field), np.max(temp_field), 50)
        cf = plt.contourf(X, Y, temp_field, levels=levels, cmap=cmap, extend='both')
        
        # añadir contornos
        cs = plt.contour(X, Y, temp_field, levels=levels[::5], colors='black', alpha=0.3, linewidths=0.5)
        
        # personalizar contornos
        plt.colorbar(cf, label='Temperature (K)')
        plt.title(f"{title}\n{temp_field.shape[0]}x{temp_field.shape[1]} grid", pad=20)
        plt.xlabel('West-East Grid Points')
        plt.ylabel('South-North Grid Points')
        
        # añadir cuadricula
        plt.grid(True, linestyle='--', alpha=0.3)
        
        # ajustar el tamaño de la grafica
        plt.tight_layout()
        
    except Exception as e:
        print(f"Error creating plot: {str(e)}") # si hay un error, mandar mensaje de error
        raise

def main(file_path, time_idx=0, level_idx=0):

    try:
        # cargar datos del archivo
        datos, times, t, p, pb = load_wrf_data(file_path)
        
        print(f"Original data shapes:") # imprimir las dimensiones de los datos
        print(f"T shape: {t.shape}") # imprimir las dimensiones de la temperatura
        print(f"P shape: {p.shape}") # imprimir las dimensiones de la presion
        print(f"PB shape: {pb.shape}") # imprimir las dimensiones de la presion base
        
        # procesar campo de temperatura
        temp_field = process_temperature_field(t, p, pb, time_idx, level_idx)
        print(f"Processed temperature field shape: {temp_field.shape}")
        
        # crear grafica de temperatura
        create_temperature_plot(
            temp_field,
            title=f'WRF Temperature Field\nTime Index: {time_idx}, Level: {level_idx}'
        )
        
        # mostrar la grafica
        plt.show()
        
        # cerrar el archivo
        datos.close()
        
    except Exception as e:
        print(f"Error in main execution: {str(e)}") # si hay un error, mandar mensaje de error
        raise

# correr el programa
if __name__ == "__main__":
    file_path = 'C:/Users/anaa_/Downloads/A3'
    main(file_path)