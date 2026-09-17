# MCP Tools Contract: Control de Gastos

**Protocol**: Model Context Protocol (MCP)  
**Transports**: `stdio` (local/demo), `streamable-http` (vía sub-app ASGI montada en `/mcp/`)

---

## 1. Tool: `registrar_gasto`

Registra un nuevo gasto ejecutando las validaciones y reglas de negocio del servicio central.

- **Nombre**: `registrar_gasto`
- **Descripción**: "Registra un nuevo gasto. Usar cuando el usuario mencione una compra o pago que quiere trackear."
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "descripcion": {
        "type": "string",
        "description": "Detalle de la compra o pago"
      },
      "monto": {
        "type": "number",
        "description": "Monto positivo gastado"
      },
      "categoria": {
        "type": "string",
        "description": "Categoría permitida (comida, transporte, entretenimiento, otros)"
      }
    },
    "required": ["descripcion", "monto", "categoria"]
  }
  ```
- **Output Success** (`dict`):
  ```json
  {
    "id": 1,
    "descripcion": "Almuerzo",
    "monto": 12.5,
    "categoria": "comida"
  }
  ```
- **Output Error de Negocio** (`dict`):
  ```json
  {
    "error": "Este gasto supera el límite de 500.0 para la categoría 'comida'"
  }
  ```

---

## 2. Tool: `listar_gastos`

Recupera los gastos del usuario autenticado en la sesión MCP.

- **Nombre**: `listar_gastos`
- **Descripción**: "Lista todos los gastos registrados del usuario. Usar cuando pregunten por sus gastos o quieran un resumen."
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {}
  }
  ```
- **Output Success** (`list[dict]`):
  ```json
  [
    {
      "id": 1,
      "descripcion": "Almuerzo",
      "monto": 12.5,
      "categoria": "comida"
    }
  ]
  ```

---

## 3. Autenticación e Identidad en MCP
- **`streamable-http` (`http://127.0.0.1:8000/mcp/`)**:
  - Requiere header `Authorization: Bearer <token>`.
  - El token es validado por `JWTTokenVerifier(TokenVerifier)`.
  - Si el token falta $\rightarrow$ `401 Unauthorized`.
  - Si el usuario no existe en la base de datos $\rightarrow$ error estructurado (nunca cae a demo).
- **`stdio`**:
  - Opera sobre `mcp_demo_email` configurado en `Settings` (`.env`) como simplificación consciente documentada en código.
