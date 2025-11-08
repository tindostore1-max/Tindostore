# -*- coding: utf-8 -*-
import sqlite3
import sys
import os

# Configurar encoding para Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Conectar a la base de datos
db_path = os.getenv('DATABASE_URL', 'tienda.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Agregar columna zone_id_required a paquetes
    cursor.execute('''
        ALTER TABLE paquetes 
        ADD COLUMN zone_id_required INTEGER DEFAULT 0
    ''')
    print("[OK] Columna zone_id_required agregada a paquetes")
except sqlite3.OperationalError as e:
    print(f"[INFO] Columna zone_id_required ya existe en paquetes o error: {e}")

try:
    # Agregar columna zone_id a ordenes
    cursor.execute('''
        ALTER TABLE ordenes 
        ADD COLUMN zone_id TEXT DEFAULT NULL
    ''')
    print("[OK] Columna zone_id agregada a ordenes")
except sqlite3.OperationalError as e:
    print(f"[INFO] Columna zone_id ya existe en ordenes o error: {e}")

# Guardar cambios
conn.commit()
conn.close()

print("\n[EXITO] Base de datos actualizada exitosamente!")
print("Ahora puedes ejecutar la aplicacion normalmente.")
