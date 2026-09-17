# Tasks: Control de Gastos Personales

**Feature**: `001-control-de-gastos` | **Branch**: `001-control-de-gastos`  
**Input**: Feature specification from `specs/001-control-de-gastos/spec.md` and plan from `specs/001-control-de-gastos/plan.md`  

> **Definition of Done (DoD) obligatoria para cada tarea de implementación**:
> 1. **Código escrito**: Implementado de forma limpia, modular y tipada en el archivo y capa correspondiente.
> 2. **Test correspondiente escrito y en verde**: Caso de prueba unitario o de integración escrito y pasando exitosamente (`100% pass`).
> 3. **No viola ningún artículo de la constitución**: Cumplimiento verificado de los principios I al VIII sin excepciones silenciosas.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inicialización del proyecto, entorno virtual, dependencias y configuración centralizada.

- [X] T001 Configurar dependencias del proyecto en `pyproject.toml` (FastAPI, uvicorn, SQLAlchemy, Alembic, pyjwt, passlib[bcrypt], bcrypt<4.1, pydantic-settings, email-validator, python-multipart, mcp[cli]<2, pytest, pytest-cov, httpx) e instalar en modo editable con hatchling (DoD: (1) código escrito en `pyproject.toml`, (2) test de verificación de entorno en verde vía `python -c "import fastapi, mcp, sqlalchemy"`, (3) no viola ningún artículo de la constitución)
- [X] T002 [P] Crear plantillas de entorno `.env.example` y `.env` con variables seguras `SECRET_KEY`, `DATABASE_URL`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `LOG_LEVEL` y settings de MCP (DoD: (1) archivos `.env.example` y `.env` escritos, (2) test de presencia de variables requeridas en verde, (3) no viola Art. IV.3)
- [X] T003 [P] Implementar configuración centralizada en `app/config.py` con test en `tests/test_config.py` usando `pydantic_settings.SettingsConfigDict(env_file=".env")` (DoD: (1) código escrito en `app/config.py`, (2) test correspondiente `test_settings_cargan_desde_entorno` en `tests/test_config.py` escrito y en verde, (3) no viola Art. IV.3)
- [X] T004 [P] Implementar logging estructurado en `app/logging_config.py` y estructura del paquete de tests en `tests/__init__.py` con test en `tests/test_logging.py` (DoD: (1) código escrito en `app/logging_config.py` y `tests/__init__.py`, (2) test correspondiente `test_logging_format` en `tests/test_logging.py` escrito y en verde, (3) no viola Art. I.4)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestructura transversal bloqueante requerida antes de implementar cualquier historia de usuario.

- [X] T005 Implementar motor de base de datos y fábrica de sesiones dual SQLite/Postgres en `app/database.py` con test en `tests/test_database.py` (DoD: (1) código escrito en `app/database.py` con `connect_args` condicional y función `get_db()`, (2) test correspondiente `test_db_session_lifecycle` en `tests/test_database.py` escrito y en verde, (3) no viola Art. III.2)
- [X] T006 [P] Implementar hashing de contraseñas con bcrypt y generación/decodificación JWT (HS256) en `app/security.py` con test en `tests/test_security.py` (DoD: (1) código escrito en `app/security.py` para `hashear_password`, `verificar_password`, `crear_access_token` y `decodificar_access_token`, (2) tests correspondientes `test_password_hash_and_verify` y `test_jwt_encode_and_decode` en `tests/test_security.py` escritos y en verde, (3) no viola Art. IV.1 y IV.2)
- [X] T007 [P] Configurar entorno de migraciones Alembic en `alembic/env.py` y `alembic.ini` vinculando `target_metadata` y URL de `app.config` (DoD: (1) código escrito en `alembic/env.py` y `alembic.ini`, (2) test correspondiente `test_alembic_config_valida` en `tests/test_database.py` escrito y en verde, (3) no viola Art. III.1)
- [X] T008 Implementar dependencias de inyección `get_current_user` y proveedor de repositorio `get_gastos_repo` en `app/dependencies.py` con test en `tests/test_dependencies.py` (DoD: (1) código escrito en `app/dependencies.py` para autenticación Bearer JWT y DIP de repositorios, (2) tests unitarios correspondientes de resolución de dependencias en `tests/test_dependencies.py` escritos y en verde, (3) no viola Art. IV.4 y II.3)
- [X] T009 Implementar aplicación FastAPI base con middleware de logs y manejador global de excepciones 500 sin exponer trazas en `app/main.py` con test en `tests/test_api_gastos.py` (DoD: (1) código escrito en `app/main.py`, (2) test correspondiente `test_error_no_controlado_devuelve_500_sin_stacktrace` en `tests/test_api_gastos.py` escrito y en verde, (3) no viola Art. IV.5)

