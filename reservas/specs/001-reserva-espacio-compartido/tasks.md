# Tasks: Sistema de Reservas de un Espacio Compartido

**Feature**: `001-reserva-espacio-compartido` | **Branch**: `001-reserva-espacio-compartido`  
**Input**: Feature specification from `specs/001-reserva-espacio-compartido/spec.md` and plan from `specs/001-reserva-espacio-compartido/plan.md`  

> **Definition of Done (DoD) obligatoria para cada tarea de implementación**:
> 1. **Código escrito**: Implementado de forma limpia, modular y tipada en el archivo y capa correspondiente.
> 2. **Test correspondiente escrito y en verde**: Caso de prueba unitario, integración o API escrito y pasando exitosamente (`100% pass`).
> 3. **No viola ningún artículo de la constitución**: Cumplimiento verificado de los principios I al VIII sin excepciones silenciosas.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inicialización del proyecto, entorno virtual, dependencias y configuración centralizada.

- [X] T001 Configurar dependencias del proyecto en `pyproject.toml` (FastAPI, uvicorn, SQLAlchemy, Alembic, pyjwt, passlib[bcrypt], bcrypt<4.1, pydantic-settings, email-validator, python-multipart, mcp[cli]<2, pytest, pytest-cov, httpx) e instalar en modo editable con hatchling (DoD: (1) código escrito en `pyproject.toml`, (2) test de verificación de entorno en verde vía `python -c "import fastapi, mcp, sqlalchemy"`, (3) no viola ningún artículo de la constitución)
- [X] T002 [P] Crear plantillas de entorno `.env.example` y `.env` con variables seguras `SECRET_KEY`, `DATABASE_URL`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `LOG_LEVEL` y `MCP_DEMO_USER_EMAIL` (DoD: (1) archivos `.env.example` y `.env` escritos, (2) test de presencia de variables requeridas en verde, (3) no viola Art. IV.3)
- [X] T003 [P] Implementar configuración centralizada en `app/config.py` con test en `tests/test_config.py` usando `pydantic_settings.SettingsConfigDict(env_file=".env")` (DoD: (1) código escrito en `app/config.py`, (2) test correspondiente `test_settings_cargan_desde_entorno` en `tests/test_config.py` escrito y en verde, (3) no viola Art. IV.3)
- [X] T004 [P] Implementar logging estructurado en `app/logging_config.py` y estructura del paquete de tests en `tests/__init__.py` con test en `tests/test_logging.py` (DoD: (1) código escrito en `app/logging_config.py` y `tests/__init__.py`, (2) test correspondiente `test_logging_format` en `tests/test_logging.py` escrito y en verde, (3) no viola Art. I.4)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestructura transversal bloqueante requerida antes de implementar cualquier historia de usuario.

- [X] T005 Implementar motor de base de datos y fábrica de sesiones dual SQLite/Postgres en `app/database.py` con test en `tests/test_database.py` (DoD: (1) código escrito en `app/database.py` con `connect_args` condicional y función `get_db()`, (2) test correspondiente `test_db_session_lifecycle` en `tests/test_database.py` escrito y en verde, (3) no viola Art. III.2)
- [X] T006 [P] Implementar hashing de contraseñas con bcrypt y generación/decodificación JWT (HS256) en `app/security.py` con test en `tests/test_security.py` (DoD: (1) código escrito en `app/security.py` para `hashear_password`, `verificar_password`, `crear_access_token` y `decodificar_access_token`, (2) tests correspondientes `test_password_hash_and_verify` y `test_jwt_encode_and_decode` en `tests/test_security.py` escritos y en verde, (3) no viola Art. IV.1 y IV.2)
- [X] T007 [P] Configurar entorno de migraciones Alembic en `alembic/env.py` y `alembic.ini` vinculando `target_metadata` y URL de `app.config` (DoD: (1) código escrito en `alembic/env.py` y `alembic.ini`, (2) test correspondiente `test_alembic_config_valida` en `tests/test_database.py` escrito y en verde, (3) no viola Art. III.1)
- [X] T008 Implementar dependencias de inyección `get_current_user` y proveedor de repositorio `get_reservas_repo` en `app/dependencies.py` con test en `tests/test_dependencies.py` (DoD: (1) código escrito en `app/dependencies.py` para autenticación Bearer JWT y DIP de repositorios, (2) tests unitarios correspondientes de resolución de dependencias en `tests/test_dependencies.py` escritos y en verde, (3) no viola Art. IV.4 y II.3)
- [X] T009 Implementar aplicación FastAPI base con middleware de logs y manejador global de excepciones 500 sin exponer trazas en `app/main.py` con test en `tests/test_api_reservas.py` (DoD: (1) código escrito en `app/main.py`, (2) test correspondiente `test_error_no_controlado_devuelve_500_sin_stacktrace` en `tests/test_api_reservas.py` escrito y en verde, (3) no viola Art. IV.5)

