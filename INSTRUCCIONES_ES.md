# Instrucciones de Configuración y Despliegue - Tindo

## 📋 Resumen de Cambios

Se ha preparado tu aplicación web para ser desplegada en Render con las siguientes mejoras de seguridad:

### ✅ Cambios Realizados

1. **Variables de Entorno (.env)**
   - Creado archivo `.env` con credenciales de administrador
   - Creado archivo `.env.example` como plantilla
   - Las credenciales están protegidas y no se subirán a Git

2. **Autenticación de Administrador**
   - El acceso de administrador ahora usa las credenciales del archivo `.env`
   - Email: `ADMIN_EMAIL`
   - Contraseña: `ADMIN_PASSWORD`

3. **Configuración de Base de Datos**
   - La ruta de la base de datos SQLite ahora es configurable
   - Variable: `DATABASE_URL`

4. **Archivos de Despliegue**
   - `render.yaml`: Configuración automática para Render
   - `build.sh`: Script de construcción
   - `Procfile`: Comando de inicio
   - `runtime.txt`: Versión de Python
   - `.gitignore`: Protección de archivos sensibles

5. **Dependencias Actualizadas**
   - `python-dotenv`: Para cargar variables de entorno
   - `gunicorn`: Servidor web para producción

## 🔐 Credenciales de Administrador

### Valores Actuales en .env

```
ADMIN_EMAIL=admin@tindo.com
ADMIN_PASSWORD=Admin123!Seguro
```

**⚠️ IMPORTANTE:** Cambia estos valores antes de desplegar en producción.

### Cómo Cambiar las Credenciales

1. Abre el archivo `.env`
2. Modifica los valores:
   ```
   ADMIN_EMAIL=tu_email@ejemplo.com
   ADMIN_PASSWORD=TuContraseñaSegura123!
   ```
3. Guarda el archivo

## 🚀 Cómo Desplegar en Render

### Paso 1: Preparar el Repositorio Git

```bash
# Inicializar Git (si no lo has hecho)
git init

# Añadir archivos
git add .

# Hacer commit
git commit -m "Preparar para deployment en Render"

# Conectar con tu repositorio (GitHub, GitLab, etc.)
git remote add origin https://github.com/tu-usuario/tu-repositorio.git

# Subir cambios
git push -u origin main
```

### Paso 2: Crear Servicio en Render