**Checkpoint**: Infraestructura base lista. Las historias de usuario pueden implementarse de forma desacoplada.

---

## Phase 3: User Story 1 - Registro e Inicio de Sesión de Usuario (Priority: P1) 🎯 MVP

**Goal**: Permitir a nuevos usuarios crear una cuenta segura y obtener un token JWT para operar en el sistema.  
**Independent Test**: Registrar un usuario vía `POST /usuarios/`, validar que la respuesta excluya el hash de la contraseña y obtener un JWT válido vía `POST /usuarios/token`.

- [X] T010 [P] [US1] Implementar modelo SQLAlchemy `Usuario` en `app/models/usuario.py` con test en `tests/test_models.py` (DoD: (1) código escrito en `app/models/usuario.py` con campos `id`, `email` con índice único y `hashed_password`, (2) test correspondiente `test_modelo_usuario_creacion_e_indice` en `tests/test_models.py` escrito y en verde, (3) no viola Art. III.3 y IV.1)
- [X] T011 [P] [US1] Implementar schemas Pydantic `UsuarioCreate` y `UsuarioResponse` en `app/schemas/usuario.py` con test en `tests/test_schemas.py` (DoD: (1) código escrito en `app/schemas/usuario.py` con validación estricta de email y exclusión absoluta de password en respuesta, (2) test correspondiente `test_usuario_schemas_password_no_expuesto` en `tests/test_schemas.py` escrito y en verde, (3) no viola Art. V.3 y IV.1)
- [X] T012 [US1] Implementar repositorio de usuarios en `app/repositories/usuarios.py` (`obtener_por_email`, `guardar`) con test en `tests/test_repositories.py` (DoD: (1) código escrito en `app/repositories/usuarios.py` con funciones puras de persistencia recibiendo sesión `db` y retornando entidades de dominio, (2) test correspondiente `test_usuario_repo_guardar_y_obtener` en `tests/test_repositories.py` escrito y en verde, (3) no viola Art. I.3 y VIII.1)
- [X] T013 [US1] Implementar servicio de lógica de negocio de usuarios en `app/services/usuarios.py` (`registrar_usuario`, `autenticar_usuario`, excepciones `EmailYaRegistradoError`, `CredencialesInvalidasError`) con test en `tests/test_services.py` (DoD: (1) código escrito en `app/services/usuarios.py` con SRP sin importar SQLAlchemy ni detalles de persistencia, (2) tests correspondientes `test_registrar_usuario_service` y `test_autenticar_usuario_service` en `tests/test_services.py` escritos y en verde, (3) no viola Art. I.2 y II.1)
- [X] T014 [US1] Implementar router REST de autenticación en `app/routers/usuarios.py` (`POST /usuarios/`, `POST /usuarios/token`) con tests API en `tests/test_api_gastos.py` (DoD: (1) código escrito en `app/routers/usuarios.py` delegando a `services/usuarios.py` y traduciendo a 201/200/400/401, (2) tests correspondientes `test_registrar_usuario`, `test_login_exitoso`, `test_login_credenciales_invalidas` y `test_registrar_usuario_email_duplicado` en `tests/test_api_gastos.py` escritos y en verde, (3) no viola Art. I.1, V.1 y IV.2)

