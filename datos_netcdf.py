import netCDF4 as nc

archivo = 'C:/Users/anaa_/Downloads/A3.nc'  # ruta del archivo
datos = nc.Dataset(archivo) # abrir el archivo

# datos del archivo
print("Variables disponibles:")
for variable in datos.variables:
    print(f" - {variable}: {datos.variables[variable].shape}")

print("\nDimensiones disponibles:")
for dimension in datos.dimensions:
    print(f" - {dimension}: {len(datos.dimensions[dimension])}")

print("\nAtributos globales:")
for attr in datos.ncattrs():
    print(f" - {attr}: {getattr(datos, attr)}")