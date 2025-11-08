from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import sqlite3
import os
import logging
import secrets
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configurar SECRET_KEY persistente
def get_secret_key():
    """Obtener o generar SECRET_KEY persistente"""
    secret_key = os.getenv('SECRET_KEY')
    
    if secret_key:
        logger.info("SECRET_KEY cargada desde variable de entorno")
        return secret_key
    
    # Determinar la ruta del archivo secret_key según el entorno
    if os.path.exists('/data'):
        secret_file = '/data/.secret_key'
    else:
        secret_file = '.secret_key'
    
    try:
        if os.path.exists(secret_file):
            with open(secret_file, 'r') as f:
                secret_key = f.read().strip()
                logger.info(f"SECRET_KEY cargada desde archivo: {secret_file}")
        else:
            # Generar nueva SECRET_KEY
            secret_key = secrets.token_hex(32)
            
            # Guardar en disco persistente
            with open(secret_file, 'w') as f:
                f.write(secret_key)
            logger.info(f"Nueva SECRET_KEY generada y guardada en: {secret_file}")
    except Exception as e:
        logger.error(f"Error manejando SECRET_KEY: {e}")
        # Usar una clave temporal (no recomendado para producción)
        secret_key = 'fallback_secret_key_' + secrets.token_hex(16)
        logger.warning("Usando SECRET_KEY temporal. Configura SECRET_KEY en variables de entorno.")
    
    return secret_key

app.secret_key = get_secret_key()

# Configuración de sesiones (común para todos los entornos)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # 24 horas
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Detectar entorno de producción y usar ruta absoluta
if os.path.exists('/data'):
    # Producción en Render con disco persistente
    app.config['UPLOAD_FOLDER'] = '/data/uploads'
    DATABASE_URL = '/data/tienda.db'
    
    # Configuración específica de producción
    # SESSION_COOKIE_SECURE = False temporalmente para debugging
    # Cambiar a True después de verificar que funciona
    app.config['SESSION_COOKIE_SECURE'] = False
    
    logger.info("Entorno de PRODUCCIÓN detectado (Render)")
else:
    # Desarrollo local
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'static/uploads')
    DATABASE_URL = os.getenv('DATABASE_URL', 'tienda.db')
    
    # Configuración específica de desarrollo
    app.config['SESSION_COOKIE_SECURE'] = False
    
    logger.info("Entorno de DESARROLLO detectado (Local)")

app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB max

# Variables de administrador desde entorno
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@tindo.com')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'Admin123!')

logger.info(f"DATABASE_URL configurado en: {DATABASE_URL}")
logger.info(f"UPLOAD_FOLDER configurado en: {app.config['UPLOAD_FOLDER']}")

