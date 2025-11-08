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

# Mostrar todos los productos
print("=== PRODUCTOS DISPONIBLES ===")
cursor.execute('SELECT id, nombre, zone_id_required FROM productos')
productos = cursor.fetchall()

for prod in productos:
    zona_status = "SI" if prod[2] == 1 else "NO"
    print(f"ID: {prod[0]} | Nombre: {prod[1]} | Zone ID Requerido: {zona_status}")

print("\n")

# Preguntar qué producto activar
try:
    producto_id = input("Ingresa el ID del producto para activar Zone ID (o 0 para cancelar): ")
    producto_id = int(producto_id)
    
    if producto_id == 0:
        print("Cancelado.")
        conn.close()
        exit()
    
    # Activar zone_id_required para ese producto
    cursor.execute('UPDATE productos SET zone_id_required = 1 WHERE id = ?', (producto_id,))
    conn.commit()
    
    print(f"\n[EXITO] Zone ID activado para el producto ID {producto_id}")
    print("Recarga la pagina del producto para ver el campo Zone ID.")
    
except ValueError:
    print("Error: Debes ingresar un numero valido")
except Exception as e:
    print(f"Error: {e}")

conn.close()