**Checkpoint**: Infraestructura base lista. Las historias de usuario pueden implementarse de forma desacoplada.

---

## Phase 3: User Story 2 - Registro y Autenticación de Usuarios (Priority: P1)

**Goal**: Permitir a nuevos usuarios crear una cuenta segura y obtener un token JWT para operar en el sistema.  
**Independent Test**: Registrar un usuario vía `POST /usuarios/`, validar que la respuesta excluya el hash de la contraseña y obtener un JWT válido vía `POST /usuarios/token`.

- [X] T010 [P] [US2] Implementar modelo SQLAlchemy `Usuario` en `app/models/usuario.py` con test en `tests/test_models.py` (DoD: (1) código escrito en `app/models/usuario.py` con campos `id`, `email` con índice único y `hashed_password`, (2) test correspondiente `test_modelo_usuario_creacion_e_indice` en `tests/test_models.py` escrito y en verde, (3) no viola Art. III.3 y IV.1)
- [X] T011 [P] [US2] Implementar schemas Pydantic `UsuarioCreate`, `UsuarioOut` y `Token` en `app/schemas/usuario.py` con test en `tests/test_schemas.py` (DoD: (1) código escrito en `app/schemas/usuario.py` con validación estricta de email y exclusión absoluta de password en respuesta, (2) test correspondiente `test_usuario_schemas_password_no_expuesto` en `tests/test_schemas.py` escrito y en verde, (3) no viola Art. V.3 y IV.1)
- [X] T012 [US2] Implementar repositorio de usuarios en `app/repositories/usuarios.py` (`obtener_por_email`, `guardar`) con test en `tests/test_repositories.py` (DoD: (1) código escrito en `app/repositories/usuarios.py` con funciones puras de persistencia recibiendo sesión `db` y retornando entidades de dominio, (2) test correspondiente `test_usuario_repo_guardar_y_obtener` en `tests/test_repositories.py` escrito y en verde, (3) no viola Art. I.3 y VIII.1)
- [X] T013 [US2] Implementar servicio de lógica de negocio de usuarios en `app/services/usuarios.py` (`registrar_usuario`, `autenticar_usuario`, excepciones `EmailYaRegistradoError`, `CredencialesInvalidasError`) con test en `tests/test_services.py` (DoD: (1) código escrito en `app/services/usuarios.py` con SRP sin importar SQLAlchemy ni detalles de persistencia, (2) tests correspondientes `test_registrar_usuario_service` y `test_autenticar_usuario_service` en `tests/test_services.py` escritos y en verde, (3) no viola Art. I.2 y II.1)
- [X] T014 [US2] Implementar router REST de autenticación en `app/routers/usuarios.py` (`POST /usuarios/`, `POST /usuarios/token`) con tests API en `tests/test_api_reservas.py` (DoD: (1) código escrito en `app/routers/usuarios.py` delegando a `services/usuarios.py` y traduciendo a 201/200/400/401, (2) tests correspondientes `test_registrar_usuario`, `test_login_exitoso`, `test_login_credenciales_invalidas` y `test_registrar_usuario_email_duplicado` en `tests/test_api_reservas.py` escritos y en verde, (3) no viola Art. I.1, V.1 y IV.2)

