# Phase 1: MCP Tools Contract

**Feature**: `001-reserva-espacio-compartido`  
**Protocol**: Model Context Protocol (MCP)  
**Transport**: `streamable-http` (montado en sub-path `/mcp`) y `stdio` (para desarrollo local)  
**Date**: 2026-09-20  

---

## 1. Reglas Generales de MCP

1. **Resolución de Identidad (Artículo VI.4)**:
   - En transporte `streamable-http`, la tool resuelve la identidad del usuario a partir del token JWT transmitido en la cabecera `Authorization: Bearer <token>` del cliente.
   - En transporte `stdio`, opera con el usuario demo configurado en `.env` como simplificación consciente de desarrollo local.
2. **Reutilización de Capas (Artículo VI.1)**:
   - Las tools nunca interactúan con SQLAlchemy ni con la base de datos de manera directa; delegan el 100% de la lógica a `app.services.reservas`.
3. **Manejo Estructurado de Errores (Artículo VI.3)**:
   - Los errores de regla de negocio devuelven diccionarios estructurados con el campo `error`, evitando excepciones no controladas que rompan la sesión MCP.

---

## 2. Herramientas Disponibles

### Tool: `crear_reserva`
Registra una nueva reserva activa para el espacio compartido tras validar disponibilidad, solapamientos y fechas.

- **Descripción expuesta al modelo**:
  > "Registra una reserva para el espacio compartido indicando fecha (YYYY-MM-DD), hora de inicio (HH:MM) y hora de fin (HH:MM). Valida que la fecha sea igual o posterior a hoy y que no existan solapamientos con otras reservas activas."
- **Parámetros**:
  ```json
  {
    "type": "object",
    "properties": {
      "fecha": { "type": "string", "description": "Fecha de la reserva en formato YYYY-MM-DD" },
      "hora_inicio": { "type": "string", "description": "Hora de inicio en formato HH:MM (24h)" },
      "hora_fin": { "type": "string", "description": "Hora de fin en formato HH:MM (24h)" }
    },
    "required": ["fecha", "hora_inicio", "hora_fin"]
  }
  ```
- **Retorno exitoso**:
  ```json
  {
    "id": 42,
    "usuario_id": 1,
    "fecha": "2026-10-15",
    "hora_inicio": "10:00",
    "hora_fin": "12:00",
    "estado": "ACTIVA"
  }
  ```
- **Retornos de error de negocio**:
  - `{"error": "El horario solicitado se solapa con una reserva existente"}`
  - `{"error": "La hora de fin debe ser posterior a la hora de inicio"}`
  - `{"error": "No se pueden crear reservas en fechas pasadas"}`

---

### Tool: `listar_reservas`
Obtiene la lista de reservas (activas o canceladas) pertenecientes al usuario autenticado.

- **Descripción expuesta al modelo**:
  > "Lista las reservas del usuario autenticado en la sesión MCP, con soporte de paginación (skip y limit)."
- **Parámetros**:
  ```json
  {
    "type": "object",
    "properties": {
      "skip": { "type": "integer", "description": "Número de registros a omitir (default 0)", "default": 0 },
      "limit": { "type": "integer", "description": "Cantidad máxima de registros a devolver (default 20)", "default": 20 }
    }
  }
  ```
- **Retorno exitoso**:
  ```json
  [
    {
      "id": 42,
      "usuario_id": 1,
      "fecha": "2026-10-15",
      "hora_inicio": "10:00",
      "hora_fin": "12:00",
      "estado": "ACTIVA"
    }
  ]
  ```

---

### Tool: `cancelar_reserva`
Cancela una reserva activa perteneciente al usuario mediante soft delete, exigiendo confirmación previa del servidor (Artículo VI.5).

- **Descripción expuesta al modelo**:
  > "Cancela una reserva activa del usuario autenticado liberando el horario. Requiere confirmacion=True para proceder con la cancelación destructiva."
- **Parámetros**:
  ```json
  {
    "type": "object",
    "properties": {
      "reserva_id": { "type": "integer", "description": "ID de la reserva a cancelar" },
      "confirmacion": { "type": "boolean", "description": "Confirmación explícita de la cancelación", "default": false }
    },
    "required": ["reserva_id"]
  }
  ```
- **Flujo de Confirmación en Dos Pasos**:
  - **Paso 1 (Sin confirmación previa, `confirmacion=False`)**:
    ```json
    {
      "status": "confirmation_required",
      "message": "La cancelación liberará el horario de la reserva #42 para otros usuarios. Confirme la operación ejecutando cancelar_reserva(reserva_id=42, confirmacion=True)."
    }
    ```
  - **Paso 2 (Con confirmación explícita, `confirmacion=True`)**:
    ```json
    {
      "status": "success",
      "message": "Reserva #42 cancelada exitosamente"
    }
    ```
- **Retornos de error de negocio**:
  - `{"error": "No tiene autorización para cancelar esta reserva"}`
  - `{"error": "Reserva no encontrada"}`
