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

        ptp = datos.variables['T'][:] # perturbación de temperatura potencial
        pp = datos.variables['P'][:] # perturbación de la presión
        pb = datos.variables['PB'][:] # presión base
        pg = datos.variables['PH'][:] # perturbación geopotencial
        gb = datos.variables['PHB'][:] # geopotencial base
        
        return datos, ptp, pp, pb, pg, gb # regresar los datos extraidos
        
    except Exception as e:
        print(f"error cargando datos WRF: {str(e)}") # si hay un error, mandar mensaje de error
        raise

def procesar_campo_temperatura(ptp, pp, pb, pg, gb, indice_tiempo=0, indice_nivel=0):
    try:
        pt = pp + pb  # presión total
        
        # Extraer un slice 2D de los datos
        t = ptp[indice_tiempo, :, 0, :]  # temperatura potencial
        pres = pt[indice_tiempo, :, 0, :]  # presión
        height = (pg[indice_tiempo, :, 0, :] + gb[indice_tiempo, :, 0, :]) / 1.352  # altura
        
        # constantes
        g = 1.352  # gravedad en titán
        to = 94.0  # temperatura de referencia
        rd = 290.0  # constante de los gases para aire seco
        cp_air = 1044.0  # calor específico a presión constante para el aire
        po = 1e5  # presión de referencia (corregido de 1*10^5)

        # Calcular temperatura real
        tr = (t + to) * (pres/po)**(rd/cp_air)
        
        return tr, height, pres
    
    except Exception as e:
        print(f"Error procesando campo de temperatura: {str(e)}")
        raise

def crear_grafica_temperatura(tr, height, pres, titulo='Perfil de Temperatura'):
    try:
        # Crear figura
        plt.figure(figsize=(10, 12))
        
        # Crear mapa de colores
        cmap = plt.cm.RdYlBu_r
        
        # Obtener las dimensiones de los datos
        ny, nx = tr.shape
        
        # Crear los niveles para el contour
        levels = np.linspace(np.min(tr), np.max(tr), 50)
        
        # Crear una malla de puntos para la altura y presión
        X, Y = np.meshgrid(np.arange(nx), np.arange(ny))
        
        # Crear el contour plot
        cf = plt.contourf(X, Y, tr, levels=levels, cmap=cmap, extend='both')
        
        # Añadir contornos en negro
        cs = plt.contour(X, Y, tr, levels=levels[::5], colors='black', alpha=0.3, linewidths=0.5)
        
        # Invertir el eje y
        plt.gca().invert_yaxis()
        
        # Añadir barra de colores
        cbar = plt.colorbar(cf)
        cbar.set_label('Temperatura (K)', rotation=270, labelpad=15)
        
        # Añadir etiquetas y título
        plt.xlabel('Distancia horizontal (puntos de malla)')
        plt.ylabel('Nivel vertical (puntos de malla)')
        plt.title(titulo)
        
        # Añadir cuadrícula
        plt.grid(True, linestyle='--', alpha=0.3)
        
        # Ajustar el diseño
        plt.tight_layout()
        
    except Exception as e:
        print(f"Error creando la gráfica: {str(e)}")
        raise

def main(file_path, time_idx=0, level_idx=0):
    try:
        # Cargar datos del archivo
        datos, ptp, pp, pb, pg, gb = obtener_datos(file_path)
        
        # Procesar campo de temperatura
        tr, height, pres = procesar_campo_temperatura(ptp, pp, pb, pg, gb, 
                                                    indice_tiempo=time_idx, 
                                                    indice_nivel=level_idx)
        
        # Crear gráfica de temperatura
        crear_grafica_temperatura(
            tr, height, pres,
            titulo=f'Temperatura real (en base a la presión y a la altura)'
        )
        
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