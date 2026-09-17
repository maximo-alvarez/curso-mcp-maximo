# Sesión 7 — Práctica: De la arquitectura al código

**Duración de la práctica:** ~146 min (con descanso). Si no alcanza, se cierra al inicio de la Sesión 8 — sin recortar contenido.
**Punto de partida:** el proyecto de la Sesión 6 (arquitectura en capas + repository en memoria + primer test unitario).
**Novedad de hoy:** el repository deja de ser una lista en memoria y pasa a una base de datos real, y el proyecto gana su primer usuario autenticado.

> **Sobre el rol de esta práctica:** esta sigue siendo la práctica guiada sobre "Gastos", no el proyecto evaluado. El checklist de cierre es para tu propia verificación, no para entrega formal.

## El mapa de seguridad (léelo antes de empezar)

Esto es lo que sembramos conceptualmente el lunes — hoy resolvemos varios puntos con código real:

| Ítem                         | Se resuelve hoy                      |
| ---------------------------- | ------------------------------------ |
| Autenticación (OAuth2 + JWT) | ✅                                    |
| Hashing de contraseñas       | ✅                                    |
| Gestión de secretos          | ✅                                    |
| Validación de entrada        | ✅ (Pydantic)                         |
| SQL injection                | ✅ (mitigado por el ORM)              |
| CORS, Rate limiting, HTTPS   | Mención — se cierran en la Sesión 10 |

## Cronograma

| Paso                                                               | Tiempo  | Acumulado                  |
| ------------------------------------------------------------------ | ------- | -------------------------- |
| 1 — Instalar dependencias                                          | 5 min   | 5 min                      |
| 2 — Configuración y secretos (`.env.example` + generar SECRET_KEY) | 8 min   | 13 min                     |
| 3 — Conexión a la base de datos                                    | 5 min   | 18 min                     |
| 4 — Modelos: Usuario y Gasto con FK                                | 10 min  | 28 min                     |
| 5 — Schemas Pydantic                                               | 5 min   | 33 min                     |
| 6 — Alembic: migración inicial                                     | 8 min   | 41 min                     |
| 🔄 Descanso                                                         | 5 min   | 46 min                     |
| 7 — Seguridad: hashing y JWT                                       | 10 min  | 56 min                     |
| 8 — Repository real                                                | 10 min  | 66 min                     |
| 9 — Actualizar `services/` (incluye actualizar `RepositorioFalso`) | 15 min  | 81 min                     |
| 10 — Dependencia de autenticación                                  | 5 min   | 86 min                     |
| 11 — Routers: registro, login, gastos protegidos                   | 15 min  | 101 min                    |
| 12 — Probar todo en `/docs`                                        | 5 min   | 106 min                    |
| 13 — Test de integración                                           | 10 min  | 116 min                    |
| 14 — Logging y manejo de errores                                   | 15 min  | 131 min                    |
| 15 — DI con `Depends` y `dependency_overrides`                     | 15 min  | 146 min                    |
| 16 — Demo: PostgreSQL con Docker (instructor, requiere Docker)     | ~15 min | — (no cuenta al acumulado) |

> 🧑‍🏫 **Nota de tiempo:** esta versión completa corre ~146 min, por encima del bloque de práctica habitual. Si vas corto de tiempo, la opción más limpia es dejar el **Paso 13 en adelante** como cierre al inicio de la Sesión 8 — auth funcionando end-to-end en `/docs` y los tests de la Sesión 6 actualizados y pasando es el contenido que no se debe recortar. El Paso 16 requiere Docker y se corre como demo en vivo, no a mano por cada estudiante.

## Antes de empezar

- [ ] Proyecto de la Sesión 6 funcionando (tests pasando)
- [ ] Python 3.12, `uv` instalado
- [ ] Conexión a internet (para instalar dependencias nuevas)

> 🧑‍🏫 **Si `uv run pytest` (o `uv run uvicorn`, o cualquier `uv run ...`) falla con algo como `exec: '/ruta/vieja/.venv/bin/python': not found`:** no es un error en tu código ni en esta guía. Pasa cuando el proyecto de la Sesión 6 se copió o movió de carpeta después de crear el `.venv` — los scripts dentro de `.venv/bin/` (`pytest`, `uvicorn`, etc.) tienen grabada la ruta absoluta de dónde se creó el entorno, y si la carpeta cambió de lugar, esa ruta ya no existe. Se arregla regenerando el entorno desde la ubicación actual:
> ```bash
> rm -rf .venv
> uv sync
> ```
> Esto no toca ni una línea de código de la práctica — solo reconstruye el `.venv` con las rutas correctas.

---

## Estructura objetivo al final de la práctica

```
proyecto-curso/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── security.py
│   ├── dependencies.py
│   ├── logging_config.py
│   ├── routers/
│   │   ├── usuarios.py
│   │   └── gastos.py
│   ├── mcp/                # sigue vacío, se llena en Sesión 8
│   ├── schemas/
│   │   ├── usuario.py
│   │   └── gasto.py
│   ├── services/
│   │   ├── gastos.py       # se actualiza, no se reescribe
│   │   └── usuarios.py     # nuevo
│   ├── repositories/
│   │   ├── gastos.py       # se reemplaza (memoria -> SQLAlchemy)
│   │   └── usuarios.py     # nuevo
│   ├── models/
│   │   ├── usuario.py
│   │   └── gasto.py
│   └── utils/               # sin cambios, se reutiliza tal cual
├── alembic/
├── alembic.ini
├── tests/
│   ├── test_gastos.py               # de la Sesión 6, se actualiza en el Paso 9
│   ├── test_integracion_gastos.py
│   └── test_api_gastos.py
├── docker-compose.yml
├── .env.example
├── .env
├── .gitignore
├── gastos.db                # generado por Alembic en el Paso 6, no se versiona
├── pyproject.toml
├── uv.lock
└── README.md
```

