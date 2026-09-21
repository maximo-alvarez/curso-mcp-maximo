# Implementation Plan: Sistema de Reservas de un Espacio Compartido

**Branch**: `001-reserva-espacio-compartido` | **Date**: 2026-09-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-reserva-espacio-compartido/spec.md`

## Summary

Implementación de un sistema backend para la gestión de reservas de un espacio compartido basado en arquitectura limpia en capas (`routers/`, `services/`, `repositories/`, `utils/`, `mcp/tools/`). Integra registro y autenticación OAuth2 con JWT (`HS256`), persistencia con SQLAlchemy 2.0 y migraciones con Alembic, lógica de solapamiento estricto sobre reservas activas con soft delete (`ACTIVA`/`CANCELADA`), servidor MCP FastMCP con transporte `streamable-http` montado sobre FastAPI, y suite completa de pruebas unitarias (con `RepositorioFalso`), de integración (SQLite) y de API con verificación de cobertura ($\ge 90\%$ en `services/` y $\ge 80\%$ global).

## Technical Context

- **Language/Version**: Python 3.12+
- **Primary Dependencies**: FastAPI 0.115+, uvicorn[standard], SQLAlchemy 2.0+, Alembic, pyjwt, passlib[bcrypt], bcrypt<4.1, pydantic-settings, email-validator, python-multipart, mcp[cli]<2
- **Storage**: SQLite 3 (`sqlite:///./reservas.db`) para desarrollo local y tests en memoria (`sqlite:///:memory:`), con configuración desacoplada compatible con PostgreSQL (`psycopg[binary]`)
- **Testing**: pytest, pytest-cov, httpx (para `TestClient`)
- **Target Platform**: macOS / Linux / Docker container
- **Project Type**: Web service ASGI dual (REST API + MCP Streamable-HTTP Server)
- **Performance Goals**: Latencia de respuesta < 100ms para creación, consulta y cancelación de reservas en condiciones normales
- **Constraints**:
  - Sin `unittest.mock` en la capa de servicios (DIP con `RepositorioFalso`).
  - Cobertura $\ge 90\%$ en `services/` y $\ge 80\%$ global en el backend.
  - Aislamiento estricto de usuario (un usuario solo consulta y cancela sus propias reservas).
  - Soft delete para cancelaciones: transiciona a `CANCELADA` y libera el intervalo horario.
- **Scale/Scope**: 2 entidades de datos (`Usuario`, `Reserva`), 5 endpoints REST, 3 herramientas MCP, 6 casos de error explícitos con tests automatizados.

## Constitution Check

*GATE: Evaluado y superado antes de pasar a la fase de tareas.*

| Artículo | Regla Constitucional | Estado en el Plan | Justificación / Mecanismo Técnico |
|---|---|---|---|
| **I. Arquitectura en capas** | Flujo unidireccional y separación estricta de responsabilidades | **PASS** | Paquetes independientes en `app/`. `routers/` solo traducen HTTP; `services/` no importan SQLAlchemy; `repositories/` son los únicos que leen/escriben DB; `mcp/tools/` llaman exclusivamente a `services/`. |
| **II. SOLID aplicado** | SRP, OCP y DIP con inyección por parámetro con default | **PASS** | `_validar_horario` y `_validar_fecha` separadas de `crear_reserva`. Parámetro `repo=reservas_repository` en `services/` permite inyectar `RepositorioFalso` sin mocks. |
| **III. Persistencia** | ORM, migraciones y FK de usuario obligatoria | **PASS** | SQLAlchemy 2.0 + Alembic. `connect_args` condicional en `database.py`. Clave foránea `usuario_id` obligatoria e indexada en modelo `Reserva`. |
| **IV. Seguridad** | Hashing bcrypt, JWT HS256, secretos en `.env`, auth estricta | **PASS** | `passlib` fijado con `bcrypt<4.1`. `ACCESS_TOKEN_EXPIRE_MINUTES=60`. Extracción obligatoria de `usuario_id` del token JWT (`get_current_user`). Middleware global con error 500 genérico sin filtrar stack traces. |
| **V. Diseño REST** | Códigos estándar, paginación y schemas separados | **PASS** | Códigos 201/200/204/400/401/403/404/422. Paginación con `skip` y `limit`. Schemas separados (`ReservaCreate` vs `ReservaOut`). |
| **VI. MCP** | Reutilización de services, paridad y confirmación destructiva | **PASS** | Herramientas `crear_reserva`, `listar_reservas` y `cancelar_reserva` reutilizan `services/reservas.py`. Montaje ASGI en `/mcp`. `cancelar_reserva` exige confirmación explícita previa (`confirmacion=True`). |
| **VII. Testing** | Pirámide de pruebas, 100% casos de error y cobertura alta | **PASS** | Pruebas unitarias (con `RepositorioFalso`) + integración (SQLite) + API (`dependency_overrides`). Tests dedicados para los 6 casos de error explícitos. Auditoría con `pytest-cov`. |
| **VIII. Repositorios y contratos** | Repositorios con funciones sueltas y firmas inmutables | **PASS** | `repositories/reservas.py` y `repositories/usuarios.py` contienen funciones libres (no clases) y retornan estructuras de datos simples (`dict` o modelo de dominio), sin exponer `Session`. |