**Checkpoint**: Historia de usuario 1 operativa y verificable de forma independiente.

---

## Phase 4: User Story 2 - Registro de Gastos con Validación y Límite de Categoría (Priority: P1)

**Goal**: Permitir a usuarios autenticados registrar gastos validando monto positivo, categorías permitidas y límite mensual acumulado de 500.0 por categoría.  
**Independent Test**: Registrar gastos con token, comprobar rechazo de montos $\le 0$, categorías inválidas (`CategoriaInvalidaError`) y exceso de límite (`LimiteExcedidoError`).

- [X] T015 [P] [US2] Implementar modelo SQLAlchemy `Gasto` en `app/models/gasto.py` con clave foránea `usuario_id` y test en `tests/test_models.py` (DoD: (1) código escrito en `app/models/gasto.py` con `id`, `descripcion`, `monto`, `categoria`, `fecha` y `usuario_id` indexado, (2) test correspondiente `test_modelo_gasto_fk_usuario` en `tests/test_models.py` escrito y en verde, (3) no viola Art. III.3)
- [X] T016 [P] [US2] Implementar schemas Pydantic `GastoCreate` y `GastoResponse` en `app/schemas/gasto.py` con test en `tests/test_schemas.py` (DoD: (1) código escrito en `app/schemas/gasto.py` con validación de tipos y `from_attributes=True`, (2) test correspondiente `test_gasto_schemas_validacion` en `tests/test_schemas.py` escrito y en verde, (3) no viola Art. V.3)
- [X] T017 [P] [US2] Implementar catálogo de categorías y función pura de validación en `app/utils/validadores.py` con test en `tests/test_validadores.py` (DoD: (1) código escrito en `app/utils/validadores.py` sobre catálogo (`comida`, `transporte`, `entretenimiento`, `otros`) como función pura, (2) test correspondiente `test_validador_categorias_permitidas` en `tests/test_validadores.py` escrito y en verde, (3) no viola Art. I.4 y II.2)
- [X] T018 [US2] Implementar repositorio de persistencia de gastos en `app/repositories/gastos.py` (`guardar`, `total_por_categoria`) con test en `tests/test_repositories.py` (DoD: (1) código escrito en `app/repositories/gastos.py` retornando diccionarios y floats sin filtrar ni fugar sesiones u objetos ORM, (2) tests correspondientes `test_gastos_repo_guardar` y `test_gastos_repo_total_por_categoria` en `tests/test_repositories.py` escritos y en verde, (3) no viola Art. I.3 y VIII.2)
- [X] T019 [US2] Implementar lógica de negocio de registro en `app/services/gastos.py` (`_validar_gasto`, `registrar_gasto`, `CategoriaInvalidaError`, `LimiteExcedidoError`, `LIMITE_POR_CATEGORIA = 500.0`, default DIP `repo=gastos_repository`) con tests unitarios en `tests/test_gastos.py` usando `RepositorioFalso` (DoD: (1) código escrito en `app/services/gastos.py` desacoplado de SQLAlchemy con SRP y DIP, (2) tests unitarios escritos y en verde cubriendo `test_registrar_gasto_exitoso`, Caso de Error 1 `test_registrar_gasto_monto_invalido_lanza_error` [monto <= 0], Caso de Error 2 `test_registrar_gasto_categoria_invalida_lanza_error` [categoría inexistente] y Caso de Error 3 `test_registrar_gasto_excede_limite_categoria_lanza_error` [límite 500.0] en `tests/test_gastos.py`, (3) no viola Art. I.2, II.1, II.3, VII.2 y VII.3)
- [X] T020 [US2] Implementar endpoint de creación `POST /gastos/` en `app/routers/gastos.py` inyectando `get_current_user` y `get_gastos_repo` con tests API en `tests/test_api_gastos.py` (DoD: (1) código escrito en `app/routers/gastos.py` extrayendo identidad del token verificado y traduciendo errores de dominio a 400, (2) tests correspondientes `test_crear_gasto_con_repo_falso` y Caso de Error 4 `test_crear_gasto_sin_token_devuelve_401` en `tests/test_api_gastos.py` escritos y en verde, (3) no viola Art. I.1, IV.4 y V.1)
- [X] T021 [US2] Implementar tests de integración para registro de gastos y límite de categoría contra base de datos SQLite en `tests/test_integracion_gastos.py` (DoD: (1) código de suite de integración con fixture de base de datos en memoria (`sqlite:///:memory:`), (2) tests correspondientes `test_registrar_y_listar_gasto_integracion` y Caso de Error 3 `test_limite_por_categoria_integracion` escritos y en verde, (3) no viola Art. III.2 y VII.4)

