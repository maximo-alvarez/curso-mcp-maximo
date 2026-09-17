# Phase 0 Research: Control de Gastos Personales

**Feature**: `001-control-de-gastos`  
**Date**: 2026-09-16  

## Technical Decisions & Rationale

### 1. Framework Web y Servidor ASGI
- **Decisión**: FastAPI con `uvicorn[standard]`.
- **Razón**: Provee soporte nativo de tipos con Pydantic, generación automática de OpenAPI (`/docs`), inyección de dependencias (`Depends`) y compatibilidad ASGI para montar servidores MCP sobre el mismo proceso.
- **Alternativas descartadas**:
  - Flask: Requiere plugins de terceros para validación Pydantic y OpenAPI; mayor complejidad para integración ASGI nativa con MCP streamable-http.

### 2. ORM y Control de Migraciones
- **Decisión**: SQLAlchemy 2.0 (declarative base) + Alembic.
- **Razón**: Cumple el Artículo III. Permite abstraer consultas SQL, aislar datos mediante claves foráneas (`usuario_id`) y soportar dualidad SQLite (desarrollo/tests) y PostgreSQL (producción) sin modificar código de servicios ni routers mediante `connect_args` condicional.
- **Alternativas descartadas**:
  - Raw SQL (`sqlite3` / `psycopg` directo): Vulnerable a inyecciones SQL y carece de portabilidad entre motores.
  - SQLModel: Excelente para CRUDs simples, pero SQLAlchemy puro ofrece mayor control para transacciones y migraciones complejas requeridas por el contrato de compatibilidad.

### 3. Autenticación y Emisión de Tokens
- **Decisión**: `pyjwt` con algoritmo simétrico `HS256`.
- **Razón**: Cumple el Artículo IV.2. Librería activamente mantenida, ligera y estándar.
- **Alternativas descartadas**:
  - `python-jose`: Proyecto desatendido y sin mantenimiento activo; desaconsejado en la comunidad moderna de FastAPI.

### 4. Hashing de Contraseñas
- **Decisión**: `passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto")` fijando `bcrypt<4.1`.
- **Razón**: Cumple el Artículo IV.1. Implementa salt automático por hash. La restricción `bcrypt<4.1` es obligatoria debido a un bug conocido de `passlib 1.7.4` que inspecciona `bcrypt.__about__.__version__` (eliminado en versiones 4.1+).
- **Alternativas descartadas**:
  - SHA256 / MD5: Inseguros y desaconsejados para almacenamiento de credenciales.
  - Argon2: Válido, pero bcrypt cumple con los estándares del curso y el contrato de pruebas del proyecto.

### 5. Protocolo MCP y Transporte
- **Decisión**: SDK oficial `mcp[cli]<2` (`mcp 1.x`), utilizando `FastMCP` montado como sub-app ASGI `streamable_http_app()` en FastAPI y transporte `stdio` para CLI/Inspector.
- **Razón**: Cumple el Artículo VI. Permite servir la API REST y los endpoints MCP en el mismo puerto y proceso. Se utiliza `mcp<2` para mantener compatibilidad con `FastMCP` y `mcp.server.fastmcp`. En HTTP se implementa `JWTTokenVerifier(TokenVerifier)` reutilizando el token JWT; en stdio se documenta el uso de usuario demo como fallback justificado.
- **Alternativas descartadas**:
  - Proceso MCP separado en stdio exclusivo: Obliga a duplicar la infraestructura de ejecución y no permite autenticar usuarios reales concurrentes vía red.

### 6. Estrategia de Testing y Cobertura
- **Decisión**: `pytest`, `pytest-cov`, `httpx` (para `TestClient` de FastAPI con lifespan module-scoped).
- **Razón**: Cumple el Artículo VII. Permite ejecutar tests unitarios con `RepositorioFalso` (sin `unittest.mock`), tests de integración contra SQLite en memoria (`sqlite:///:memory:`), y tests de API con `app.dependency_overrides`. Cobertura auditada mediante `pytest --cov=app --cov-report=term-missing`.
