# Feature Specification: Control de Gastos Personales

**Feature Branch**: `001-control-de-gastos`

**Created**: 2026-09-16

**Status**: Clarified

**Input**: User description: "Sistema de control de gastos personales con arquitectura en capas, autenticación OAuth2/JWT, endpoints REST y herramientas MCP."

## Clarifications

### Session 2026-09-16
- Q: ¿Existen roles especiales de usuario (por ejemplo, administradores) con privilegios para consultar o modificar gastos de otros usuarios en el sistema? → A: No, no existen roles especiales; todos los usuarios tienen el mismo nivel y el aislamiento es absoluto (ningún usuario puede ver o modificar gastos de otros).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registro e Inicio de Sesión de Usuario (Priority: P1)

Como nuevo usuario del sistema, quiero crear una cuenta con mi correo y contraseña e iniciar sesión para obtener un token de acceso que me permita gestionar mis finanzas de forma segura.

**Why this priority**: Es la base de seguridad y aislamiento del sistema. Sin autenticación no se puede garantizar la privacidad de los gastos ni la identificación del propietario.

**Independent Test**: Se puede verificar registrando un usuario vía `POST /usuarios/`, validando que la respuesta excluya la contraseña y luego obteniendo un JWT válido vía `POST /usuarios/token`.

**Acceptance Scenarios**:

1. **Given** un correo no registrado y una contraseña válida, **When** el usuario envía la solicitud de registro, **Then** el sistema crea el usuario, retorna código 201 y el identificador único sin exponer la contraseña.
2. **Given** un correo ya registrado, **When** se intenta registrar nuevamente, **Then** el sistema rechaza la solicitud con código 400 y mensaje descriptivo.
3. **Given** credenciales correctas, **When** el usuario solicita un token en `/usuarios/token`, **Then** el sistema emite un token JWT con tiempo de expiración definido (30 minutos).
4. **Given** credenciales erróneas, **When** el usuario solicita un token, **Then** el sistema responde con error 401.

---

### User Story 2 - Registro de Gastos con Validación y Límite de Categoría (Priority: P1)

Como usuario autenticado, quiero registrar mis compras diarias indicando descripción, monto y categoría, asegurando que se validen los datos y no se exceda el presupuesto máximo asignado a cada categoría.

**Why this priority**: Es la funcionalidad central de negocio del sistema de control de gastos.

**Independent Test**: Se prueba registrando gastos con token válido y comprobando que se persistan, que montos inválidos o categorías inexistentes sean rechazados, y que se impida superar el límite acumulado de 500.0 por categoría.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado y un gasto con descripción no vacía, monto positivo y categoría válida ("comida", "transporte", "entretenimiento", "otros"), **When** el gasto no hace superar el acumulado de 500.0 en esa categoría, **Then** se registra el gasto con código 201 y se asocia al usuario del token.
2. **Given** un gasto con monto menor o igual a cero o descripción vacía, **When** se envía al sistema, **Then** se rechaza con error 400 (o 422 si falla el schema) y mensaje claro.
3. **Given** un gasto con una categoría no permitida, **When** se intenta registrar, **Then** se rechaza con error de negocio 400 (`CategoriaInvalidaError`).
4. **Given** una categoría cuyo acumulado más el nuevo monto supera 500.0, **When** se intenta registrar, **Then** el sistema rechaza la transacción con error 400 (`LimiteExcedidoError`) sin modificar la base de datos.

---

### User Story 3 - Consulta y Paginación de Gastos Propios (Priority: P2)

Como usuario autenticado, quiero consultar la lista de mis gastos registrados con soporte de paginación para revisar mi historial sin que se mezclen con los datos de otros usuarios.

**Why this priority**: Permite al usuario auditar sus finanzas con desempeño controlado mediante paginación y estricto aislamiento multi-usuario.