**Checkpoint**: Historias de usuario 1 y 2 operativas de forma desacoplada y probadas con persistencia e inyección.

---

## Phase 5: User Story 3 - Consulta y Paginación de Gastos Propios con Aislamiento (Priority: P2)

**Goal**: Permitir al usuario autenticado consultar sus gastos con paginación (`skip`, `limit`) garantizando estricto aislamiento entre usuarios.  
**Independent Test**: Llamar a `GET /gastos/?skip=0&limit=10` con token y confirmar que sólo se listan gastos propios y nunca de otros usuarios.

- [X] T022 [US3] Implementar consulta paginada `listar(db, usuario_id, skip=0, limit=20)` en `app/repositories/gastos.py` con test en `tests/test_repositories.py` (DoD: (1) código escrito en `app/repositories/gastos.py` con filtro mandatorio por `usuario_id` retornando lista de diccionarios, (2) test correspondiente `test_gastos_repo_listar_con_filtro_usuario` en `tests/test_repositories.py` escrito y en verde, (3) no viola Art. III.3 y VIII.2)
- [X] T023 [US3] Implementar servicio de listado `listar_gastos(db, usuario_id, skip=0, limit=20, repo=gastos_repository)` en `app/services/gastos.py` con test unitario en `tests/test_gastos.py` (DoD: (1) código escrito en `app/services/gastos.py` con DIP recibiendo `repo` con default, (2) test unitario correspondiente `test_listar_gastos_con_repositorio_falso` en `tests/test_gastos.py` escrito y en verde, (3) no viola Art. I.2, II.3 y VIII.1)
- [X] T024 [US3] Implementar endpoint `GET /gastos/` con parámetros `skip`/`limit` y autenticación en `app/routers/gastos.py` con tests API en `tests/test_api_gastos.py` (DoD: (1) código escrito en `app/routers/gastos.py` consumiendo `get_current_user` e ignorando cualquier `usuario_id` provisto externamente, (2) tests correspondientes `test_listar_gastos_con_paginacion`, Caso de Error 4 `test_listar_gastos_sin_token_devuelve_401` y Caso de Error 5 `test_listar_gastos_usuario_id_ajeno_ignorado` en `tests/test_api_gastos.py` escritos y en verde, (3) no viola Art. I.1, IV.4, V.1 y V.2)
- [X] T025 [US3] Implementar test de integración para aislamiento multiusuario estricto y paginación en `tests/test_integracion_gastos.py` (DoD: (1) código de prueba de aislamiento registrando gastos para dos usuarios distintos en SQLite, (2) test correspondiente Caso de Error 5 `test_aislamiento_entre_usuarios_integracion` escrito y en verde comprobando 0% de fuga de datos entre usuarios, (3) no viola Art. III.3, IV.4 y VII.4)

**Checkpoint**: Historias de usuario 1, 2 y 3 operan integradas con aislamiento multiusuario estricto.

---

## Phase 6: User Story 4 - Interacción Mediante Herramientas MCP con Paridad y Seguridad (Priority: P2)

**Goal**: Exponer herramientas MCP (`registrar_gasto`, `listar_gastos`) montadas en FastAPI sobre streamable-http con autenticación JWT y fallback documentado en stdio.  
**Independent Test**: Conectar cliente MCP streamable-http con JWT a `/mcp/`, ejecutar tools y verificar reflejo de los datos en REST.