## Project Structure

### Documentation (this feature)

```text
specs/001-reserva-espacio-compartido/
├── spec.md              # Especificación funcional y reglas de negocio
├── plan.md              # Plan de implementación y trazabilidad técnica (este archivo)
├── research.md          # Investigación técnica y justificación de decisiones (Fase 0)
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
├── dependencies.py          # get_current_user (OAuth2) y get_reservas_repo (DI)
├── logging_config.py        # Configuración de formato y nivel de logs
├── models/
│   ├── __init__.py
│   ├── usuario.py           # Modelo SQLAlchemy Usuario
│   └── reserva.py           # Modelo SQLAlchemy Reserva con FK usuario_id y estado
├── schemas/
│   ├── __init__.py
│   ├── usuario.py           # UsuarioCreate, UsuarioOut, Token
│   └── reserva.py           # ReservaCreate, ReservaOut
├── repositories/
│   ├── __init__.py
│   ├── reservas.py          # Operaciones de persistencia SQLAlchemy para reservas (funciones sueltas)
│   └── usuarios.py          # Operaciones de persistencia SQLAlchemy para usuarios (funciones sueltas)
├── services/
│   ├── __init__.py
│   ├── reservas.py          # Lógica y validaciones de negocio de reservas (DIP, soft delete)
│   └── usuarios.py          # Registro y autenticación de usuarios
├── routers/
│   ├── __init__.py
│   ├── usuarios.py          # Endpoints POST /usuarios/ y POST /usuarios/token
│   └── reservas.py          # Endpoints POST /reservas/, GET /reservas/ y DELETE /reservas/{id}
├── utils/
│   ├── __init__.py
│   └── validadores.py       # Funciones puras de validación de formato de fechas y horas
└── mcp/
    ├── __init__.py
    ├── server.py            # Instancia FastMCP con streamable_http y auth
    ├── auth.py              # JWTTokenVerifier reutilizando app.security
    └── tools/
        ├── __init__.py
        └── reservas.py      # Tools crear_reserva, listar_reservas y cancelar_reserva
alembic/
├── env.py                   # Configuración de migraciones leyendo settings y Base.metadata
├── script.py.mako
└── versions/                # Scripts de migración autogenerados
alembic.ini
tests/
├── __init__.py
├── test_reservas.py         # Pruebas unitarias con RepositorioFalso (sin mocks)
├── test_integracion_reservas.py # Pruebas de integración con base de datos real
└── test_api_reservas.py     # Pruebas de endpoints FastAPI con dependency_overrides
.env.example
.env
pyproject.toml
```

## Trazabilidad Plan → Constitución

- **Separación en capas (Artículo I)**: Paquetes Python independientes bajo `app/`, asegurando que `routers/` solo deleguen a `services/`, `services/` contenga las reglas de negocio y `repositories/` aísle la persistencia.
- **Inversión de Dependencias (Artículo II.3)**: `services/reservas.py` recibe `repo=reservas_repository` como parámetro por defecto. Los tests unitarios inyectan `RepositorioFalso`, garantizando 0 dependencias de `unittest.mock`.
- **Persistencia desacoplada (Artículo III)**: `database.py` usa `connect_args` condicional solo para SQLite (`check_same_thread=False`), permitiendo conectar a PostgreSQL sin tocar la lógica de negocio. Clave foránea `usuario_id` requerida en `Reserva`.
- **Seguridad integral (Artículo IV)**: `passlib[bcrypt]` con `bcrypt<4.1`, tokens JWT firmados con `HS256`, `get_current_user` inyectando `usuario_id` sin permitir su paso por URL o body, y middleware de captura genérica de excepciones retornando 500 sin trazas.
- **Diseño de Endpoints REST (Artículo V)**: Códigos de respuesta HTTP estrictos (201 creación, 200 listado, 204 eliminación lógica, 400 reglas de negocio, 401 sin auth, 403 no es dueño, 404 inexistente). Schemas `ReservaCreate` y `ReservaOut` completamente disociados del modelo ORM.
- **Protocolo MCP con Paridad y Seguridad (Artículo VI)**:
  - `mcp_server.streamable_http_app()` montado en `/mcp` con gestión de lifespan en FastAPI.
  - `JWTTokenVerifier` resuelve la identidad del usuario real a partir del Bearer token.
  - La tool destructiva `cancelar_reserva` implementa confirmación obligatoria del servidor (`confirmacion=True`) antes de ejecutar.
- **Testing y Cobertura (Artículo VII)**: Pirámide completa de pruebas con pytest; verificación de los 6 casos de error explícitos; umbral de cobertura medido con `pytest-cov` ($\ge 90\%$ en `services/`, $\ge 80\%$ global).
- **Repositorios Modulares (Artículo VIII)**: `repositories/reservas.py` implementado con funciones libres que retornan tipos simples (`dict` o modelo de dominio), sin filtrar la `Session` al exterior.

## Complexity Tracking

| Violación | Por qué es necesaria | Alternativa más simple rechazada porque |
|---|---|---|
| *Ninguna* | El diseño respeta al 100% todos los artículos de la constitución sin añadir abstracciones innecesarias. | No aplica. |
