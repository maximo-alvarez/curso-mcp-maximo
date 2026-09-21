# Feature Specification: Sistema de Reservas de un Espacio Compartido

**Feature Branch**: `001-reserva-espacio-compartido`

**Created**: 2026-09-20

**Status**: Draft

**Input**: User description: "Sistema de reservas de un espacio compartido con gestión de usuarios, reservas por fecha y franja horaria sin solapamientos, cancelación exclusiva por propietario, API REST y herramientas MCP equivalentes."

## Clarifications

### Session 2026-09-20
- Q: ¿Cómo debe persistirse la cancelación de una reserva en la base de datos? → A: Eliminación lógica (`soft delete`): la reserva cambia su estado a `CANCELADA`, preservando el registro para auditoría e historial; el horario queda liberado ya que la verificación de solapamiento ignora reservas canceladas.
- Q: ¿Debe el sistema validar y rechazar reservas con fechas en el pasado? → A: Sí, rechazar fechas anteriores a hoy con HTTP 400 (excepción de negocio `FechaPasadaError`). La fecha de la reserva debe ser mayor o igual a la fecha actual del sistema.
- Q: ¿Existe alguna restricción de tiempo o plazo límite para que un usuario pueda cancelar su reserva activa? → A: No, cancelación sin restricción de antelación previa: el usuario propietario puede cancelar su reserva en cualquier momento mientras permanezca en estado `ACTIVA`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Crear Reserva de Espacio sin Solapamiento (Priority: P1)

Como usuario autenticado del sistema, quiero reservar el espacio compartido indicando fecha, hora de inicio y hora de fin, para asegurar mi tiempo de uso sin interferencias ni conflictos con otros usuarios.

**Why this priority**: Es la funcionalidad central del sistema. Sin la capacidad de reservar válidamente un espacio sin solapamientos, el producto no cumple su propósito esencial.

**Independent Test**: Puede probarse creando una reserva válida mediante el endpoint `POST /reservas/` o la tool MCP `crear_reserva`, verificando que la reserva se persiste con estado `ACTIVA` y que un segundo intento de reserva en el mismo intervalo de fecha/hora es rechazado con error 400.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado y un horario disponible en una fecha determinada (fecha >= hoy), **When** solicita crear una reserva con `hora_fin > hora_inicio`, **Then** el sistema crea la reserva con estado `ACTIVA` y código 201 (o payload MCP exitoso) asociada al usuario autenticado.
2. **Given** una reserva activa existente en una fecha entre las 10:00 y las 12:00, **When** cualquier usuario intenta reservar esa misma fecha de 11:00 a 13:00, **Then** el sistema rechaza la solicitud con error de negocio 400 ("horario solapado").
3. **Given** una reserva previamente cancelada (`CANCELADA`) entre las 10:00 y las 12:00, **When** un usuario intenta reservar en ese mismo rango horario, **Then** el sistema crea la nueva reserva exitosamente (201) al ignorar reservas canceladas.
4. **Given** un usuario autenticado, **When** intenta crear una reserva con fecha anterior a la fecha actual del sistema, **Then** el sistema rechaza la solicitud con error 400 (`FechaPasadaError`).
5. **Given** un usuario autenticado, **When** intenta crear una reserva donde `hora_fin <= hora_inicio`, **Then** el sistema rechaza la solicitud con error 400 ("horas inválidas").

---

### User Story 2 - Registro y Autenticación de Usuarios (Priority: P1)

Como nuevo usuario o usuario recurrente, quiero registrarme con mi correo y autenticarme con credenciales seguras para obtener un token de acceso JWT con el cual operar en la API y el servidor MCP.

**Why this priority**: Es el prerequisito para la identificación, aislamiento multi-usuario y cumplimiento de las reglas de seguridad de la constitución.

**Independent Test**: Enviar `POST /usuarios/` con email y contraseña, verificar creación con 201 y contraseña hasheada, y autenticarse con `POST /usuarios/token` recibiendo un token JWT válido con 200.

**Acceptance Scenarios**:

1. **Given** un email no registrado previamente, **When** se envía `POST /usuarios/`, **Then** el usuario se crea con estado 201 sin retornar la contraseña en texto plano ni hasheada.
2. **Given** un usuario registrado, **When** envía sus credenciales correctas a `POST /usuarios/token`, **Then** recibe un token JWT firmado.
3. **Given** un email ya registrado, **When** se intenta registrar nuevamente, **Then** el sistema responde con 400 (email duplicado).

---

### User Story 3 - Listar Reservas Propias (Priority: P2)

Como usuario autenticado, quiero ver la lista de mis reservas (activas o canceladas) con soporte de paginación (`skip`, `limit`), para consultar mis horarios asignados sin acceder a reservas ajenas.

