#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de migración completa para actualizar esquema de base de datos existente.
Agrega todas las columnas faltantes de manera segura.
"""
import sqlite3
import os
import sys

def migrar_todas_columnas():
    """Migrar base de datos existente con todas las columnas faltantes"""
    db_path = os.getenv('DATABASE_URL', 'tienda.db')
    print(f'\n=== MIGRACIÓN COMPLETA DE ESQUEMA ===')
    print(f'Base de datos: {db_path}\n')
    
    if not os.path.exists(db_path):
        print('[ERROR] Base de datos no existe. Ejecuta init_db.py primero.')
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Lista de todas las columnas a agregar
    migraciones = [
        # Tabla configuracion
        ('configuracion', 'pagomovil_imagen', 'TEXT DEFAULT NULL'),
        ('configuracion', 'binance_imagen', 'TEXT DEFAULT NULL'),
        
        # Tabla productos
        ('productos', 'zone_id_required', 'INTEGER DEFAULT 0'),
        
        # Tabla paquetes
        ('paquetes', 'imagen', 'TEXT DEFAULT NULL'),
        ('paquetes', 'zone_id_required', 'INTEGER DEFAULT 0'),
        
        # Tabla ordenes
        ('ordenes', 'zone_id', 'TEXT DEFAULT NULL'),
    ]
    
    actualizadas = 0
    errores = 0
    
    for tabla, columna, tipo in migraciones:
        try:
            # Verificar si la tabla existe
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tabla}'")
            if not cursor.fetchone():
                print(f'[SKIP] Tabla {tabla} no existe')
                continue
            
            # Intentar agregar la columna
            cursor.execute(f'ALTER TABLE {tabla} ADD COLUMN {columna} {tipo}')
            print(f'[OK] Agregada columna {tabla}.{columna}')
            actualizadas += 1
            
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e).lower():
                print(f'[SKIP] Columna {tabla}.{columna} ya existe')
            else:
                print(f'[ERROR] {tabla}.{columna}: {e}')
                errores += 1
        except Exception as e:
            print(f'[ERROR] {tabla}.{columna}: {e}')
            errores += 1
    
    conn.commit()
    
    # Verificar las migraciones
    print(f'\n=== VERIFICACIÓN ===')
    for tabla, columna, _ in migraciones:
        try:
            cursor.execute(f"PRAGMA table_info({tabla})")
            columnas = [row[1] for row in cursor.fetchall()]
            if columna in columnas:
                print(f'[✓] {tabla}.{columna}')
            else:
                print(f'[✗] {tabla}.{columna} NO EXISTE')
        except:
            pass
    
    conn.close()
    
    print(f'\n=== RESUMEN ===')
    print(f'Columnas agregadas: {actualizadas}')
    print(f'Errores: {errores}')
    print(f'\n[ÉXITO] Migración completada\n')
    
    return errores == 0

if __name__ == '__main__':
    success = migrar_todas_columnas()
    sys.exit(0 if success else 1)
