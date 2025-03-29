import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

tiempo_especifico = 18 # graficar en este tiempo

# cargar archivo
archivo_netcdf = 'C:/Users/anaa_/Downloads/A3'
datos = xr.open_dataset(archivo_netcdf)

# leer y guardar variables
u = datos['U']  # componente zonal del viento (U)
w = datos['W']  # componente vertical del viento (W)
ph = datos['PH']  # perturbación del geopotencial
phb = datos['PHB']  # geopotencial base
dx = datos.DX  # resolución espacial en x (metros)
dy = datos.DY  # resolución espacial en y (metros)

# constantes para Titán
g_titan = 1.352  # gravedad
R_titan = 8.3145  # constante de los gases
T_surface = 100  # temperatura superficial media
P_surface = 1e5  # presión superficial media

altura = (ph + phb) / g_titan  # calcular altura en metros

def calcular_vorticidad(u, w, dx, altura):
    u_values = u.values
    w_values = w.values
    altura_values = altura.values
    
    u_interp_z = np.zeros_like(w_values)
    
    # ajustar las dimensiones para que coincidan
    for i in range(min(u_values.shape[1], u_interp_z.shape[1])):
        u_interp_z[:, i, :, :] = u_values[:, min(i, u_values.shape[1]-1), :, :-1]
    
    # calcular gradientes
    dw_dx = np.zeros_like(w_values)
    
    for i in range(1, w_values.shape[3]-1):
        dw_dx[:, :, :, i] = (w_values[:, :, :, i+1] - w_values[:, :, :, i-1]) / (2 * dx)
    
    dw_dx[:, :, :, 0] = (w_values[:, :, :, 1] - w_values[:, :, :, 0]) / dx
    dw_dx[:, :, :, -1] = (w_values[:, :, :, -1] - w_values[:, :, :, -2]) / dx
    
    du_dz = np.zeros_like(w_values)
    
    for i in range(1, min(altura_values.shape[1], u_interp_z.shape[1])-1):
        delta_z = (altura_values[:, i+1, :, :] - altura_values[:, i-1, :, :]) / 2
        mask = np.abs(delta_z) < 1e-10
        safe_delta_z = np.where(mask, 1.0, delta_z)
        du_dz_temp = (u_interp_z[:, i+1, :, :] - u_interp_z[:, i-1, :, :]) / (2 * safe_delta_z)
        du_dz[:, i, :, :] = np.where(mask, 0.0, du_dz_temp)
    
    if altura_values.shape[1] > 1 and u_interp_z.shape[1] > 1:
        delta_z = altura_values[:, 1, :, :] - altura_values[:, 0, :, :]
        mask = np.abs(delta_z) < 1e-10
        safe_delta_z = np.where(mask, 1.0, delta_z)
        du_dz_temp = (u_interp_z[:, 1, :, :] - u_interp_z[:, 0, :, :]) / safe_delta_z
        du_dz[:, 0, :, :] = np.where(mask, 0.0, du_dz_temp)
    
    if altura_values.shape[1] > 1 and u_interp_z.shape[1] > 1:
        last_idx = min(altura_values.shape[1], u_interp_z.shape[1]) - 1
        delta_z = altura_values[:, last_idx, :, :] - altura_values[:, last_idx-1, :, :]
        mask = np.abs(delta_z) < 1e-10
        safe_delta_z = np.where(mask, 1.0, delta_z)
        du_dz_temp = (u_interp_z[:, last_idx, :, :] - u_interp_z[:, last_idx-1, :, :]) / safe_delta_z
        du_dz[:, last_idx, :, :] = np.where(mask, 0.0, du_dz_temp)
    
    # calcular vorticidad
    vorticidad = dw_dx - du_dz
    
    # limpiar valores
    vorticidad = np.where(np.isinf(vorticidad), np.nan, vorticidad)
    valid_data = vorticidad[~np.isnan(vorticidad)]
    if len(valid_data) > 0:  
        percentil_99 = np.nanpercentile(vorticidad, 99)
        percentil_1 = np.nanpercentile(vorticidad, 1)
        vorticidad = np.clip(vorticidad, percentil_1, percentil_99)
    
    return vorticidad

