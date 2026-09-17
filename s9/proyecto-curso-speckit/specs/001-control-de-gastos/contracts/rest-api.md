# REST API Contract: Control de Gastos

**Base URL**: `http://127.0.0.1:8000`  
**Security**: Bearer JWT (`Authorization: Bearer <token>`)

---

## 1. Registro de Usuario

`POST /usuarios/`

Crea una nueva cuenta de usuario en el sistema.

- **Headers**: `Content-Type: application/json`
- **Request Body** (`UsuarioCreate`):
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword123"
  }
  ```
- **Responses**:
  - `201 Created` (`UsuarioResponse`):
    ```json
    {
      "id": 1,
      "email": "user@example.com"
    }
    ```
  - `400 Bad Request`: Email ya registrado (`{"detail": "El email user@example.com ya está registrado"}`).
  - `422 Unprocessable Entity`: Formato de email inválido o cuerpo incompleto.

---

## 2. Autenticación (Login)

`POST /usuarios/token`

Autentica al usuario mediante OAuth2 Password Flow y emite un JWT.

- **Headers**: `Content-Type: application/x-www-form-urlencoded`
- **Request Body** (`OAuth2PasswordRequestForm`):
  - `username`: `user@example.com`
  - `password`: `securepassword123`
- **Responses**:
  - `200 OK`:
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
      "token_type": "bearer"
    }
    ```
  - `401 Unauthorized`: Credenciales inválidas (`{"detail": "Email o contraseña incorrectos"}`).
  - `422 Unprocessable Entity`: Campos requeridos faltantes.

---

## 3. Crear Gasto

`POST /gastos/`

Registra un nuevo gasto para el usuario autenticado.

- **Headers**:
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **Request Body** (`GastoCreate`):
  ```json
  {
    "descripcion": "Almuerzo de trabajo",
    "monto": 15.50,
    "categoria": "comida"
  }
  ```
- **Responses**:
  - `201 Created` (`GastoResponse`):
    ```json
    {
      "id": 1,
      "descripcion": "Almuerzo de trabajo",
      "monto": 15.50,
      "categoria": "comida"
    }
    ```
  - `400 Bad Request`:
    - Monto $\le 0$ o descripción vacía.
    - Categoría inválida: `{"detail": "'inventada' no es una categoría válida"}`.
    - Límite excedido: `{"detail": "Este gasto supera el límite de 500.0 para la categoría 'comida'"}`.
  - `401 Unauthorized`: Token ausente, inválido o expirado.
  - `422 Unprocessable Entity`: Tipos de datos inválidos.

---

## 4. Listar Gastos

`GET /gastos/`

Lista los gastos pertenecientes exclusivamente al usuario autenticado.

- **Headers**: `Authorization: Bearer <token>`
- **Query Parameters**:
  - `skip` (opcional, int, default 0, $\ge 0$)
  - `limit` (opcional, int, default 20, $> 0$)
- **Responses**:
  - `200 OK` (`list[GastoResponse]`):
    ```json
    [
      {
        "id": 1,
        "descripcion": "Almuerzo de trabajo",
        "monto": 15.50,
        "categoria": "comida"
      }
    ]
    ```
  - `401 Unauthorized`: Token ausente o inválido.
  - `422 Unprocessable Entity`: Valores de `skip` o `limit` negativos o no enteros.
