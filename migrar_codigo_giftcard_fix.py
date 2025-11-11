import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrar_codigo_giftcard():
    """Agregar columna codigo_giftcard a la tabla ordenes si no existe"""
    
    # Detectar ruta de la base de datos
    if os.path.exists('/data'):
        db_path = '/data/tienda.db'
    else:
        db_path = os.getenv('DATABASE_URL', 'tienda.db')
    
    logger.info(f"Conectando a base de datos: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(ordenes)")
        columnas = [row[1] for row in cursor.fetchall()]
        
        if 'codigo_giftcard' not in columnas:
            logger.info("Agregando columna 'codigo_giftcard' a tabla ordenes...")
            cursor.execute("ALTER TABLE ordenes ADD COLUMN codigo_giftcard TEXT DEFAULT NULL")
            conn.commit()
            logger.info("✓ Columna 'codigo_giftcard' agregada exitosamente")
        else:
            logger.info("✓ Columna 'codigo_giftcard' ya existe")
        
        conn.close()
        logger.info("✓ Migración completada exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error en migración: {e}", exc_info=True)
        return False

if __name__ == '__main__':
    migrar_codigo_giftcard()
