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

# Activar zone_id_required para Mobile Legends (ID 3)
cursor.execute('UPDATE productos SET zone_id_required = 1 WHERE id = 3')
conn.commit()

print("[EXITO] Zone ID activado para Mobile Legends (ID 3)")
print("Recarga la pagina del producto para ver el campo Zone ID.")

# Verificar
cursor.execute('SELECT id, nombre, zone_id_required FROM productos WHERE id = 3')
producto = cursor.fetchone()
print(f"\nVerificacion: {producto[1]} - Zone ID Requerido: {'SI' if producto[2] == 1 else 'NO'}")

conn.close()
