# Clase 1 — Práctica guiada: arma tu entorno de trabajo

**Curso:** Programación de Backend y MCP en Python para IA Generativa
**Sesión:** 1 de 10
**Duración:** 50 minutos + 10 minutos de cierre
**Calificación:** ninguna — pero todo lo que instales hoy lo vuelves a usar en las clases siguientes.

> **Convención del curso:** el código (nombres de variables, funciones, comentarios,
> docstrings) siempre se escribe en inglés, aunque las clases se dicten en español. Es el
> estándar que vas a encontrar en cualquier equipo real y en toda la documentación de las
> librerías que vamos a usar.

---

## Antes de empezar: por qué esta práctica importa

Todo lo que vas a instalar hoy es la base técnica que vas a reutilizar en cada sesión del
curso: un lenguaje, un gestor de dependencias, control de versiones y contenedores. No es
burocracia de instalación — es la primera pieza de la arquitectura de cualquier proyecto de
backend que construyas de aquí en adelante.

Vamos a ir pieza por pieza. En cada paso vas a entender **qué es**, **para qué sirve** y
**cómo confirmar que quedó bien puesto**, antes de pasar al siguiente. Al final, un solo
comando revisa las seis piezas juntas.

---

## Paso 1 — Python: el lenguaje base del curso

### Por qué Python

Python es uno de los lenguajes más usados para desarrollo backend: tiene un ecosistema
enorme de librerías, documentación abundante y una curva de aprendizaje suave. Vas a
escribir Python en todas las sesiones, así que hoy solo confirmamos que está bien instalado.

### Por qué la versión importa

Usamos **Python 3.12** específicamente. Las librerías que vamos a usar (FastAPI, los clientes
de MCP) asumen características de esta versión. Si tienes 3.10 u 11, no pasa nada grave —
en el Paso 2 `uv` te deja fijar 3.12 sin tocar el Python de tu sistema operativo.

### Verifica si ya lo tienes

```bash
python --version
```

Salida esperada: `Python 3.12.x`. Si sale otra cosa (o `command not found`), instálalo:

### Instala en macOS

