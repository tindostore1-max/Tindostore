import sqlite3
import os

def migrar_base_datos():
    db_path = os.getenv('DATABASE_URL', 'tienda.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    print("Iniciando migración de base de datos...")
    
    # Lista de columnas a agregar
    columnas_nuevas = [
        ("tasa_cambio", "REAL DEFAULT 36.5"),
        ("pagomovil_banco", "TEXT DEFAULT 'Banco'"),
        ("pagomovil_telefono", "TEXT DEFAULT '0424-0000000'"),
        ("pagomovil_cedula", "TEXT DEFAULT 'V-00000000'"),
        ("pagomovil_titular", "TEXT DEFAULT 'Titular'"),
        ("binance_correo", "TEXT DEFAULT 'ejemplo@correo.com'"),
        ("binance_pay_id", "TEXT DEFAULT ''")
    ]
    
    # Intentar agregar cada columna
    for columna, tipo in columnas_nuevas:
        try:
            c.execute(f'ALTER TABLE configuracion ADD COLUMN {columna} {tipo}')
            print(f"[OK] Columna '{columna}' agregada exitosamente")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"[SKIP] Columna '{columna}' ya existe, saltando...")
            else:
                print(f"[ERROR] Error agregando columna '{columna}': {e}")
    
    conn.commit()
    conn.close()
    print("\nMigracion completada!")

if __name__ == '__main__':
    migrar_base_datos()