**Checkpoint**: Historia de usuario 2 operativa y verificable de forma independiente.

---

## Phase 4: User Story 1 - Crear Reserva de Espacio sin Solapamiento (Priority: P1) 🎯 Core MVP

**Goal**: Permitir a usuarios autenticados crear reservas para un espacio compartido validando formato de horas, que la fecha sea igual o posterior a hoy (`fecha >= hoy`) y previniendo cualquier solapamiento con reservas en estado `ACTIVA`.  
**Independent Test**: Crear una reserva con token válido vía `POST /reservas/` obteniendo 201 y estado `ACTIVA`, y verificar que un segundo intento en el mismo intervalo horario es rechazado con HTTP 400 (`HorarioSolapadoError`).

- [X] T015 [P] [US1] Implementar modelo SQLAlchemy `Reserva` en `app/models/reserva.py` con clave foránea `usuario_id`, campos `fecha`, `hora_inicio`, `hora_fin`, `estado` (`ACTIVA` por defecto) e índices en `tests/test_models.py` (DoD: (1) código escrito en `app/models/reserva.py` con índice compuesto `(fecha, estado)` y FK `usuario_id`, (2) test correspondiente `test_modelo_reserva_atributos_e_indices` en `tests/test_models.py` escrito y en verde, (3) no viola Art. III.3)
- [X] T016 [P] [US1] Implementar schemas Pydantic `ReservaCreate` y `ReservaOut` en `app/schemas/reserva.py` con test en `tests/test_schemas.py` (DoD: (1) código escrito en `app/schemas/reserva.py` exponiendo `id`, `usuario_id`, `fecha`, `hora_inicio`, `hora_fin` y `estado`, (2) test correspondiente `test_reserva_schemas_serializacion` en `tests/test_schemas.py` escrito y en verde, (3) no viola Art. V.3)
- [X] T017 [P] [US1] Implementar funciones puras de validación de fechas y horas en `app/utils/validadores.py` con test en `tests/test_validadores.py` (DoD: (1) código escrito en `app/utils/validadores.py` para verificar formato `YYYY-MM-DD`, `HH:MM` y coherencia temporal como funciones sin efectos secundarios, (2) test correspondiente `test_validadores_formatos_temporales` en `tests/test_validadores.py` escrito y en verde, (3) no viola Art. I.4 y II.2)
- [X] T018 [US1] Implementar repositorio de persistencia de reservas en `app/repositories/reservas.py` (`guardar`, `buscar_solapamiento` filtrando estrictamente `estado == 'ACTIVA'`) con test en `tests/test_repositories.py` (DoD: (1) código escrito en `app/repositories/reservas.py` retornando diccionarios sin fugar sesiones ORM, (2) tests correspondientes `test_reservas_repo_guardar` y `test_reservas_repo_buscar_solapamiento` en `tests/test_repositories.py` escritos y en verde, (3) no viola Art. I.3 y VIII.1)
- [X] T019 [US1] Implementar servicio de reservas en `app/services/reservas.py` (`_validar_horario`, `_validar_fecha`, `crear_reserva`, excepciones `HorarioSolapadoError`, `HorarioInvalidoError`, `FechaPasadaError`, default DIP `repo=reservas_repository`) con tests unitarios en `tests/test_reservas.py` usando `RepositorioFalso` (DoD: (1) código escrito en `app/services/reservas.py` desacoplado de persistencia con DIP, (2) tests unitarios en verde cubriendo `test_crear_reserva_exitosa`, Caso de Error 1 `test_crear_reserva_horario_solapado_lanza_error`, Caso de Error 2 `test_crear_reserva_hora_fin_menor_o_igual_lanza_error` y Caso de Error 6 `test_crear_reserva_fecha_pasada_lanza_error` en `tests/test_reservas.py`, (3) no viola Art. I.2, II.1, II.3, VII.2 y VII.3)
- [X] T020 [US1] Implementar endpoint de creación `POST /reservas/` en `app/routers/reservas.py` inyectando `get_current_user` y `get_reservas_repo` con tests API en `tests/test_api_reservas.py` (DoD: (1) código escrito en `app/routers/reservas.py` extrayendo identidad del token JWT y traduciendo excepciones a 201/400/422, (2) tests correspondientes `test_crear_reserva_con_repo_falso` y Caso de Error 3 `test_crear_reserva_sin_token_devuelve_401` en `tests/test_api_reservas.py` escritos y en verde, (3) no viola Art. I.1, IV.4 y V.1)
- [X] T021 [US1] Implementar tests de integración para creación de reservas y detección de solapamiento en `tests/test_integracion_reservas.py` contra SQLite (DoD: (1) código de suite de integración con fixture de base de datos en memoria, (2) tests correspondientes `test_crear_reserva_integracion`, Caso de Error 1 `test_solapamiento_bloqueado_integracion` y verificación de reservas contiguas permitidas escritos y en verde, (3) no viola Art. III.2 y VII.4)

