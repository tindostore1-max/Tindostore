#!/usr/bin/env bash
# exit on error
set -o errexit

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Crear directorios en static para desarrollo local
mkdir -p static/uploads/logos
mkdir -p static/uploads/banners
mkdir -p static/uploads/productos
mkdir -p static/uploads/galeria

echo "Build: Directorios locales creados"
echo "NOTA: El disco persistente /data se montará cuando el servicio inicie"
echo "La base de datos se inicializará automáticamente al primer acceso"

echo "Build completado exitosamente!"
