# Configuración de Variables de Entorno en Render

## Variables Requeridas

Para que las sesiones funcionen correctamente en producción, debes configurar las siguientes variables de entorno en Render:

### 1. SECRET_KEY (REQUERIDA)
```
SECRET_KEY=tu_clave_secreta_muy_larga_y_aleatoria_aqui
```

**Cómo generar una SECRET_KEY segura:**
```python
import secrets
print(secrets.token_hex(32))
```

### 2. Credenciales de Administrador
```
ADMIN_EMAIL=tu-email@example.com
ADMIN_PASSWORD=TuPasswordSeguro123!
```

### 3. Variables Opcionales
```
PORT=5000
MAX_CONTENT_LENGTH=16777216
```

## Pasos para Configurar en Render

1. Ve a tu Web Service en Render Dashboard
2. Click en "Environment" en el menú lateral
3. Agrega cada variable de entorno:
   - Clave: `SECRET_KEY`
   - Valor: (pega tu clave generada)
4. Click en "Save Changes"
5. Render reiniciará automáticamente tu servicio

## Verificar que las Sesiones Funcionan

Después de configurar las variables:

1. Inicia sesión en tu sitio
2. Los botones "Admin" y "Perfil" deberían aparecer en el navbar
3. La sesión debería mantenerse activa durante 24 horas
4. No deberías tener que iniciar sesión constantemente

## Problemas Comunes

### Las sesiones no persisten
- Verifica que `SECRET_KEY` esté configurada en Render
- Asegúrate de que tu app use HTTPS (Render lo hace por defecto)
- Revisa los logs de Render para mensajes sobre SECRET_KEY

### Botones de Admin/Perfil no aparecen
- Verifica en los logs que el login fue exitoso
- Busca mensajes de "Admin login exitoso" o "Usuario login exitoso"
- Verifica que uses las credenciales correctas configuradas en `ADMIN_EMAIL` y `ADMIN_PASSWORD`

## Logs Útiles

En los logs de Render deberías ver:
```
INFO:__main__:SECRET_KEY cargada desde variable de entorno
INFO:__main__:Entorno de PRODUCCIÓN detectado (Render)
INFO:__main__:Admin login exitoso: admin@example.com
```
