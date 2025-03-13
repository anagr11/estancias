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

# Imprimir información sobre las dimensiones de los datos
print("Forma de u:", u.shape)
print("Forma de w:", w.shape)
print("Forma de altura:", altura.shape)

# Calcular vorticidad relativa
def calcular_vorticidad(u, w, dx, altura):
    # Imprimir información de diagnóstico
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
    # Crear un array para u interpolado con el mismo tamaño que w
    u_interp_z = np.zeros_like(w_values)
    
    # Interpolación vertical - asegurar que tienen el mismo número de niveles verticales
    for i in range(min(u_values.shape[1], u_interp_z.shape[1])):
        # Recortar correctamente en la dimensión x para que coincidan
        # u tiene 2001 puntos en x, w tiene 2000 puntos en x
        u_interp_z[:, i, :, :] = u_values[:, min(i, u_values.shape[1]-1), :, :-1]
    
    print("Forma de u interpolada:", u_interp_z.shape)
    
    # Calcular gradientes en dimensiones consistentes
    dw_dx = np.zeros_like(w_values)
    
    # Usar diferencias centradas para dw_dx para mayor precisión
    for i in range(1, w_values.shape[3]-1):
        dw_dx[:, :, :, i] = (w_values[:, :, :, i+1] - w_values[:, :, :, i-1]) / (2 * dx)
    
    # Para los bordes, usar diferencias hacia adelante/atrás
    dw_dx[:, :, :, 0] = (w_values[:, :, :, 1] - w_values[:, :, :, 0]) / dx
    dw_dx[:, :, :, -1] = (w_values[:, :, :, -1] - w_values[:, :, :, -2]) / dx
    
    # Para el gradiente vertical, necesitamos la diferencia de altura entre niveles
    du_dz = np.zeros_like(w_values)
    
    for i in range(1, min(altura_values.shape[1], u_interp_z.shape[1])-1):
        # Diferencias centradas para mayor precisión
        delta_z = (altura_values[:, i+1, :, :] - altura_values[:, i-1, :, :]) / 2
        # Usar una máscara para evitar división por cero
        mask = np.abs(delta_z) < 1e-10
        safe_delta_z = np.where(mask, 1.0, delta_z)  # Usar 1.0 donde delta_z es muy pequeño
        du_dz_temp = (u_interp_z[:, i+1, :, :] - u_interp_z[:, i-1, :, :]) / (2 * safe_delta_z)
        # Usar ceros donde delta_z era muy pequeño
        du_dz[:, i, :, :] = np.where(mask, 0.0, du_dz_temp)
    
    # Para los bordes
    # Borde inferior
    if altura_values.shape[1] > 1 and u_interp_z.shape[1] > 1:
        delta_z = altura_values[:, 1, :, :] - altura_values[:, 0, :, :]
        mask = np.abs(delta_z) < 1e-10
        safe_delta_z = np.where(mask, 1.0, delta_z)
        du_dz_temp = (u_interp_z[:, 1, :, :] - u_interp_z[:, 0, :, :]) / safe_delta_z
        du_dz[:, 0, :, :] = np.where(mask, 0.0, du_dz_temp)
    
    # Borde superior
    if altura_values.shape[1] > 1 and u_interp_z.shape[1] > 1:
        last_idx = min(altura_values.shape[1], u_interp_z.shape[1]) - 1
        delta_z = altura_values[:, last_idx, :, :] - altura_values[:, last_idx-1, :, :]
        mask = np.abs(delta_z) < 1e-10
        safe_delta_z = np.where(mask, 1.0, delta_z)
        du_dz_temp = (u_interp_z[:, last_idx, :, :] - u_interp_z[:, last_idx-1, :, :]) / safe_delta_z
        du_dz[:, last_idx, :, :] = np.where(mask, 0.0, du_dz_temp)
    
    # Calcular vorticidad
    vorticidad = dw_dx - du_dz
    
    # Limpiar valores extremos que podrían ser errores numéricos
    # Reemplazar infinitos con NaN
    vorticidad = np.where(np.isinf(vorticidad), np.nan, vorticidad)
    
    # Recortar valores extremos
    valid_data = vorticidad[~np.isnan(vorticidad)]
    if len(valid_data) > 0:  # Asegurarse de que hay datos válidos
        percentil_99 = np.nanpercentile(vorticidad, 99)
        percentil_1 = np.nanpercentile(vorticidad, 1)
        vorticidad = np.clip(vorticidad, percentil_1, percentil_99)
    
    return vorticidad

vorticidad = calcular_vorticidad(u, w, dx, altura)

# Reemplazar NaN con ceros
vorticidad = np.nan_to_num(vorticidad, nan=0.0)

