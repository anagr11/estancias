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

def ajustar_dimensiones(temp_perfil, altura_perfil):
    """
    Ajusta las dimensiones de los perfiles para que tengan el mismo tamaño
    usando interpolación para el perfil más corto
    """
    if len(temp_perfil) < len(altura_perfil):
        # Si temperatura tiene menos puntos, añadimos uno interpolado
        ultimo_valor = temp_perfil[-1]
        penultimo_valor = temp_perfil[-2]
        valor_nuevo = (ultimo_valor + penultimo_valor) / 2
        temp_perfil = np.append(temp_perfil, valor_nuevo)
    elif len(altura_perfil) < len(temp_perfil):
        # Si altura tiene menos puntos, añadimos uno interpolado
        ultimo_valor = altura_perfil[-1]
        penultimo_valor = altura_perfil[-2]
        valor_nuevo = (ultimo_valor + penultimo_valor) / 2
        altura_perfil = np.append(altura_perfil, valor_nuevo)
    
    return temp_perfil, altura_perfil

def graficar_temperatura(temperatura_potencial, altura, tiempo=0):
    try:
        # Extraer los perfiles para tiempo=0
        temp_perfil = temperatura_potencial[tiempo, :, 0, 0]  # Tomar el primer punto en x,y
        altura_perfil = altura[tiempo, :, 0, 0]
        
        # Ajustar dimensiones
        temp_perfil, altura_perfil = ajustar_dimensiones(temp_perfil, altura_perfil)
        
        # Verificar que las dimensiones coincidan
        print(f"Dimensiones después del ajuste - Temperatura: {temp_perfil.shape}, Altura: {altura_perfil.shape}")
        
        plt.figure(figsize=(10, 6))
        plt.plot(temp_perfil, altura_perfil, 'b-', linewidth=2)
        plt.xlabel('Temperatura Potencial (K)')
        plt.ylabel('Altura (m)')
        plt.title(f'Perfil de Temperatura Potencial (Tiempo = {tiempo})')
        plt.grid(True)
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