**Independent Test**: Se prueba llamando a `GET /gastos/?skip=0&limit=10` con token de un usuario A y confirmando que sólo se devuelven gastos del usuario A, nunca del usuario B.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado con gastos registrados, **When** solicita `GET /gastos/`, **Then** recibe código 200 con la lista de sus gastos paginada según `skip` y `limit`.
2. **Given** un usuario sin gastos registrados, **When** consulta la lista, **Then** recibe una lista vacía `[]` con código 200.
3. **Given** parámetros `skip` o `limit` negativos o no numéricos, **When** se consulta la ruta, **Then** el sistema responde con error de validación 422.
4. **Given** dos usuarios en el sistema, **When** el usuario A consulta sus gastos, **Then** en ningún caso se muestran gastos del usuario B.

---

### User Story 4 - Interacción Mediante Herramientas MCP (Priority: P2)

Como asistente de IA o cliente MCP, quiero disponer de herramientas (`registrar_gasto`, `listar_gastos`) para interactuar con el sistema de gastos en lenguaje natural, respetando exactamente las mismas reglas de negocio y seguridad que la API REST.

**Why this priority**: Expone la funcionalidad a agentes inteligentes manteniendo paridad absoluta con la lógica de negocio.

**Independent Test**: Se prueba invocando las herramientas MCP vía cliente streamable-http (con JWT) y stdio (con usuario demo documentado), verificando respuestas estructuradas y manejo controlado de errores.

**Acceptance Scenarios**:

1. **Given** una sesión MCP sobre `streamable-http` con token JWT válido, **When** se invoca `registrar_gasto`, **Then** el gasto se crea para el usuario del token ejecutando las mismas validaciones que REST.
2. **Given** una sesión MCP sobre `stdio` sin token, **When** se invoca un tool, **Then** opera sobre el usuario demo configurado en `.env` documentando la simplificación.
3. **Given** una invocación a un tool que viola una regla de negocio (ej. categoría inválida o límite excedido), **When** se ejecuta, **Then** el tool devuelve un objeto estructurado `{"error": "..."}` sin romper la sesión MCP.

---

### Edge Cases

- **Monto límite exacto**: Un gasto que lleva el total acumulado de la categoría exactamente a 500.0 DEBE ser aceptado; un gasto que lo lleve a 500.01 DEBE ser rechazado.
- **Espacios en blanco en descripción**: Descripciones compuestas únicamente por espacios (`"   "`) se consideran vacías y DEBEN ser rechazadas.
- **Inyección de ID de usuario en solicitudes**: Si un cliente o atacante envía `usuario_id` en el cuerpo, query params o headers personalizados, el sistema DEBE ignorarlo por completo y usar exclusivamente el `usuario_id` verificado del token JWT.
- **Roles especiales y elevación de privilegios**: No existen roles administrativos ni privilegios especiales. Ningún usuario puede ver, modificar ni sumar totales de gastos de otro usuario.
- **Intentos de acceso sin token**: Cualquier llamada a rutas o tools protegidas sin token válido DEBE responder 401 antes de ejecutar cualquier lógica de base de datos o servicio.
- **Reintentos de red**: Si un cliente o agente reintenta una llamada a `registrar_gasto` con idénticos parámetros tras un timeout, el sistema contabiliza cada inserción; se documenta la necesidad de idempotencia.
- **Inyección de prompt indirecto en datos**: Textos que contengan instrucciones maliciosas en la descripción del gasto se guardan como cadenas inertes y se devuelven sin ejecución al cliente.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE permitir el registro de usuarios con email único y contraseña hasheada de manera unidireccional con salt (bcrypt).
- **FR-002**: El sistema DEBE proveer un endpoint de autenticación OAuth2 Password Request Form que emita tokens de acceso JWT (HS256) con expiración configurable (30 min).
- **FR-003**: El sistema DEBE permitir a usuarios autenticados registrar gastos con descripción no vacía, monto positivo y categoría válida.
- **FR-004**: El sistema DEBE validar que la categoría pertenezca al catálogo permitido (`comida`, `transporte`, `entretenimiento`, `otros`) y rechazar cualquier otra con un error de dominio `CategoriaInvalidaError`.
- **FR-005**: El sistema DEBE calcular el monto total acumulado por usuario y categoría, rechazando cualquier gasto que haga superar el límite de 500.0 con `LimiteExcedidoError`.
- **FR-006**: El sistema DEBE asociar de forma invariable cada gasto creado al `usuario_id` extraído del token JWT verificado en la capa de dependencias.
- **FR-007**: El sistema DEBE garantizar que todos los usuarios poseen el mismo nivel de acceso plano; no existen roles especiales, administradores ni permisos para acceder a gastos de otros usuarios.
- **FR-008**: El sistema DEBE permitir paginar los listados de gastos mediante parámetros `skip` (default 0) y `limit` (default 20).
- **FR-009**: El sistema DEBE exponer herramientas MCP equivalentes (`registrar_gasto` y `listar_gastos`) que deleguen su ejecución a los mismos servicios de la capa de aplicación.
- **FR-010**: El sistema DEBE interceptar excepciones no controladas en un middleware/handler global y retornar un código 500 con formato `{"detail": "Error interno del servidor"}` sin exponer trazas internas.
- **FR-011**: El sistema DEBE mantener compatibilidad estricta con el contrato de pruebas del proyecto de referencia (firmas de funciones, nombres de módulos y excepciones).

