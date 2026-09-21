# Phase 1: Quickstart & Validation Guide

**Feature**: `001-reserva-espacio-compartido`  
**Date**: 2026-09-20  

---

## 1. Requisitos Previos y Entorno

- **Python**: 3.12+ gestionado con `uv`.
- **Variables de Entorno**: Archivo `.env` en la raíz del proyecto (creado a partir de `.env.example`):
  ```bash
  cp .env.example .env
  ```
  Contenido mínimo requerido de `.env`:
  ```ini
  SECRET_KEY=clave_secreta_super_segura_de_32_bytes_minimo
  DATABASE_URL=sqlite:///./reservas.db
  ACCESS_TOKEN_EXPIRE_MINUTES=60
  MCP_DEMO_USER_EMAIL=demo@reservas.local
  ```

---

## 2. Instalación de Dependencias

Ejecutar en la raíz del proyecto:
```bash
uv sync
```

---

## 3. Ejecución de Migraciones de Base de Datos

Inicializar el esquema de tablas (`usuarios`, `reservas`):
```bash
uv run alembic upgrade head
```

---

## 4. Ejecución de la Suite de Pruebas

Correr la pirámide de pruebas unitarias, de integración y de API verificando cobertura:
```bash
uv run pytest -v --cov=app --cov-report=term-missing
```

### Verificación de Calidad
- 100% de los 6 casos de error explícitos cubiertos.
- Cobertura de líneas en `app/services/` $\ge 90\%$.
- Cobertura global $\ge 80\%$.

---

## 5. Arranque del Servidor Local (REST + MCP)

Iniciar FastAPI con Uvicorn:
```bash
uv run uvicorn app.main:app --reload --port 8000
```
- **Documentación Swagger / OpenAPI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Endpoint MCP Streamable HTTP**: [http://localhost:8000/mcp/](http://localhost:8000/mcp/)

---

## 6. Flujo de Validación Manual Paso a Paso (cURL)

### Paso A: Registrar Usuario
```bash
curl -X POST http://localhost:8000/usuarios/ \
  -H "Content-Type: application/json" \
  -d '{"email": "juan@example.com", "password": "Password123!"}'
```
*Respuesta esperada: `201 Created` con `{"id": 1, "email": "juan@example.com"}`.*

### Paso B: Obtener Token JWT
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/usuarios/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=juan@example.com&password=Password123!" | jq -r .access_token)
echo "Token: $TOKEN"
```

### Paso C: Crear Reserva Válida
```bash
curl -X POST http://localhost:8000/reservas/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fecha": "2026-10-20", "hora_inicio": "09:00", "hora_fin": "11:00"}'
```
*Respuesta esperada: `201 Created` con `estado: "ACTIVA"`.*

### Paso D: Intentar Reserva Solapada (Debe Fallar)
```bash
curl -i -X POST http://localhost:8000/reservas/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fecha": "2026-10-20", "hora_inicio": "10:00", "hora_fin": "12:00"}'
```
*Respuesta esperada: `400 Bad Request` con `{"detail": "El horario solicitado se solapa con una reserva existente"}`.*

### Paso E: Cancelar Reserva (Soft Delete)
```bash
curl -i -X DELETE http://localhost:8000/reservas/1 \
  -H "Authorization: Bearer $TOKEN"
```
*Respuesta esperada: `204 No Content`.*

### Paso F: Reintentar Reserva sobre Horario Cancelado (Debe Tener Éxito)
```bash
curl -X POST http://localhost:8000/reservas/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fecha": "2026-10-20", "hora_inicio": "10:00", "hora_fin": "12:00"}'
```
*Respuesta esperada: `201 Created`, validando que el horario quedó liberado.*
