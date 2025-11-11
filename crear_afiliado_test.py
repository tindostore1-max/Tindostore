import sqlite3
import os
from werkzeug.security import generate_password_hash

# Detectar ruta de la base de datos
if os.path.exists('/data'):
    db_path = '/data/tienda.db'
else:
    db_path = os.getenv('DATABASE_URL', 'tienda.db')

print(f"\n=== CREANDO AFILIADO DE PRUEBA ===")
print(f"Base de datos: {db_path}\n")

# Datos del afiliado de prueba
nombre = "Test Afiliado"
correo = "afiliado@test.com"
password = "12345678"
codigo = "TEST2024"
descuento = 10.0

print(f"Nombre: {nombre}")
print(f"Correo: {correo}")
print(f"Contrasena: {password}")
print(f"Codigo: {codigo}")
print(f"Descuento: {descuento}%\n")

# Hash de la contraseña
password_hash = generate_password_hash(password)
print(f"Password hash generado: {password_hash[:50]}...\n")

# Conectar a la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Verificar si ya existe
    cursor.execute('SELECT id FROM afiliados WHERE correo = ?', (correo,))
    existe = cursor.fetchone()
    
    if existe:
        print(f"[INFO] El afiliado con correo {correo} ya existe.")
        print(f"[INFO] Actualizando contraseña y activando...\n")
        cursor.execute('''
            UPDATE afiliados 
            SET password = ?, activo = 1, codigo_afiliado = ?, descuento_porcentaje = ?
            WHERE correo = ?
        ''', (password_hash, codigo, descuento, correo))
        conn.commit()
        print(f"[OK] Afiliado actualizado!")
    else:
        # Insertar nuevo afiliado
        cursor.execute('''
            INSERT INTO afiliados (nombre, correo, password, codigo_afiliado, descuento_porcentaje, activo)
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (nombre, correo, password_hash, codigo, descuento))
        conn.commit()
        print(f"[OK] Afiliado creado exitosamente!")
    
    print(f"\n=== DATOS PARA LOGIN ===")
    print(f"URL: http://127.0.0.1:5000/afiliado/login")
    print(f"Correo: {correo}")
    print(f"Contrasena: {password}")
    print(f"\n=== COPIA Y PEGA EXACTAMENTE ===")
    print(f"Correo: afiliado@test.com")
    print(f"Contrasena: 12345678")
    
except Exception as e:
    print(f"[ERROR] {e}")
finally:
    conn.close()

print("\n=== FIN ===\n")