**Checkpoint**: Core MVP operativo. Usuarios pueden registrarse y crear reservas con validación de horarios y solapamientos.

---

## Phase 5: User Story 3 - Consulta y Paginación de Reservas Propias (Priority: P2)

**Goal**: Permitir al usuario autenticado consultar sus reservas (activas o canceladas) con paginación (`skip`, `limit`) garantizando aislamiento estricto entre usuarios.  
**Independent Test**: Consultar `GET /reservas/?skip=0&limit=10` con token de usuario A y confirmar que solo se listan sus reservas y nunca las del usuario B.

- [X] T022 [US3] Implementar consulta paginada `listar_por_usuario(db, usuario_id, skip=0, limit=20)` en `app/repositories/reservas.py` con test en `tests/test_repositories.py` (DoD: (1) código escrito en `app/repositories/reservas.py` con filtro mandatorio por `usuario_id` retornando lista de diccionarios, (2) test correspondiente `test_reservas_repo_listar_por_usuario` en `tests/test_repositories.py` escrito y en verde, (3) no viola Art. III.3 y VIII.1)
- [X] T023 [US3] Implementar servicio de listado `listar_reservas(db, usuario_id, skip=0, limit=20, repo=reservas_repository)` en `app/services/reservas.py` con test unitario en `tests/test_reservas.py` (DoD: (1) código escrito en `app/services/reservas.py` con DIP recibiendo `repo` con default, (2) test unitario correspondiente `test_listar_reservas_con_repositorio_falso` en `tests/test_reservas.py` escrito y en verde, (3) no viola Art. I.2, II.3 y VIII.1)
- [X] T024 [US3] Implementar endpoint `GET /reservas/` con parámetros `skip`/`limit` y autenticación en `app/routers/reservas.py` con tests API en `tests/test_api_reservas.py` (DoD: (1) código escrito en `app/routers/reservas.py` consumiendo `get_current_user` e ignorando cualquier ID externo, (2) tests correspondientes `test_listar_reservas_paginadas` y Caso de Error 3 `test_listar_reservas_sin_token_devuelve_401` en `tests/test_api_reservas.py` escritos y en verde, (3) no viola Art. I.1, IV.4, V.1 y V.2)
- [X] T025 [US3] Implementar test de integración para aislamiento multiusuario estricto y paginación en `tests/test_integracion_reservas.py` (DoD: (1) código de prueba de aislamiento registrando reservas para dos usuarios en SQLite, (2) test correspondiente `test_aislamiento_entre_usuarios_reservas_integracion` escrito y en verde confirmando 0% de fuga de datos entre usuarios, (3) no viola Art. III.3, IV.4 y VII.4)