- [X] T026 [P] [US4] Implementar verificador de tokens Bearer `JWTTokenVerifier` en `app/mcp/auth.py` con test en `tests/test_mcp_tools.py` (DoD: (1) código escrito en `app/mcp/auth.py` validando token JWT y claim `sub` contra `app.security`, (2) test correspondiente `test_jwt_token_verifier_valido_e_invalido` en `tests/test_mcp_tools.py` escrito y en verde, (3) no viola Art. VI.4 y IV.2)
- [X] T027 [P] [US4] Configurar instancia del servidor FastMCP con autenticación en `app/mcp/server.py` con test en `tests/test_mcp_tools.py` (DoD: (1) código escrito en `app/mcp/server.py` con `FastMCP("gastos-mcp")`, `streamable_http_path="/"` y `AuthSettings`, (2) test correspondiente `test_mcp_server_initialization` en `tests/test_mcp_tools.py` escrito y en verde, (3) no viola Art. VI.4)
- [X] T028 [US4] Implementar herramientas MCP `registrar_gasto` y `listar_gastos` en `app/mcp/tools/gastos.py` reutilizando `services/gastos.py` con tests automatizados en `tests/test_mcp_tools.py` (DoD: (1) código escrito en `app/mcp/tools/gastos.py` delegando exclusivamente a `services/gastos.py`, devolviendo diccionarios de error estructurados ante fallos de dominio y resolviendo identidad desde token verificado o fallback documentado a demo en stdio, (2) tests correspondientes `test_mcp_registrar_gasto_tool`, `test_mcp_listar_gastos_tool` y `test_mcp_error_limite_excedido_tool` en `tests/test_mcp_tools.py` escritos y en verde, (3) no viola Art. VI.1, VI.2, VI.3, VI.4 y VII.6)
- [X] T029 [US4] Montar subaplicación streamable-http de MCP en `app/main.py` con gestión de lifespan (`session_manager.run()`) con test en `tests/test_mcp_tools.py` (DoD: (1) código escrito en `app/main.py` montando el servidor MCP en `/mcp` administrando su ciclo de vida, (2) test correspondiente `test_mcp_streamable_http_endpoint_mounted` en `tests/test_mcp_tools.py` escrito y en verde, (3) no viola Art. VI.4 y VII.5)
- [X] T030 [P] [US4] Crear configuración de cliente MCP para VS Code y GitHub Copilot en `.vscode/mcp.json` (DoD: (1) archivo `.vscode/mcp.json` escrito con configuración dual streamable-http (puerto 8000 con prompt `jwt_token`) y stdio, (2) validación de esquema JSON y parámetros de conexión en verde, (3) no viola Art. VI.4)

**Checkpoint**: Todas las historias de usuario están implementadas con contratos y paridad funcional.

---

## Phase 7: Polish, Migraciones & Coverage Verification

**Purpose**: Migraciones de base de datos, validación en PostgreSQL y verificación final obligatoria de umbrales constitucionales.

