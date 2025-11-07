# Guía de Despliegue en Render

Esta guía te ayudará a desplegar la aplicación Tindo en Render.

## Requisitos Previos

1. Una cuenta en [Render](https://render.com)
2. Tu código en un repositorio Git (GitHub, GitLab, etc.)

## Variables de Entorno Requeridas

Antes de desplegar, configura estas variables de entorno en Render:

### Variables Obligatorias

- `ADMIN_EMAIL`: Correo electrónico del administrador (ej: admin@tindo.com)
- `ADMIN_PASSWORD`: Contraseña del administrador (usa una contraseña segura)
- `SECRET_KEY`: Clave secreta de Flask (Render puede generarla automáticamente)

### Variables Opcionales (con valores predeterminados)

- `DATABASE_URL`: Ruta a la base de datos SQLite (default: /opt/render/project/src/tienda.db)
- `FLASK_ENV`: Entorno de Flask (default: production)
- `DEBUG`: Modo debug (default: False)
- `MAX_CONTENT_LENGTH`: Tamaño máximo de archivos en bytes (default: 16777216)
- `UPLOAD_FOLDER`: Carpeta de uploads (default: static/uploads)

## Pasos para Desplegar en Render

### Opción 1: Usando render.yaml (Recomendado)

1. **Sube tu código a GitHub/GitLab**
   ```bash
   git init
   git add .
   git commit -m "Preparar para deployment en Render"
   git remote add origin <tu-repositorio>
   git push -u origin main
   ```

2. **Conecta tu repositorio en Render**
   - Ve a tu [dashboard de Render](https://dashboard.render.com)
   - Click en "New +" → "Blueprint"
   - Conecta tu repositorio
   - Render detectará automáticamente el archivo `render.yaml`

3. **Configura las variables de entorno**
   - En el dashboard, ve a tu servicio web
   - Ve a "Environment"
   - Configura `ADMIN_EMAIL` y `ADMIN_PASSWORD`
   - Render generará `SECRET_KEY` automáticamente

4. **Despliega**
   - Click en "Deploy"
   - Espera a que el build se complete

### Opción 2: Despliegue Manual

1. **Crea un nuevo Web Service en Render**
   - Ve a tu dashboard de Render
   - Click en "New +" → "Web Service"
   - Conecta tu repositorio

2. **Configura el servicio**
   - **Name**: tindo-tienda (o el nombre que prefieras)
   - **Environment**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free (o el plan que necesites)

3. **Configura las variables de entorno**
   - Añade las variables mencionadas arriba
   - Asegúrate de marcar `ADMIN_PASSWORD` como "secret"

4. **Despliega**
   - Click en "Create Web Service"
   - Espera a que el build se complete

## Acceso de Administrador

Una vez desplegada la aplicación:

1. Ve a `https://tu-app.onrender.com/login`
2. Usa las credenciales configuradas en las variables de entorno:
   - **Usuario**: El valor de `ADMIN_EMAIL`
   - **Contraseña**: El valor de `ADMIN_PASSWORD`

## Estructura de Archivos para Deployment

```
Tindo/
├── app.py                  # Aplicación principal
├── requirements.txt        # Dependencias Python
├── runtime.txt            # Versión de Python
├── build.sh               # Script de construcción
├── render.yaml            # Configuración de Render
├── .env.example           # Ejemplo de variables de entorno
├── .gitignore             # Archivos ignorados por Git
├── init_db.py             # Inicialización de base de datos
├── static/                # Archivos estáticos
├── templates/             # Plantillas HTML
└── tienda.db              # Base de datos SQLite (no incluir en Git)
```

## Notas Importantes

### Seguridad

- **NUNCA** incluyas el archivo `.env` en tu repositorio Git
- Usa contraseñas seguras para `ADMIN_PASSWORD`
- Render encriptará automáticamente las variables de entorno marcadas como "secret"

### Base de Datos

- La base de datos SQLite se creará automáticamente en el primer despliegue
- Los datos se perderán si borras el servicio o cambias de plan
- Para producción real, considera usar PostgreSQL en lugar de SQLite

### Archivos Subidos

- Los archivos subidos se almacenan en el sistema de archivos efímero de Render
- Se perderán con cada redespliegue
- Para producción, considera usar un servicio de almacenamiento como:
  - AWS S3
  - Cloudinary
  - DigitalOcean Spaces

### Performance

- El plan gratuito de Render hiberna después de 15 minutos de inactividad
- La primera solicitud después de hibernar puede tardar 30-60 segundos
- Para mejor rendimiento, considera un plan de pago

## Solución de Problemas

### Error: "ModuleNotFoundError"
- Asegúrate de que todas las dependencias están en `requirements.txt`
- Verifica que el script `build.sh` se ejecute correctamente

### Error: "Database is locked"
- SQLite no es ideal para múltiples conexiones concurrentes
- Considera migrar a PostgreSQL para producción

### Error de Login
- Verifica que las variables de entorno estén configuradas correctamente
- Asegúrate de usar los valores exactos de `ADMIN_EMAIL` y `ADMIN_PASSWORD`

### Archivos no se suben
- Verifica que los directorios de upload existen (se crean en `build.sh`)
- Recuerda que los archivos se perderán en cada redespliegue

## Próximos Pasos

1. **Migrar a PostgreSQL**: Para una base de datos persistente
2. **Configurar almacenamiento externo**: Para archivos subidos
3. **Configurar dominio personalizado**: En la configuración de Render
4. **Configurar SSL**: Render lo proporciona automáticamente
5. **Monitoreo**: Usar las herramientas de Render para monitorear logs y métricas

## Soporte

Para más información, consulta:
- [Documentación de Render](https://render.com/docs)
- [Documentación de Flask](https://flask.palletsprojects.com/)
- [Guía de Deployment de Flask](https://flask.palletsprojects.com/en/3.0.x/deploying/)
