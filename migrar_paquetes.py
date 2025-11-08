import sqlite3
import os

def migrar_paquetes():
    db_path = os.getenv('DATABASE_URL', 'tienda.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    print("Agregando columna imagen a paquetes...")
    
    try:
        c.execute('ALTER TABLE paquetes ADD COLUMN imagen TEXT DEFAULT NULL')
        print("[OK] Columna 'imagen' agregada exitosamente")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("[SKIP] Columna 'imagen' ya existe")
        else:
            print(f"[ERROR] {e}")
    
    conn.commit()
    conn.close()
    print("Migracion completada!")

if __name__ == '__main__':
    migrar_paquetes()
