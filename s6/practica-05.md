# Sesión 6 — Práctica: Cimientos de un backend serio

**Duración de la práctica:** 65 minutos, después de la teoría.
**Punto de partida:** ninguno — hoy arranca el proyecto del curso (control de gastos personales). Este mismo proyecto se retoma en cada sesión siguiente.
**Novedad de hoy:** por primera vez separan su código en capas, y prueban una función de negocio sin tocar infraestructura real.

> **Sobre el rol de esta práctica:** "Gastos" es el ejemplo guiado sobre el que van a aprender arquitectura, REST, MCP y seguridad en las Sesiones 6-8. El proyecto que se evalúa es distinto — en la Sesión 9 van a aplicar todo esto a una idea propia, usando spec-kit. Esta práctica no se entrega; el checklist de abajo es para tu propia verificación.

## La arquitectura (léela antes de empezar)

```
ROUTERS       → reciben la solicitud (hoy quedan vacías, se llenan en la Sesión 7)
SERVICES      → deciden: reglas de negocio (hoy sí se llenan)
REPOSITORIES  → guardan/leen datos (hoy en memoria, en la Sesión 7 será una base de datos real)
UTILS         → funciones puras reutilizables, sin depender de nada más (hoy sí se llenan)
```

Un `service` **no** debe hablar directo con la base de datos, y un `router` **no** debe decidir reglas de negocio — cada capa hace una sola cosa. Hoy van a sentir por qué, al construir un repository falso que `services/` ni siquiera nota que es falso.

## Cronograma

| Paso                                              | Tiempo | Acumulado |
| ------------------------------------------------- | ------ | --------- |
| 1 — Estructura y marcadores de continuidad        | 10 min | 10 min    |
| 2 — Entorno virtual clásico (`venv` + `pip`)      | 10 min | 20 min    |
| 3 — Migrar a `uv`                                 | 10 min | 30 min    |
| 4 — `utils/`, mini-módulo y repository en memoria | 20 min | 50 min    |
| 5 — Test unitario con DIP                         | 10 min | 60 min    |
| 6 — Git: primer commit                            | 5 min  | 65 min    |

## Antes de empezar

