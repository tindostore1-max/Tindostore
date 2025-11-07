import sqlite3

def migrar_paquetes():
    conn = sqlite3.connect('tienda.db')
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
