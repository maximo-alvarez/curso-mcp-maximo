# Implementation Plan: Control de Gastos Personales

**Branch**: `001-control-de-gastos` | **Date**: 2026-09-16 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-control-de-gastos/spec.md`

## Summary

Implementación del sistema backend de control de gastos personales basado en arquitectura limpia en capas (`routers/`, `services/`, `repositories/`, `utils/`, `mcp/tools/`). Integra autenticación OAuth2 con tokens JWT (HS256), persistencia ORM con SQLAlchemy y migraciones con Alembic, servidor MCP con transporte `streamable-http` montado sobre la misma aplicación FastAPI, y suite completa de pruebas unitarias, de integración y de API con verificación de cobertura ($\ge 90\%$ en `services/` y $\ge 80\%$ global).

## Technical Context

- **Language/Version**: Python 3.12
- **Primary Dependencies**: FastAPI 0.141+, uvicorn[standard], SQLAlchemy 2.0+, Alembic, pyjwt, passlib[bcrypt], bcrypt<4.1, pydantic-settings, email-validator, python-multipart, mcp[cli]<2
- **Storage**: SQLite 3 (`sqlite:///./gastos.db`) para desarrollo local y tests en memoria (`sqlite:///:memory:`), con configuración desacoplada compatible con PostgreSQL (`psycopg[binary]`)
- **Testing**: pytest, pytest-cov, httpx (para `TestClient`)
- **Target Platform**: macOS / Linux / Docker container
- **Project Type**: Web service ASGI dual (REST API + MCP Streamable-HTTP Server)
- **Performance Goals**: Latencia de respuesta < 100ms para registro y listado de gastos en condiciones de carga normales
- **Constraints**:
  - Sin `unittest.mock` en la capa de servicios (DIP con repositorios falsos).
  - Cobertura $\ge 90\%$ en `services/` y $\ge 80\%$ global en el backend.
  - Aislamiento estricto de usuario (sin conceptos de administradores ni elevación de privilegios).
- **Scale/Scope**: 2 entidades de datos (`Usuario`, `Gasto`), 4 endpoints REST, 2 herramientas MCP, 1 suite de 8+ tests automatizados.

## Constitution Check

*GATE: Evaluado y superado antes de pasar a la fase de tareas.*

| Artículo | Regla Constitucional | Estado en el Plan | Justificación / Mecanismo Técnico |
|---|---|---|---|
| **I. Arquitectura en capas** | Flujo unidireccional y separación estricta de responsabilidades | **PASS** | Paquetes independientes en `app/`. `routers/` solo traducen HTTP; `services/` no importan SQLAlchemy; `repositories/` solo persisten; `mcp/tools/` llaman exclusivamente a `services/`. |
| **II. SOLID aplicado** | SRP, OCP y DIP con inyección por parámetro por defecto | **PASS** | `_validar_gasto` separada de `registrar_gasto`. Parámetro `repo=gastos_repository` en services permite inyectar `RepositorioFalso` sin mocks. |
| **III. Persistencia** | ORM, migraciones y FK de usuario obligatoria | **PASS** | SQLAlchemy 2.0 + Alembic. `connect_args` condicional en `database.py`. Clave foránea `usuario_id` indexada en modelo `Gasto`. |
| **IV. Seguridad** | Hashing bcrypt, JWT HS256, secretos en `.env`, auth estricta | **PASS** | `passlib` con `bcrypt<4.1`. `ACCESS_TOKEN_EXPIRE_MINUTES=30`. Extracción obligatoria de `usuario_id` del token JWT (`get_current_user`). Manejo de 500 genérico sin fugar stack trace. |
| **V. Diseño REST** | Códigos estándar, paginación y schemas separados | **PASS** | Códigos 201/200/400/401/422. Paginación con `skip` y `limit`. Schemas separados (`GastoCreate` vs `GastoResponse`). |
| **VI. MCP** | Reutilización de services, paridad e identidad segura | **PASS** | Herramientas `registrar_gasto` y `listar_gastos` reutilizan `services/gastos.py`. `streamable_http_path="/"` montado en `/mcp/` con autenticación `JWTTokenVerifier`. Fallback a usuario demo únicamente en `stdio`. |
| **VII. Testing** | Pirámide de pruebas, 100% casos de error y cobertura alta | **PASS** | 4 tests unitarios (con `RepositorioFalso`) + 2 integración (SQLite) + 2 API (`dependency_overrides`). Se agregan tests para los 5 casos de error explícitos. Auditoría con `pytest-cov`. |
| **VIII. Compatibilidad** | Contrato inmutable con tests de Sesiones 6-8 | **PASS** | Firmas posicionales exactas y nombres de excepciones preservados en `services/`, `repositories/` y `dependencies`. |

## Project Structure

### Documentation (this feature)

```text
specs/001-control-de-gastos/
├── spec.md              # Especificación funcional y reglas de negocio
├── plan.md              # Plan de implementación y trazabilidad técnica (este archivo)
├── research.md          # Investigación técnica y justificación de stack (Fase 0)
├── data-model.md        # Definición de entidades, restricciones y diagrama ER (Fase 1)
├── quickstart.md        # Guía paso a paso de ejecución y verificación (Fase 1)
├── contracts/           # Contratos de interfaz REST y MCP (Fase 1)
│   ├── rest-api.md
│   └── mcp-tools.md
├── checklists/
│   └── requirements.md  # Validación de calidad de la especificación
└── tasks.md             # Tareas atómicas con definition of done (Fase 2 - generado por /speckit-tasks)
```

