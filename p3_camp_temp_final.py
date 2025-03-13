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

def procesar_campo_temperatura(ptp, pp, pb, pg, gb, indice_tiempo=0):
    try:
        pt = pp + pb  # presión total
        
        # Extraer un slice 2D de los datos y asegurar dimensiones compatibles
        t = ptp[indice_tiempo, :, 0, :]  # temperatura potencial
        pres = pt[indice_tiempo, :, 0, :]  # presión
        
        # Ajustar height para que tenga las mismas dimensiones
        height_full = (pg[indice_tiempo, :, 0, :] + gb[indice_tiempo, :, 0, :]) / g  # altura geopotencial
        height = (height_full[:-1, :] + height_full[1:, :]) / 2  # Promediar niveles adyacentes
        
        # constantes
        g = 1.352  # gravedad en titán
        to = 94.0  # temperatura de referencia
        rd = 290.0  # constante de los gases para aire seco
        cp_air = 1044.0  # calor específico a presión constante para el aire
        po = 1e5  # presión de referencia

        # Calcular temperatura real
        tr = (t + to) * (pres/po)**(rd/cp_air)

        # Imprimir dimensiones para verificación
        print(f"Dimensiones finales:")
        print(f"tr: {tr.shape}")
        print(f"height: {height.shape}")
        print(f"pres: {pres.shape}")
        
        return tr, height, pres
    
    except Exception as e:
        print(f"Error procesando campo de temperatura: {str(e)}")
        raise

def crear_grafica_temperatura(tr, height, pres, titulo='Perfil de Temperatura'):
    try:
        # Crear figura
        plt.figure(figsize=(12, 8))
        
        # Crear mapa de colores
        cmap = plt.cm.RdYlBu_r
        
        # Crear malla para el plotting
        X, Y = np.meshgrid(np.arange(tr.shape[1]), np.arange(tr.shape[0]))
        
        # Crear los niveles para el contour
        levels = np.linspace(np.min(tr), np.max(tr), 50)
        
        # Crear el contour plot usando índices de malla
        cf = plt.contourf(X, Y, tr, levels=levels, cmap=cmap, extend='both')
        
        # Añadir contornos en negro
        cs = plt.contour(X, Y, tr, levels=levels[::5], colors='black', alpha=0.3, linewidths=0.5)
        
        # Invertir el eje y (presión)
        plt.gca().invert_yaxis()
        
        # Configurar los ticks de los ejes
        # Configurar eje x (altura)
        x_ticks = np.linspace(0, tr.shape[1]-1, 6)
        x_labels = np.linspace(np.min(height[0,:]), np.max(height[0,:]), 6)
        plt.xticks(x_ticks, [f'{x:0.0f}' for x in x_labels])
        
        # Configurar eje y (presión)
        y_ticks = np.linspace(0, tr.shape[0]-1, 6)
        y_labels = np.linspace(np.min(pres[:,0]), np.max(pres[:,0]), 6)
        plt.yticks(y_ticks, [f'{y:0.0f}' for y in y_labels])
        
        # Añadir barra de colores
        cbar = plt.colorbar(cf)
        cbar.set_label('Temperatura (K)', rotation=270, labelpad=15)
        
        # Etiquetas y título
        plt.xlabel('Altura (m)')
        plt.ylabel('Presión (Pa)')
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
            titulo='Temperatura Real vs Altura y Presión'
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