### Key Entities *(include if feature involves data)*

- **Usuario**: Representa la cuenta del usuario. Atributos: `id` (entero, clave primaria), `email` (cadena única e indexada), `hashed_password` (cadena con hash bcrypt). Nunca expone la contraseña en respuestas públicas ni incluye roles diferenciados.
- **Gasto**: Representa una transacción financiera personal. Atributos: `id` (entero, clave primaria), `descripcion` (cadena no vacía), `monto` (flotante > 0), `categoria` (cadena dentro del catálogo permitido), `usuario_id` (entero, clave foránea obligatoria hacia Usuario).

## Contrato de la API (REST)

| Método | Ruta | Auth | Request | Éxito | Errores esperados |
|---|---|---|---|---|---|
| `POST` | `/usuarios/` | No | `{ "email": "...", "password": "..." }` | `201 Created` (`UsuarioResponse`: id, email) | `400 Bad Request` (email ya registrado), `422 Unprocessable Entity` (formato inválido) |
| `POST` | `/usuarios/token` | No | Form-data: `username`, `password` | `200 OK` (`{ "access_token": "...", "token_type": "bearer" }`) | `401 Unauthorized` (credenciales incorrectas), `422 Unprocessable Entity` |
| `POST` | `/gastos/` | Sí (Bearer JWT) | `{ "descripcion": "...", "monto": 12.5, "categoria": "comida" }` | `201 Created` (`GastoResponse`: id, descripcion, monto, categoria) | `400 Bad Request` (categoría inválida, límite excedido, monto $\le 0$), `401 Unauthorized`, `422` |
| `GET` | `/gastos/` | Sí (Bearer JWT) | Query params opcionales: `skip` (int $\ge 0$), `limit` (int $> 0$) | `200 OK` (`list[GastoResponse]`) | `401 Unauthorized`, `422 Unprocessable Entity` (parámetros negativos o inválidos) |

## Contrato Equivalente por MCP

- **Tool `registrar_gasto(descripcion: str, monto: float, categoria: str) -> dict`**:
  - Mismo comportamiento y reglas que `POST /gastos/`.
  - En caso de éxito, retorna el diccionario con los datos del gasto creado.
  - En caso de error de negocio (`ValueError`, `CategoriaInvalidaError`, `LimiteExcedidoError`), retorna `{"error": str(e)}`.
- **Tool `listar_gastos() -> list[dict]`**:
  - Mismo comportamiento que `GET /gastos/`.
  - Retorna la lista de diccionarios de los gastos del usuario autenticado.
