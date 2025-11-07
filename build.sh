#!/usr/bin/env bash
# exit on error
set -o errexit

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Crear directorios necesarios
mkdir -p static/uploads/logos
mkdir -p static/uploads/banners
mkdir -p static/uploads/productos
mkdir -p static/uploads/galeria

# Inicializar la base de datos si no existe
if [ ! -f tienda.db ]; then
    echo "Inicializando base de datos..."
    python init_db.py
fi

echo "Build completado exitosamente!"
