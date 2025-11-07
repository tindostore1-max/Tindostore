# Tienda Online - Sistema de Venta de Juegos y Gift Cards

Sistema completo de tienda online desarrollado en Python con Flask para la venta de juegos móviles y gift cards.

## 🚀 Características

### Frontend (Usuario)
- **Header personalizable** con logo PNG en esquina superior izquierda
- **Carrusel principal** de 3 imágenes/banners
- **Escaparate de juegos móviles** con scroll lateral
- **Carrusel secundario** de 3 banners promocionales
- **Sección de categorías** con íconos
- **Carrusel de gift cards** con tarjetas deslizables
- **Sistema de login** con botón SVG en header
- **Perfil de usuario** con visualización de órdenes y datos editables

### Sistema de Compra (4 Pasos)
1. **ID de Jugador** (solo para juegos, no para gift cards)
2. **Selección de paquete** con precios
3. **Método de pago** (Pago Móvil o Binance)
4. **Datos personales** (nombre y correo)
5. **Checkout** con referencia de pago que genera orden

### Panel Administrativo
- **Dashboard** con estadísticas y órdenes recientes
- **Configuración** del sitio (nombre y logo)
- **Gestión de productos** (crear, editar, eliminar)
- **Gestión de paquetes** (precios por producto)
- **Gestión de banners** (carruseles)
- **Gestión de categorías**
- **Galería de imágenes** (repositorio centralizado de imágenes)
- **Gestión de órdenes** (cambiar estados: pendiente/completado/cancelado)

### Nueva Funcionalidad: Galería de Imágenes
- **Repositorio centralizado** de todas las imágenes
- **Subida múltiple:** Sube varias imágenes al mismo tiempo con un solo click
- **Selección múltiple:** Selecciona múltiples imágenes con checkboxes visuales
- **Selector visual** al crear productos, banners y configurar logo
- **Botón "Elegir de Galería"** - Única forma de agregar imágenes a productos/banners
- **Preview de archivos:** Ve qué archivos vas a subir antes de confirmar
- **Organización por tipo** (general, producto, banner, logo)
- **Prefijo opcional:** Agrega un prefijo a todas las imágenes subidas
- **Flujo simplificado:** Sube primero a galería, luego selecciona donde necesites

### Seguridad
- Sistema de autenticación con hash de contraseñas
- Decoradores para rutas protegidas (usuario y admin)
- Usuario admin predeterminado: `admin` / `123456`

## 📦 Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Inicializar la base de datos

```bash
python init_db.py
```

Esto creará:
- Base de datos SQLite `tienda.db`
- Tablas necesarias
- Usuario admin por defecto

### 3. Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

## 🔑 Credenciales de Admin

- **Usuario:** admin
- **Contraseña:** 123456

## 📁 Estructura del Proyecto

```
Tindo/
├── app.py                      # Aplicación principal Flask
├── init_db.py                  # Script de inicialización de BD
├── requirements.txt            # Dependencias Python
├── tienda.db                   # Base de datos SQLite (se crea automáticamente)
├── static/                     # Archivos estáticos
│   └── uploads/                # Imágenes subidas
│       ├── logos/              # Logos del sitio
│       ├── banners/            # Imágenes de banners
│       └── productos/          # Imágenes de productos
└── templates/                  # Templates HTML
    ├── base.html               # Template base
    ├── index.html              # Página principal
    ├── login.html              # Login
    ├── registro.html           # Registro
    ├── perfil.html             # Perfil de usuario
    ├── producto_detalle.html   # Detalle de producto
    ├── checkout.html           # Checkout
    └── admin/                  # Templates del admin
        ├── dashboard.html      # Dashboard admin
        ├── configuracion.html  # Configuración
        ├── productos.html      # Gestión de productos
        ├── paquetes.html       # Gestión de paquetes
        ├── banners.html        # Gestión de banners
        ├── categorias.html     # Gestión de categorías
        └── ordenes.html        # Gestión de órdenes
```

## 🗄️ Base de Datos

### Tablas Principales

- **usuarios**: Información de usuarios y admins
- **configuracion**: Configuración del sitio (nombre, logo)
- **categorias**: Categorías de productos
- **productos**: Juegos y gift cards
- **paquetes**: Paquetes y precios por producto
- **banners**: Imágenes para carruseles
- **ordenes**: Órdenes de compra

## 🎯 Flujo de Uso

### Para Usuarios
1. Navegar en la tienda
2. Seleccionar un producto (juego o gift card)
3. Completar los 4 pasos de compra
4. Realizar pago y obtener referencia
5. Ingresar referencia en checkout
6. Orden creada (visible en perfil y admin)

### Para Administradores
1. Login con credenciales admin
2. Acceder al panel administrativo
3. **Subir imágenes a la Galería** (subida múltiple disponible)
4. Configurar sitio (logo desde galería, nombre)
5. Crear categorías
6. Crear productos eligiendo imágenes de galería
7. Asignar paquetes y precios a productos
8. Crear banners eligiendo imágenes de galería
9. Gestionar órdenes (aprobar/rechazar)

## 🎨 Tecnologías Utilizadas

- **Backend:** Python 3 + Flask
- **Base de Datos:** SQLite3
- **Frontend:** Bootstrap 5, Bootstrap Icons
- **Autenticación:** Werkzeug (hash de contraseñas)
- **Templates:** Jinja2

## 📝 Notas Importantes

- Las imágenes se suben a `static/uploads/`
- Los tipos de producto son: `juego` o `giftcard`
- Los juegos requieren ID de jugador, las gift cards no
- Los métodos de pago son: `pagomovil` o `binance`
- Los estados de orden son: `pendiente`, `completado`, `cancelado`

## 🔧 Personalización

### Cambiar Logo
1. Login como admin
2. Ir a "Configuración"
3. Subir nuevo logo PNG

### Agregar Productos
1. **Primero:** Subir imágenes a la Galería
2. Ir a "Productos" → "Nuevo Producto"
3. Click en "Elegir de Galería" para seleccionar imagen
4. Completar datos y guardar
5. Ir a "Paquetes" del producto
6. Agregar paquetes con precios

### Agregar Banners
1. **Primero:** Subir imágenes a la Galería
2. Ir a "Banners" → "Crear Banner"
3. Click en "Elegir de Galería" para seleccionar imagen
4. Ordenar con el campo "Orden"

### Usar la Galería de Imágenes

**Subir múltiples imágenes:**
1. Ir a "Galería" → "Subir Imagen"
2. Agregar prefijo opcional (ej: "Producto")
3. Seleccionar tipo (general, producto, banner, logo)
4. Click en "Seleccionar Imágenes" y elegir **múltiples archivos** (Ctrl+Click o Shift+Click)
5. Ver preview de archivos seleccionados
6. Click "Subir" - ¡todas las imágenes se suben juntas!

**Elegir imágenes al crear productos/banners:**
1. Click en "Elegir de Galería"
2. Ver todas las imágenes disponibles
3. **Click en checkboxes** para seleccionar una o más imágenes
4. Las imágenes seleccionadas se resaltan con borde azul
5. Click "Seleccionar" para confirmar
6. La primera imagen se asigna automáticamente

## 📞 Soporte

Para modificaciones o consultas, revisar el código en `app.py` y los templates en la carpeta `templates/`.

---

**Desarrollado con Flask** 🐍