**Checkpoint**: Historias 1, 2 y 3 operan integradas con aislamiento multiusuario estricto.

---

## Phase 6: User Story 4 - Cancelar Reserva Propia mediante Soft Delete (Priority: P2)

**Goal**: Permitir al usuario autenticado cancelar sus reservas propias cambiando su estado a `CANCELADA`, liberando inmediatamente el horario para nuevos registros y bloqueando cancelaciones ajenas.  
**Independent Test**: Cancelar una reserva vía `DELETE /reservas/{id}` recibiendo 204 y confirmando que un usuario B recibe 403 al intentar cancelarla.

- [X] T026 [US4] Implementar operaciones `buscar_por_id(db, reserva_id)` y `cancelar(db, reserva_id)` (actualizar `estado = 'CANCELADA'`) en `app/repositories/reservas.py` con test en `tests/test_repositories.py` (DoD: (1) código escrito en `app/repositories/reservas.py` ejecutando actualización lógica, (2) tests correspondientes `test_reservas_repo_buscar_y_cancelar` en `tests/test_repositories.py` escritos y en verde, (3) no viola Art. I.3 y VIII.1)
- [X] T027 [US4] Implementar servicio de cancelación `cancelar_reserva(db, usuario_id, reserva_id, repo=reservas_repository)` en `app/services/reservas.py` (excepciones `NoAutorizadoError`, `ReservaNoEncontradaError`) con tests unitarios en `tests/test_reservas.py` usando `RepositorioFalso` (DoD: (1) código escrito en `app/services/reservas.py` validando que la reserva exista y pertenezca al usuario, (2) tests unitarios Caso de Error 4 `test_cancelar_reserva_ajena_lanza_no_autorizado` [403] y Caso de Error 5 `test_cancelar_reserva_inexistente_lanza_error` [404] escritos y en verde en `tests/test_reservas.py`, (3) no viola Art. I.2, II.1, IV.4 y VII.3)
- [X] T028 [US4] Implementar endpoint `DELETE /reservas/{id}` en `app/routers/reservas.py` inyectando `get_current_user` con tests API en `tests/test_api_reservas.py` (DoD: (1) código escrito en `app/routers/reservas.py` traduciendo a 204 No Content, 403 Forbidden y 404 Not Found, (2) tests correspondientes `test_cancelar_reserva_exitosa`, `test_cancelar_reserva_ajena_devuelve_403` y `test_cancelar_reserva_inexistente_devuelve_404` en `tests/test_api_reservas.py` escritos y en verde, (3) no viola Art. I.1, IV.4 y V.1)
- [X] T029 [US4] Implementar test de integración para cancelación y liberación de horario en `tests/test_integracion_reservas.py` (DoD: (1) código de prueba creando reserva, cancelándola y volviendo a reservar el mismo horario, (2) test correspondiente `test_cancelacion_soft_delete_y_reutilizacion_horario_integracion` escrito y en verde, (3) no viola Art. III.2 y VII.4)

**Checkpoint**: Ciclo completo de reservas y cancelaciones operativo en la API REST.

---

## Phase 7: Herramientas MCP con Paridad y Seguridad

**Goal**: Exponer herramientas MCP (`crear_reserva`, `listar_reservas`, `cancelar_reserva`) sobre transporte `streamable-http` con autenticación Bearer JWT y confirmación destructiva en dos pasos.  
**Independent Test**: Conectar cliente MCP con JWT a `/mcp/`, ejecutar las 3 herramientas y verificar su reflejo en la API REST.

