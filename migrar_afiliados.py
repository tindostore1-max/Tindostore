import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrar_sistema_afiliados():
    """Agregar tablas y columnas para el sistema de afiliados"""
    
    # Detectar ruta de la base de datos
    if os.path.exists('/data'):
        db_path = '/data/tienda.db'
    else:
        db_path = os.getenv('DATABASE_URL', 'tienda.db')
    
    logger.info(f"Conectando a base de datos: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Crear tabla de afiliados si no existe
        logger.info("Creando tabla 'afiliados'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS afiliados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                correo TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                codigo_afiliado TEXT UNIQUE NOT NULL,
                descuento_porcentaje REAL DEFAULT 10.0,
                saldo_acumulado REAL DEFAULT 0.0,
                activo INTEGER DEFAULT 1,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        logger.info("✓ Tabla 'afiliados' creada/verificada")
        
        # 2. Crear tabla de comisiones si no existe
        logger.info("Creando tabla 'comisiones_afiliados'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comisiones_afiliados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                afiliado_id INTEGER NOT NULL,
                orden_id INTEGER NOT NULL,
                monto_orden REAL NOT NULL,
                porcentaje_comision REAL NOT NULL,
                monto_comision REAL NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (afiliado_id) REFERENCES afiliados (id),
                FOREIGN KEY (orden_id) REFERENCES ordenes (id)
            )
        ''')
        logger.info("✓ Tabla 'comisiones_afiliados' creada/verificada")
        
        # 3. Agregar columnas a tabla ordenes
        cursor.execute("PRAGMA table_info(ordenes)")
        columnas_ordenes = [row[1] for row in cursor.fetchall()]
        
        columnas_nuevas = [
            ('afiliado_id', 'INTEGER DEFAULT NULL'),
            ('codigo_afiliado', 'TEXT DEFAULT NULL'),
            ('descuento_aplicado', 'REAL DEFAULT 0.0'),
            ('precio_original', 'REAL DEFAULT 0.0'),
            ('precio_final', 'REAL DEFAULT 0.0')
        ]
        
        for columna, tipo in columnas_nuevas:
            if columna not in columnas_ordenes:
                logger.info(f"Agregando columna '{columna}' a tabla ordenes...")
                cursor.execute(f"ALTER TABLE ordenes ADD COLUMN {columna} {tipo}")
                logger.info(f"✓ Columna '{columna}' agregada")
            else:
                logger.info(f"✓ Columna '{columna}' ya existe")
        
        conn.commit()
        conn.close()
        
        logger.info("✓ Migración del sistema de afiliados completada exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error en migración: {e}", exc_info=True)
        return False

if __name__ == '__main__':
    migrar_sistema_afiliados()