vorticidad = calcular_vorticidad(u, w, dx, altura)

# eliminar nan
vorticidad = np.nan_to_num(vorticidad, nan=0.0)

def graficar_vorticidad_2d(vorticidad, altura, tiempo_idx):
    vorticidad_tiempo = vorticidad[tiempo_idx, :, :, :].mean(axis=1)
    altura_tiempo = altura[tiempo_idx, :, :, :].mean(axis=1)

    distancia = np.arange(vorticidad_tiempo.shape[1]) * dx
    niveles_altura = altura_tiempo.mean(axis=1)
    
    vmin = np.nanpercentile(vorticidad_tiempo[~np.isnan(vorticidad_tiempo)], 5)
    vmax = np.nanpercentile(vorticidad_tiempo[~np.isnan(vorticidad_tiempo)], 95)
    
    print(f"Tiempo {tiempo_idx}:")
    print(f"  Valores NaN: {np.isnan(vorticidad_tiempo).sum()} de {vorticidad_tiempo.size}")
    print(f"  Rango de valores: {np.nanmin(vorticidad_tiempo)} a {np.nanmax(vorticidad_tiempo)}")
    print(f"  Rango para visualización: {vmin} a {vmax}")

    # graficar
    plt.figure(figsize=(12, 6))
    
    # mapa de calor para la vorticidad
    contour_fill = plt.contourf(distancia, niveles_altura, vorticidad_tiempo, 
                          cmap='coolwarm', levels=50,
                          vmin=vmin, vmax=vmax)
    
    # contorno en v = cero (separar zonas positivas y negativas)
    contour_zero = plt.contour(distancia, niveles_altura, vorticidad_tiempo, 
                        levels=[0], 
                        colors='black', 
                        linewidths=0.8)
    
    # vorticidad positiva (rojo)
    contour_pos = plt.contour(distancia, niveles_altura, vorticidad_tiempo,
                        levels=[0.0006, 0.0012, 0.0018], 
                        colors=['darkred'], 
                        linewidths=0.5, 
                        linestyles='solid')
    
    # vorticidad negativa (azul)
    contour_neg = plt.contour(distancia, niveles_altura, vorticidad_tiempo,
                        levels=[-0.0018, -0.0012, -0.0006], 
                        colors=['darkblue'], 
                        linewidths=0.5, 
                        linestyles='solid')
    
    plt.clabel(contour_zero, inline=True, fontsize=8, fmt='%1.1f')
    
    colorbar = plt.colorbar(contour_fill, label='Vorticidad (1/s)')
    
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='black', lw=0.8, label='Vorticidad = 0'),
        Line2D([0], [0], color='darkred', lw=0.5, label='Vorticidad positiva'),
        Line2D([0], [0], color='darkblue', lw=0.5, label='Vorticidad negativa')
    ]
    plt.legend(handles=legend_elements, loc='upper right')
    
    plt.title(f'Vorticidad en Titán (Tiempo {tiempo_idx})')
    plt.xlabel('Distancia (m)')
    plt.ylabel('Altura (m)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.show()

# verificar si el tiempo está en un rango válido
if tiempo_especifico < vorticidad.shape[0]:
    print(f"Generando gráfica para el tiempo {tiempo_especifico}...")
    graficar_vorticidad_2d(vorticidad, altura, tiempo_especifico)
else:
    print(f"Error: El tiempo {tiempo_especifico} está fuera del rango. El rango válido es de 0 a {vorticidad.shape[0]-1}.")
    tiempo_sugerido = min(20, vorticidad.shape[0]-1)
    print(f"Se sugiere usar tiempo_especifico = {tiempo_sugerido}")