### Source Code (repository root)

```text
app/
├── __init__.py
├── main.py                  # Aplicación FastAPI, lifespan de MCP, middleware y handlers de error
├── config.py                # Pydantic Settings leyendo .env (secretos y config MCP)
├── database.py              # Motor SQLAlchemy, SessionLocal y get_db()
├── security.py              # Hashing bcrypt y generación/decodificación de JWT
├── dependencies.py          # get_current_user (OAuth2) y get_gastos_repo (DI)
├── logging_config.py        # Configuración de formato y nivel de logs
├── models/
│   ├── __init__.py
│   ├── usuario.py           # Modelo SQLAlchemy Usuario
│   └── gasto.py             # Modelo SQLAlchemy Gasto con FK usuario_id
├── schemas/
│   ├── __init__.py
│   ├── usuario.py           # UsuarioCreate, UsuarioResponse
│   └── gasto.py             # GastoCreate, GastoResponse
├── repositories/
│   ├── __init__.py
│   ├── gastos.py            # Operaciones de persistencia SQLAlchemy para gastos
│   └── usuarios.py          # Operaciones de persistencia SQLAlchemy para usuarios
├── services/
│   ├── __init__.py
│   ├── gastos.py            # Lógica y validaciones de negocio de gastos (DIP)
│   └── usuarios.py          # Registro y autenticación de usuarios
├── routers/
│   ├── __init__.py
│   ├── usuarios.py          # Endpoints POST /usuarios/ y POST /usuarios/token
│   └── gastos.py            # Endpoints POST /gastos/ y GET /gastos/ (protegidos)
├── utils/
│   ├── __init__.py
│   ├── validadores.py       # Funciones puras (categoría válida, etc.)
│   └── formato.py           # Funciones puras de formateo monetario
└── mcp/
    ├── __init__.py
    ├── server.py            # Instancia FastMCP con streamable_http y auth
    ├── auth.py              # JWTTokenVerifier reutilizando app.security
    └── tools/
        ├── __init__.py
        └── gastos.py        # Tools registrar_gasto y listar_gastos delegando a services
alembic/
├── env.py                   # Configuración de migraciones leyendo settings y Base.metadata
├── script.py.mako
└── versions/                # Scripts de migración autogenerados
alembic.ini
tests/
├── __init__.py
├── test_gastos.py           # Pruebas unitarias con RepositorioFalso (S6/S7)
├── test_integracion_gastos.py # Pruebas de integración con base de datos real
└── test_api_gastos.py       # Pruebas de endpoints FastAPI con dependency_overrides y lifespan module-scoped
.env.example
.env
pyproject.toml
```

## Trazabilidad Plan → Constitución

- **Separación en capas (Artículo I)**: Se implementa mediante paquetes Python separados bajo `app/`, sin importaciones inversas ni dependencias cíclicas.
- **Inversión de Dependencias (Artículo II.3)**: `services/gastos.py` recibe `repo=gastos_repository` como parámetro por defecto. Los tests unitarios sustituyen este argumento por `RepositorioFalso`, asegurando cero dependencias de `unittest.mock`.
- **Persistencia desacoplada (Artículo III)**: `database.py` calcula dinámicamente `connect_args` según el prefijo del driver de base de datos (`sqlite` vs `postgresql`), permitiendo ejecutar tanto en SQLite como en Docker PostgreSQL sin tocar ninguna otra capa.
- **Seguridad integral (Artículo IV)**: 
  - `passlib[bcrypt]` fijado en `bcrypt<4.1` evita incompatibilidades en runtime.
  - `pyjwt` gestiona tokens `HS256` con expiración.
  - `get_current_user` inyecta la identidad en los endpoints; ningún router acepta `usuario_id` por URL o body.
  - El middleware global de FastAPI atrapa `Exception` y responde 500 genérico.
- **Protocolo MCP con Paridad y Seguridad (Artículo VI)**:
  - `mcp_server.streamable_http_app()` se monta como sub-app ASGI en `app.mount("/mcp", mcp_app)`.
  - El lifespan de FastAPI gestiona `mcp_server.session_manager.run()`.
  - `JWTTokenVerifier` valida el Bearer token JWT emitido por la API REST y garantiza que los gastos creados por MCP queden asociados al usuario real.
- **Testing y Cobertura (Artículo VII)**:
  - Pirámide de pruebas completa implementada con `pytest`.
  - El fixture `client` de `test_api_gastos.py` utiliza `scope="module"` para evitar que múltiples tests reabran el lifespan de sesión de MCP y provoquen un `RuntimeError`.
  - Se añade auditoría de cobertura con `pytest-cov` verificando $\ge 90\%$ en `services/` y $\ge 80\%$ global.

## Complexity Tracking

| Violación | Por qué es necesaria | Alternativa más simple rechazada porque |
|---|---|---|
| *Ninguna* | El diseño respeta al 100% todos los artículos de la constitución sin añadir abstracciones innecesarias. | No aplica. |
