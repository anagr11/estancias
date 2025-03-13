# Importar librerías
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

# Cargar archivo netCDF
archivo_netcdf = 'C:/Users/anaa_/Downloads/A3'
datos = xr.open_dataset(archivo_netcdf)

# Obtener variables
u = datos['U']  # Componente zonal del viento (U)
w = datos['W']  # Componente vertical del viento (W)
ph = datos['PH']  # Perturbación del geopotencial
phb = datos['PHB']  # Geopotencial base
dx = datos.DX  # Resolución espacial en x (metros)
dy = datos.DY  # Resolución espacial en y (metros)

# Constantes específicas para Titán
g_titan = 1.352  # Gravedad en Titán (m/s^2)
R_titan = 8.3145  # Constante de los gases ideales (J/(mol·K))
T_surface = 100  # Temperatura superficial media (K)
P_surface = 1e5  # Presión superficial media (Pa)

# Calcular la altura geométrica
altura = (ph + phb) / g_titan  # Altura en metros

# Añade esto antes de la función calcular_vorticidad
print("Forma de u:", u.shape)
print("Forma de w:", w.shape)
print("Forma de altura:", altura.shape)

def calcular_vorticidad(u, w, dx, altura):
    print("Dimensiones de u:", u.dims)
    print("Forma de u:", u.shape)
    print("Dimensiones de w:", w.dims)
    print("Forma de w:", w.shape)
    print("Forma de altura:", altura.shape)
    
    # Convertir a numpy arrays
    u_values = u.values
    w_values = w.values
    altura_values = altura.values
    
    # Interpolación para alinear las rejillas
    # Interpolar u a los puntos de w para la dimensión vertical
    u_interp_z = np.zeros_like(w_values)
    for i in range(u_values.shape[1]):
        if i < u_values.shape[1]:
            u_interp_z[:, i, :, :] = u_values[:, i, :, :-1]  # Quitar el último punto en x que es extra
    
    # Ahora todas las variables deberían tener la forma (43, 100, 1, 2000)
    print("Forma de u interpolada:", u_interp_z.shape)
    
    # Calcular gradientes en dimensiones consistentes
    dw_dx = np.zeros_like(w_values)
    for i in range(w_values.shape[3]-1):
        dw_dx[:, :, :, i] = (w_values[:, :, :, i+1] - w_values[:, :, :, i]) / dx
    
    # Para el gradiente vertical, necesitamos la diferencia de altura entre niveles
    du_dz = np.zeros_like(w_values)
    for i in range(altura_values.shape[1]-1):
        delta_z = altura_values[:, i+1, :, :] - altura_values[:, i, :, :]
        # Evitar división por cero
        delta_z = np.where(np.abs(delta_z) < 1e-10, 1e-10, delta_z)
        du_dz[:, i, :, :] = (u_interp_z[:, i+1, :, :] - u_interp_z[:, i, :, :]) / delta_z
    
    # Calcular vorticidad
    vorticidad = dw_dx - du_dz
    return vorticidad

vorticidad = calcular_vorticidad(u, w, dx, altura)

# Añade después de calcular la vorticidad
plt.figure(figsize=(8, 6))
plt.hist(vorticidad.flatten(), bins=50)
plt.title('Distribución de valores de vorticidad')
plt.xlabel('Vorticidad')
plt.ylabel('Frecuencia')
plt.show()

# Mostrar algunos percentiles para ayudar a elegir el umbral
percentiles = [50, 75, 90, 95, 99]
for p in percentiles:
    print(f"Percentil {p}%: {np.percentile(vorticidad, p)}")

# Definir umbral para identificar zonas de turbulencia o vórtices
umbral = 0.5

# Identificar las zonas donde la vorticidad supera el umbral
zonas_turbulencia = vorticidad > umbral

# Función para graficar la vorticidad en 2D (distancia vs altura)
def graficar_vorticidad_2d(vorticidad, altura, tiempo_idx):
    # Seleccionar el paso de tiempo
    vorticidad_tiempo = vorticidad[tiempo_idx, :, :, :].mean(axis=1)  # Promedio en la dimensión south_north
    altura_tiempo = altura[tiempo_idx, :, :, :].mean(axis=1)  # Promedio en la dimensión south_north

    # Crear la malla de distancia y altura
    distancia = np.arange(vorticidad_tiempo.shape[1]) * dx  # Distancia en metros
    niveles_altura = altura_tiempo.mean(axis=1)  # Altura promedio en cada nivel

    # Graficar
    plt.figure(figsize=(12, 6))
    contour = plt.contourf(distancia, niveles_altura, vorticidad_tiempo, cmap='coolwarm', levels=50)
    plt.colorbar(contour, label='Vorticidad (1/s)')
    plt.title(f'Vorticidad en Titán (Tiempo {tiempo_idx})')
    plt.xlabel('Distancia (m)')
    plt.ylabel('Altura (m)')
    plt.show()

# Visualizar varios pasos de tiempo
for tiempo_idx in [0, 10, 20, 30, 40]:
    graficar_vorticidad_2d(vorticidad, altura, tiempo_idx)

# Graficar
graficar_vorticidad_2d(vorticidad, altura, tiempo_idx)

# Guardar resultados
np.save('vorticidad.npy', vorticidad)
np.save('zonas_turbulencia.npy', zonas_turbulencia)