- [ ] Python 3.12 instalado
- [ ] Terminal (bash, zsh o PowerShell)
- [ ] Editor de código (VS Code recomendado)
- [ ] `uv` instalado ([instrucciones oficiales](https://docs.astral.sh/uv/getting-started/installation/))

### Principios que vas a aplicar hoy (sin sobre-ingeniería)

| Principio                       | Dónde se aplica        | Cómo                                                                                                                                                              |
| ------------------------------- | ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Clean Code**                  | Todo el módulo         | Nombres explícitos, funciones pequeñas, sin números mágicos, validación con guard clauses                                                                         |
| **SRP** (Single Responsibility) | `services/gastos.py`   | `_validar_gasto` solo valida; `registrar_gasto` solo orquesta; el repository solo persiste                                                                        |
| **OCP** (Open/Closed)           | `utils/validadores.py` | Agregar una categoría nueva = agregar un valor a un conjunto, no tocar lógica                                                                                     |
| **DIP** (Dependency Inversion)  | `services/gastos.py`   | El service recibe el repository como parámetro (con un valor por defecto), no lo importa "a fuego" — así se puede sustituir en los tests sin librerías de mocking |

*No forzamos LSP ni ISP: con funciones simples (sin jerarquías de clases) no hay un caso real donde apliquen sin agregar complejidad artificial — se dejan para cuando el proyecto lo pida de verdad.*

### Glosario de siglas

| Sigla     | Significado                                                                      | En una frase                                                                                                             |
| --------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **SOLID** | Conjunto de 5 principios de diseño orientado a objetos (SRP, OCP, LSP, ISP, DIP) | El paraguas bajo el que caen los otros 4                                                                                 |
| **SRP**   | Single Responsibility Principle (Principio de Responsabilidad Única)             | Cada función/módulo hace UNA sola cosa                                                                                   |
| **OCP**   | Open/Closed Principle (Principio de Abierto/Cerrado)                             | Abierto a extender (agregar datos/casos), cerrado a modificar (la lógica ya escrita no cambia)                           |
| **LSP**   | Liskov Substitution Principle (Principio de Sustitución de Liskov)               | Una subclase debe poder reemplazar a su clase padre sin romper nada — no aplica aquí, no usamos herencia                 |
| **ISP**   | Interface Segregation Principle (Principio de Segregación de Interfaces)         | Mejor varias interfaces pequeñas y específicas que una grande y genérica — no aplica aquí, no usamos interfaces formales |
| **DIP**   | Dependency Inversion Principle (Principio de Inversión de Dependencias)          | Depender de una abstracción (cualquier objeto con cierto comportamiento), no de una implementación concreta              |

---

## Estructura objetivo al final de la práctica

```
proyecto-curso/
├── app/
│   ├── main.py
│   ├── routers/          # marcador: se llena en Sesión 7
│   ├── mcp/               # marcador: se llena en Sesión 8
│   ├── schemas/           # marcador: se llena en Sesión 7
│   ├── services/
│   │   └── gastos.py
│   ├── repositories/
│   │   └── gastos.py
│   ├── models/            # marcador: se llena en Sesión 7
│   └── utils/
│       ├── formato.py
│       └── validadores.py
├── tests/
│   └── test_gastos.py
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

*Nota: `.env` no aparece todavía — hoy el proyecto no usa ninguna variable de entorno real. Se crea recién en la Sesión 7, cuando `SECRET_KEY` y `DATABASE_URL` empiezan a existir de verdad.*

---

## Paso 1 — Crear el proyecto y la estructura de carpetas (10 min)

```bash
mkdir proyecto-curso
cd proyecto-curso

mkdir -p app/routers app/mcp app/schemas app/services app/repositories app/models app/utils tests

touch app/__init__.py app/main.py
touch app/services/__init__.py app/repositories/__init__.py app/utils/__init__.py
touch tests/__init__.py
touch README.md
```

> 🧑‍🏫 **Si usas PowerShell y `touch` no existe:** usa `New-Item -ItemType File -Path app\main.py -Force` (repite por cada archivo), o simplemente crea los archivos desde el explorador de VS Code. No dejes que esto frene la clase.

En `README.md`, escribe una descripción mínima:

```markdown
# Proyecto Curso — Control de Gastos con IA Generativa

Backend de control de gastos personales, construido durante el curso.
Arquitectura: monolito modular + capas + Repository.
```

### Marcadores de continuidad

```bash
cat > app/routers/__init__.py << 'PYEOF'
# Endpoints REST (FastAPI). Se llena en la Sesión 7.
PYEOF

cat > app/schemas/__init__.py << 'PYEOF'
# Modelos Pydantic de entrada/salida. Se llena en la Sesión 7.
PYEOF

cat > app/models/__init__.py << 'PYEOF'
# Tablas SQLAlchemy (Usuario, Gasto). Se llena en la Sesión 7.
PYEOF

cat > app/mcp/__init__.py << 'PYEOF'
# Servidor y tools de MCP, reutilizando services/. Se llena en la Sesión 8.
PYEOF
```

**Checkpoint:** todas las carpetas existen; las que aún no tienen código tienen su comentario-marcador.

---

## Paso 2 — Entorno virtual clásico: `venv` + `pip` (10 min)

```bash
python -m venv venv
source venv/bin/activate        # Linux / Mac
venv\Scripts\activate           # Windows

pip install python-dotenv pytest
pip freeze > requirements.txt
```

**Checkpoint:** el archivo `requirements.txt` existe y no está vacío.

*Nota: este archivo es temporal — sirve para comparar el flujo clásico contra `uv` en el Paso 3, donde se borra porque `pyproject.toml` + `uv.lock` lo reemplazan.*

---

## Paso 3 — Migrar el proyecto a `uv` (10 min)

```bash
deactivate

uv init --no-readme .
uv python pin 3.12
uv add python-dotenv pytest
```

> 🧑‍🏫 **`uv init` hace más de lo que parece.** Además de `pyproject.toml`, crea automáticamente: (1) un archivo/paquete de arranque que **no** es el que ya tenían en `app/` — según la versión de `uv` puede ser un `main.py` suelto en la **raíz**, o (en versiones más recientes) una carpeta `src/<nombre_del_proyecto>/` con su propio `__init__.py` — bórralo, ya tienen el suyo dentro de `app/` (ver comandos abajo); (2) un `.gitignore` genérico — se reemplaza por el propio en el Paso 6, no hay que hacer nada ahora; (3) inicializa `git` automáticamente si la carpeta todavía no era un repositorio. Por eso, cuando lleguen al Paso 6 y corran `git init`, es normal ver "ya existe un repositorio" — no es un error, es este paso adelantándose.

```bash
rm -f main.py
rm -rf src
rm -f requirements.txt
```

`requirements.txt` era del flujo clásico (`pip freeze`) del Paso 2 — ya cumplió su propósito de comparación y `uv.lock` lo reemplaza de aquí en adelante.

Si `uv init` generó la carpeta `src/`, tu `pyproject.toml` va a traer también un bloque `[project.scripts]` (apuntando a ese paquete que acabas de borrar) y un `[build-system]`. Ese layout `src/` es el default de `uv` para **paquetes distribuibles** (algo que se publica o se instala vía `pip`) — no es nuestro caso: este proyecto se corre en su lugar, con `python -m app.main`, y toda la guía (incluida la Sesión 7 con FastAPI) usa `app/` como raíz de imports (`from app.services import ...`). Adaptar `uv` a esa convención cuesta reemplazar esas dos secciones por una sola línea; adaptar la guía al layout de `uv` obligaría a reescribir imports en cada sesión futura. Por eso reemplaza `[project.scripts]` y `[build-system]` por:

```toml
[tool.uv]
package = false
```

y corre `uv lock` de nuevo para que `uv.lock` quede consistente con el `pyproject.toml` editado.

```bash
cat pyproject.toml
cat uv.lock
```

> 🧑‍🏫 **Si `uv python pin 3.12` falla porque no hay un Python 3.12 instalado en la máquina:** ejecuta `uv python install 3.12` primero. Si tampoco hay red o el paso sigue fallando, continúa con el `venv` clásico del Paso 2 para el resto de la práctica — lo importante hoy es la arquitectura, no la herramienta de entornos.

**Observa mientras corre:** ¿cuánto tardó `uv add` comparado con el `pip install` del Paso 2? Guarda ese dato mentalmente, lo vas a comentar al cierre.

**Checkpoint:** existen `pyproject.toml` y `uv.lock` en la raíz del proyecto; no queda `main.py` suelto, carpeta `src/` fuera de `app/`, ni `requirements.txt`.

---

## Paso 4 — `utils/`, mini-módulo funcional y repository en memoria (20 min)

### `app/utils/validadores.py`

```python
# OCP: agregar una categoría nueva = agregar un valor aquí.
# La función de abajo nunca cambia.
CATEGORIAS_PERMITIDAS = {"comida", "transporte", "entretenimiento", "otros"}


def categoria_valida(categoria: str) -> bool:
    return categoria in CATEGORIAS_PERMITIDAS
```

### `app/utils/formato.py`

```python
def formatear_moneda(monto: float) -> str:
    return f"${monto:,.2f}"
```

### `app/repositories/gastos.py`

```python
# Repository en memoria — se reemplazará por SQLAlchemy en la Sesión 7
# SRP: cada función hace UNA sola cosa (guardar, listar o sumar). Cero lógica de negocio aquí.
_gastos: list[dict] = []
_siguiente_id = 1


def guardar(descripcion: str, monto: float, categoria: str) -> dict:
    global _siguiente_id
    gasto = {
        "id": _siguiente_id,
        "descripcion": descripcion,
        "monto": monto,
        "categoria": categoria,
    }
    _gastos.append(gasto)
    _siguiente_id += 1
    return gasto


def listar() -> list[dict]:
    return _gastos


def total_por_categoria(categoria: str) -> float:
    return sum(g["monto"] for g in _gastos if g["categoria"] == categoria)
```

### `app/services/gastos.py`

```python
from app.repositories import gastos as gastos_repository
from app.utils.validadores import categoria_valida

LIMITE_POR_CATEGORIA = 500.0


class CategoriaInvalidaError(Exception):
    pass


class LimiteExcedidoError(Exception):
    pass


# SRP: esta función SOLO valida. No decide reglas de negocio, no persiste.
def _validar_gasto(descripcion: str, monto: float, categoria: str) -> None:
    if not descripcion or not descripcion.strip():
        raise ValueError("La descripción no puede estar vacía")

    if monto <= 0:
        raise ValueError("El monto debe ser mayor a cero")

    if not categoria_valida(categoria):
        raise CategoriaInvalidaError(f"'{categoria}' no es una categoría válida")


# SRP: esta función SOLO orquesta (valida -> revisa regla de negocio -> persiste).
# DIP: recibe "repo" como parámetro en vez de usar gastos_repository fijo dentro del
# cuerpo de la función -> se puede sustituir por cualquier objeto con el mismo contrato.
def registrar_gasto(
    descripcion: str,
    monto: float,
    categoria: str,
    repo=gastos_repository,
) -> dict:
    _validar_gasto(descripcion, monto, categoria)

    total_actual = repo.total_por_categoria(categoria)
    if total_actual + monto > LIMITE_POR_CATEGORIA:
        raise LimiteExcedidoError(
            f"Este gasto supera el límite de {LIMITE_POR_CATEGORIA} para la categoría '{categoria}'"
        )

    return repo.guardar(descripcion, monto, categoria)


# DIP: mismo patrón — "repo" es la abstracción, gastos_repository es solo el valor por defecto.
def listar_gastos(repo=gastos_repository) -> list[dict]:
    return repo.listar()
```

### `app/main.py`

```python
from app.services import gastos as gastos_service
from app.utils.formato import formatear_moneda

if __name__ == "__main__":
    gastos_service.registrar_gasto("Almuerzo", 12.50, "comida")
    gastos_service.registrar_gasto("Bus", 2.00, "transporte")

    for gasto in gastos_service.listar_gastos():
        print(f"{gasto['descripcion']}: {formatear_moneda(gasto['monto'])} ({gasto['categoria']})")
```

```bash
uv run python -m app.main
```

**Observa mientras corre:** el monto sale formateado como moneda (`$12.50`), no como un `float` crudo (`12.5`) — eso es `utils/formato.py` trabajando, no una casualidad de `print`.

> 🧑‍🏫 **Si sale `ModuleNotFoundError: No module named 'app'`:** casi siempre es porque el comando se corrió desde dentro de `app/` en vez de la raíz del proyecto. Verifica con `pwd` que estás en `proyecto-curso/`, no en `proyecto-curso/app/`.

**Checkpoint:** el comando imprime los 2 gastos con el monto formateado (ej. `Almuerzo: $12.50 (comida)`).

---

## Paso 5 — Test unitario con un repositorio falso, gracias a DIP (10 min)

**`tests/test_gastos.py`**

```python
import pytest
from app.services import gastos as gastos_service
from app.services.gastos import LimiteExcedidoError, CategoriaInvalidaError


class RepositorioFalso:
    """Test double: mismo contrato que app/repositories/gastos.py, sin persistencia real."""

    def __init__(self, total_inicial_por_categoria: float = 0.0):
        self._gastos: list[dict] = []
        self._total_inicial = total_inicial_por_categoria

    def guardar(self, descripcion: str, monto: float, categoria: str) -> dict:
        gasto = {"id": len(self._gastos) + 1, "descripcion": descripcion, "monto": monto, "categoria": categoria}
        self._gastos.append(gasto)
        return gasto

    def listar(self) -> list[dict]:
        return self._gastos

    def total_por_categoria(self, categoria: str) -> float:
        return self._total_inicial + sum(g["monto"] for g in self._gastos if g["categoria"] == categoria)


# Gracias a DIP: se inyecta un repositorio falso, no se necesita unittest.mock.
def test_registrar_gasto_exitoso():
    repo = RepositorioFalso()

    resultado = gastos_service.registrar_gasto("Almuerzo", 12.50, "comida", repo=repo)

    assert resultado["descripcion"] == "Almuerzo"
    assert repo.listar() == [resultado]


def test_registrar_gasto_monto_invalido_lanza_error():
    with pytest.raises(ValueError):
        gastos_service.registrar_gasto("Café", -5.0, "comida", repo=RepositorioFalso())


def test_registrar_gasto_categoria_invalida_lanza_error():
    with pytest.raises(CategoriaInvalidaError):
        gastos_service.registrar_gasto("Cine", 20.0, "categoria-inventada", repo=RepositorioFalso())


def test_registrar_gasto_excede_limite_categoria_lanza_error():
    repo = RepositorioFalso(total_inicial_por_categoria=490.0)

    with pytest.raises(LimiteExcedidoError):
        gastos_service.registrar_gasto("Cena cara", 50.0, "comida", repo=repo)
```

```bash
uv run pytest -v
```

> 🧑‍🏫 **Si sale `ModuleNotFoundError` al correr pytest:** confirma que existe `tests/__init__.py` y que estás corriendo el comando desde la raíz del proyecto. Alternativa rápida: `uv run python -m pytest -v`.

**Checkpoint:** los 4 tests pasan (`4 passed`) — y nota que en ningún test se importó `unittest.mock`.

---

## Cómo se conectan las piezas (léelo antes de seguir)

No hay magia entre `services/`, el repository y el test — la conexión es literal: `registrar_gasto` recibe un objeto llamado `repo` y le llama tres métodos (`guardar`, `total_por_categoria`, `listar`). No le importa si ese objeto es `app/repositories/gastos.py` (una lista en memoria) o `RepositorioFalso` (una clase de prueba) — con tal de que tenga esos tres métodos, funciona.

```
services/gastos.py (registrar_gasto)
        ↓ llama a
repo.total_por_categoria(...) y repo.guardar(...)
        ↓ "repo" puede ser...
app/repositories/gastos.py (real, en memoria hoy)   O   RepositorioFalso (de prueba)
```

**Esa es toda la "inversión de dependencias" de hoy:** el service decide qué necesita (un objeto con esos 3 métodos), no de dónde viene. Por eso en la Sesión 7, cuando `repo` sea una base de datos real, `services/gastos.py` casi no va a notar la diferencia.

---

## Paso 6 — Git: versionar el proyecto (5 min)

**`.gitignore`**

```
venv/
__pycache__/
*.pyc
.env
*.db
.pytest_cache/
.venv/
```

```bash
git init
git add .
git commit -m "Estructura inicial: arquitectura en capas + Clean Code + SOLID (SRP/OCP/DIP) + primer test unitario (gastos)"
```

> 🧑‍🏫 **Si `git init` dice que ya existe un repositorio:** es esperado — `uv init` del Paso 3 ya lo había inicializado automáticamente. No es un error ni significa que el proyecto esté versionado dos veces; simplemente continúa con `git add` y `git commit`.

**Checkpoint:** `git log` muestra el commit inicial.

---

## Reflexión (antes del cierre)

Respondan en pareja o en grupo, 2-3 minutos:

1. Si mañana quisieras agregar un segundo tipo de repository (por ejemplo, uno que guarde los gastos en un archivo JSON en vez de en memoria), ¿qué tendrías que cambiar en `services/gastos.py`?
2. Un compañero te dice: "para ir más rápido, voy a poner la validación del monto directo en el router". Basado en lo que construiste hoy, ¿qué le responderías?

---

## Cierre (5 min)

Completa en `README.md` o en voz alta:

> "Hoy pude probar mi lógica de negocio sin ______, gracias a ______."

**Guarda todo tu trabajo** — este mismo repositorio se retoma completo en la Sesión 7, no vas a empezar un proyecto nuevo.

---

## Checklist de autoverificación

Esta práctica no se entrega formalmente — es el ejemplo guiado sobre el que van a aprender haciendo en las próximas sesiones. Úsalo para confirmar que quedó bien construido antes de seguir:

- [ ] Estructura completa de carpetas, con marcadores de continuidad en `routers/`, `schemas/`, `models/`, `mcp/`
- [ ] `pyproject.toml` y `uv.lock` generados por `uv`, con Python 3.12 fijado
- [ ] No quedó un `main.py` suelto ni una carpeta `src/` en la raíz del proyecto (lo que crea `uv init` automáticamente) — solo existe `app/main.py`
- [ ] `app/utils/validadores.py` y `app/utils/formato.py` funcionando y usados desde `services/`
- [ ] `services/gastos.py` separa validación (`_validar_gasto`) de orquestación (`registrar_gasto`) — SRP
- [ ] `services/gastos.py` recibe el repository como parámetro, no lo importa fijo dentro de la función — DIP
- [ ] `python -m app.main` corre sin errores y muestra montos formateados
- [ ] `pytest -v` corre y pasa los 4 tests, sin usar `unittest.mock`
- [ ] `.gitignore` correcto y un primer commit hecho

---

## Conexión con la próxima sesión

En la **Sesión 7**, este proyecto crece llenando los marcadores de hoy:

1. El repository en memoria se reemplaza por uno real con SQLAlchemy + Alembic. **Nota honesta:** la firma de las funciones sí cambia un poco (se agregan `db` y `usuario_id`, porque un repository real con múltiples usuarios necesita esos datos) — lo que **no cambia** gracias a DIP es `_validar_gasto` (ni una línea distinta) ni el patrón de "el service recibe el repo como parámetro, no lo importa fijo".
2. `app/models/` se llena con `Usuario` y `Gasto` (FK `usuario_id`).
3. `app/schemas/` se llena con los Pydantic de entrada/salida.
4. `app/routers/` se llena con los endpoints REST y autenticación OAuth2 + JWT — ahí verán DI "de verdad" con `Depends()` de FastAPI, que sigue el mismo principio (DIP) que ya practicaron hoy a mano.
5. `utils/` se reutiliza tal cual, sin ningún cambio.

El "aha moment" que buscamos para el miércoles: **`Depends()` de FastAPI no es magia nueva — es el mismo DIP que ya escribieron hoy con un simple parámetro por defecto.** Y aunque la firma de las funciones del repository crezca un poco, el corazón de la lógica de negocio (`_validar_gasto`) queda intacto — esa es la prueba real de que la arquitectura funcionó.
