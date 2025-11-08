import sqlite3
import os

def migrar_rutas():
    """Migrar rutas de imágenes de 'uploads/...' a formato relativo"""
    db_path = os.getenv('DATABASE_URL', 'tienda.db')
    print(f'\n=== MIGRANDO RUTAS DE IMÁGENES ===')
    print(f'Base de datos: {db_path}')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    tablas_rutas = [
        ('configuracion', 'logo'),
        ('configuracion', 'pagomovil_imagen'),
        ('configuracion', 'binance_imagen'),
        ('productos', 'imagen'),
        ('paquetes', 'imagen'),
        ('banners', 'imagen'),
        ('banners_intermedios', 'imagen'),
        ('galeria', 'ruta')
    ]
    
    actualizaciones = 0
    
    for tabla, columna in tablas_rutas:
        try:
            # Verificar si la tabla y columna existen
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tabla}'")
            if not cursor.fetchone():
                print(f'[SKIP] Tabla {tabla} no existe')
                continue
            
            # Actualizar rutas que empiecen con 'uploads/'
            cursor.execute(f"""
                UPDATE {tabla} 
                SET {columna} = REPLACE({columna}, 'uploads/', '')
                WHERE {columna} LIKE 'uploads/%'
            """)
            
            if cursor.rowcount > 0:
                print(f'[OK] Actualizadas {cursor.rowcount} rutas en {tabla}.{columna}')
                actualizaciones += cursor.rowcount
            
        except Exception as e:
            print(f'[ERROR] Error en {tabla}.{columna}: {e}')
    
    conn.commit()
    conn.close()
    
    print(f'\n[ÉXITO] Total de rutas migradas: {actualizaciones}\n')

if __name__ == '__main__':
    migrar_rutas()