**Why this priority**: Permite al usuario auditar y consultar sus reservas de forma clara y respetando la privacidad multi-inquilino.

**Independent Test**: Crear reservas con dos usuarios distintos y verificar que `GET /reservas/` (o la tool MCP `listar_reservas`) solo retorna las reservas del usuario autenticado en la sesión.

**Acceptance Scenarios**:

1. **Given** un usuario con reservas registradas, **When** consulta `GET /reservas/?skip=0&limit=10`, **Then** recibe una lista con sus reservas y código 200, mostrando el `estado` de cada una (`ACTIVA` o `CANCELADA`).
2. **Given** un usuario B autenticado, **When** lista reservas, **Then** nunca recibe reservas creadas por el usuario A.
3. **Given** una consulta de reservas sin token de autenticación válido, **When** se invoca el endpoint, **Then** responde 401 Unauthorized.

---

### User Story 4 - Cancelar Reserva Propia mediante Soft Delete (Priority: P2)

Como usuario que reservó el espacio, quiero poder cancelar mi reserva en cualquier momento cuando ya no la necesite, cambiando su estado a `CANCELADA` para liberar el espacio a otros usuarios y asegurando que nadie más pueda cancelarla en mi lugar.

**Why this priority**: Garantiza la liberación de recursos, conservación del historial para auditoría y la protección de autorización sobre operaciones destructivas.

**Independent Test**: Invocar `DELETE /reservas/{id}` o la tool MCP `cancelar_reserva` con el dueño de la reserva verificando estado 204 y transición a `CANCELADA`, e intentar lo mismo con otro usuario verificando error 403.

**Acceptance Scenarios**:

1. **Given** una reserva activa existente perteneciente al usuario autenticado, **When** el usuario ejecuta `DELETE /reservas/{id}` (en cualquier momento mientras permanezca activa), **Then** la reserva cambia su estado a `CANCELADA`, responde con código 204 y el horario queda liberado para nuevas reservas.
2. **Given** una reserva existente perteneciente al usuario A, **When** el usuario B autenticado intenta cancelarla vía `DELETE /reservas/{id}`, **Then** el sistema responde 403 Forbidden ("no es dueño").
3. **Given** un identificador de reserva que no existe, **When** se intenta cancelar, **Then** el sistema responde 404 Not Found.
4. **Given** la tool MCP `cancelar_reserva`, **When** es invocada, **Then** exige confirmación explícita del servidor antes de ejecutar la mutación.

---

### Edge Cases

- **Solapamiento exacto y parcial**:
  - Intento de reserva que coincide exactamente en inicio y fin con una existente activa → rechazado (400).
  - Intento de reserva que comienza antes y termina durante una activa existente → rechazado (400).
  - Intento de reserva que comienza durante y termina después de una activa existente → rechazado (400).
  - Intento de reserva que engloba completamente a una activa existente → rechazado (400).
  - Intento de reserva contigua (inicia exactamente cuando otra termina) → permitido (201), no se considera solapamiento.
  - Intento de reserva sobre horario de una reserva previa en estado `CANCELADA` → permitido (201).
- **Validación temporal de límites y fechas**:
  - `fecha < fecha_actual` → rechazado (400 `FechaPasadaError`).
  - `hora_fin == hora_inicio` → rechazado (400 horas inválidas).
  - `hora_fin < hora_inicio` → rechazado (400 horas inválidas).
- **Parámetros de paginación inválidos**:
  - Valores negativos para `skip` o `limit` en `GET /reservas/` → rechazados con error de validación (422).
- **Aislamiento de sesiones MCP**:
  - En transporte `stdio`, identidad documentada en entorno de pruebas; en transporte HTTP, resolución obligatoria desde token JWT bearer.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE permitir el registro de usuarios con email único y contraseña protegida mediante hash `bcrypt`.