- **Identidad en MCP**:
  - En transporte `streamable-http`: la identidad se resuelve desde el Bearer token JWT validado por `JWTTokenVerifier`. Si el usuario no existe en la base de datos, se rechaza la operación sin fallback.
  - En transporte `stdio`: opera con el usuario demo configurado en `app/config.py` (`Settings.mcp_demo_email`) documentando la simplificación explícitamente en el código.

## Contrato de Compatibilidad (No Negociable)

Los tests de las Sesiones 6-8 se integran como criterio de aceptación estricto. Se fijan las siguientes firmas exactas:

- **`app/services/gastos.py`**:
  - Excepciones: `CategoriaInvalidaError`, `LimiteExcedidoError`.
  - Constantes: `LIMITE_POR_CATEGORIA = 500.0`.
  - Funciones:
    - `registrar_gasto(db, usuario_id: int, descripcion: str, monto: float, categoria: str, repo=gastos_repository) -> dict`
    - `listar_gastos(db, usuario_id: int, skip: int = 0, limit: int = 20, repo=gastos_repository) -> list[dict]`
    - Orden posicional exacto; `repo` como keyword argument con default (DIP).
- **`app/repositories/gastos.py`** (módulo con funciones sueltas, no clase):
  - `guardar(db, usuario_id: int, descripcion: str, monto: float, categoria: str) -> dict`
  - `listar(db, usuario_id: int, skip: int = 0, limit: int = 20) -> list[dict]`
  - `total_por_categoria(db, usuario_id: int, categoria: str) -> float`
  - Retornan estructuras simples (`dict`, `float`), nunca objetos ORM hacia el servicio.
- **`app/repositories/usuarios.py`**:
  - `obtener_por_email(db, email: str) -> Usuario | None`
  - `guardar(db, email: str, hashed_password: str) -> Usuario`
- **Símbolos y dependencias importadas directamente por tests**:
  - `app.database.get_db`
  - `app.dependencies.get_current_user`
  - `app.dependencies.get_gastos_repo`
  - `app.models.usuario.Usuario(id=..., email=..., hashed_password=...)`
  - `tests/__init__.py` (necesario para importaciones entre archivos de test).

## Casos de Error Explícitos que Deben Tener Test

1. **Monto inválido**: Registrar gasto con monto negativo o cero lanza error / retorna 400.
2. **Categoría inexistente**: Registrar gasto con categoría no contemplada lanza `CategoriaInvalidaError` / retorna 400.
3. **Límite excedido**: Registrar gasto que hace que el acumulado de la categoría supere 500.0 lanza `LimiteExcedidoError` / retorna 400.
4. **Falta de autenticación**: Listar o registrar gastos sin token JWT responde 401 Unauthorized.
5. **Aislamiento de usuario**: Listar gastos intentando filtrar por un `usuario_id` ajeno es ignorado; el sistema filtra únicamente por el usuario del token.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de los 5 casos de error explícitos de negocio y seguridad cuentan con tests dedicados y automatizados en verde.
- **SC-002**: Las operaciones de creación y consulta de gastos responden en menos de 100 milisegundos en condiciones estándar.
- **SC-003**: 0% de fuga de información entre usuarios: ningún usuario puede acceder, modificar ni calcular totales sobre registros de otro usuario.
- **SC-004**: La suite de pruebas alcanza $\ge 90\%$ de cobertura de líneas en `services/` y $\ge 80\%$ de cobertura combinada en `services/ + repositories/ + routers/ + utils/`.

## Assumptions

- Se utiliza SQLite como motor de base de datos local por defecto, con configuración compatible para migración inmediata a PostgreSQL.
- Los secretos (`SECRET_KEY`) y credenciales de demostración MCP se administran mediante variables de entorno en `.env`.
- La expiración del token JWT por defecto es de 30 minutos.
- El catálogo base de categorías permitidas está conformado por: `comida`, `transporte`, `entretenimiento`, `otros`.
- Todos los usuarios tienen exactamente los mismos privilegios de acceso plano; no existe jerarquía de roles.