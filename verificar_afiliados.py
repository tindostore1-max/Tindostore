import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Detectar ruta de la base de datos
if os.path.exists('/data'):
    db_path = '/data/tienda.db'
else:
    db_path = os.getenv('DATABASE_URL', 'tienda.db')

print(f"\n=== VERIFICANDO AFILIADOS EN: {db_path} ===\n")

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Listar todos los afiliados
afiliados = cursor.execute('SELECT * FROM afiliados').fetchall()

if not afiliados:
    print("[X] No hay afiliados en la base de datos\n")
else:
    print(f"[OK] Encontrados {len(afiliados)} afiliado(s):\n")
    
    for afiliado in afiliados:
        print(f"ID: {afiliado['id']}")
        print(f"Nombre: {afiliado['nombre']}")
        print(f"Correo: {afiliado['correo']}")
        print(f"Codigo: {afiliado['codigo_afiliado']}")
        print(f"Descuento: {afiliado['descuento_porcentaje']}%")
        print(f"Saldo: ${afiliado['saldo_acumulado']}")
        print(f"Activo: {afiliado['activo']}")
        print(f"Password hash: {afiliado['password'][:50]}...")
        print(f"Fecha registro: {afiliado['fecha_registro']}")
        print("-" * 60)
        
        # Probar verificación de contraseña
        print("\n[TEST] Prueba de contrasena:")
        test_password = input(f"Ingresa la contrasena que usaste para {afiliado['correo']}: ")
        
        if check_password_hash(afiliado['password'], test_password):
            print("[OK] Contrasena CORRECTA!")
        else:
            print("[ERROR] Contrasena INCORRECTA")
            
            # Ofrecer resetear la contraseña
            reset = input("\nQuieres resetear la contrasena de este afiliado? (s/n): ")
            if reset.lower() == 's':
                nueva_password = input("Nueva contrasena: ")
                nueva_hash = generate_password_hash(nueva_password)
                cursor.execute('UPDATE afiliados SET password = ? WHERE id = ?', (nueva_hash, afiliado['id']))
                conn.commit()
                print(f"[OK] Contrasena actualizada para {afiliado['correo']}")
                print(f"  Nueva contrasena: {nueva_password}")
        
        print("\n")

# Opción para crear un afiliado de prueba
if input("\nQuieres crear un afiliado de prueba? (s/n): ").lower() == 's':
    nombre = input("Nombre: ")
    correo = input("Correo: ")
    password = input("Contrasena: ")
    codigo = input("Codigo de afiliado: ").upper()
    descuento = input("Descuento % (default 10): ") or "10"
    
    password_hash = generate_password_hash(password)
    
    try:
        cursor.execute('''
            INSERT INTO afiliados (nombre, correo, password, codigo_afiliado, descuento_porcentaje)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre, correo, password_hash, codigo, float(descuento)))
        conn.commit()
        print(f"\n[OK] Afiliado creado exitosamente!")
        print(f"   Correo: {correo}")
        print(f"   Contrasena: {password}")
        print(f"   Codigo: {codigo}")
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")

conn.close()
print("\n=== FIN ===\n")