- **FR-002**: El sistema DEBE autenticar usuarios mediante OAuth2 password flow emitiendo tokens JWT con expiración definida.
- **FR-003**: El sistema DEBE permitir a los usuarios autenticados crear reservas para un espacio compartido especificando fecha (formato `YYYY-MM-DD`), hora de inicio y hora de fin (formato `HH:MM`). Toda reserva creada se inicia con estado `ACTIVA`.
- **FR-004**: El sistema DEBE validar que `hora_fin` sea estrictamente posterior a `hora_inicio`.
- **FR-005**: El sistema DEBE impedir la creación de cualquier reserva que se solape en fecha y rango horario con cualquier reserva en estado `ACTIVA` existente en la base de datos, con independencia del usuario dueño. Las reservas en estado `CANCELADA` DEBEN ser ignoradas al validar solapamientos.
- **FR-006**: El sistema DEBE filtrar automáticamente las reservas por `usuario_id` en las consultas de listado (`GET /reservas/` y tool MCP `listar_reservas`), garantizando que un usuario solo reciba sus propias reservas.
- **FR-007**: El sistema DEBE permitir a un usuario cancelar sus reservas propias en cualquier momento mientras permanezcan en estado `ACTIVA` (sin restricciones de antelación mínima previa), mediante `DELETE /reservas/{id}` y la tool MCP `cancelar_reserva`, realizando una eliminación lógica (`soft delete`) que actualice su `estado` a `CANCELADA`.
- **FR-008**: El sistema DEBE responder con `403 Forbidden` si un usuario intenta cancelar una reserva existente cuyo `usuario_id` no coincide con el del token.
- **FR-009**: El sistema DEBE responder con `404 Not Found` si la reserva solicitada para cancelación no existe en la base de datos.
- **FR-010**: Las tools MCP (`crear_reserva`, `listar_reservas`, `cancelar_reserva`) DEBEN invocar las mismas funciones de la capa `services/` que los routers HTTP correspondientes.
- **FR-011**: La tool MCP `cancelar_reserva` DEBE requerir confirmación explícita previa para mitigar ejecuciones destructivas accidentales.
- **FR-012**: Las respuestas de error no controladas DEBEN emitir código 500 con formato `{"detail": "Error interno del servidor"}` sin filtrar trazas de excepción.
- **FR-013**: El sistema DEBE validar que la fecha indicada para una reserva sea igual o posterior a la fecha actual del sistema (`fecha >= hoy`). Toda reserva con fecha en el pasado DEBE ser rechazada con HTTP 400 (`FechaPasadaError`).

### Key Entities

- **Usuario**: Representa al actor del sistema. Posee `id` (entero único), `email` (string único no nulo) y `hashed_password` (string seguro). No expone su contraseña en ninguna respuesta.
- **Reserva**: Representa la asignación del espacio compartido en un intervalo de tiempo. Posee `id` (entero único), `usuario_id` (clave foránea a Usuario), `fecha` (fecha de la reserva formato YYYY-MM-DD), `hora_inicio` (hora de entrada formato HH:MM), `hora_fin` (hora de salida formato HH:MM) y `estado` (string o Enum: `ACTIVA` o `CANCELADA`, por defecto `ACTIVA`).

---

## Contrato de la API (REST)

| Método | Ruta | Auth | Request Body / Query | Éxito | Errores esperados |
|--------|------|------|----------------------|-------|-------------------|
| POST | `/usuarios/` | No | `{ "email": "str", "password": "str" }` | `201 Created` (`UsuarioOut`) | `400` (email duplicado), `422` (validación de schema) |
| POST | `/usuarios/token` | No | Form data: `username`, `password` | `200 OK` (`Token`) | `401` (credenciales inválidas) |
| POST | `/reservas/` | Sí (JWT) | `{ "fecha": "YYYY-MM-DD", "hora_inicio": "HH:MM", "hora_fin": "HH:MM" }` | `201 Created` (`ReservaOut`) | `400` (horario solapado, horas inválidas, fecha en el pasado), `401` (no autenticado), `422` (schema) |
| GET | `/reservas/` | Sí (JWT) | Query params: `skip` (default 0), `limit` (default 20) | `200 OK` (`list[ReservaOut]`) | `401` (no autenticado), `422` (query params inválidos) |
| DELETE | `/reservas/{id}` | Sí (JWT) | Path param: `id` (int) | `204 No Content` | `401` (no autenticado), `403` (no es dueño), `404` (no encontrada) |

*Nota sobre schemas:* `ReservaOut` expone: `id`, `usuario_id`, `fecha`, `hora_inicio`, `hora_fin` y `estado`.

---

## Contrato equivalente por MCP

- **Tool `crear_reserva(fecha: str, hora_inicio: str, hora_fin: str)`**:
  - Aplica las mismas reglas de validación que `POST /reservas/` (incluyendo no solapamiento y `fecha >= hoy`).
  - Resuelve la identidad del usuario a partir de la sesión autenticada.
  - Invoca `services.reservas.crear_reserva(...)`.
  - Retorna diccionario estructurado con los datos de la reserva creada (incluyendo `estado: "ACTIVA"`) o `{"error": "<mensaje>"}` en caso de error de negocio.
- **Tool `listar_reservas(skip: int = 0, limit: int = 20)`**:
  - Aplica el mismo filtrado por `usuario_id` que `GET /reservas/`.
  - Invoca `services.reservas.listar_reservas(...)`.
  - Retorna lista de diccionarios de reservas del usuario.