# Verificar y crear base de datos si no existe
def inicializar_sistema():
    """Inicializar base de datos y directorios al arrancar el servicio"""
    logger.info("=== INICIALIZANDO SISTEMA ===")
    
    # 1. Crear directorios de uploads si no existen
    upload_folder = app.config['UPLOAD_FOLDER']
    logger.info(f"Verificando directorio de uploads: {upload_folder}")
    
    try:
        directorios = [
            upload_folder,
            os.path.join(upload_folder, 'logos'),
            os.path.join(upload_folder, 'banners'),
            os.path.join(upload_folder, 'productos'),
            os.path.join(upload_folder, 'galeria')
        ]
        
        for directorio in directorios:
            if not os.path.exists(directorio):
                logger.info(f"Creando directorio: {directorio}")
                os.makedirs(directorio, exist_ok=True)
            else:
                logger.info(f"Directorio existe: {directorio}")
    except Exception as e:
        logger.error(f"Error creando directorios: {e}")
        raise
    
    # 2. Verificar/crear base de datos
    logger.info(f"Verificando base de datos: {DATABASE_URL}")
    
    try:
        # Crear directorio de la BD si no existe
        db_dir = os.path.dirname(DATABASE_URL)
        if db_dir and not os.path.exists(db_dir):
            logger.info(f"Creando directorio de BD: {db_dir}")
            os.makedirs(db_dir, exist_ok=True)
        
        # Verificar si la BD existe y tiene tablas
        if not os.path.exists(DATABASE_URL):
            logger.warning(f"Base de datos no existe: {DATABASE_URL}")
            logger.info("Inicializando base de datos...")
            from init_db import init_database
            init_database()
        else:
            # Verificar que tenga las tablas necesarias
            conn = sqlite3.connect(DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='configuracion'")
            
            if not cursor.fetchone():
                logger.warning("Base de datos sin tablas. Inicializando...")
                conn.close()
                from init_db import init_database
                init_database()
            else:
                # Verificar si necesita migraciones de esquema
                cursor.execute("PRAGMA table_info(productos)")
                columnas = [row[1] for row in cursor.fetchall()]
                
                if 'zone_id_required' not in columnas:
                    logger.warning("Base de datos necesita migraciones de esquema. Ejecutando...")
                    conn.close()
                    from migrar_todas_columnas import migrar_todas_columnas
                    migrar_todas_columnas()
                    logger.info("Migraciones de esquema completadas")
                else:
                    logger.info("Esquema de BD verificado correctamente")
                
                # Migrar rutas de imágenes si es necesario
                cursor.execute("SELECT logo FROM configuracion WHERE logo LIKE 'uploads/%' LIMIT 1")
                if cursor.fetchone():
                    logger.warning("BD tiene rutas antiguas. Migrando rutas de imágenes...")
                    conn.close()
                    from migrar_rutas_imagenes import migrar_rutas
                    migrar_rutas()
                    logger.info("Rutas de imágenes migradas")
                else:
                    logger.info("Rutas de imágenes correctas")
                    conn.close()
                
    except Exception as e:
        logger.error(f"Error verificando base de datos: {e}", exc_info=True)
        raise
    
    logger.info("=== SISTEMA INICIALIZADO ===")

# Inicializar sistema al arrancar
inicializar_sistema()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    try:
        conn = sqlite3.connect(DATABASE_URL)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Error conectando a base de datos {DATABASE_URL}: {str(e)}")
        raise

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            logger.warning(f"Acceso no autorizado a {f.__name__}: session vacía")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            logger.warning(f"Acceso admin denegado a {f.__name__}: no hay user_id en session")
            flash('Acceso denegado. Por favor inicia sesión.', 'danger')
            return redirect(url_for('login'))
        if not session.get('is_admin'):
            logger.warning(f"Acceso admin denegado a {f.__name__}: user_id={session.get('user_id')} no es admin")
            flash('Acceso denegado', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ============= RUTAS PÚBLICAS =============

@app.route('/')
def index():
    logger.info(f"→ Cargando index: session tiene user_id={session.get('user_id')}, is_admin={session.get('is_admin')}")
    try:
        db = get_db()
        
        # Obtener configuración del sitio
        try:
            config = db.execute('SELECT * FROM configuracion WHERE id = 1').fetchone()
            if not config:
                logger.warning("No se encontró configuración con id=1, creando por defecto")
                # Crear configuración por defecto
                db.execute('''
                    INSERT INTO configuracion (nombre_sitio, logo)
                    VALUES (?, ?)
                ''', ('Mi Tienda Online', 'logos/default-logo.png'))
                db.commit()
                config = db.execute('SELECT * FROM configuracion WHERE id = 1').fetchone()
        except sqlite3.OperationalError as e:
            logger.error(f"Error en tabla configuracion: {e}")
            # Si la tabla no existe, reinicializar base de datos
            logger.warning("Reinicializando base de datos...")
            db.close()
            from init_db import init_database
            init_database()
            db = get_db()
            config = db.execute('SELECT * FROM configuracion WHERE id = 1').fetchone()
        
        # Obtener banners activos
        banners = db.execute('SELECT * FROM banners WHERE activo = 1 ORDER BY orden').fetchall()
        
        # Obtener banners intermedios activos (máximo 3)
        banners_intermedios = db.execute('SELECT * FROM banners_intermedios WHERE activo = 1 ORDER BY orden LIMIT 3').fetchall()
        
        # Obtener productos activos (juegos móviles)
        productos = db.execute('''
            SELECT p.*, c.nombre as categoria_nombre 
            FROM productos p 
            LEFT JOIN categorias c ON p.categoria_id = c.id 
            WHERE p.activo = 1 
            ORDER BY p.orden
        ''').fetchall()
        
        # Obtener categorías activas
        categorias = db.execute('SELECT * FROM categorias WHERE activo = 1 ORDER BY orden').fetchall()
        
        db.close()
        
        return render_template('index.html', 
                             config=config, 
                             banners=banners,
                             banners_intermedios=banners_intermedios, 
                             productos=productos,
                             categorias=categorias)
    except Exception as e:
        logger.error(f"Error en ruta /: {str(e)}", exc_info=True)
        return f"Error al cargar la página: {str(e)}<br><br>DATABASE_URL: {DATABASE_URL}<br>Revisa los logs para más información.", 500

@app.route('/producto/<int:id>')
def producto_detalle(id):
    db = get_db()
    
    producto = db.execute('SELECT * FROM productos WHERE id = ? AND activo = 1', (id,)).fetchone()
    if not producto:
        flash('Producto no encontrado', 'danger')
        return redirect(url_for('index'))
    
    # Obtener paquetes del producto
    paquetes = db.execute('SELECT * FROM paquetes WHERE producto_id = ? ORDER BY precio', (id,)).fetchall()
    
    config = db.execute('SELECT * FROM configuracion WHERE id = 1').fetchone()
    
    db.close()
    
    return render_template('producto_detalle.html', 
                         producto=producto, 
                         paquetes=paquetes,
                         config=config)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        db = get_db()
        
        # Obtener datos del formulario
        producto_id = request.form.get('producto_id')
        paquete_id = request.form.get('paquete_id')
        player_id = request.form.get('player_id', '')
        zone_id = request.form.get('zone_id', '')
        metodo_pago = request.form.get('metodo_pago')
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        
        # Guardar en sesión para el checkout
        session['checkout_data'] = {
            'producto_id': producto_id,
            'paquete_id': paquete_id,
            'player_id': player_id,
            'zone_id': zone_id,
            'metodo_pago': metodo_pago,
            'nombre': nombre,
            'correo': correo
        }
        
        # Obtener información del producto y paquete
        producto = db.execute('SELECT * FROM productos WHERE id = ?', (producto_id,)).fetchone()
        paquete = db.execute('SELECT * FROM paquetes WHERE id = ?', (paquete_id,)).fetchone()
        config = db.execute('SELECT * FROM configuracion WHERE id = 1').fetchone()
        
        db.close()
        
        return render_template('checkout.html', 
                             producto=producto,
                             paquete=paquete,
                             checkout_data=session['checkout_data'],
                             config=config)
    
    return redirect(url_for('index'))

@app.route('/confirmar_orden', methods=['POST'])
def confirmar_orden():
    if 'checkout_data' not in session:
        flash('Sesión expirada', 'danger')
        return redirect(url_for('index'))
    
    referencia = request.form.get('referencia')
    if not referencia:
        flash('Debe proporcionar una referencia de pago', 'danger')
        return redirect(url_for('checkout'))
    
    checkout_data = session['checkout_data']
    
    db = get_db()
    
    # Crear la orden
    user_id = session.get('user_id', None)
    
    db.execute('''
        INSERT INTO ordenes 
        (usuario_id, producto_id, paquete_id, player_id, zone_id, metodo_pago, nombre, correo, referencia, estado, fecha)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        checkout_data['producto_id'],
        checkout_data['paquete_id'],
        checkout_data['player_id'],
        checkout_data.get('zone_id', ''),
        checkout_data['metodo_pago'],
        checkout_data['nombre'],
        checkout_data['correo'],
        referencia,
        'pendiente',
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    
    db.commit()
    orden_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    
    # Limpiar sesión
    session.pop('checkout_data', None)
    
    flash(f'¡Orden #{orden_id} creada exitosamente! Procesaremos tu pedido pronto.', 'success')
    return redirect(url_for('index'))

# ============= AUTENTICACIÓN =============

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Verificar si es el administrador desde variables de entorno
        if username == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session.permanent = True  # Mantener sesión activa
            session['user_id'] = 0  # ID especial para admin de entorno
            session['username'] = ADMIN_EMAIL
            session['is_admin'] = True
            session['is_env_admin'] = True
            logger.info(f"✓ Admin login exitoso: {ADMIN_EMAIL}")
            logger.info(f"✓ Sesión configurada: user_id={session.get('user_id')}, is_admin={session.get('is_admin')}, permanent={session.permanent}")
            return redirect(url_for('admin_dashboard'))
        
        # Verificar usuarios en la base de datos
        db = get_db()
        user = db.execute('SELECT * FROM usuarios WHERE username = ?', (username,)).fetchone()
        db.close()
        
        if user and check_password_hash(user['password'], password):
            session.permanent = True  # Mantener sesión activa
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            session['is_env_admin'] = False
            logger.info(f"Usuario login exitoso: {user['username']}")
            
            if user['is_admin']:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('perfil'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    
    db = get_db()
    config = db.execute('SELECT * FROM configuracion WHERE id = 1').fetchone()
    db.close()
    
    return render_template('login.html', config=config)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        db = get_db()
        
        # Verificar si el usuario ya existe
        existing = db.execute('SELECT * FROM usuarios WHERE username = ? OR email = ?', 
                            (username, email)).fetchone()
        
        if existing:
            flash('El usuario o correo ya existe', 'danger')
        else:
            hashed_password = generate_password_hash(password)
            db.execute('''
                INSERT INTO usuarios (username, email, password, is_admin)
                VALUES (?, ?, ?, 0)
            ''', (username, email, hashed_password))
            db.commit()
            flash('Cuenta creada exitosamente. Ahora puedes iniciar sesión.', 'success')
            db.close()
            return redirect(url_for('login'))
        
        db.close()
    
    db = get_db()
    config = db.execute('SELECT * FROM configuracion WHERE id = 1').fetchone()
    db.close()
    
    return render_template('registro.html', config=config)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/perfil')
@login_required
def perfil():
    db = get_db()
    
    user = db.execute('SELECT * FROM usuarios WHERE id = ?', (session['user_id'],)).fetchone()
    
    # Obtener órdenes del usuario
    ordenes = db.execute('''
        SELECT o.*, p.nombre as producto_nombre, pk.nombre as paquete_nombre, pk.precio
        FROM ordenes o
        LEFT JOIN productos p ON o.producto_id = p.id
        LEFT JOIN paquetes pk ON o.paquete_id = pk.id
        WHERE o.usuario_id = ?
        ORDER BY o.fecha DESC
    ''', (session['user_id'],)).fetchall()
    
    config = db.execute('SELECT * FROM configuracion WHERE id = 1').fetchone()
    
    db.close()
    
    return render_template('perfil.html', user=user, ordenes=ordenes, config=config)

@app.route('/actualizar_perfil', methods=['POST'])
@login_required
def actualizar_perfil():
    email = request.form.get('email')
    nueva_password = request.form.get('nueva_password')
    
    db = get_db()
    
    if nueva_password:
        hashed_password = generate_password_hash(nueva_password)
        db.execute('UPDATE usuarios SET email = ?, password = ? WHERE id = ?',
                  (email, hashed_password, session['user_id']))
    else:
        db.execute('UPDATE usuarios SET email = ? WHERE id = ?',
                  (email, session['user_id']))
    
    db.commit()
    db.close()
    
    flash('Perfil actualizado exitosamente', 'success')
    return redirect(url_for('perfil'))

# ============= PANEL ADMIN =============

@app.route('/admin')
@admin_required
def admin_dashboard():
    logger.info(f"✓ Acceso a admin_dashboard: user_id={session.get('user_id')}, is_admin={session.get('is_admin')}, username={session.get('username')}")
    
    db = get_db()
    
    # Estadísticas
    total_productos = db.execute('SELECT COUNT(*) as total FROM productos').fetchone()['total']
    total_ordenes = db.execute('SELECT COUNT(*) as total FROM ordenes').fetchone()['total']
    ordenes_pendientes = db.execute('SELECT COUNT(*) as total FROM ordenes WHERE estado = "pendiente"').fetchone()['total']
    
    # Órdenes recientes
    ordenes = db.execute('''
        SELECT o.*, p.nombre as producto_nombre, pk.nombre as paquete_nombre, pk.precio
        FROM ordenes o
        LEFT JOIN productos p ON o.producto_id = p.id
        LEFT JOIN paquetes pk ON o.paquete_id = pk.id
        ORDER BY o.fecha DESC
        LIMIT 10
    ''').fetchall()
    
    config = db.execute('SELECT * FROM configuracion WHERE id = 1').fetchone()
    
    db.close()
    
    return render_template('admin/dashboard.html', 
                         total_productos=total_productos,
                         total_ordenes=total_ordenes,
                         ordenes_pendientes=ordenes_pendientes,
                         ordenes=ordenes,
                         config=config)

@app.route('/admin/configuracion', methods=['GET', 'POST'])
@admin_required
def admin_configuracion():
    db = get_db()
    
    if request.method == 'POST':
        nombre_sitio = request.form.get('nombre_sitio')
        logo_path = request.form.get('logo_ruta')
        tasa_cambio = request.form.get('tasa_cambio', 36.5)
        
        # Datos de Pago Móvil
        pagomovil_banco = request.form.get('pagomovil_banco', '')
        pagomovil_telefono = request.form.get('pagomovil_telefono', '')
        pagomovil_cedula = request.form.get('pagomovil_cedula', '')
        pagomovil_titular = request.form.get('pagomovil_titular', '')
        
        # Datos de Binance
        binance_correo = request.form.get('binance_correo', '')
        binance_pay_id = request.form.get('binance_pay_id', '')
        
        # Imágenes de métodos de pago
        pagomovil_imagen = request.form.get('pagomovil_imagen')
        binance_imagen = request.form.get('binance_imagen')
        
        # Actualizar o crear configuración
        config = db.execute('SELECT * FROM configuracion WHERE id = 1').fetchone()
        
        if config:
            # Construir query dinámico
            if logo_path:
                db.execute('''UPDATE configuracion SET 
                    nombre_sitio = ?, logo = ?, tasa_cambio = ?,
                    pagomovil_banco = ?, pagomovil_telefono = ?, pagomovil_cedula = ?, pagomovil_titular = ?, pagomovil_imagen = ?,
                    binance_correo = ?, binance_pay_id = ?, binance_imagen = ?
                    WHERE id = 1''',
                    (nombre_sitio, logo_path, tasa_cambio,
                     pagomovil_banco, pagomovil_telefono, pagomovil_cedula, pagomovil_titular, pagomovil_imagen,
                     binance_correo, binance_pay_id, binance_imagen))
            else:
                db.execute('''UPDATE configuracion SET 
                    nombre_sitio = ?, tasa_cambio = ?,
                    pagomovil_banco = ?, pagomovil_telefono = ?, pagomovil_cedula = ?, pagomovil_titular = ?, pagomovil_imagen = ?,
                    binance_correo = ?, binance_pay_id = ?, binance_imagen = ?
                    WHERE id = 1''',
                    (nombre_sitio, tasa_cambio,
                     pagomovil_banco, pagomovil_telefono, pagomovil_cedula, pagomovil_titular, pagomovil_imagen,
                     binance_correo, binance_pay_id, binance_imagen))
        else:
            logo_path = logo_path or 'logos/default-logo.png'
            db.execute('''INSERT INTO configuracion 
                (nombre_sitio, logo, tasa_cambio, pagomovil_banco, pagomovil_telefono, pagomovil_cedula, pagomovil_titular, pagomovil_imagen,
                 binance_correo, binance_pay_id, binance_imagen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (nombre_sitio, logo_path, tasa_cambio,
                 pagomovil_banco, pagomovil_telefono, pagomovil_cedula, pagomovil_titular, pagomovil_imagen,
                 binance_correo, binance_pay_id, binance_imagen))
        
        db.commit()
        flash('Configuración actualizada', 'success')
    
    config = db.execute('SELECT * FROM configuracion WHERE id = 1').fetchone()
    db.close()
    
    return render_template('admin/configuracion.html', config=config)

@app.route('/admin/productos', methods=['GET'])
@admin_required
def admin_productos():
    db = get_db()
    productos = db.execute('''
        SELECT p.*, c.nombre as categoria_nombre 
        FROM productos p 
        LEFT JOIN categorias c ON p.categoria_id = c.id 
        ORDER BY p.orden
    ''').fetchall()
    categorias = db.execute('SELECT * FROM categorias ORDER BY nombre').fetchall()
    config = db.execute('SELECT * FROM configuracion WHERE id = 1').fetchone()
    db.close()
    
    return render_template('admin/productos.html', productos=productos, categorias=categorias, config=config)

@app.route('/admin/productos/crear', methods=['POST'])
@admin_required
def admin_productos_crear():
    try:
        logger.info("Iniciando creación de producto")
        db = get_db()
        
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        categoria_id = request.form.get('categoria_id')
        tipo = request.form.get('tipo')  # juego o giftcard
        orden = request.form.get('orden', 0)
        zone_id_required = 1 if request.form.get('zone_id_required') else 0
        
        # Obtener imagen de galería
        imagen_path = request.form.get('imagen_ruta')
        
        logger.info(f"Datos producto: nombre={nombre}, tipo={tipo}, imagen={imagen_path}")
        
        db.execute('''
            INSERT INTO productos (nombre, descripcion, imagen, categoria_id, tipo, activo, orden, zone_id_required)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?)
        ''', (nombre, descripcion, imagen_path, categoria_id, tipo, orden, zone_id_required))
        
        db.commit()
        db.close()
        
        logger.info("Producto creado exitosamente")
        flash('Producto creado exitosamente', 'success')
        return redirect(url_for('admin_productos'))
    except Exception as e:
        logger.error(f"Error creando producto: {str(e)}", exc_info=True)
        flash(f'Error al crear producto: {str(e)}', 'danger')
        return redirect(url_for('admin_productos'))

@app.route('/admin/productos/<int:id>/datos', methods=['GET'])
@admin_required
def admin_productos_datos(id):
    db = get_db()
    producto = db.execute('SELECT * FROM productos WHERE id = ?', (id,)).fetchone()
    db.close()
    
    if producto:
        return {
            'id': producto['id'],
            'nombre': producto['nombre'],
            'descripcion': producto['descripcion'],
            'imagen': producto['imagen'],
            'categoria_id': producto['categoria_id'],
            'tipo': producto['tipo'],
            'activo': producto['activo'],
            'orden': producto['orden'],
            'zone_id_required': producto['zone_id_required'] if 'zone_id_required' in producto.keys() else 0
        }
    return {'error': 'Producto no encontrado'}, 404

@app.route('/admin/productos/editar/<int:id>', methods=['POST'])
@admin_required
def admin_productos_editar(id):
    db = get_db()
    
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    categoria_id = request.form.get('categoria_id')
    tipo = request.form.get('tipo')
    orden = request.form.get('orden', 0)
    activo = 1 if request.form.get('activo') else 0
    zone_id_required = 1 if request.form.get('zone_id_required') else 0
    
    # Obtener imagen de galería
    imagen_path = request.form.get('imagen_ruta')
    
    # Si hay imagen nueva de galería
    if imagen_path:
        db.execute('''
            UPDATE productos 
            SET nombre = ?, descripcion = ?, imagen = ?, categoria_id = ?, tipo = ?, activo = ?, orden = ?, zone_id_required = ?
            WHERE id = ?
        ''', (nombre, descripcion, imagen_path, categoria_id, tipo, activo, orden, zone_id_required, id))
    else:
        db.execute('''
            UPDATE productos 
            SET nombre = ?, descripcion = ?, categoria_id = ?, tipo = ?, activo = ?, orden = ?, zone_id_required = ?
            WHERE id = ?
        ''', (nombre, descripcion, categoria_id, tipo, activo, orden, zone_id_required, id))
    
    db.commit()
    db.close()
    
    flash('Producto actualizado exitosamente', 'success')
    return redirect(url_for('admin_productos'))

@app.route('/admin/productos/eliminar/<int:id>')
@admin_required
def admin_productos_eliminar(id):
    db = get_db()
    db.execute('DELETE FROM productos WHERE id = ?', (id,))
    db.commit()
    db.close()
    
    flash('Producto eliminado', 'success')
    return redirect(url_for('admin_productos'))

@app.route('/admin/paquetes/<int:producto_id>')
@admin_required
def admin_paquetes(producto_id):
    db = get_db()
    producto = db.execute('SELECT * FROM productos WHERE id = ?', (producto_id,)).fetchone()
    paquetes = db.execute('SELECT * FROM paquetes WHERE producto_id = ? ORDER BY precio', (producto_id,)).fetchall()
    config = db.execute('SELECT * FROM configuracion WHERE id = 1').fetchone()
    db.close()
    
    return render_template('admin/paquetes.html', producto=producto, paquetes=paquetes, config=config)

@app.route('/admin/paquetes/crear/<int:producto_id>', methods=['POST'])
@admin_required
def admin_paquetes_crear(producto_id):
    db = get_db()
    
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    precio = request.form.get('precio')
    imagen_ruta = request.form.get('imagen_ruta')
    zone_id_required = 1 if request.form.get('zone_id_required') else 0
    
    db.execute('''
        INSERT INTO paquetes (producto_id, nombre, descripcion, precio, imagen, zone_id_required)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (producto_id, nombre, descripcion, precio, imagen_ruta, zone_id_required))
    
    db.commit()
    db.close()
    
    flash('Paquete creado exitosamente', 'success')
    return redirect(url_for('admin_paquetes', producto_id=producto_id))

@app.route('/admin/paquetes/<int:id>/datos', methods=['GET'])
@admin_required
def admin_paquetes_datos(id):
    db = get_db()
    paquete = db.execute('SELECT * FROM paquetes WHERE id = ?', (id,)).fetchone()
    db.close()
    
    if paquete:
        return {
            'id': paquete['id'],
            'nombre': paquete['nombre'],
            'descripcion': paquete['descripcion'],
            'precio': float(paquete['precio']),
            'imagen': paquete['imagen'],
            'producto_id': paquete['producto_id'],
            'zone_id_required': paquete['zone_id_required'] if 'zone_id_required' in paquete.keys() else 0
        }
    return {'error': 'Paquete no encontrado'}, 404

@app.route('/admin/paquetes/editar/<int:id>', methods=['POST'])
@admin_required
def admin_paquetes_editar(id):
    db = get_db()
    
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    precio = request.form.get('precio')
    imagen_ruta = request.form.get('imagen_ruta')
    zone_id_required = 1 if request.form.get('zone_id_required') else 0
    
    # Obtener el producto_id del paquete
    paquete = db.execute('SELECT producto_id FROM paquetes WHERE id = ?', (id,)).fetchone()
    producto_id = paquete['producto_id']
    
    db.execute('''
        UPDATE paquetes 
        SET nombre = ?, descripcion = ?, precio = ?, imagen = ?, zone_id_required = ?
        WHERE id = ?
    ''', (nombre, descripcion, precio, imagen_ruta, zone_id_required, id))
    
    db.commit()
    db.close()
    
    flash('Paquete actualizado exitosamente', 'success')
    return redirect(url_for('admin_paquetes', producto_id=producto_id))

@app.route('/admin/paquetes/eliminar/<int:id>/<int:producto_id>')
@admin_required
def admin_paquetes_eliminar(id, producto_id):
    db = get_db()
    db.execute('DELETE FROM paquetes WHERE id = ?', (id,))
    db.commit()
    db.close()
    
    flash('Paquete eliminado', 'success')
    return redirect(url_for('admin_paquetes', producto_id=producto_id))

@app.route('/admin/banners')
@admin_required
def admin_banners():
    db = get_db()
    banners = db.execute('SELECT * FROM banners ORDER BY orden').fetchall()
    config = db.execute('SELECT * FROM configuracion WHERE id = 1').fetchone()
    db.close()
    
    return render_template('admin/banners.html', banners=banners, config=config)

@app.route('/admin/banners/crear', methods=['POST'])
@admin_required
def admin_banners_crear():
    db = get_db()
    
    titulo = request.form.get('titulo')
    enlace = request.form.get('enlace', '')
    orden = request.form.get('orden', 0)
    
    # Obtener imagen de galería
    imagen_path = request.form.get('imagen_ruta')
    
    db.execute('''
        INSERT INTO banners (titulo, imagen, enlace, activo, orden)
        VALUES (?, ?, ?, 1, ?)
    ''', (titulo, imagen_path, enlace, orden))
    
    db.commit()
    db.close()
    
    flash('Banner creado exitosamente', 'success')
    return redirect(url_for('admin_banners'))

@app.route('/admin/banners/editar/<int:id>', methods=['POST'])
@admin_required
def admin_banners_editar(id):
    db = get_db()
    
    titulo = request.form.get('titulo')
    enlace = request.form.get('enlace', '')
    orden = request.form.get('orden', 0)
    activo = 1 if request.form.get('activo') else 0
    
    # Obtener imagen de galería
    imagen_path = request.form.get('imagen_ruta')
    
    # Si hay imagen nueva de galería
    if imagen_path:
        db.execute('''
            UPDATE banners 
            SET titulo = ?, imagen = ?, enlace = ?, activo = ?, orden = ?
            WHERE id = ?
        ''', (titulo, imagen_path, enlace, activo, orden, id))
    else:
        db.execute('''
            UPDATE banners 
            SET titulo = ?, enlace = ?, activo = ?, orden = ?
            WHERE id = ?
        ''', (titulo, enlace, activo, orden, id))
    
    db.commit()
    db.close()
    
    flash('Banner actualizado exitosamente', 'success')
    return redirect(url_for('admin_banners'))

@app.route('/admin/banners/eliminar/<int:id>')
@admin_required
def admin_banners_eliminar(id):
    db = get_db()
    db.execute('DELETE FROM banners WHERE id = ?', (id,))
    db.commit()
    db.close()
    
    flash('Banner eliminado', 'success')
    return redirect(url_for('admin_banners'))

# ============= BANNERS INTERMEDIOS =============

@app.route('/admin/banners-intermedios')
@admin_required
def admin_banners_intermedios():
    db = get_db()
    banners = db.execute('SELECT * FROM banners_intermedios ORDER BY orden').fetchall()
    config = db.execute('SELECT * FROM configuracion WHERE id = 1').fetchone()
    db.close()
    
    return render_template('admin/banners_intermedios.html', banners=banners, config=config)

@app.route('/admin/banners-intermedios/crear', methods=['POST'])
@admin_required
def admin_banners_intermedios_crear():
    db = get_db()
    
    titulo = request.form.get('titulo')
    enlace = request.form.get('enlace', '')
    orden = request.form.get('orden', 0)
    
    # Obtener imagen de galería
    imagen_path = request.form.get('imagen_ruta')
    
    db.execute('''
        INSERT INTO banners_intermedios (titulo, imagen, enlace, activo, orden)
        VALUES (?, ?, ?, 1, ?)
    ''', (titulo, imagen_path, enlace, orden))
    
    db.commit()
    db.close()
    
    flash('Banner intermedio creado exitosamente', 'success')
    return redirect(url_for('admin_banners_intermedios'))

@app.route('/admin/banners-intermedios/editar/<int:id>', methods=['POST'])
@admin_required
def admin_banners_intermedios_editar(id):
    db = get_db()
    
    titulo = request.form.get('titulo')
    enlace = request.form.get('enlace', '')
    orden = request.form.get('orden', 0)
    activo = 1 if request.form.get('activo') else 0
    
    # Obtener imagen de galería
    imagen_path = request.form.get('imagen_ruta')
    
    # Si hay imagen nueva de galería
    if imagen_path:
        db.execute('''
            UPDATE banners_intermedios 
            SET titulo = ?, imagen = ?, enlace = ?, activo = ?, orden = ?
            WHERE id = ?
        ''', (titulo, imagen_path, enlace, activo, orden, id))
    else:
        db.execute('''
            UPDATE banners_intermedios 
            SET titulo = ?, enlace = ?, activo = ?, orden = ?
            WHERE id = ?
        ''', (titulo, enlace, activo, orden, id))
    
    db.commit()
    db.close()
    
    flash('Banner intermedio actualizado exitosamente', 'success')
    return redirect(url_for('admin_banners_intermedios'))

@app.route('/admin/banners-intermedios/eliminar/<int:id>')
@admin_required
def admin_banners_intermedios_eliminar(id):
    db = get_db()
    db.execute('DELETE FROM banners_intermedios WHERE id = ?', (id,))
    db.commit()
    db.close()
    
    flash('Banner intermedio eliminado', 'success')
    return redirect(url_for('admin_banners_intermedios'))

@app.route('/admin/categorias')
@admin_required
def admin_categorias():
    db = get_db()
    categorias = db.execute('SELECT * FROM categorias ORDER BY orden').fetchall()
    config = db.execute('SELECT * FROM configuracion WHERE id = 1').fetchone()
    db.close()
    
    return render_template('admin/categorias.html', categorias=categorias, config=config)

@app.route('/admin/categorias/crear', methods=['POST'])
@admin_required
def admin_categorias_crear():
    db = get_db()
    
    nombre = request.form.get('nombre')
    orden = request.form.get('orden', 0)
    
    db.execute('''
        INSERT INTO categorias (nombre, activo, orden)
        VALUES (?, 1, ?)
    ''', (nombre, orden))
    
    db.commit()
    db.close()
    
    flash('Categoría creada exitosamente', 'success')
    return redirect(url_for('admin_categorias'))

@app.route('/admin/categorias/editar/<int:id>', methods=['POST'])
@admin_required
def admin_categorias_editar(id):
    db = get_db()
    
    nombre = request.form.get('nombre')
    orden = request.form.get('orden', 0)
    activo = 1 if request.form.get('activo') else 0
    
    db.execute('''
        UPDATE categorias 
        SET nombre = ?, activo = ?, orden = ?
        WHERE id = ?
    ''', (nombre, activo, orden, id))
    
    db.commit()
    db.close()
    
    flash('Categoría actualizada exitosamente', 'success')
    return redirect(url_for('admin_categorias'))

@app.route('/admin/categorias/eliminar/<int:id>')
@admin_required
def admin_categorias_eliminar(id):
    db = get_db()
    db.execute('DELETE FROM categorias WHERE id = ?', (id,))
    db.commit()
    db.close()
    
    flash('Categoría eliminada', 'success')
    return redirect(url_for('admin_categorias'))

@app.route('/admin/galeria')
@admin_required
def admin_galeria():
    db = get_db()
    imagenes = db.execute('SELECT * FROM galeria ORDER BY fecha_subida DESC').fetchall()
    config = db.execute('SELECT * FROM configuracion WHERE id = 1').fetchone()
    db.close()
    
    return render_template('admin/galeria.html', imagenes=imagenes, config=config)

@app.route('/admin/galeria/subir', methods=['POST'])
@admin_required
def admin_galeria_subir():
    db = get_db()
    
    if 'imagenes' not in request.files:
        flash('No se seleccionó ninguna imagen', 'danger')
        return redirect(url_for('admin_galeria'))
    
    files = request.files.getlist('imagenes')
    
    if not files or len(files) == 0:
        flash('No se seleccionó ninguna imagen', 'danger')
        return redirect(url_for('admin_galeria'))
    
    nombre_prefijo = request.form.get('nombre_prefijo', '')
    tipo = request.form.get('tipo', 'general')
    
    # Crear carpeta si no existe
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'galeria'), exist_ok=True)
    
    import time
    subidas_exitosas = 0
    archivos_rechazados = []
    
    for file in files:
        if file.filename == '':
            continue
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            # Agregar timestamp para evitar conflictos
            timestamp = str(int(time.time()))
            
            # Agregar prefijo si existe
            if nombre_prefijo:
                nombre_base = os.path.splitext(filename)[0]
                extension = os.path.splitext(filename)[1]
                filename = f"{timestamp}_{nombre_prefijo}_{nombre_base}{extension}"
            else:
                filename = f"{timestamp}_{filename}"
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'galeria', filename)
            
            try:
                file.save(filepath)
                # Guardar solo la ruta relativa (galeria/filename) para que funcione con /uploads/
                ruta = f'galeria/{filename}'
                logger.info(f"Imagen guardada en: {filepath}, ruta BD: {ruta}")
                
                # Nombre para la base de datos
                nombre_display = f"{nombre_prefijo} {file.filename}" if nombre_prefijo else file.filename
                
                db.execute('''
                    INSERT INTO galeria (nombre, ruta, tipo)
                    VALUES (?, ?, ?)
                ''', (nombre_display, ruta, tipo))
                
                subidas_exitosas += 1
                time.sleep(0.01)  # Pequeño delay para timestamps únicos
            except Exception as e:
                archivos_rechazados.append(file.filename)
        else:
            archivos_rechazados.append(file.filename)
    
    db.commit()
    db.close()
    
    # Mensajes de resultado
    if subidas_exitosas > 0:
        flash(f'{subidas_exitosas} imagen(es) subida(s) exitosamente', 'success')
    
    if archivos_rechazados:
        flash(f'Archivos no permitidos o con error: {", ".join(archivos_rechazados)}', 'warning')
    
    return redirect(url_for('admin_galeria'))

@app.route('/admin/galeria/eliminar/<int:id>')
@admin_required
def admin_galeria_eliminar(id):
    db = get_db()
    
    # Obtener la ruta de la imagen para eliminarla del sistema
    imagen = db.execute('SELECT ruta FROM galeria WHERE id = ?', (id,)).fetchone()
    if imagen:
        try:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], imagen['ruta'])
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Imagen eliminada: {filepath}")
        except Exception as e:
            logger.warning(f"No se pudo eliminar imagen física: {e}")
    
    db.execute('DELETE FROM galeria WHERE id = ?', (id,))
    db.commit()
    db.close()
    
    flash('Imagen eliminada', 'success')
    return redirect(url_for('admin_galeria'))

@app.route('/admin/galeria/listar')
@admin_required
def admin_galeria_listar():
    db = get_db()
    imagenes = db.execute('SELECT * FROM galeria ORDER BY fecha_subida DESC').fetchall()
    db.close()
    
    # Retornar como JSON para el modal de selección
    return jsonify([{
        'id': img['id'],
        'nombre': img['nombre'],
        'ruta': img['ruta'],
        'tipo': img['tipo']
    } for img in imagenes])

@app.route('/admin/ordenes')
@admin_required
def admin_ordenes():
    db = get_db()
    ordenes = db.execute('''
        SELECT o.*, p.nombre as producto_nombre, pk.nombre as paquete_nombre, pk.precio,
               u.username as usuario_nombre
        FROM ordenes o
        LEFT JOIN productos p ON o.producto_id = p.id
        LEFT JOIN paquetes pk ON o.paquete_id = pk.id
        LEFT JOIN usuarios u ON o.usuario_id = u.id
        ORDER BY o.fecha DESC
    ''').fetchall()
    config = db.execute('SELECT * FROM configuracion WHERE id = 1').fetchone()
    db.close()
    
    return render_template('admin/ordenes.html', ordenes=ordenes, config=config)

@app.route('/admin/ordenes/cambiar_estado/<int:id>/<estado>')
@admin_required
def admin_ordenes_cambiar_estado(id, estado):
    db = get_db()
    db.execute('UPDATE ordenes SET estado = ? WHERE id = ?', (estado, id))
    db.commit()
    db.close()
    
    flash(f'Estado de orden cambiado a {estado}', 'success')
    return redirect(url_for('admin_ordenes'))

# Servir archivos estáticos desde el disco persistente cuando UPLOAD_FOLDER es absoluto
@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    """Servir archivos desde el disco persistente o static/uploads"""
    from flask import send_from_directory
    upload_folder = app.config['UPLOAD_FOLDER']
    
    # Si UPLOAD_FOLDER es absoluto (como /data/uploads), usar esa ruta
    if os.path.isabs(upload_folder):
        return send_from_directory(upload_folder, filename)
    # Si es relativo, usar static/uploads
    else:
        return send_from_directory('static/uploads', filename)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)
