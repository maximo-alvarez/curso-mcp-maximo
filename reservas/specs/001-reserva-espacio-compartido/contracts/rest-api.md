# Phase 1: REST API Contract

**Feature**: `001-reserva-espacio-compartido`  
**Base URL**: `/`  
**Date**: 2026-09-20  

---

## 1. Endpoints de Usuarios y Autenticación

### `POST /usuarios/`
Crea una nueva cuenta de usuario en el sistema.

- **Autenticación**: Ninguna (pública).
- **Request Body** (`application/json`):
  ```json
  {
    "email": "usuario@ejemplo.com",
    "password": "PasswordSegura123!"
  }
  ```
- **Respuestas**:
  - `201 Created`:
    ```json
    {
      "id": 1,
      "email": "usuario@ejemplo.com"
    }
    ```
  - `400 Bad Request`:
    ```json
    {
      "detail": "El email ya está registrado"
    }
    ```
  - `422 Unprocessable Entity`: Formato de email inválido o campos faltantes.

---

### `POST /usuarios/token`
Autentica credenciales y emite un token JWT firmado.

- **Autenticación**: Ninguna.
- **Request Body** (`application/x-www-form-urlencoded` - RFC 6749 OAuth2 Password):
  - `username`: `usuario@ejemplo.com`
  - `password`: `PasswordSegura123!`
- **Respuestas**:
  - `200 OK`:
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
      "token_type": "bearer"
    }
    ```
  - `401 Unauthorized`:
    ```json
    {
      "detail": "Credenciales inválidas"
    }
    ```

---

## 2. Endpoints de Reservas

### `POST /reservas/`
Crea una reserva en estado `ACTIVA` para el espacio compartido.

- **Autenticación**: Requerida (`Authorization: Bearer <token>`).
- **Request Body** (`application/json`):
  ```json
  {
    "fecha": "2026-10-15",
    "hora_inicio": "10:00",
    "hora_fin": "12:00"
  }
  ```
- **Respuestas**:
  - `201 Created`:
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
  - `400 Bad Request` (Horario solapado):
    ```json
    {
      "detail": "El horario solicitado se solapa con una reserva existente"
    }
    ```
  - `400 Bad Request` (Horas inválidas):
    ```json
    {
      "detail": "La hora de fin debe ser posterior a la hora de inicio"
    }
    ```
  - `400 Bad Request` (Fecha en el pasado):
    ```json
    {
      "detail": "No se pueden crear reservas en fechas pasadas"
    }
    ```
  - `401 Unauthorized`: Token faltante, expirado o manipulado.
  - `422 Unprocessable Entity`: Formato de fecha o datos inválidos.

---

### `GET /reservas/`
Lista las reservas pertenecientes al usuario autenticado (con soporte de paginación).

- **Autenticación**: Requerida (`Authorization: Bearer <token>`).
- **Query Parameters**:
  - `skip` (opcional, entero $\ge 0$, default `0`): Número de registros a omitir.
  - `limit` (opcional, entero $1 \dots 100$, default `20`): Cantidad máxima de registros.
- **Respuestas**:
  - `200 OK`:
    ```json
    [
      {
        "id": 42,
        "usuario_id": 1,
        "fecha": "2026-10-15",
        "hora_inicio": "10:00",
        "hora_fin": "12:00",
        "estado": "ACTIVA"
      },
      {
        "id": 12,
        "usuario_id": 1,
        "fecha": "2026-09-10",
        "hora_inicio": "14:00",
        "hora_fin": "15:00",
        "estado": "CANCELADA"
      }
    ]
    ```
  - `401 Unauthorized`: Token no provisto o inválido.
  - `422 Unprocessable Entity`: Valores negativos de `skip` o `limit`.

---

### `DELETE /reservas/{id}`
Cancela una reserva propia mediante eliminación lógica (`soft delete`).

- **Autenticación**: Requerida (`Authorization: Bearer <token>`).
- **Path Parameter**:
  - `id` (entero): Identificador de la reserva.
- **Respuestas**:
  - `204 No Content`: Reserva cancelada exitosamente (pasa a estado `CANCELADA`).
  - `401 Unauthorized`: Token no provisto o inválido.
  - `403 Forbidden` (No es propietario):
    ```json
    {
      "detail": "No tiene autorización para cancelar esta reserva"
    }
    ```
  - `404 Not Found`:
    ```json
    {
      "detail": "Reserva no encontrada"
    }
    ```
