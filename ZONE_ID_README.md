# Sistema de Zone ID para Paquetes

## Descripción
Se ha implementado el sistema de Zone ID para juegos como Mobile Legends que requieren tanto Player ID como Zone ID para las recargas.

## Pasos para Activar el Sistema

### 1. Actualizar la Base de Datos
Antes de usar el sistema, debes ejecutar el script de actualización:

```bash
python update_db_zone_id.py
```

Este script agregará las siguientes columnas:
- `zone_id_required` en la tabla `paquetes` (para indicar si el paquete requiere Zone ID)
- `zone_id` en la tabla `ordenes` (para guardar el Zone ID del cliente)

### 2. Configurar Paquetes con Zone ID

En el panel de admin, ve a **Productos** → **Selecciona un producto** → **Ver Paquetes**.

Cuando crees o edites un paquete:

1. Rellena los campos normales (nombre, descripción, precio, imagen)
2. **Marca el checkbox "Requiere Zone ID"** si el paquete necesita Zone ID (como Mobile Legends)
3. Guarda el paquete

**Indicadores Visuales:**
- Los paquetes que requieren Zone ID mostrarán un badge azul con el ícono de llave y texto "Zone ID"
- Este badge aparece en la lista de paquetes del admin

### 3. Flujo de Compra con Zone ID

Cuando un cliente selecciona un paquete que requiere Zone ID:

1. El campo "Zone ID" aparecerá automáticamente junto al Player ID
2. El cliente deberá ingresar tanto su Player ID como su Zone ID
3. Ambos datos se guardarán en la orden

### 4. Visualización de Zone ID

El Zone ID se mostrará en:

**Panel de Admin:**
- Vista Desktop (tabla): Columnas separadas para Player ID y Zone ID
- Vista Móvil (tarjetas): En la información de la orden

**Perfil de Usuario:**
- En la tabla de "Mis Órdenes"

## Ejemplo de Uso

### Mobile Legends
Mobile Legends requiere tanto Player ID como Zone ID:
- Player ID: 123456789
- Zone ID: 1234

Para configurar un paquete de Mobile Legends:
1. Ve a Admin → Productos → Mobile Legends → Ver Paquetes
2. Al crear/editar un paquete, marca el checkbox "Requiere Zone ID"
3. El sistema automáticamente pedirá Zone ID cuando los clientes compren este paquete

## Campos Agregados

### Tabla: paquetes
- `zone_id_required` (INTEGER): 0 = No requiere, 1 = Requiere Zone ID

### Tabla: ordenes
- `zone_id` (TEXT): El Zone ID ingresado por el cliente (puede ser NULL si no aplica)

## Notas Importantes

1. El campo Zone ID solo es visible cuando se selecciona un paquete que lo requiere
2. Si el paquete requiere Zone ID, el campo es obligatorio (required)
3. Si se cambia a un paquete que no requiere Zone ID, el campo se oculta automáticamente
4. Los datos se validan en el cliente y en el servidor

## Características Implementadas

✅ Checkbox "Requiere Zone ID" en el formulario de crear/editar paquetes en el admin
✅ Indicador visual (badge azul) en la lista de paquetes para saber cuáles requieren Zone ID
✅ Campo Zone ID dinámico que aparece solo cuando es necesario
✅ Validación automática del Zone ID cuando es requerido
✅ Visualización del Zone ID en todas las vistas de órdenes (admin y usuario)
✅ Diseño responsive para móvil y desktop

## Próximas Mejoras Sugeridas

1. Agregar tooltip explicando qué es el Zone ID para usuarios nuevos
2. Agregar validación de formato para Zone ID (si aplica por juego)
3. Agregar campo de búsqueda de órdenes por Player ID o Zone ID