---

## Paso 1 — Instalar dependencias (5 min)

```bash
uv add fastapi "uvicorn[standard]" sqlalchemy alembic pyjwt "passlib[bcrypt]" pydantic-settings python-multipart email-validator
```

*`email-validator` es necesario porque `EmailStr` de Pydantic (Paso 5) no puede construirse sin él — sin este paquete, el schema falla al importarse, no al usarse.*

> 🧑‍🏫 **Sobre `passlib[bcrypt]`:** la instalación en sí no da problemas (instala `bcrypt` 5.x sin fallar). El problema real aparece **en tiempo de ejecución**, al llamar `pwd_context.hash(...)` — ver la nota específica en el Paso 7.

**Nota sobre `requirements.txt`:** en la Sesión 6 ya se generó y se borró (era temporal, solo para comparar `pip` vs `uv`) — no debería existir en tu proyecto a esta altura. Las dependencias se gestionan con `uv add`, que actualiza `pyproject.toml` y `uv.lock`. Si de verdad necesitas un `requirements.txt` (por ejemplo, para un entorno que solo entienda `pip`), regenéralo así:

```bash
uv export --format requirements-txt > requirements.txt
```

**Checkpoint:** `pyproject.toml` lista las nuevas dependencias.

---

## Paso 2 — Configuración y gestión de secretos (8 min)

Antes de crear el `.env` real, se crea un `.env.example` — es la plantilla que documenta **qué variables necesita el proyecto**, sin exponer ningún valor real. Este archivo sí se sube a Git; el `.env` real, nunca.

**`.env.example`**

```
SECRET_KEY=
DATABASE_URL=sqlite:///./gastos.db
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Generar un SECRET_KEY seguro

No escribas el `SECRET_KEY` a mano ("cambia-esto-por-algo-aleatorio" no es aleatorio de verdad). Genera uno criptográficamente seguro con alguna de estas opciones:

**Opción 1 — terminal (recomendada, no depende de ningún sitio externo):**

```bash
openssl rand -hex 32
```

Si no tienes `openssl` disponible (por ejemplo, en algunas instalaciones de Windows), usa Python, que ya tienen instalado:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Opción 2 — página web, si no tienes terminal a mano:** [randomkeygen.com](https://randomkeygen.com/) genera claves aleatorias del lado del navegador (no las envía a ningún servidor). Cualquiera de las claves largas ("CodeIgniter Encryption Keys" o similar, de 256 bits) sirve para este propósito.

> 🧑‍🏫 **Por qué importa esto:** un `SECRET_KEY` corto o predecible (como `"secreto123"`) puede romperse por fuerza bruta fuera de línea si alguien obtiene un token — con eso podría firmar tokens falsos. La clave debe tener al menos 32 bytes de aleatoriedad real (256 bits), nunca una palabra o frase elegida a mano.

### Crear el `.env` real a partir de la plantilla

```bash
cp .env.example .env
```

Abre `.env` y pega el valor generado en `SECRET_KEY`:

```
SECRET_KEY=<pega aquí el valor que generaste>
DATABASE_URL=sqlite:///./gastos.db
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Confirma que `.env` está en `.gitignore` (debería estarlo desde la Sesión 6) — **`.env.example` sí se commitea, `.env` nunca**.

**`app/config.py`**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str
    database_url: str = "sqlite:///./gastos.db"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
```

**Checkpoint:** `from app.config import settings` no lanza error, y `.env.example` no contiene ningún valor real, solo la lista de variables.

---

## Paso 3 — Conexión a la base de datos (5 min)

**`app/database.py`**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

> 🧑‍🏫 **`connect_args={"check_same_thread": False}` es específico de SQLite** (permite compartir la conexión entre threads, algo que SQLite bloquea por defecto). Si migran a Postgres en el trabajo autónomo, ese argumento se quita — no aplica ahí.

**Checkpoint:** el módulo importa sin errores.

---

## Paso 4 — Modelos SQLAlchemy: Usuario y Gasto con FK (10 min)

**`app/models/usuario.py`**

```python
from sqlalchemy import Column, Integer, String
from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
```

**`app/models/gasto.py`**

```python
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.database import Base


