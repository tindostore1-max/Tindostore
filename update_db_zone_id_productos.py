# -*- coding: utf-8 -*-
import sqlite3
import sys

# Configurar encoding para Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Conectar a la base de datos
conn = sqlite3.connect('tienda.db')
cursor = conn.cursor()

try:
    # Agregar columna zone_id_required a productos
    cursor.execute('''
        ALTER TABLE productos 
        ADD COLUMN zone_id_required INTEGER DEFAULT 0
    ''')
    print("[OK] Columna zone_id_required agregada a productos")
except sqlite3.OperationalError as e:
    print(f"[INFO] Columna zone_id_required ya existe en productos o error: {e}")

# Guardar cambios
conn.commit()
conn.close()

print("\n[EXITO] Base de datos actualizada para zone_id en productos!")
print("Ahora el Zone ID se activa a nivel de producto, no de paquete individual.")
