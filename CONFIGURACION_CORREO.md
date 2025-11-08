# Configuración de Notificaciones por Correo Electrónico

## Instrucciones de Configuración

### 1. Crear/Editar archivo `.env`

Crea un archivo llamado `.env` en la raíz del proyecto (si no existe) y agrega las siguientes líneas:

```env
# Configuración de correo para notificaciones
EMAIL_USER=tindostore1@gmail.com
EMAIL_PASSWORD=wmmxpdtjwifvcuhx
```

### 2. Características del Sistema de Notificaciones

El sistema enviará correos automáticamente en los siguientes casos:

#### A) Cuando un cliente crea una orden:
- **Al Administrador**: Notificación de nueva orden con todos los detalles
- **Al Cliente**: Confirmación de que la orden fue recibida y está siendo procesada

#### B) Cuando se completa una orden:
- **Al Cliente**: Notificación de que su recarga ha sido completada exitosamente

### 3. Tipos de Correos

#### 📧 Notificación al Administrador (Nueva Orden)
- Asunto: `🔔 Nueva Orden #[ID] - [Producto]`
- Contiene todos los detalles de la orden
- Diseño profesional con gradiente morado

#### ✅ Confirmación al Cliente (Orden Creada)
- Asunto: `✅ Orden #[ID] Recibida - Tindo Store`
- Confirma que la orden está siendo procesada
- Diseño profesional con gradiente azul

#### 🎉 Notificación al Cliente (Orden Completada)
- Asunto: `🎉 Recarga Completada - Orden #[ID] - Tindo Store`
- Informa que la recarga fue exitosa
- Diseño profesional con gradiente verde

### 4. Seguridad

- Las credenciales están en el archivo `.env` que está excluido del control de versiones (`.gitignore`)
- Se usa la contraseña de aplicación de Gmail (no la contraseña de la cuenta)
- Todos los correos son enviados desde `tindostore1@gmail.com`

### 5. Logs

El sistema registrará en los logs:
- ✓ Correos enviados exitosamente
- ✗ Errores al enviar correos (sin detener el funcionamiento de la aplicación)

### 6. Verificación

Para verificar que el sistema está configurado correctamente:

1. Reinicia el servidor Flask
2. Crea una orden de prueba
3. Revisa que lleguen los correos tanto al admin como al cliente
4. Cambia el estado de la orden a "completada" desde el panel admin
5. Verifica que llegue el correo de confirmación al cliente

### 7. Solución de Problemas

Si los correos no se envían:

1. Verifica que las variables `EMAIL_USER` y `EMAIL_PASSWORD` estén en el archivo `.env`
2. Asegúrate de que el archivo `.env` esté en la raíz del proyecto
3. Verifica que la contraseña de aplicación sea correcta
4. Revisa los logs del servidor para mensajes de error
5. Confirma que Gmail permita el acceso desde aplicaciones menos seguras o uses una contraseña de aplicación

### 8. Formato de las Fechas en Español

El sistema muestra las fechas en español (ejemplo: "8 de noviembre de 2025")

---

**Nota**: Los correos están diseñados con HTML responsive y se verán correctamente en todos los clientes de correo modernos.
