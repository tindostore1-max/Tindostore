import sqlite3
import os
from werkzeug.security import generate_password_hash

def init_database():
    db_path = os.getenv('DATABASE_URL', 'tienda.db')
    print(f'\n=== INICIALIZANDO BASE DE DATOS ===')
    print(f'Ruta: {db_path}')
    
    # Verificar si el directorio existe
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        print(f'Creando directorio: {db_dir}')
        os.makedirs(db_dir, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    print('Conexión a base de datos exitosa')
    
    # Tabla de usuarios
    print('Creando tabla: usuarios')
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de configuración del sitio
    print('Creando tabla: configuracion')
    c.execute('''
        CREATE TABLE IF NOT EXISTS configuracion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_sitio TEXT DEFAULT 'Mi Tienda',
            logo TEXT DEFAULT 'uploads/logos/default-logo.png',
            tasa_cambio REAL DEFAULT 36.5,
            pagomovil_banco TEXT DEFAULT 'Banco',
            pagomovil_telefono TEXT DEFAULT '0424-0000000',
            pagomovil_cedula TEXT DEFAULT 'V-00000000',
            pagomovil_titular TEXT DEFAULT 'Titular',
            binance_correo TEXT DEFAULT 'ejemplo@correo.com',
            binance_pay_id TEXT DEFAULT ''
        )
    ''')
    
    # Tabla de categorías
    print('Creando tabla: categorias')
    c.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            activo INTEGER DEFAULT 1,
            orden INTEGER DEFAULT 0
        )
    ''')
    
    # Tabla de productos
    print('Creando tabla: productos')
    c.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            imagen TEXT,
            categoria_id INTEGER,
            tipo TEXT DEFAULT 'juego',
            activo INTEGER DEFAULT 1,
            orden INTEGER DEFAULT 0,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (categoria_id) REFERENCES categorias (id)
        )
    ''')
    
    # Tabla de paquetes
    print('Creando tabla: paquetes')
    c.execute('''
        CREATE TABLE IF NOT EXISTS paquetes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio REAL NOT NULL,
            FOREIGN KEY (producto_id) REFERENCES productos (id) ON DELETE CASCADE
        )
    ''')
    
    # Tabla de banners
    print('Creando tabla: banners')
    c.execute('''
        CREATE TABLE IF NOT EXISTS banners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            imagen TEXT,
            enlace TEXT,
            activo INTEGER DEFAULT 1,
            orden INTEGER DEFAULT 0
        )
    ''')
    
    # Tabla de banners intermedios (3 banners entre juegos móviles y gift cards)
    print('Creando tabla: banners_intermedios')
    c.execute('''
        CREATE TABLE IF NOT EXISTS banners_intermedios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            imagen TEXT,
            enlace TEXT,
            activo INTEGER DEFAULT 1,
            orden INTEGER DEFAULT 0
        )
    ''')
    
    # Tabla de galería de imágenes
    print('Creando tabla: galeria')
    c.execute('''
        CREATE TABLE IF NOT EXISTS galeria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            ruta TEXT NOT NULL,
            tipo TEXT DEFAULT 'general',
            fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de órdenes
    print('Creando tabla: ordenes')
    c.execute('''
        CREATE TABLE IF NOT EXISTS ordenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            producto_id INTEGER NOT NULL,
            paquete_id INTEGER NOT NULL,
            player_id TEXT,
            metodo_pago TEXT NOT NULL,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL,
            referencia TEXT NOT NULL,
            estado TEXT DEFAULT 'pendiente',
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
            FOREIGN KEY (producto_id) REFERENCES productos (id),
            FOREIGN KEY (paquete_id) REFERENCES paquetes (id)
        )
    ''')
    
    # Crear usuario admin por defecto
    print('\n=== DATOS INICIALES ===')
    admin_password = generate_password_hash('123456')
    try:
        c.execute('''
            INSERT INTO usuarios (username, email, password, is_admin)
            VALUES (?, ?, ?, ?)
        ''', ('admin', 'admin@tienda.com', admin_password, 1))
        print('[OK] Usuario admin creado (user: admin, pass: 123456)')
    except sqlite3.IntegrityError:
        print('[SKIP] Usuario admin ya existe')
    
    # Crear configuración por defecto
    try:
        c.execute('''
            INSERT INTO configuracion (nombre_sitio, logo)
            VALUES (?, ?)
        ''', ('Mi Tienda Online', 'uploads/logos/default-logo.png'))
        print('[OK] Configuración inicial creada')
    except sqlite3.IntegrityError:
        print('[SKIP] Configuración ya existe')
    
    conn.commit()
    
    # Verificar que la tabla configuracion existe y tiene datos
    result = c.execute('SELECT COUNT(*) FROM configuracion').fetchone()
    print(f'\n=== VERIFICACIÓN ===')
    print(f'Registros en tabla configuracion: {result[0]}')
    
    conn.close()
    print('\n[ÉXITO] Base de datos inicializada correctamente\n')

if __name__ == '__main__':
    init_database()