- [X] T030 [P] Implementar verificador de tokens Bearer `JWTTokenVerifier` en `app/mcp/auth.py` con test en `tests/test_mcp_tools.py` (DoD: (1) código escrito en `app/mcp/auth.py` validando JWT y claim `sub` contra `app.security`, (2) test correspondiente `test_jwt_token_verifier_mcp` en `tests/test_mcp_tools.py` escrito y en verde, (3) no viola Art. VI.4 y IV.2)
- [X] T031 [P] Configurar instancia del servidor FastMCP con autenticación en `app/mcp/server.py` con test en `tests/test_mcp_tools.py` (DoD: (1) código escrito en `app/mcp/server.py` con `FastMCP("reservas-mcp")`, `streamable_http_path="/"` y `AuthSettings`, (2) test correspondiente `test_mcp_server_setup` en `tests/test_mcp_tools.py` escrito y en verde, (3) no viola Art. VI.4)
- [X] T032 Implementar herramientas MCP `crear_reserva`, `listar_reservas` y `cancelar_reserva` (con confirmación destructiva en dos pasos) en `app/mcp/tools/reservas.py` reutilizando `services/reservas.py` con tests en `tests/test_mcp_tools.py` (DoD: (1) código escrito en `app/mcp/tools/reservas.py` delegando exclusivamente a `services/reservas.py`, devolviendo diccionarios estructurados y exigiendo `confirmacion=True` para cancelar, (2) tests correspondientes `test_mcp_crear_reserva_tool`, `test_mcp_listar_reservas_tool`, `test_mcp_cancelar_reserva_requiere_confirmacion` y `test_mcp_cancelar_reserva_confirmada` en `tests/test_mcp_tools.py` escritos y en verde, (3) no viola Art. VI.1, VI.2, VI.3, VI.5 y VII.6)
- [X] T033 Montar subaplicación streamable-http de MCP en `app/main.py` con gestión de lifespan (`session_manager.run()`) con test en `tests/test_mcp_tools.py` (DoD: (1) código escrito en `app/main.py` montando el servidor MCP en `/mcp` administrando su ciclo de vida, (2) test correspondiente `test_mcp_streamable_http_endpoint_mounted` en `tests/test_mcp_tools.py` escrito y en verde, (3) no viola Art. VI.4 y VII.5)
- [X] T034 [P] Crear configuración de cliente MCP para VS Code y Antigravity en `.vscode/mcp.json` (DoD: (1) archivo `.vscode/mcp.json` escrito con configuración dual streamable-http y stdio, (2) validación de JSON en verde, (3) no viola Art. VI.4)

**Checkpoint**: Paridad total entre endpoints REST y herramientas MCP.

---

## Phase 8: Polish, Migraciones & Coverage Verification

**Purpose**: Migraciones de base de datos, portabilidad a PostgreSQL y verificación de umbrales constitucionales.