- [X] T031 [P] Generar y aplicar migración inicial de Alembic en `alembic/versions/` para tablas `usuarios` y `gastos` con test en `tests/test_database.py` (DoD: (1) script de migración escrito con creación de tablas e índices, (2) test correspondiente `test_migracion_alembic_aplica_exitosamente` en `tests/test_database.py` escrito y en verde sobre `gastos.db`, (3) no viola Art. III.1)
- [X] T032 [P] Crear archivo `docker-compose.yml` para validación de base de datos PostgreSQL y verificar portabilidad en `tests/test_database_postgres.py` (DoD: (1) configuración escrita en `docker-compose.yml` con servicio Postgres en puerto 5433 y credenciales de práctica, (2) test condicional `test_postgres_portabilidad` en `tests/test_database_postgres.py` en verde, (3) no viola Art. III.2)
- [X] T033 Configurar fixture `client` con `scope="module"` en `tests/test_api_gastos.py` para evitar conflictos de reentrada del gestor de sesiones de `FastMCP` (DoD: (1) código de fixture ajustado en `tests/test_api_gastos.py` con `scope="module"` y limpieza de dependencias al finalizar, (2) suite de `tests/test_api_gastos.py` ejecutándose en verde sin fallos de lifespan, (3) no viola Art. VII.5)
- [X] T034 Correr `pytest --cov=app --cov-report=term-missing` y confirmar que se cumple el umbral de cobertura del Artículo VII.3 (>=90% en `services/` y >=80% global en `app/`) (DoD: (1) ejecución del reporte de cobertura sin fallos técnicos, (2) suite completa en verde confirmando >=90% de cobertura en `app/services/` y >=80% global en `app/` con los 5 casos de error explícitos cubiertos, (3) no viola ningún artículo de la constitución, certificando calidad de entrega)

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: Puede comenzar de inmediato.
- **Foundational (Phase 2)**: Depende de Phase 1 completada — BLOQUEA todas las historias de usuario.
- **User Story 1 (Phase 3)**: Depende de Phase 2. Establece persistencia de usuarios y autenticación.
- **User Story 2 (Phase 4)**: Depende de US1 (requiere usuario y seguridad).
- **User Story 3 (Phase 5)**: Depende de US2 (requiere entidad gasto y lógica de negocio).
- **User Story 4 (Phase 6)**: Depende de US2 y US3 (las herramientas MCP envuelven servicios existentes).
- **Polish & Coverage (Phase 7)**: Depende de todas las historias de usuario completadas.

---

## Parallel Execution Opportunities

- `T002`, `T003`, `T004` (Variables de entorno, config centralizada y logging) pueden ejecutarse en paralelo.
- `T006`, `T007` (Seguridad y configuración inicial de Alembic) pueden ejecutarse en paralelo tras T005.
- `T010`, `T011` (Modelos y schemas de Usuario) pueden ejecutarse en paralelo.
- `T015`, `T016`, `T017` (Modelos, schemas de Gasto y validador de categorías) pueden ejecutarse en paralelo.
- `T026`, `T027`, `T030` (MCP auth, MCP server config y `.vscode/mcp.json`) pueden ejecutarse en paralelo.
- `T031`, `T032` (Migración de Alembic y Docker Compose para Postgres) pueden ejecutarse en paralelo.

---

## Coverage Verification Checklist (Art. VII.3)

Mapeo de los 5 casos de error explícitos exigidos por `spec.md` y `constitution.md`:

- [X] 1. **Monto negativo o cero**: Cubierto en `T019` con `tests/test_gastos.py::test_registrar_gasto_monto_invalido_lanza_error` en verde.
- [X] 2. **Categoría no permitida (`CategoriaInvalidaError`)**: Cubierto en `T019` con `tests/test_gastos.py::test_registrar_gasto_categoria_invalida_lanza_error` en verde.
- [X] 3. **Límite mensual acumulado de 500.0 (`LimiteExcedidoError`)**: Cubierto en `T019` con `tests/test_gastos.py::test_registrar_gasto_excede_limite_categoria_lanza_error` y en `T021` con `tests/test_integracion_gastos.py::test_limite_por_categoria_integracion` en verde.
- [X] 4. **Solicitudes sin token JWT responden 401**: Cubierto en `T020` con `tests/test_api_gastos.py::test_crear_gasto_sin_token_devuelve_401` y en `T024` con `tests/test_api_gastos.py::test_listar_gastos_sin_token_devuelve_401` en verde.
- [X] 5. **Intento de listar gastos con `usuario_id` ajeno ignorado**: Cubierto en `T024` con `tests/test_api_gastos.py::test_listar_gastos_usuario_id_ajeno_ignorado` y en `T025` con `tests/test_integracion_gastos.py::test_aislamiento_entre_usuarios_integracion` en verde.
- [X] **Umbral en servicios**: Cobertura de líneas en `app/services/` $\ge 90\%$ (Alcanzado: 100%).
- [X] **Umbral global**: Cobertura de líneas global en `app/` $\ge 80\%$ (Alcanzado: 97%).