1. Ve a [Render.com](https://render.com) y crea una cuenta
2. Click en "New +" → "Blueprint" (si usas render.yaml)
   - O "Web Service" (para configuración manual)
3. Conecta tu repositorio de GitHub/GitLab
4. Render detectará automáticamente la configuración

### Paso 3: Configurar Variables de Entorno en Render

En el dashboard de Render, añade estas variables:

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `ADMIN_EMAIL` | tu_email@ejemplo.com | Email del administrador |
| `ADMIN_PASSWORD` | Tu contraseña segura | Contraseña del administrador |
| `SECRET_KEY` | (auto-generada) | Clave secreta de Flask |
| `DATABASE_URL` | tienda.db | Ruta de la base de datos |
| `FLASK_ENV` | production | Entorno de Flask |
| `DEBUG` | False | Modo debug (False en producción) |

**Nota:** Marca `ADMIN_PASSWORD` como "secret" en Render para mayor seguridad.

### Paso 4: Desplegar

1. Click en "Deploy" o "Create Web Service"
2. Espera a que termine el build (5-10 minutos)
3. Una vez completado, recibirás una URL: `https://tu-app.onrender.com`

## 🔑 Acceso de Administrador

### Para Entrar al Panel Admin

1. Ve a: `https://tu-app.onrender.com/login`
2. Usa las credenciales que configuraste:
   - **Usuario:** El valor de `ADMIN_EMAIL`
   - **Contraseña:** El valor de `ADMIN_PASSWORD`

## 📁 Estructura de Archivos

```
Tindo/
├── .env                    # ⚠️ Variables de entorno (NO SUBIR A GIT)
├── .env.example            # Plantilla de variables de entorno
├── .gitignore              # Archivos ignorados por Git
├── app.py                  # Aplicación Flask (actualizada)
├── requirements.txt        # Dependencias (actualizado)
├── runtime.txt             # Versión de Python
├── build.sh                # Script de construcción
├── render.yaml             # Configuración de Render
├── Procfile                # Comando de inicio
├── DEPLOYMENT_README.md    # Guía de despliegue (inglés)
├── INSTRUCCIONES_ES.md     # Este archivo
├── init_db.py              # Inicializar base de datos
├── static/                 # Archivos estáticos
├── templates/              # Plantillas HTML
└── tienda.db               # Base de datos (creada automáticamente)
```

## ⚙️ Probar Localmente

Antes de desplegar, puedes probar localmente:

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python app.py
```

Luego ve a: `http://localhost:5000`

## 🔒 Seguridad

### ✅ Buenas Prácticas Implementadas

- ✅ Variables de entorno para credenciales
- ✅ `.env` excluido de Git (.gitignore)
- ✅ Contraseña de admin configurable
- ✅ Secret key de Flask configurable
- ✅ Modo debug desactivado en producción

### ⚠️ Recomendaciones Adicionales

1. **Usa contraseñas fuertes:**
   - Mínimo 12 caracteres
   - Combinación de letras, números y símbolos
   - Ejemplo: `Tk9$mP2#xL5@qR8!`

2. **Cambia las credenciales en producción:**
   - No uses los valores del ejemplo
   - Usa el generador de contraseñas de tu navegador

3. **Para producción seria:**
   - Considera migrar de SQLite a PostgreSQL
   - Usa almacenamiento externo para archivos (AWS S3, Cloudinary)
   - Configura backups automáticos

## 📊 Base de Datos SQLite

### Ubicación

- **Local:** `tienda.db` (en la raíz del proyecto)
- **Render:** `/data/tienda.db`

### Inicialización

La base de datos se crea automáticamente en el primer despliegue usando `init_db.py`.

### ⚠️ Limitaciones de SQLite en Render

- No debes guardar la base de datos dentro de `/opt/render/project/src` porque Render no permite escribir en el directorio del código durante la ejecución
- Los datos se pueden perder si se reinicia el servicio
- No es ideal para tráfico alto
- Recomendado solo para desarrollo/pruebas

### Migrar a PostgreSQL (Recomendado para Producción)

1. Crea una base de datos PostgreSQL en Render
2. Actualiza `DATABASE_URL` con la URL de PostgreSQL
3. Instala `psycopg2-binary` en requirements.txt
4. Adapta las consultas SQL si es necesario

## 🐛 Solución de Problemas

### Error: "Usuario o contraseña incorrectos"

**Solución:** Verifica que:
- Las variables de entorno estén configuradas en Render
- Estés usando exactamente los valores de `ADMIN_EMAIL` y `ADMIN_PASSWORD`
- No haya espacios extra en las credenciales

### Error: "ModuleNotFoundError: No module named 'dotenv'"

**Solución:** 
```bash
pip install python-dotenv
```

### La base de datos no se crea

**Solución:**
```bash
python init_db.py
```

### Los archivos subidos desaparecen

**Causa:** El sistema de archivos de Render es efímero

**Solución:** Configura almacenamiento externo (S3, Cloudinary, etc.)

## 📞 Contacto y Soporte

Para problemas con:
- **Render:** [Documentación de Render](https://render.com/docs)
- **Flask:** [Documentación de Flask](https://flask.palletsprojects.com/)
- **Python:** [Documentación de Python](https://docs.python.org/)

## 📝 Notas Finales

1. **No incluyas `.env` en Git** - Ya está en `.gitignore`
2. **Cambia las credenciales por defecto** - Usa valores seguros
3. **Prueba localmente antes de desplegar** - Evita errores
4. **Configura las variables en Render** - Son obligatorias
5. **El plan gratuito de Render hiberna** - Primera carga puede ser lenta

---

**¡Tu aplicación está lista para ser desplegada en Render!** 🎉

Para cualquier duda, consulta `DEPLOYMENT_README.md` (en inglés) para más detalles técnicos.
