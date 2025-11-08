import sqlite3
import os

def migrar_imagenes_pago():
    db_path = os.getenv('DATABASE_URL', 'tienda.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    print("Agregando columnas de imagenes de metodos de pago...")
    
    columnas = [
        ("pagomovil_imagen", "TEXT DEFAULT NULL"),
        ("binance_imagen", "TEXT DEFAULT NULL")
    ]
    
    for columna, tipo in columnas:
        try:
            c.execute(f'ALTER TABLE configuracion ADD COLUMN {columna} {tipo}')
            print(f"[OK] Columna '{columna}' agregada exitosamente")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"[SKIP] Columna '{columna}' ya existe")
            else:
                print(f"[ERROR] {e}")
    
    conn.commit()
    conn.close()
    print("Migracion completada!")

if __name__ == '__main__':
    migrar_imagenes_pago()
