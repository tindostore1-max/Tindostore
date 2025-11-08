import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

def migrar_codigo_giftcard():
    """Agregar campo codigo_giftcard a tabla ordenes"""
    
    # Detectar entorno
    if os.path.exists('/data'):
        DATABASE_URL = '/data/tienda.db'
    else:
        DATABASE_URL = os.getenv('DATABASE_URL', 'tienda.db')
    
    print(f"Migrando base de datos: {DATABASE_URL}")
    
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Verificar si la columna ya existe
    cursor.execute("PRAGMA table_info(ordenes)")
    columnas = [row[1] for row in cursor.fetchall()]
    
    if 'codigo_giftcard' not in columnas:
        print("Agregando columna 'codigo_giftcard' a tabla ordenes...")
        cursor.execute('ALTER TABLE ordenes ADD COLUMN codigo_giftcard TEXT')
        conn.commit()
        print("OK - Columna 'codigo_giftcard' agregada exitosamente")
    else:
        print("OK - Columna 'codigo_giftcard' ya existe")
    
    conn.close()
    print("Migración completada")

if __name__ == '__main__':
    migrar_codigo_giftcard()
