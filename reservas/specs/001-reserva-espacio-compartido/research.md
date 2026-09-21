# Phase 0: Research & Technical Decisions

**Feature**: `001-reserva-espacio-compartido`  
**Date**: 2026-09-20  
**Context**: Sistema de reservas de un espacio compartido con gestión de usuarios, detección estricta de solapamientos, soft delete y herramientas MCP equivalentes.

---

## 1. Detección Matemática de Solapamiento de Horarios

### Contexto
El sistema gestiona un único espacio compartido. Dos reservas no pueden ocupar simultáneamente el mismo intervalo horario en una misma fecha, a menos que una de ellas esté en estado `CANCELADA`. Las reservas contiguas (donde una inicia en el instante exacto en que la anterior termina) deben ser permitidas.

### Decisión
Modelar los intervalos como semiabiertos $[H_{inicio}, H_{fin})$. Dos intervalos $A$ y $B$ en la misma fecha se solapan si y solo si:
$$\text{solapa} = (A_{inicio} < B_{fin}) \land (A_{fin} > B_{inicio})$$

En SQLAlchemy, la consulta de solapamiento contra reservas activas se formula como:
```python
stmt = select(Reserva).where(
    Reserva.fecha == fecha,
    Reserva.estado == "ACTIVA",
    Reserva.hora_inicio < nueva_fin,
    Reserva.hora_fin > nueva_inicio,
)
```

### Justificación
- Esta condición cubre todos los casos posibles de colisión: solapamiento exacto, solapamiento parcial al inicio, solapamiento parcial al final y contención total.
- Reservas contiguas: si $A_{fin} == B_{inicio}$, la condición $A_{fin} > B_{inicio}$ es falsa, por lo que NO hay solapamiento y la reserva es permitida.
- El filtrado por `estado == "ACTIVA"` garantiza que reservas previamente canceladas no bloqueen el espacio.

### Alternativas Descartadas
- *Comparación basada en timestamps absolutos*: Descartada para evitar complejidad de zonas horarias en v1; almacenar `fecha` (`YYYY-MM-DD`) y `hora` (`HH:MM`) como strings ISO garantiza orden léxico compatible (`"10:00" < "11:00"`).

---

## 2. Stack Tecnológico y Dependencias

### Decisión
- **Framework Web**: `FastAPI` (0.115+) montado sobre servidor ASGI `uvicorn[standard]`.
- **Autenticación y Seguridad**:
  - Hashing: `passlib[bcrypt]` con fijación explícita `bcrypt<4.1` (evita el bug de compatibilidad en runtime con `passlib 1.7.4`).
  - Tokens: `pyjwt` con algoritmo simétrico `HS256` y expiración (`exp`).
  - Formularios: `python-multipart` para compatibilidad con `OAuth2PasswordRequestForm`.
  - Validación de email: `email-validator` para `pydantic.EmailStr`.
  - Configuración: `pydantic-settings` para cargar variables de entorno (`SECRET_KEY`, `DATABASE_URL`, `ACCESS_TOKEN_EXPIRE_MINUTES`).
- **Persistencia**:
  - ORM: `SQLAlchemy` (2.0+) en modo declarativo tipado (`Mapped`, `mapped_column`).
  - Migraciones: `Alembic` para versionado de esquema.
  - Base de datos: `SQLite 3` para desarrollo local y tests en memoria (`sqlite:///:memory:`), con arquitectura desacoplada lista para PostgreSQL (`psycopg[binary]`).
- **Servidor MCP**:
  - SDK oficial Python `mcp` (`FastMCP`) montado como sub-aplicación ASGI en `/mcp` mediante transporte `streamable-http`.
  - Autenticación mediante `JWTTokenVerifier` que intercepta cabeceras `Authorization: Bearer <token>` del cliente MCP.
- **Testing**:
  - `pytest` como runner.
  - `pytest-cov` para auditoría de cobertura de código.
  - `httpx` para peticiones ASGI asíncronas con `TestClient`.

### Justificación
- Satisface directamente los Artículos I, III, IV, VI y VII de la Constitución del proyecto.
- Cero bibliotecas obsoletas (se descarta `python-jose` por falta de mantenimiento, optando por `pyjwt`).

---

## 3. Estrategia de Soft Delete para Cancelación

### Decisión
La cancelación de una reserva mediante `DELETE /reservas/{id}` o la tool MCP `cancelar_reserva` no ejecuta un `DELETE FROM reservas`, sino un `UPDATE reservas SET estado = 'CANCELADA'`.
- El endpoint REST responde con HTTP `204 No Content`.
- La lista de reservas (`GET /reservas/`) devuelve todas las reservas del usuario indicando su `estado` (`ACTIVA` o `CANCELADA`).
- La función `buscar_solapamiento` en `repositories/reservas.py` filtra estrictamente por `estado == 'ACTIVA'`, de modo que el intervalo horario queda automáticamente liberado.

### Justificación
- Cumple con la clarificación acordada (Opción B).
- Preserva la trazabilidad y auditoría histórica de reservas sin impactar la disponibilidad del espacio compartido.

---

## 4. Confirmación Gestionada por el Servidor para Operaciones Destructivas en MCP

### Decisión
La tool MCP `cancelar_reserva(reserva_id: int, confirmacion: bool = False)` implementa un mecanismo de confirmación en dos pasos:
1. Si se invoca con `confirmacion=False`, la tool NO ejecuta la cancelación y devuelve:
   ```json
   {
     "status": "confirmation_required",
     "message": "La cancelación liberará el horario de la reserva #<id> para otros usuarios. Confirme la operación ejecutando cancelar_reserva con confirmacion=True."
   }
   ```
2. Solo cuando se envía `confirmacion=True`, el servidor procede a validar que el usuario sea el dueño y ejecuta la cancelación en `services/reservas.py`.

### Justificación
- Cumple estrictamente con el Artículo VI.5 de la Constitución: *"Cualquier tool con efecto destructivo debe pedir confirmación explícita gestionada por el servidor, nunca depender de que el modelo decida preguntar por su cuenta."*

---

## 5. Diseño de Testing y Cumplimiento de Inversión de Dependencias (DIP)

### Decisión
- Los servicios de negocio en `app/services/reservas.py` reciben la dependencia del repositorio como argumento con valor por defecto:
  ```python
  def crear_reserva(db, usuario_id: int, fecha: str, hora_inicio: str, hora_fin: str, repo=reservas_repository) -> dict: ...
  ```
- En las pruebas unitarias (`tests/test_reservas.py`), se define una clase `RepositorioFalso` que almacena registros en memoria en un `dict` y simula las operaciones de persistencia.
- Se prohíbe el uso de `unittest.mock` para simular la persistencia en las pruebas unitarias de servicios (Artículo VII.2).
- Las pruebas de API (`tests/test_api_reservas.py`) utilizan `app.dependency_overrides` para inyectar un usuario autenticado simulado y una sesión de base de datos de pruebas.
