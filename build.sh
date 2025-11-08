#!/usr/bin/env bash
# exit on error
set -o errexit

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Crear directorios necesarios en el disco persistente
mkdir -p /data/uploads/logos
mkdir -p /data/uploads/banners
mkdir -p /data/uploads/productos
mkdir -p /data/uploads/galeria

# También crear directorios en static para desarrollo local
mkdir -p static/uploads/logos
mkdir -p static/uploads/banners
mkdir -p static/uploads/productos
mkdir -p static/uploads/galeria

# Inicializar la base de datos
DB_PATH="${DATABASE_URL:-tienda.db}"
echo "Verificando base de datos en: $DB_PATH"

# Siempre ejecutar init_db.py (usa CREATE TABLE IF NOT EXISTS)
# Esto asegura que todas las tablas existan
echo "Ejecutando inicializacion de base de datos..."
python init_db.py

echo "Base de datos lista en: $DB_PATH"

echo "Build completado exitosamente!"