# Verificar el rango de valores
print("Valor mínimo de vorticidad:", np.min(vorticidad))
print("Valor máximo de vorticidad:", np.max(vorticidad))

# Examinar la distribución de valores de vorticidad
plt.figure(figsize=(8, 6))
plt.hist(vorticidad.flatten(), bins=50)
plt.title('Distribución de valores de vorticidad')
plt.xlabel('Vorticidad')
plt.ylabel('Frecuencia')
plt.show()

# Mostrar algunos percentiles para ayudar a elegir el umbral
percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
for p in percentiles:
    print(f"Percentil {p}%: {np.percentile(vorticidad, p)}")

# Basado en los percentiles, definir un umbral adaptativo
umbral = np.percentile(vorticidad, 75)  # Podemos usar el percentil 75 como umbral
print(f"Umbral adaptativo seleccionado: {umbral}")

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
    
    # Determinar el rango de valores para la escala de colores
    # Ignorar valores extremos para mejor visualización
    vmin = np.nanpercentile(vorticidad_tiempo[~np.isnan(vorticidad_tiempo)], 5)
    vmax = np.nanpercentile(vorticidad_tiempo[~np.isnan(vorticidad_tiempo)], 95)
    
    # Imprimir algunos diagnósticos
    print(f"Tiempo {tiempo_idx}:")
    print(f"  Valores NaN: {np.isnan(vorticidad_tiempo).sum()} de {vorticidad_tiempo.size}")
    print(f"  Rango de valores: {np.nanmin(vorticidad_tiempo)} a {np.nanmax(vorticidad_tiempo)}")
    print(f"  Rango para visualización: {vmin} a {vmax}")

    # Graficar
    plt.figure(figsize=(12, 6))
    contour = plt.contourf(distancia, niveles_altura, vorticidad_tiempo, 
                           cmap='coolwarm', levels=50,
                           vmin=vmin, vmax=vmax)
    plt.colorbar(contour, label='Vorticidad (1/s)')
    plt.title(f'Vorticidad en Titán (Tiempo {tiempo_idx})')
    plt.xlabel('Distancia (m)')
    plt.ylabel('Altura (m)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.show()

# Analizar todos los pasos de tiempo disponibles
tiempos_validos = []
for t in range(vorticidad.shape[0]):
    vorticidad_t = vorticidad[t, :, :, :].mean(axis=1)
    if not np.all(np.isnan(vorticidad_t)):
        valid_percent = 100 * (1 - np.isnan(vorticidad_t).sum() / vorticidad_t.size)
        print(f"Tiempo {t}: {valid_percent:.1f}% de datos válidos")
        if valid_percent > 50:  # Si más del 50% de los datos son válidos
            tiempos_validos.append(t)

print("Tiempos con suficientes datos válidos:", tiempos_validos)

# Visualizar los tiempos válidos
for t in tiempos_validos[:5]:  # Limitar a los primeros 5 para no generar demasiadas gráficas
    graficar_vorticidad_2d(vorticidad, altura, t)

# Para un análisis más detallado, visualizar algunos pasos de tiempo específicos
# incluyendo los que sabemos que funcionan bien (20 y 30)
for t in [20, 30]:
    if t not in tiempos_validos[:5]:  # Evitar duplicados
        graficar_vorticidad_2d(vorticidad, altura, t)

# Guardar resultados
np.save('vorticidad.npy', vorticidad)
np.save('zonas_turbulencia.npy', zonas_turbulencia)

# Análisis adicional: calcular estadísticas por nivel vertical
print("\nEstadísticas de vorticidad por nivel vertical:")
vorticidad_por_nivel = np.nanmean(vorticidad, axis=(0, 2, 3))  # Promedio en tiempo, south_north y west_east
for i, valor in enumerate(vorticidad_por_nivel):
    print(f"Nivel {i}: {valor}")

# Crear gráfico de vorticidad promedio por nivel
plt.figure(figsize=(10, 6))
plt.plot(vorticidad_por_nivel, range(len(vorticidad_por_nivel)), 'b-')
plt.xlabel('Vorticidad promedio')
plt.ylabel('Nivel vertical')
plt.title('Perfil vertical de vorticidad')
plt.grid(True)
plt.show()

# Análisis adicional: evolución temporal de la vorticidad
vorticidad_tiempo = np.nanmean(vorticidad, axis=(1, 2, 3))  # Promedio en todos los espacios
plt.figure(figsize=(10, 6))
plt.plot(range(len(vorticidad_tiempo)), vorticidad_tiempo, 'r-')
plt.xlabel('Paso de tiempo')
plt.ylabel('Vorticidad promedio')
plt.title('Evolución temporal de la vorticidad')
plt.grid(True)
plt.show()