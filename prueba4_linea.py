import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def obtener_datos(ruta_archivo):
    try:
        if not Path(ruta_archivo).exists():
            raise FileNotFoundError(f"archivo no encontrado: {ruta_archivo}")
            
        datos = nc.Dataset(ruta_archivo)
        perturbacion_temperatura = datos.variables['T'][:]
        perturbacion_geopotencial = datos.variables['PH'][:]
        geopotencial_base = datos.variables['PHB'][:]
        
        print(f"Forma de perturbacion_temperatura: {perturbacion_temperatura.shape}")
        print(f"Forma de perturbacion_geopotencial: {perturbacion_geopotencial.shape}")
        print(f"Forma de geopotencial_base: {geopotencial_base.shape}")
        
        return datos, perturbacion_temperatura, perturbacion_geopotencial, geopotencial_base
        
    except Exception as e:
        print(f"error cargando datos WRF: {str(e)}")
        raise

def procesar_campo_temperatura(perturbacion_temperatura, perturbacion_geopotencial, geopotencial_base):
    try:
        temperatura_base = 100
        gravedad_titan = 1.352
        temperatura_potencial = temperatura_base + perturbacion_temperatura
        altura = (perturbacion_geopotencial + geopotencial_base) / gravedad_titan
        return temperatura_potencial, altura

    except Exception as e:
        print(f"error haciendo cálculos: {str(e)}")
        raise

def interpolar_temperatura(temp_perfil):
    # calcular el nuevo punto usando el promedio de los dos últimos valores
    ultimo_valor = temp_perfil[-1]
    penultimo_valor = temp_perfil[-2]
    nuevo_valor = (ultimo_valor + penultimo_valor) / 2
    
    # añadir el nuevo punto al array
    return np.append(temp_perfil, nuevo_valor)

def graficar_temperatura(temperatura_potencial, altura, tiempo=0):
    try:
        # extraer un perfil vertical para el tiempo=0
        x_punto = temperatura_potencial.shape[3] // 2
        temp_perfil = temperatura_potencial[tiempo, :, 0, x_punto]
        altura_perfil = altura[tiempo, :, 0, x_punto]
        
        print(f"Dimensiones del perfil de temperatura antes de interpolar: {temp_perfil.shape}")
        print(f"Dimensiones del perfil de altura: {altura_perfil.shape}")
        
        # interpolar temperatura para que coincida con la dimensión de altura
        temp_perfil = interpolar_temperatura(temp_perfil)
        
        print(f"Dimensiones del perfil de temperatura después de interpolar: {temp_perfil.shape}")
        print(f"Rango de temperatura: {np.min(temp_perfil)} a {np.max(temp_perfil)}")
        print(f"Rango de altura: {np.min(altura_perfil)} a {np.max(altura_perfil)}")
        
        # crear la figura y los ejes
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # graficar el perfil
        line, = ax.plot(temp_perfil, altura_perfil, 'b-', linewidth=2, label='0 Hrs')
        
        # configurar los ejes
        ax.set_xlabel('Temperatura Potencial (K)')
        ax.set_ylabel('Altura (m)')
        ax.set_title('Perfil de Temperatura Potencial')
        ax.grid(True)
        
        # añadir leyenda en la esquina superior derecha
        ax.legend(loc='upper right', frameon=True)
        
        plt.show()

    except Exception as e:
        print(f"error graficando datos: {str(e)}")
        raise

def main(file_path, time_idx=0):
    try:
        datos, perturbacion_temperatura, perturbacion_geopotencial, geopotencial_base = obtener_datos(file_path)
        temperatura_potencial, altura = procesar_campo_temperatura(
            perturbacion_temperatura, perturbacion_geopotencial, geopotencial_base)
        graficar_temperatura(temperatura_potencial, altura, tiempo=time_idx)
        datos.close()
        
    except Exception as e:
        print(f"Error en la ejecución principal: {str(e)}")
        raise

if __name__ == "__main__":
    file_path = 'C:/Users/anaa_/Downloads/A3'
    main(file_path)