La forma recomendada es con [Homebrew](https://brew.sh/), el gestor de paquetes de macOS.
Si no lo tienes:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Luego instala Python 3.12:

```bash
brew install python@3.12
```

> En Mac con chip Apple Silicon (M1/M2/M3/M4), Homebrew instala en `/opt/homebrew`; en Mac
> con Intel, en `/usr/local`. No necesitas hacer nada distinto — Homebrew lo resuelve solo,
> pero si el comando `python --version` no lo detecta después de instalar, cierra y vuelve a
> abrir la terminal.

Verifica de nuevo:

```bash
python3.12 --version
```

> En macOS es común que el comando quede como `python3.12` en vez de `python`, porque el
> sistema trae su propio Python reservado para uso interno. No lo problema — `uv` (Paso 2)
> va a manejar esto por ti sin que tengas que preocuparte por cuál `python` usa la terminal.

### Instala en Windows

Descarga el instalador oficial desde [python.org/downloads](https://www.python.org/downloads/)
y elige la versión **3.12.x**. Al ejecutar el instalador, **marca la casilla
"Add python.exe to PATH"** en la primera pantalla — es el error más común al instalar Python
en Windows, y si no la marcas, la terminal no va a reconocer el comando `python`.

Verifica en PowerShell o CMD:

```powershell
python --version
```

> Si sale una versión distinta a 3.12 porque ya tenías otra instalada, no la desinstales:
> `uv` (Paso 2) puede fijar 3.12 para este proyecto específico sin afectar tu instalación
> existente.

### Instala en Linux

La mayoría de distribuciones ya traen Python, pero no siempre la versión 3.12. Según tu
distribución:

**Ubuntu / Debian**
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv
```

Si tu versión de Ubuntu no ofrece 3.12 en sus repositorios oficiales, agrega el PPA
`deadsnakes` antes de instalar:

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12 python3.12-venv
```

**Fedora**
```bash
sudo dnf install python3.12
```

**Arch Linux**
```bash
sudo pacman -S python
```

Verifica:

```bash
python3.12 --version
```

> En Linux, igual que en macOS, es normal que el comando quede como `python3.12` en vez de
> `python`, porque el sistema reserva `python3` para su propio uso interno. `uv` (Paso 2) se
> encarga de usar la versión correcta sin que tengas que resolver esto a mano.

---

## Paso 2 — uv: quién administra tus dependencias

### El problema que resuelve

Cada proyecto de Python necesita sus propias librerías, con versiones específicas. Si las
instalas "sueltas" en tu computador, un proyecto puede romper a otro sin que lo notes. La
solución clásica es `pip + venv + pip-tools`: tres herramientas separadas, lentas, que hay
que coordinar a mano.

### Qué es uv

`uv` es un gestor de proyectos escrito en Rust que reemplaza a esas tres herramientas en una
sola, y es de 10 a 100 veces más rápido. Con un solo comando crea el entorno, instala las
dependencias y fija las versiones exactas para que a todos en el curso les funcione igual.

### Instala en macOS

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

O, si prefieres usar Homebrew:

```bash
brew install uv
```

### Instala en Windows

**PowerShell**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

> Si acabas de instalarlo y el siguiente comando dice "no reconocido", **cierra y vuelve a
> abrir la terminal**. El instalador agrega uv al PATH, pero la terminal abierta no se entera.

### Instala en Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Si tu distribución usa un gestor de paquetes con `uv` disponible (por ejemplo Arch Linux vía
`pacman -S uv`), también puedes usarlo, pero el instalador oficial de arriba funciona igual
en cualquier distribución.

### Verifica (en cualquier sistema)

```bash
uv --version
```

---

## Paso 3 — El proyecto: la carpeta que vas a usar hoy

### Por qué una estructura fija

Vas a trabajar hoy con dos scripts y una carpeta de evidencia. Mantener una convención
simple desde ya te facilita pedir ayuda en el foro: todos describen el mismo mapa de
carpetas.

### Crea el proyecto y fija la versión de Python

```bash
uv init curso-mcp-<tu-usuario>
cd curso-mcp-<tu-usuario>
uv python pin 3.12
```

`uv python pin 3.12` le dice a este proyecto, específicamente, que use Python 3.12 sin
importar qué versión tengas instalada por fuera. Así tu proyecto es reproducible.

### Agrega tu primera dependencia

```bash
uv add rich
```

`rich` es una librería para imprimir tablas y texto con color en la terminal. La vamos a usar
en el script de verificación de más abajo — no tiene nada que ver con lo que instalamos
antes, es pura comodidad visual para que leas los resultados sin esfuerzo.

Fíjate qué acaba de pasar: `uv add` creó (o actualizó) dos archivos:

| Archivo | Qué contiene | Por qué existe |
|---|---|---|
| `pyproject.toml` | Qué necesita tu proyecto | Es la lista de compras |
| `uv.lock` | Las versiones exactas instaladas | Es el recibo — garantiza que a todos les funcione igual |

Ambos se suben al repositorio. Nunca los borres a mano.

### Crea la carpeta de evidencia

```bash
mkdir -p entregas/s01/evidencia
```

En Windows con PowerShell:
```powershell
New-Item -ItemType Directory -Force -Path entregas/s01/evidencia
```

Ahí vas a guardar la captura de la verificación final. **Los dos scripts de hoy los vas a
crear directo en la raíz del proyecto** — con solo dos archivos, una subcarpeta adicional no
suma orden, solo un paso más.

> La carpeta `app/` (con `routers/`, `services/`, `clients/`) todavía no la creamos. Esa
> organización tiene sentido cuando empieces a escribir el backend con FastAPI, en la
> Clase 2 — hoy estaría vacía y sin propósito.

---

## Paso 4 — Tu primer script: confirmar que Python y uv se hablan

### Por qué empezamos con algo tan simple

Antes de instalar nada más complejo, necesitas un termómetro rápido: ¿el intérprete de Python
que corre dentro de tu proyecto (el que maneja `uv`) es el mismo que esperas? Este primer
script no verifica nada de tu proyecto todavía — solo confirma que la cadena "tú escribes `uv run python` →
se ejecuta tu Python 3.12 → imprime algo" funciona sin errores.

Crea `hello_course.py` **en la raíz del proyecto**:

```python
"""Confirms the environment can run Python correctly, before installing anything else."""

import sys
import platform


def main() -> None:
    name = sys.argv[1] if len(sys.argv) > 1 else "participant"
    print(f"Hello, {name}")
    print(f"Python version : {platform.python_version()}")
    print(f"Executable     : {sys.executable}")


if __name__ == "__main__":
    main()
```

Ejecuta:

```bash
uv run python hello_course.py "Tu Nombre"
```

**Fíjate en `uv run`.** No ejecutamos `python hello_course.py` directo — eso usaría el
Python de tu sistema operativo, no el que `uv` fijó para este proyecto. `uv run` es el
prefijo que vas a usar **siempre** en este curso para correr algo dentro del entorno del
proyecto. Si alguna vez ves `ModuleNotFoundError` con algo que "sí instalaste", casi siempre
es porque olvidaste el `uv run`.

---

## Paso 5 — Git y GitHub: dónde vive tu código y por qué eso es un riesgo

### El problema que resuelve

Vas a construir un proyecto en varias clases, en tu máquina. Git guarda el historial de
cambios para que puedas volver atrás si rompes algo, y GitHub aloja una copia remota — la
que tu docente revisa y la que tú recuperas si tu computador falla.

### El riesgo que trae: los secretos

En clases más adelante vas a tener credenciales sensibles (claves de acceso a servicios,
contraseñas de bases de datos, etc.) guardadas en un archivo `.env` dentro de este mismo
proyecto. Si ese archivo se sube a GitHub por accidente, cualquiera puede tomar esa
credencial y usarla a tu nombre. **Una clave publicada en GitHub la detectan bots
automáticos en menos de un minuto.** Por eso este paso va antes del primer commit, no después.

### Verifica si ya tienes Git

```bash
git --version
```

Si el comando responde con un número de versión, salta directo a "Crea el `.gitignore`" más
abajo. Si no lo tienes, instálalo según tu sistema:

### Instala en macOS

macOS te va a ofrecer instalar las **Command Line Tools de Xcode** en una ventana emergente
la primera vez que ejecutes `git --version` — acepta esa opción, es la forma más simple. Si
no aparece la ventana:

```bash
xcode-select --install
```

Alternativa, si prefieres una versión más reciente que la de Apple:

```bash
brew install git
```

### Instala en Windows

Descarga el instalador desde [git-scm.com/downloads](https://git-scm.com/downloads) y
ejecútalo. Las opciones por defecto del instalador funcionan bien para este curso; no hace
falta cambiar nada salvo que ya sepas lo que buscas. Al terminar, verifica en PowerShell:

```powershell
git --version
```

### Instala en Linux

**Ubuntu / Debian**
```bash
sudo apt update
sudo apt install git
```

**Fedora**
```bash
sudo dnf install git
```

**Arch Linux**
```bash
sudo pacman -S git
```

### Configura tu identidad (una sola vez, en cualquier sistema)

Git necesita saber quién eres para firmar tus commits — hazlo antes del primer commit de
hoy si no lo has hecho antes en esta máquina:

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu-correo@ejemplo.com"
```

Usa el mismo correo que registraste en GitHub.

### Crea el `.gitignore` — la lista de lo que Git debe ignorar

En la raíz del proyecto, crea `.gitignore`:

```gitignore
# Secrets — never committed
.env
.env.local
*.key

# Python
__pycache__/
*.py[cod]
.venv/
build/
dist/
*.egg-info/

# Editors and OS
.idea/
.vscode/
.DS_Store

# Local test data
*.sqlite3
*.db
```

### Crea `.env.example` — la plantilla pública de tus secretos

```dotenv
# Copy this file as .env and fill in real values.
# .env is never committed to the repository; this file is.
DATABASE_URL=
API_KEY=
APP_ENV=development
```

Esto le dice a cualquiera que clone tu repo (o a ti mismo en tres semanas) qué variables
necesita definir, sin exponer ningún valor real.

### Ahora sí, el primer commit

```bash
git init
git add .
git status --short
```

**Detente en el `git status --short` y lee la lista.** Confirma que **no aparece `.env`**
(hoy probablemente ni siquiera lo has creado, pero acostúmbrate a revisar siempre antes de
un commit). Si todo se ve bien:

```bash
git commit -m "Class 1: working environment"
git branch -M main
```

### Conecta con GitHub

Crea el repositorio vacío en GitHub con el nombre `curso-mcp-<tu-usuario>` y luego:

```bash
git remote add origin https://github.com/<tu-usuario>/curso-mcp-<tu-usuario>.git
git push -u origin main
```

Refresca la página de tu repositorio en GitHub: ese es tu comprobante de que quedó publicado.

---

## Paso 6 — Docker: por qué lo instalamos hoy aunque no lo usemos hoy

### Qué problema resuelve (adelanto)

"Funciona en mi máquina" es el problema más viejo del desarrollo de software: tu compañero
tiene otra versión de una librería, u otro sistema operativo, y tu backend no le corre igual.
Docker empaqueta tu aplicación con **todo** lo que necesita para funcionar, de modo que corre
igual en cualquier computador. Más adelante en el curso vas a empaquetar tu backend completo
con Docker para desplegarlo.

### Instala Docker Desktop en macOS

Descarga el instalador desde [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
y elige el chip correcto de tu Mac:

- **Apple Silicon** (M1/M2/M3/M4) → "Mac with Apple Chip"
- **Intel** → "Mac with Intel Chip"

Si no sabes cuál chip tienes: menú Apple → *Acerca de este Mac*.

Instala el `.dmg` como cualquier aplicación (arrastra el ícono a Aplicaciones), ábrelo desde
Launchpad, y acepta los permisos que te pida. Espera a que el ícono de la ballena en la barra
de menú deje de animarse — eso indica que Docker terminó de iniciar.

### Instala Docker Desktop en Windows

Descarga el instalador desde
[docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) y
ejecútalo. Docker Desktop en Windows necesita **WSL2** (Windows Subsystem for Linux); el
instalador te avisa si falta y te guía para activarlo — puede pedirte reiniciar el
computador una vez. Después del reinicio, abre Docker Desktop desde el menú de inicio y
espera a que el ícono de la ballena en la barra de tareas se quede quieto.

> Si tu Windows es Home (no Pro), igual funciona: WSL2 es compatible con ambas ediciones.

### Instala Docker en Linux

En Linux, Docker corre nativo (sin Docker Desktop, aunque también existe esa opción). La
instalación varía por distribución; el script de conveniencia de Docker cubre las más
comunes:

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

Para no tener que anteponer `sudo` a cada comando de Docker, agrega tu usuario al grupo
`docker` y cierra sesión y vuelve a entrar (o reinicia):

```bash
sudo usermod -aG docker $USER
```

### Hoy solo verificamos que está instalado (en cualquier sistema)

No vamos a construir ninguna imagen todavía. Solo confirmamos que Docker está corriendo:

```bash
docker run hello-world
```

Si ves un mensaje que empieza con "Hello from Docker!", quedó listo. Si Docker Desktop no
está abierto (macOS/Windows), ábrelo, espera a que el ícono deje de girar, y reintenta.

> Si esto no te funciona hoy, **no te detiene**. Coméntalo con tu docente y sigue —
> lo vas a necesitar más adelante, no en la próxima clase.

---

## Paso 7 — El momento de la verdad: verificar todo junto

Ya instalaste y probaste cada pieza por separado. Este último script hace exactamente lo
mismo que hiciste a mano en los pasos 1 a 6, pero en un solo comando — y de paso revisa que
tu `.gitignore` de verdad proteja el `.env`.

Crea `verify_environment.py` **en la raíz del proyecto**:

```python
"""Environment traffic light for the course.

Checks, in one place, everything you set up by hand in steps 1 to 6:
Python, uv, Git, Docker, and the .gitignore protection.
"""

import shutil
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()

ROOT = Path(__file__).resolve().parent


def version_of(command: list[str]) -> str | None:
    if shutil.which(command[0]) is None:
        return None
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=15)
    except Exception:
        return None
    output = (result.stdout + result.stderr).strip()
    return output.splitlines()[0] if output else None


def check_gitignore() -> tuple[bool, str]:
    path = ROOT / ".gitignore"
    if not path.exists():
        return False, "not found"
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    if ".env" in lines:
        return True, "protects .env"
    return False, "exists but does not ignore .env"


def main() -> None:
    python_ok = sys.version_info[:2] == (3, 12)

    checks: list[tuple[str, bool, str, bool]] = [
        ("Python 3.12", python_ok, sys.version.split()[0], True),
    ]

    uv_version = version_of(["uv", "--version"])
    checks.append(("uv", uv_version is not None, uv_version or "not found", True))

    git_version = version_of(["git", "--version"])
    checks.append(("Git", git_version is not None, git_version or "not found", True))

    docker_version = version_of(["docker", "--version"])
    checks.append(
        ("Docker", docker_version is not None, docker_version or "not found (not required yet)", False)
    )

    gitignore_ok, gitignore_detail = check_gitignore()
    checks.append((".gitignore protects .env", gitignore_ok, gitignore_detail, True))

    table = Table(title="Environment check — Class 1")
    table.add_column("Component", style="bold")
    table.add_column("Status", justify="center")
    table.add_column("Detail", style="dim")

    for name, ok, detail, required in checks:
        status = "[green]OK[/green]" if ok else ("[red]FAIL[/red]" if required else "[yellow]WARNING[/yellow]")
        table.add_row(name, status, detail)

    console.print(table)

    required_ok = all(ok for _, ok, _, required in checks if required)

    if required_ok:
        console.print("\n[bold green]Environment ready. See you in Class 2.[/bold green]")
    else:
        console.print("\n[bold red]Some required components failed. Fix them before Class 2.[/bold red]")

    sys.exit(0 if required_ok else 1)


if __name__ == "__main__":
    main()
```

Ejecuta:

```bash
uv run python verify_environment.py
```

Lee la tabla de arriba hacia abajo: cada fila es uno de los pasos que acabas de hacer a mano.
Si todo salió verde, tu entorno está listo para la Clase 2. Si algo sale en rojo, vuelve al
paso correspondiente de esta guía — no lo dejes pendiente.

---

## Cierre: guarda la evidencia

Copia (o toma una captura de) la salida de `verify_environment.py` y pégala en tu
`README.md`:

```markdown
## Environment check — Class 1

                                 Environment check — Class 1                                 
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Component                ┃ Status ┃ Detail                                                ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python 3.12              │   OK   │ 3.12.4                                                │
│ uv                       │   OK   │ uv 0.12.6 (7938ca5d5 2026-08-25 aarch64-apple-darwin) │
│ Git                      │   OK   │ git version 2.50.1 (Apple Git-155)                    │
│ Docker                   │   OK   │ Docker version 29.4.0, build 9d7ad9f                  │
│ .gitignore protects .env │   OK   │ protects .env                                         │
└──────────────────────────┴────────┴───────────────────────────────────────────────────────┘

Environment ready. See you in Class 2.
```

Haz un último commit y push:

```bash
git add .
git commit -m "Class 1: environment check"
git push
```

**Cierre de la sesión:** esta práctica no se entrega ni se sube a ninguna plataforma. Al
terminar, muéstrale a tu docente (o dile en voz alta en la sesión) que tu tabla de
`verify_environment.py` salió en verde. El objetivo de hoy es que tu entorno quede listo —
no generar un entregable.

---

## Checklist final

- [ ] `verify_environment.py` muestra Python, uv, Git en verde.
- [ ] El `.gitignore` protege tu `.env` (aunque aún no tengas uno).
- [ ] El repositorio está publicado en GitHub.
- [ ] `hello_course.py` corrió con tu nombre.
- [ ] Docker respondió (o quedó reportado en el foro si no).

---

## Si algo falla

| Síntoma | Causa habitual | Qué hacer |
|---|---|---|
| `uv: command not found` | El PATH no se recargó | Cierra y abre la terminal |
| macOS: `zsh: command not found: brew` tras instalar Homebrew | El PATH no se actualizó | Ejecuta el comando `eval` que Homebrew imprime al final de su instalación, o reabre la terminal |
| macOS: `python --version` da `Python 2.7.x` o no reconoce 3.12 | macOS trae su propio Python del sistema | Usa `python3.12 --version`, o dentro del proyecto simplemente `uv run python ...` — uv usa la versión correcta sin que tengas que cambiar el comando `python` global |
| `python` abre la Microsoft Store | Alias de Windows | Desactívalo en *Administrar alias de ejecución*, o usa `py -3.12` |
| `ModuleNotFoundError: rich` | Ejecutaste sin `uv run` | Usa siempre `uv run python ...` |
| PowerShell no deja ejecutar scripts | Política de ejecución | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Linux: `docker: permission denied` al correr `docker run` | Tu usuario no está en el grupo `docker` | `sudo usermod -aG docker $USER`, luego cierra sesión y vuelve a entrar |
| Linux: Docker Desktop / Engine no arranca tras instalar | El servicio no está activo | `sudo systemctl start docker` y `sudo systemctl enable docker` para que arranque solo |
| `git push` pide contraseña y falla | GitHub ya no acepta contraseña | Usa un Personal Access Token o configura SSH |
| `remote origin already exists` | Ya habías corrido ese comando | `git remote set-url origin <url>` |
| `docker: Cannot connect to the Docker daemon` | Docker Desktop cerrado | Ábrelo y reintenta |
| macOS: Docker Desktop pide permisos de virtualización o no abre | Falta autorizar la extensión del sistema | *Preferencias del Sistema → Privacidad y Seguridad*, permite la extensión de Docker, y reinicia el Mac si te lo pide |
| Subiste `.env` sin querer | El `.gitignore` llegó tarde | `git rm --cached .env`, commit, y **rota la clave afectada** |

Cualquier otro caso: consúltalo con tu docente en la sesión, con la captura completa del error.
