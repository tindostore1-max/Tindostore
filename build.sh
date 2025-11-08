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
DB_PATH="${DATABASE_URL:-tienda.db}"
if [ ! -f "$DB_PATH" ]; then
    echo "Inicializando base de datos en $DB_PATH..."
    python init_db.py
else
    echo "Base de datos ya existe en $DB_PATH"
fi

echo "Build completado exitosamente!"