- [X] T035 [P] Generar y aplicar migración inicial de Alembic en `alembic/versions/` para tablas `usuarios` y `reservas` con test en `tests/test_database.py` (DoD: (1) script de migración escrito con creación de tablas e índices, (2) test correspondiente `test_migracion_alembic_aplica_exitosamente` en `tests/test_database.py` escrito y en verde sobre `reservas.db`, (3) no viola Art. III.1)
- [X] T036 [P] Crear archivo `docker-compose.yml` para validación de base de datos PostgreSQL y verificar portabilidad en `tests/test_database_postgres.py` (DoD: (1) configuración escrita en `docker-compose.yml` con servicio Postgres en puerto 5433 y credenciales de práctica, (2) test condicional `test_postgres_portabilidad` en `tests/test_database_postgres.py` en verde, (3) no viola Art. III.2)
- [X] T037 Configurar fixture `client` con `scope="module"` en `tests/test_api_reservas.py` para evitar conflictos de reentrada del gestor de sesiones de `FastMCP` (DoD: (1) código de fixture ajustado en `tests/test_api_reservas.py` con `scope="module"`, (2) suite de `tests/test_api_reservas.py` ejecutándose en verde sin fallos de lifespan, (3) no viola Art. VII.5)
- [X] T038 Correr `pytest --cov=app --cov-report=term-missing` y confirmar que se cumple el umbral de cobertura del Artículo VII.3 (>=90% en `services/` y >=80% global en `app/`) (DoD: (1) ejecución del reporte de cobertura sin fallos técnicos, (2) suite completa en verde confirmando >=90% de cobertura en `app/services/` y >=80% global en `app/` con los 6 casos de error explícitos cubiertos, (3) no viola ningún artículo de la constitución)

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: Puede comenzar de inmediato.
- **Foundational (Phase 2)**: Depende de Phase 1 completada — BLOQUEA todas las historias de usuario.
- **User Story 2 (Phase 3)**: Depende de Phase 2. Establece persistencia de usuarios y autenticación.
- **User Story 1 (Phase 4)**: Depende de Phase 3 (requiere usuario y seguridad).
- **User Story 3 (Phase 5)**: Depende de Phase 4 (requiere entidad reserva y persistencia).
- **User Story 4 (Phase 6)**: Depende de Phase 4 y 5 (requiere reservas existentes y listado).
- **MCP Parity (Phase 7)**: Depende de Phase 4, 5 y 6 (las herramientas envuelven servicios probados).
- **Polish & Coverage (Phase 8)**: Depende de todas las fases anteriores completadas.

---

## Parallel Execution Opportunities

- `T002`, `T003`, `T004` (Variables de entorno, config centralizada y logging) pueden ejecutarse en paralelo.
- `T006`, `T007` (Seguridad y configuración de Alembic) pueden ejecutarse en paralelo tras T005.
- `T010`, `T011` (Modelos y schemas de Usuario) pueden ejecutarse en paralelo.
- `T015`, `T016`, `T017` (Modelos, schemas de Reserva y validador de fechas/horas) pueden ejecutarse en paralelo.
- `T030`, `T031`, `T034` (MCP auth, MCP server y `.vscode/mcp.json`) pueden ejecutarse en paralelo.
- `T035`, `T036` (Migración de Alembic y Docker Compose para Postgres) pueden ejecutarse en paralelo.

---

## Coverage Verification Checklist (Art. VII.3)

Mapeo de los 6 casos de error explícitos exigidos por `spec.md` y `constitution.md`:

- [X] 1. **Horario solapado con reserva activa existente (`HorarioSolapadoError`)**: Cubierto en `T019` (`tests/test_reservas.py`) y `T021` (`tests/test_integracion_reservas.py`).
- [X] 2. **`hora_fin` menor o igual a `hora_inicio` (`HorarioInvalidoError`)**: Cubierto en `T019` (`tests/test_reservas.py`).
- [X] 3. **Solicitudes sin token JWT responden 401 Unauthorized**: Cubierto en `T020` y `T024` (`tests/test_api_reservas.py`).
- [X] 4. **Intento de cancelar reserva ajena (`NoAutorizadoError` → 403 Forbidden)**: Cubierto en `T027` (`tests/test_reservas.py`) y `T028` (`tests/test_api_reservas.py`).
- [X] 5. **Intento de cancelar reserva inexistente (`ReservaNoEncontradaError` → 404 Not Found)**: Cubierto en `T027` (`tests/test_reservas.py`) y `T028` (`tests/test_api_reservas.py`).
- [X] 6. **Crear reserva con fecha anterior a la fecha actual (`FechaPasadaError` → 400 Bad Request)**: Cubierto en `T019` (`tests/test_reservas.py`).
- [X] **Umbral en servicios**: Cobertura de líneas en `app/services/` $\ge 90\%$ (Alcanzado: 100%).
- [X] **Umbral global**: Cobertura de líneas global en `app/` $\ge 80\%$ (Alcanzado: 97%).