class Gasto(Base):
    __tablename__ = "gastos"

    id = Column(Integer, primary_key=True)
    descripcion = Column(String, nullable=False)
    monto = Column(Float, nullable=False)
    categoria = Column(String, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
```

**Checkpoint:** ambos modelos importan sin errores. Actualiza `app/models/__init__.py` (quita el comentario-marcador de la Sesión 6, ya se llenó).

---

## Paso 5 — Schemas Pydantic (5 min)

**`app/schemas/usuario.py`**

```python
from pydantic import BaseModel, EmailStr


class UsuarioCreate(BaseModel):
    email: EmailStr
    password: str


class UsuarioResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True
```

**`app/schemas/gasto.py`**

```python
from pydantic import BaseModel


class GastoCreate(BaseModel):
    descripcion: str
    monto: float
    categoria: str


class GastoResponse(BaseModel):
    id: int
    descripcion: str
    monto: float
    categoria: str

    class Config:
        from_attributes = True
```

*Nota: `UsuarioResponse` nunca incluye `hashed_password` — el schema de salida decide qué se expone, no el modelo de la base de datos.*

**Checkpoint:** ambos schemas importan sin errores. Actualiza `app/schemas/__init__.py` (quita el comentario-marcador de la Sesión 6, ya se llenó).

---

## Paso 6 — Alembic: migración inicial (8 min)

```bash
uv run alembic init alembic
```

Este comando genera `alembic.ini` con una URL de base de datos de ejemplo (`sqlalchemy.url = driver://user:pass@localhost/dbname`) y `alembic/env.py` con `target_metadata = None` — ninguno de los dos apunta todavía a tu proyecto. **No edites `alembic.ini` a mano**; en vez de eso, resuelve ambas cosas dentro de `env.py`, para que Alembic siempre lea la URL real desde tu `.env` (vía `settings`), no desde un valor fijo en el `.ini`.

Abre `alembic/env.py` y, justo después de la línea `config = context.config`, agrega:

```python
from app.config import settings
from app.database import Base
from app.models import usuario, gasto  # noqa: F401 (necesario para que Alembic los detecte)

config.set_main_option("sqlalchemy.url", settings.database_url)
```

Y reemplaza la línea `target_metadata = None` (más abajo en el mismo archivo) por:

```python
target_metadata = Base.metadata
```

> 🧑‍🏫 **Si `alembic revision --autogenerate` genera una migración vacía o falla con un error de conexión:** revisa dos cosas — (1) que `target_metadata = None` haya quedado reemplazado por `Base.metadata`, y (2) que el `config.set_main_option(...)` esté antes de que Alembic intente conectarse (si quedó después, sigue usando el placeholder del `.ini`). Ambos son necesarios; con solo uno de los dos, el comando falla o no detecta las tablas.

```bash
uv run alembic revision --autogenerate -m "crear tablas usuarios y gastos"
uv run alembic upgrade head
```

**Checkpoint:** existe el archivo `gastos.db` y una carpeta `alembic/versions/` con tu primera migración.

---

## 🔄 DESCANSO (5 min)

---

## Paso 7 — Seguridad: hashing y JWT (10 min)

**`app/security.py`**

```python
from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def crear_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def decodificar_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
```

**Observa mientras corre:** si abres una consola de Python y llamas `hash_password("1234")` dos veces con la misma contraseña, el resultado sale **distinto** cada vez. Eso es intencional (el "salt" de bcrypt) — no es un bug, es lo que hace que dos contraseñas iguales no se vean iguales en la base de datos.

> 🧑‍🏫 **Si al llamar `hash_password(...)` o `verify_password(...)` aparece un error mencionando `bcrypt` y `__about__`:** es un problema real y conocido de compatibilidad entre `passlib` 1.7.4 (su última versión) y versiones de `bcrypt` 4.1 en adelante — no es algo que hicieron mal. Corrige con `uv add "bcrypt<4.1"` y vuelve a intentar.

**Checkpoint:** puedes hashear y verificar una contraseña de prueba en una consola de Python.

---

## Paso 8 — Repository real: usuarios y gastos (10 min)

**`app/repositories/usuarios.py`** (nuevo)

```python
from sqlalchemy.orm import Session
from app.models.usuario import Usuario


def obtener_por_email(db: Session, email: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.email == email).first()


def guardar(db: Session, email: str, hashed_password: str) -> Usuario:
    usuario = Usuario(email=email, hashed_password=hashed_password)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario
```

**`app/repositories/gastos.py`** (reemplaza el de memoria de la Sesión 6)

```python
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.gasto import Gasto


def guardar(db: Session, usuario_id: int, descripcion: str, monto: float, categoria: str) -> dict:
    gasto = Gasto(usuario_id=usuario_id, descripcion=descripcion, monto=monto, categoria=categoria)
    db.add(gasto)
    db.commit()
    db.refresh(gasto)
    return {"id": gasto.id, "descripcion": gasto.descripcion, "monto": gasto.monto, "categoria": gasto.categoria}


def listar(db: Session, usuario_id: int, skip: int = 0, limit: int = 20) -> list[dict]:
    gastos = (
        db.query(Gasto)
        .filter(Gasto.usuario_id == usuario_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [{"id": g.id, "descripcion": g.descripcion, "monto": g.monto, "categoria": g.categoria} for g in gastos]


def total_por_categoria(db: Session, usuario_id: int, categoria: str) -> float:
    total = (
        db.query(func.sum(Gasto.monto))
        .filter(Gasto.usuario_id == usuario_id, Gasto.categoria == categoria)
        .scalar()
    )
    return total or 0.0
```

**Nota honesta sobre "casi no cambia":** la interfaz sí cambia un poco — ahora cada función necesita `db` (la sesión) y `usuario_id` (para aislar los datos de cada usuario). Lo que **no cambia** es el contrato de fondo (guardar, listar, sumar por categoría) ni la forma en que `services/gastos.py` los usa.

**Checkpoint:** ambos repositories importan sin errores.

---

## Paso 9 — Actualizar `services/` (15 min)

**`app/services/gastos.py`** (actualizado — DIP se mantiene, solo cambia qué se le pasa a `repo`)

```python
from app.repositories import gastos as gastos_repository
from app.utils.validadores import categoria_valida

LIMITE_POR_CATEGORIA = 500.0


class CategoriaInvalidaError(Exception):
    pass


class LimiteExcedidoError(Exception):
    pass


def _validar_gasto(descripcion: str, monto: float, categoria: str) -> None:
    if not descripcion or not descripcion.strip():
        raise ValueError("La descripción no puede estar vacía")
    if monto <= 0:
        raise ValueError("El monto debe ser mayor a cero")
    if not categoria_valida(categoria):
        raise CategoriaInvalidaError(f"'{categoria}' no es una categoría válida")


def registrar_gasto(db, usuario_id: int, descripcion: str, monto: float, categoria: str, repo=gastos_repository) -> dict:
    _validar_gasto(descripcion, monto, categoria)

    total_actual = repo.total_por_categoria(db, usuario_id, categoria)
    if total_actual + monto > LIMITE_POR_CATEGORIA:
        raise LimiteExcedidoError(
            f"Este gasto supera el límite de {LIMITE_POR_CATEGORIA} para la categoría '{categoria}'"
        )

    return repo.guardar(db, usuario_id, descripcion, monto, categoria)


def listar_gastos(db, usuario_id: int, skip: int = 0, limit: int = 20, repo=gastos_repository) -> list[dict]:
    return repo.listar(db, usuario_id, skip, limit)
```

*Compáralo con la versión de la Sesión 6: `_validar_gasto` no cambió ni una línea.*

**`app/services/usuarios.py`** (nuevo)

```python
from app.repositories import usuarios as usuarios_repository
from app.security import hash_password, verify_password


class EmailYaRegistradoError(Exception):
    pass


class CredencialesInvalidasError(Exception):
    pass


def registrar_usuario(db, email: str, password: str, repo=usuarios_repository):
    if repo.obtener_por_email(db, email):
        raise EmailYaRegistradoError(f"El email {email} ya está registrado")

    hashed = hash_password(password)
    return repo.guardar(db, email, hashed)


def autenticar_usuario(db, email: str, password: str, repo=usuarios_repository):
    usuario = repo.obtener_por_email(db, email)
    if not usuario or not verify_password(password, usuario.hashed_password):
        raise CredencialesInvalidasError("Email o contraseña incorrectos")
    return usuario
```

### Actualizar `RepositorioFalso` a la nueva firma

`registrar_gasto` y `listar_gastos` ahora llaman a `repo.guardar(db, usuario_id, ...)`, `repo.listar(db, usuario_id, skip, limit)` y `repo.total_por_categoria(db, usuario_id, categoria)` — con dos parámetros nuevos (`db`, `usuario_id`) que `RepositorioFalso` de la Sesión 6 todavía no tiene. Si no lo actualizas, los 4 tests de la Sesión 6 van a fallar con `TypeError` en cuanto corras `pytest` después de este paso.

En **`tests/test_gastos.py`**, actualiza la clase y las 4 llamadas:

```python
class RepositorioFalso:
    """Test double: mismo contrato que app/repositories/gastos.py, sin persistencia real."""

    def __init__(self, total_inicial_por_categoria: float = 0.0):
        self._gastos: list[dict] = []
        self._total_inicial = total_inicial_por_categoria

    def guardar(self, db, usuario_id: int, descripcion: str, monto: float, categoria: str) -> dict:
        gasto = {"id": len(self._gastos) + 1, "descripcion": descripcion, "monto": monto, "categoria": categoria}
        self._gastos.append(gasto)
        return gasto

    def listar(self, db, usuario_id: int, skip: int = 0, limit: int = 20) -> list[dict]:
        return self._gastos[skip: skip + limit]

    def total_por_categoria(self, db, usuario_id: int, categoria: str) -> float:
        return self._total_inicial + sum(g["monto"] for g in self._gastos if g["categoria"] == categoria)


def test_registrar_gasto_exitoso():
    repo = RepositorioFalso()

    resultado = gastos_service.registrar_gasto(None, 1, "Almuerzo", 12.50, "comida", repo=repo)

    assert resultado["descripcion"] == "Almuerzo"
    assert repo.listar(None, 1) == [resultado]


def test_registrar_gasto_monto_invalido_lanza_error():
    with pytest.raises(ValueError):
        gastos_service.registrar_gasto(None, 1, "Café", -5.0, "comida", repo=RepositorioFalso())


def test_registrar_gasto_categoria_invalida_lanza_error():
    with pytest.raises(CategoriaInvalidaError):
        gastos_service.registrar_gasto(None, 1, "Cine", 20.0, "categoria-inventada", repo=RepositorioFalso())


def test_registrar_gasto_excede_limite_categoria_lanza_error():
    repo = RepositorioFalso(total_inicial_por_categoria=490.0)

    with pytest.raises(LimiteExcedidoError):
        gastos_service.registrar_gasto(None, 1, "Cena cara", 50.0, "comida", repo=repo)
```

`db` se pasa como `None` y `usuario_id` como `1` porque `RepositorioFalso` los recibe pero nunca los usa — el doble de prueba no necesita una sesión de base de datos real ni valida el usuario, solo mantiene el mismo contrato de posiciones que ahora exige `services/gastos.py`.

> 🧑‍🏫 **Si corriste `pytest` entre el Paso 9 (services) y este ajuste:** es normal ver `TypeError: total_por_categoria() takes 2 positional arguments but 4 were given` (o similar) — es justo la señal de que el contrato cambió y `RepositorioFalso` quedó desactualizado. No es un error de tu código nuevo, es el doble de prueba que faltaba actualizar.

**Checkpoint:** actualizaste `RepositorioFalso` a la nueva firma (con `db` y `usuario_id`) y confirmas que los 4 tests de la Sesión 6 siguen pasando con `uv run pytest -v`.

---

## Paso 10 — Dependencia de autenticación (5 min)

**`app/dependencies.py`**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.security import decodificar_token
from app.repositories import usuarios as usuarios_repository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/token")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credenciales_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decodificar_token(token)
        email = payload.get("sub")
        if email is None:
            raise credenciales_exception
    except Exception:
        raise credenciales_exception

    usuario = usuarios_repository.obtener_por_email(db, email)
    if usuario is None:
        raise credenciales_exception
    return usuario
```

**Checkpoint:** `app/dependencies.py` importa sin errores. Todavía no se puede probar de verdad — necesita un router que la use, y eso llega en el paso siguiente.

---

## Paso 11 — Routers: registro, login y gastos protegidos con paginación (15 min)

**`app/routers/usuarios.py`**

```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.usuario import UsuarioCreate, UsuarioResponse
from app.services import usuarios as usuarios_service
from app.services.usuarios import EmailYaRegistradoError, CredencialesInvalidasError
from app.security import crear_access_token

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.post("/", response_model=UsuarioResponse, status_code=201)
def registrar(datos: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        return usuarios_service.registrar_usuario(db, datos.email, datos.password)
    except EmailYaRegistradoError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        usuario = usuarios_service.autenticar_usuario(db, form.username, form.password)
    except CredencialesInvalidasError as e:
        raise HTTPException(status_code=401, detail=str(e))

    token = crear_access_token({"sub": usuario.email})
    return {"access_token": token, "token_type": "bearer"}
```

**`app/routers/gastos.py`**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.gasto import GastoCreate, GastoResponse
from app.services import gastos as gastos_service
from app.services.gastos import CategoriaInvalidaError, LimiteExcedidoError
from app.dependencies import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/gastos", tags=["gastos"])


@router.post("/", response_model=GastoResponse, status_code=201)
def crear(
    datos: GastoCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    try:
        return gastos_service.registrar_gasto(
            db, usuario_actual.id, datos.descripcion, datos.monto, datos.categoria
        )
    except (ValueError, CategoriaInvalidaError, LimiteExcedidoError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[GastoResponse])
def listar(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    return gastos_service.listar_gastos(db, usuario_actual.id, skip, limit)
```

**`app/main.py`** (actualizado)

```python
from fastapi import FastAPI
from app.routers import usuarios, gastos

app = FastAPI(title="API de Control de Gastos")
app.include_router(usuarios.router)
app.include_router(gastos.router)
```

Actualiza también `app/routers/__init__.py` (quita el comentario-marcador, ya se llenó).

> 🧑‍🏫 **Ojo con `app/main.py`:** deja de ser un script ejecutable. El demo de la Sesión 6 —el que registraba dos gastos e imprimía los montos con `formatear_moneda`— se reemplaza por la app FastAPI, así que `uv run python -m app.main` ya no imprime nada. De aquí en adelante el proyecto se levanta con `uvicorn` (Paso 12). Como efecto lateral, `utils/formato.py` queda temporalmente sin ningún llamador: el código sigue ahí, intacto y reutilizable, pero hoy quien decide cómo se ve la salida es el schema de respuesta (`GastoResponse`), no la capa de formato.

---

## Paso 12 — Probar todo en `/docs` (5 min)

```bash
uv run uvicorn app.main:app --reload
```

1. Abre `http://127.0.0.1:8000/docs`
2. `POST /usuarios/` — registra un usuario
3. `POST /usuarios/token` — inicia sesión, copia el `access_token`
4. Autoriza en Swagger (botón "Authorize", pega el token)
5. `POST /gastos/` — crea un gasto (funciona, estás autenticado)
6. Cierra sesión en Swagger y prueba `GET /gastos/` de nuevo

**Observa mientras corre:** sin token, `GET /gastos/` responde `401`. Con token, responde `200` con tu lista. Esa diferencia — no una línea de código que "se ve distinta" — es la prueba real de que la autenticación funciona.

> 🧑‍🏫 **Si el token da `401` incluso después de autorizar:** revisa que el `SECRET_KEY` en `.env` no haya cambiado entre que generaste el token y que lo usaste (si reinician el servidor y cambiaron el `.env` entre medio, los tokens viejos dejan de ser válidos — es el comportamiento esperado, no un bug).

**Checkpoint:** sin token → `401`. Con token → funciona.

---

## Demo (no ejercicio) — El mismo modelo en SQLModel

```python
from sqlmodel import SQLModel, Field


class Gasto(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    descripcion: str
    monto: float
    categoria: str
    usuario_id: int = Field(foreign_key="usuarios.id")
```

*Una sola clase reemplaza el modelo SQLAlchemy + el schema Pydantic. Trade-off: ideal para CRUD directo; para queries complejas se puede seguir usando SQLAlchemy puro por debajo.*

---

## Paso 13 — Test de integración (segundo nivel de la pirámide) (10 min)

**`tests/test_integracion_gastos.py`**

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.repositories import usuarios as usuarios_repository
from app.repositories import gastos as gastos_repository
from app.services import gastos as gastos_service


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    yield db
    db.close()


def test_registrar_y_listar_gasto_integracion(db_session):
    usuario = usuarios_repository.guardar(db_session, "test@ejemplo.com", "hash-de-prueba")

    gastos_service.registrar_gasto(
        db_session, usuario.id, "Almuerzo", 12.50, "comida", repo=gastos_repository
    )

    gastos = gastos_service.listar_gastos(db_session, usuario.id, repo=gastos_repository)

    assert len(gastos) == 1
    assert gastos[0]["descripcion"] == "Almuerzo"


def test_limite_por_categoria_integracion(db_session):
    usuario = usuarios_repository.guardar(db_session, "otro@ejemplo.com", "hash-de-prueba")

    gastos_service.registrar_gasto(db_session, usuario.id, "Gasto 1", 490.0, "comida", repo=gastos_repository)

    with pytest.raises(gastos_service.LimiteExcedidoError):
        gastos_service.registrar_gasto(db_session, usuario.id, "Gasto 2", 50.0, "comida", repo=gastos_repository)
```

```bash
uv run pytest -v
```

**Checkpoint:** los tests unitarios de la Sesión 6 (con `RepositorioFalso`) y los de integración de hoy (con SQLite real) pasan juntos.

---

## Paso 14 — Logging y manejo de errores (15 min)

Hasta ahora, si algo falla dentro de una ruta, o no queda rastro (nadie llama `print`), o el cliente recibe el stack trace crudo de SQLAlchemy. Ninguna de las dos es aceptable en un backend real.

**`app/logging_config.py`** (nuevo)

```python
import logging
import sys

FORMATO = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def configurar_logging(nivel: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, nivel.upper(), logging.INFO),
        format=FORMATO,
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
```

Agrega `log_level: str = "INFO"` a `Settings` en `app/config.py`, y `LOG_LEVEL=INFO` en `.env.example` y `.env`.

**`app/main.py`** (actualizado — logging, middleware y manejo de errores)

```python
import logging
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.logging_config import configurar_logging
from app.routers import usuarios, gastos

configurar_logging(settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(title="API de Control de Gastos")
app.include_router(usuarios.router)
app.include_router(gastos.router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    inicio = time.perf_counter()
    response = await call_next(request)
    duracion_ms = (time.perf_counter() - inicio) * 1000
    logger.info(
        "%s %s -> %d (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duracion_ms,
    )
    return response


@app.exception_handler(Exception)
async def manejar_error_no_controlado(request: Request, exc: Exception):
    logger.exception("Error no controlado en %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Error interno del servidor"})
```

**`app/services/gastos.py` y `app/services/usuarios.py`** — agrega `logger = logging.getLogger(__name__)` y loguea en los puntos de decisión: `logger.info` cuando un gasto o un usuario se registra con éxito, `logger.warning` cuando se rechaza un gasto por límite excedido o un login por credenciales inválidas. **`_validar_gasto` sigue sin cambiar ni una línea** — el logging es aditivo, no reemplaza validación.

> 🧑‍🏫 **Qué nunca se loguea:** contraseñas, hashes ni tokens. Un `logger.info` con la contraseña en texto plano convierte tus logs en la misma fuga de datos que estás tratando de evitar con bcrypt.

> 🧑‍🏫 **Por qué `Exception` y no rompe los `HTTPException` que ya lanzas (401, 400):** FastAPI/Starlette resuelven primero el handler más específico registrado para cada tipo de excepción; `HTTPException` ya tiene el suyo por defecto y nunca cae en el handler genérico de `Exception`. Este handler solo atrapa lo que nadie anticipó — un `RuntimeError`, un `AttributeError`, un fallo real de la base de datos.

**Observa mientras corre:** relanza `uvicorn` (Paso 12) y repite un par de llamadas en `/docs`. En la terminal del servidor aparecen líneas como:

```
2026-09-09 18:44:59 | INFO     | app.services.gastos | Gasto registrado: usuario_id=7 gasto_id=6 categoria=comida
2026-09-09 18:44:59 | INFO     | app.main | POST /gastos/ -> 201 (23.1 ms)
```

Y si el gasto se rechaza por límite excedido, la línea sale en `WARNING`, no en `INFO` — el nivel del log ya te dice si algo salió como se esperaba o no, sin tener que leer el mensaje.

**Checkpoint:** los logs muestran nivel, ruta y status en cada request; un error no controlado devuelve `500` con `{"detail": "Error interno del servidor"}`, nunca un stack trace de SQLAlchemy.

---

## Paso 15 — DI con `Depends` y `dependency_overrides` (15 min)

> 🧑‍🏫 **La idea en una frase, antes del código:** la función no busca lo que necesita — se lo entregan. Es como pedir un taxi por app en vez de tener tu propio carro: no te importa qué carro llega ni quién lo maneja, solo que te lleve de A a B. La app decide cuál carro te manda — si mañana cambian de compañía de taxis, a ti no te afecta, sigues pidiendo "un taxi" igual. `registrar_gasto(repo)` es lo mismo: no le importa si `repo` guarda en una lista en memoria, en SQLite o en Postgres, solo que tenga un método `.guardar()`. Quien llama a la función decide qué `repo` mandar.

Desde la Sesión 6, `services/gastos.py` recibe el repository como parámetro (`repo=gastos_repository`) — un default de Python, no un mecanismo de FastAPI. Funciona, y es la razón por la que este mismo `repo` sobrevivió intacto toda la migración a SQLAlchemy. Pero FastAPI tiene su **propio** sistema de inyección de dependencias, con una ventaja concreta para testing: `app.dependency_overrides`, que sustituye una dependencia completa sin tocar el código de la ruta.

**`app/dependencies.py`** — agrega:

```python
from app.repositories import gastos as gastos_repository

def get_gastos_repo():
    return gastos_repository
```

**`app/routers/gastos.py`** — ambos endpoints reciben el repo vía `Depends`:

```python
from app.dependencies import get_current_user, get_gastos_repo

@router.post("/", response_model=GastoResponse, status_code=201)
def crear(
    datos: GastoCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
    repo=Depends(get_gastos_repo),
):
    try:
        return gastos_service.registrar_gasto(
            db, usuario_actual.id, datos.descripcion, datos.monto, datos.categoria, repo=repo
        )
    except (ValueError, CategoriaInvalidaError, LimiteExcedidoError) as e:
        raise HTTPException(status_code=400, detail=str(e))
```

(mismo patrón en `listar`, con `repo=repo` pasado a `gastos_service.listar_gastos`). `services/gastos.py` no cambia — ya aceptaba `repo` desde la Sesión 6; lo único nuevo es *quién* lo provee.

> 🧑‍🏫 **Dos mecanismos, mismo principio (DIP):** el default de parámetro (`repo=gastos_repository`) y `Depends(get_gastos_repo)` resuelven el mismo problema — la ruta/función no decide su repository, lo recibe. La diferencia es que `Depends` se puede sustituir *desde fuera* con `app.dependency_overrides`, sin tocar la firma de la función ni pasar `repo=` a mano en cada llamada de test.

**`tests/test_api_gastos.py`** (nuevo — reutiliza `RepositorioFalso` de `tests/test_gastos.py`):

```python
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import get_current_user, get_gastos_repo
from app.database import get_db
from app.models.usuario import Usuario
from tests.test_gastos import RepositorioFalso

USUARIO_DE_PRUEBA = Usuario(id=1, email="test@ejemplo.com", hashed_password="no-importa")


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = lambda: None
    app.dependency_overrides[get_current_user] = lambda: USUARIO_DE_PRUEBA
    # raise_server_exceptions=False: sin esto, el TestClient re-lanza la excepción
    # en vez de dejar que el exception_handler de la app la convierta en 500.
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_crear_gasto_con_repo_falso(client):
    app.dependency_overrides[get_gastos_repo] = lambda: RepositorioFalso()

    response = client.post(
        "/gastos/", json={"descripcion": "Almuerzo", "monto": 12.50, "categoria": "comida"}
    )

    assert response.status_code == 201
    assert response.json()["descripcion"] == "Almuerzo"


class RepositorioRoto:
    """Simula un fallo inesperado del repositorio (ej. la DB se cae a mitad de la request)."""

    def total_por_categoria(self, db, usuario_id, categoria):
        raise RuntimeError("la base de datos no responde")


def test_error_no_controlado_devuelve_500_sin_stacktrace(client):
    app.dependency_overrides[get_gastos_repo] = lambda: RepositorioRoto()

    response = client.post(
        "/gastos/", json={"descripcion": "Falla", "monto": 10.0, "categoria": "comida"}
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Error interno del servidor"}
```

`fastapi.testclient.TestClient` necesita `httpx`:

```bash
uv add --dev httpx
```

**Checkpoint:** `uv run pytest -v` corre todo junto — unitarios (S6), integración (Paso 13) y API con `dependency_overrides` (este paso) — sin tocar la base de datos real en los tests de API.

---

## Paso 16 — Demo: migrar a PostgreSQL con Docker (~15 min, instructor)

Este paso responde en código a la Pregunta 1 de la Reflexión: ¿qué archivo hay que tocar para cambiar de motor de base de datos, y qué archivos **no**? Es una demostración del instructor, no un ejercicio a mano — verifica en vivo que `services/` y `routers/` sobreviven intactos al cambio de SQLite a Postgres.

**`docker-compose.yml`** (nuevo, en la raíz del proyecto — equivalente al provisto en el aula virtual; si el tuyo usa otro puerto o credenciales, ajusta la URL de conexión más abajo)

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: gastos
      POSTGRES_USER: gastos
      POSTGRES_PASSWORD: gastos
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U gastos -d gastos"]
      interval: 2s
      timeout: 3s
      retries: 10

volumes:
  postgres_data:
```

> 🧑‍🏫 **Puerto 5433, no 5432:** si ya tienes otro Postgres corriendo en tu máquina (otro curso, otro proyecto), 5432 va a estar ocupado. Ajusta el mapeo de puertos si te choca con algo más.

```bash
docker compose up -d
uv add "psycopg[binary]"
```

### El único archivo de infraestructura que cambia: `app/database.py`

```python
# connect_args={"check_same_thread": False} es específico de SQLite (Paso 3).
# Con Postgres el driver no acepta ese argumento — se aplica solo cuando la URL es sqlite.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
```

### Migrar apuntando a Postgres, sin tocar tu `.env` de trabajo

En vez de editar `.env` (que el resto del curso sigue usando en SQLite), sobreescribe la variable solo para este comando — `pydantic-settings` prioriza las variables de entorno del shell por encima del `.env`:

```bash
DATABASE_URL="postgresql+psycopg://gastos:gastos@localhost:5433/gastos" uv run alembic upgrade head
```

**Observa mientras corre:** el log de Alembic dice `Context impl PostgresqlImpl` (no `SQLiteImpl`) y aplica la **misma** migración del Paso 6 — no se escribió una migración nueva para Postgres, la migración ya era portable.

### Confirmar que `services/` y `routers/` no se tocan — la API completa contra Postgres

```bash
DATABASE_URL="postgresql+psycopg://gastos:gastos@localhost:5433/gastos" uv run uvicorn app.main:app --port 8001
```

Repite el flujo del Paso 12 (`/docs`: registrar, login, crear gasto, listar) contra este servidor. Funciona igual, sin haber tocado una sola línea de `app/services/` ni `app/routers/`.

### Confirmar que los tests de integración pasan contra Postgres — en una base separada

```python
# tests/test_integracion_gastos.py — el fixture ahora lee la URL de un env var
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")

@pytest.fixture
def db_session():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(engine)
    engine.dispose()
```

Sin `TEST_DATABASE_URL`, sigue corriendo en SQLite en memoria por defecto. Para probar contra Postgres, crea una base **separada** de la que usa la API manualmente:

```bash
docker exec -it proyecto-curso-db-1 psql -U gastos -d gastos -c "CREATE DATABASE gastos_test;"
TEST_DATABASE_URL="postgresql+psycopg://gastos:gastos@localhost:5433/gastos_test" uv run pytest -v tests/test_integracion_gastos.py
```

> 🧑‍🏫 **Por qué una base separada y no la misma `gastos`:** el fixture hace `Base.metadata.drop_all(engine)` al terminar cada test — en SQLite en memoria no importa (el motor entero desaparece), pero contra un Postgres real **eso borra las tablas de la base que estés usando en `/docs`**. Si corres los tests apuntando a la misma `gastos` que usas para probar manualmente, tu próxima llamada a `/docs` falla con `relation "usuarios" does not exist`. La causa no es un bug de tu código: es un test de integración limpiando después de sí mismo en una base que no era solo suya. La solución en cualquier proyecto real es la misma: la base de tests nunca es la base con la que interactúas a mano.

> 🧑‍🏫 **Si después de un `drop_all` accidental `alembic upgrade head` no recrea las tablas:** Alembic guarda en qué migración estás en la tabla `alembic_version`, que **no** es parte de `Base.metadata` — así que `drop_all` no la toca, y Alembic sigue creyendo que ya aplicó la migración aunque las tablas ya no existan. Arréglalo borrando esa tabla de seguimiento (`DROP TABLE alembic_version;`) y corriendo `alembic upgrade head` de nuevo.

### Apagar todo al terminar la demo

```bash
docker compose down -v
```

Esto borra el contenedor y su volumen — tu `.env` sigue apuntando a SQLite, `gastos.db` sigue intacto, el resto de la práctica no se entera de que esto pasó.

**Checkpoint:** la migración corrió contra Postgres con el mismo comando y el mismo archivo del Paso 6; la API completa funcionó contra Postgres sin tocar `services/` ni `routers/`; los tests de integración pasaron contra Postgres en una base separada de la que usó la demo manual.

---

## Reflexión (antes del cierre)

1. Si mañana quisieras cambiar de SQLite a Postgres, ¿qué archivo específico tendrías que tocar? ¿Y qué archivos NO tendrías que tocar?
2. ¿Qué pasaría si alguien intentara hacer `GET /gastos/` pasando el `usuario_id` de otra persona en la URL en vez de en el token? ¿Podría ver los gastos de otro usuario, con el código que escribiste hoy?

---

## Cierre (5 min)

Completa:

> "Si mañana un atacante consigue mi archivo `.env`, podría ______, pero NO podría ______, porque ______."

**Guarda todo tu trabajo** — este mismo repositorio se retoma completo en la Sesión 8, donde `app/mcp/` deja de estar vacía.

---

## Trabajo autónomo (post-clase)

1. Migrar `DATABASE_URL` de SQLite a PostgreSQL usando Docker (`docker-compose.yml` provisto en el aula virtual)
2. Confirmar que los tests de integración siguen pasando contra Postgres, sin tocar `services/` ni `routers/` (usa una base de datos separada de la que uses para probar `/docs` a mano)
3. Corregir el warning `PydanticDeprecatedSince20` que sale al correr `pytest` (en `app/config.py`, `app/schemas/usuario.py` y `app/schemas/gasto.py`): la `class Config:` interna es sintaxis de Pydantic v1 — en v2 se reemplaza por `model_config = ConfigDict(...)` (o `SettingsConfigDict` en `Settings`, que hereda de `BaseSettings`)
4. Explorar el "mapa resumen para profundizar" (Caching, Background tasks, CI/CD) visto en la teoría de hoy

---

## Checklist de autoverificación

- [ ] `.env.example` existe y no contiene ningún valor real (solo la lista de variables)
- [ ] `.env` generado a partir de `.env.example`, con un `SECRET_KEY` generado de forma segura (no escrito a mano)
- [ ] `app/config.py` con `pydantic-settings` leyendo `.env`
- [ ] `models/usuario.py` y `models/gasto.py` (con FK `usuario_id`)
- [ ] Migración de Alembic aplicada (`alembic upgrade head`), con `target_metadata` apuntando a `Base.metadata` y la URL tomada de `settings`, no del placeholder de `alembic.ini`
- [ ] `repositories/gastos.py` reemplazado por la versión con SQLAlchemy
- [ ] `services/gastos.py` actualizado, `_validar_gasto` sin cambios respecto a S6
- [ ] `RepositorioFalso` en `tests/test_gastos.py` actualizado a la nueva firma (`db`, `usuario_id`), y los 4 tests de la Sesión 6 siguen pasando
- [ ] `POST /usuarios/` y `POST /usuarios/token` funcionando
- [ ] `POST /gastos/` y `GET /gastos/` protegidos — `401` sin token, funcionan con token
- [ ] Paginación (`skip`/`limit`) funcionando en `GET /gastos/`
- [ ] Tests unitarios (S6, actualizados) + tests de integración (hoy) pasando juntos
- [ ] Logs visibles en consola con nivel, ruta y status en cada request
- [ ] Un error no controlado devuelve `500` con `{"detail": "Error interno del servidor"}`, nunca un stack trace
- [ ] `tests/test_api_gastos.py` pasa usando `app.dependency_overrides` sobre `get_gastos_repo`, `get_db` y `get_current_user`

---

## Conexión con la próxima sesión

En la **Sesión 8**, `app/mcp/` deja de estar vacía: se construyen tools de MCP que llaman exactamente a `app/services/gastos.py` y `app/services/usuarios.py` — los mismos que ya usa el router REST. Ahí se prueba el tercer y último nivel de la pirámide de testing: **e2e**, con un cliente MCP real hablando con el servidor completo.