- **Tool `cancelar_reserva(reserva_id: int, confirmacion: bool = False)`**:
  - Exige `confirmacion=True` gestionada por el servidor antes de proceder con la cancelación. Si `confirmacion=False`, responde solicitando confirmación explícita.
  - Verifica que la reserva pertenezca al usuario autenticado.
  - Invoca `services.reservas.cancelar_reserva(...)` actualizando a `CANCELADA`.

---

## Casos de error explícitos que deben tener test

1. **Crear una reserva cuyo horario se solapa con una existente activa**: Debe arrojar excepción de negocio `HorarioSolapadoError` y responder con HTTP 400.
2. **Crear una reserva con `hora_fin` anterior o igual a `hora_inicio`**: Debe arrojar excepción de negocio `HorarioInvalidoError` y responder con HTTP 400.
3. **Listar o crear reservas sin token de autorización**: Debe rechazar la petición con HTTP 401 Unauthorized.
4. **Cancelar una reserva de otro usuario pasando su ID manualmente**: Debe arrojar `NoAutorizadoError` y responder con HTTP 403 Forbidden.
5. **Cancelar una reserva inexistente**: Debe arrojar `ReservaNoEncontradaError` y responder con HTTP 404 Not Found.
6. **Crear una reserva con fecha anterior a la fecha actual (`fecha < hoy`)**: Debe arrojar excepción de negocio `FechaPasadaError` y responder con HTTP 400.

---

## Contrato de compatibilidad y arquitectura

Para cumplir con la Constitución del proyecto, las capas de software mantendrán las siguientes firmas inmutables:

- `app/services/reservas.py`:
  - Excepciones: `HorarioSolapadoError`, `HorarioInvalidoError`, `FechaPasadaError`, `ReservaNoEncontradaError`, `NoAutorizadoError`.
  - `crear_reserva(db, usuario_id: int, fecha: str, hora_inicio: str, hora_fin: str, repo=reservas_repository) -> dict`
  - `listar_reservas(db, usuario_id: int, skip: int = 0, limit: int = 20, repo=reservas_repository) -> list[dict]`
  - `cancelar_reserva(db, usuario_id: int, reserva_id: int, repo=reservas_repository) -> bool`
- `app/repositories/reservas.py` (módulo con funciones sueltas, no clases):
  - `guardar(db, usuario_id: int, fecha: str, hora_inicio: str, hora_fin: str) -> dict`
  - `listar_por_usuario(db, usuario_id: int, skip: int = 0, limit: int = 20) -> list[dict]`
  - `buscar_por_id(db, reserva_id: int) -> dict | None`
  - `buscar_solapamiento(db, fecha: str, hora_inicio: str, hora_fin: str) -> bool` (filtra únicamente reservas con `estado == 'ACTIVA'`)
  - `cancelar(db, reserva_id: int) -> bool` (actualiza `estado = 'CANCELADA'`)
- `app/repositories/usuarios.py`:
  - `obtener_por_email(db, email: str) -> Usuario | None`
  - `guardar(db, email: str, hashed_password: str) -> Usuario`

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los intentos de reserva con solapamiento de horario contra reservas en estado `ACTIVA` son prevenidos y rechazados antes de persistirse.
- **SC-002**: El 100% de las consultas de reservas realizadas por un usuario devuelven única y exclusivamente registros correspondientes a su `usuario_id`.
- **SC-003**: Cero reservas ajenas pueden ser canceladas por usuarios no autorizados (100% de cobertura en verificación de propiedad con error 403).
- **SC-004**: Los 6 casos de error explícitos cuentan con tests automatizados dedicados en verde en la suite de `pytest`.
- **SC-005**: Las tools MCP y los endpoints REST comparten el 100% de la lógica de negocio a través de `services/reservas.py` sin duplicación de código.
- **SC-006**: La cancelación de reservas preserva el 100% de los registros en base de datos con estado `CANCELADA`, liberando exitosamente el intervalo horario para nuevas reservas.
- **SC-007**: El 100% de los intentos de crear reservas con fecha anterior a la fecha del sistema son interceptados y rechazados con HTTP 400 (`FechaPasadaError`).

---

## Assumptions

- Se asume un único espacio compartido (sala/recurso único) para la v1.
- El formato de fechas es ISO `YYYY-MM-DD` y los horarios corresponden a formato 24 horas `HH:MM`.
- Las reservas se realizan para el mismo día (inicio y fin dentro de la misma fecha de calendario).
- El transporte principal para desarrollo local y CLI MCP puede operar en modo `stdio` con usuario de pruebas o autenticado mediante cabeceras Bearer cuando se expone vía HTTP.
