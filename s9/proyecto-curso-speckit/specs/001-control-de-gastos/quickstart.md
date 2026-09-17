# Quickstart Validation Guide: Control de Gastos Personales

**Feature**: `001-control-de-gastos`  
**Date**: 2026-09-16  

Guía de validación end-to-end para comprobar la correcta implementación del sistema.

---

## 1. Requisitos Previos y Entorno

1. Python 3.12+ y `uv` instalados.
2. Copiar variables de entorno:
   ```bash
   cp .env.example .env
   ```
3. Generar `SECRET_KEY` criptográfico y asignarlo en `.env`:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
4. Sincronizar dependencias:
   ```bash
   uv sync
   ```

---

## 2. Base de Datos y Migraciones

Ejecutar las migraciones de Alembic para crear las tablas `usuarios` y `gastos`:
```bash
uv run alembic upgrade head
```
Verificar que se genera el archivo de base de datos `gastos.db`.

---

## 3. Ejecución de la Suite de Pruebas y Cobertura

Correr la pirámide completa de pruebas verificando el umbral de cobertura ($\ge 90\%$ en `services/` y $\ge 80\%$ global):
```bash
uv run pytest -v --cov=app --cov-report=term-missing
```

Criterio de éxito:
- 8/8 tests en verde.
- Ningún error de sesión en `StreamableHTTPSessionManager`.

---

## 4. Validación de la API REST

Iniciar el servidor local:
```bash
uv run uvicorn app.main:app --port 8000 --reload
```

1. **Registrar un nuevo usuario**:
   ```bash
   curl -X POST "http://127.0.0.1:8000/usuarios/" \
     -H "Content-Type: application/json" \
     -d '{"email": "testuser@curso.com", "password": "securepassword123"}'
   ```
   *Respuesta esperada*: `201 Created` con `id` y `email`.

2. **Obtener Token JWT**:
   ```bash
   curl -X POST "http://127.0.0.1:8000/usuarios/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=testuser@curso.com&password=securepassword123"
   ```
   *Respuesta esperada*: `200 OK` con `access_token`.

3. **Registrar un gasto con token**:
   ```bash
   curl -X POST "http://127.0.0.1:8000/gastos/" \
     -H "Authorization: Bearer <TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"descripcion": "Almuerzo", "monto": 25.0, "categoria": "comida"}'
   ```
   *Respuesta esperada*: `201 Created`.

4. **Intentar superar el límite de 500.0**:
   ```bash
   curl -X POST "http://127.0.0.1:8000/gastos/" \
     -H "Authorization: Bearer <TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"descripcion": "Cena de gala", "monto": 500.0, "categoria": "comida"}'
   ```
   *Respuesta esperada*: `400 Bad Request` con mensaje de límite excedido.

5. **Listar gastos**:
   ```bash
   curl -X GET "http://127.0.0.1:8000/gastos/?skip=0&limit=10" \
     -H "Authorization: Bearer <TOKEN>"
   ```
   *Respuesta esperada*: `200 OK` con la lista de gastos del usuario.

---

## 5. Validación de MCP (Streamable-HTTP)

1. Conexión sin token a `/mcp/`:
   ```bash
   curl -i -X POST "http://127.0.0.1:8000/mcp/" \
     -H "Content-Type: application/json" \
     -H "Accept: application/json, text/event-stream" \
     -d '{}'
   ```
   *Respuesta esperada*: `401 Unauthorized` con header `WWW-Authenticate`.

2. Verificación de tools por cliente MCP (usando JWT del paso 4.2):
   - Conexión autorizada, listado de `['registrar_gasto', 'listar_gastos']`.
   - Invocación de `registrar_gasto` y posterior reflejo en `GET /gastos/` por REST.
