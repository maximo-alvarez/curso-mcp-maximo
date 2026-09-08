# Clase 2 — Práctica guiada: tu primera llamada a un modelo, y por qué olvida

**Curso:** Programación de Backend y MCP en Python para IA Generativa
**Sesión:** 2 de 10
**Duración:** 50 minutos + 10 minutos de cierre
**Calificación:** ninguna — pero `gemini_client.py` y `conversation.py` los vuelves a usar en las próximas sesiones.

> **Convención del curso:** el código (nombres de variables, funciones, comentarios,
> docstrings) siempre se escribe en inglés, aunque las clases se dicten en español.

---

## Antes de empezar

Hoy no tocamos FastAPI ni backend todavía — eso viene después. El hilo conductor de la
sesión es uno solo: llamar a Gemini desde Python puro, y ver con sus propias manos **dos
fallos distintos**, antes de resolverlos:

1. **El olvido** (garantizado, pasa siempre) — el modelo no recuerda entre llamadas.
2. **El límite de solicitudes por minuto** (hay que provocarlo) — el tier gratuito no cobra
de más, pero sí corta si mandas demasiadas llamadas seguidas.

Usamos **`gemini-2.5-flash`** en todo el código de hoy — es el mismo modelo que vieron en
las diapositivas, y el único que instalan y ejecutan. En la teoría vieron cómo se ve el mismo
patrón en OpenAI y Anthropic: eso es solo para reconocerlo si algún día cambian de proveedor,
hoy no se escribe ni se corre.

> **Nota — por qué no usamos el modelo más nuevo:** al momento de escribir esta guía existe
> `gemini-3.5-flash-lite` (lanzado el 21 de julio de 2026), también gratuito y con un límite
> de solicitudes por minuto más alto (~15 RPM) que `gemini-2.5-flash` (~10 RPM). No lo usamos
> aquí por dos razones concretas, no solo por costumbre:
>
> 1. **Las 24 diapositivas de esta sesión ya están armadas con `gemini-2.5-flash`.** Cambiar
> solo el código de la práctica sin tocar las slides genera exactamente el tipo de
> desalineación que corregimos en la revisión anterior de esta guía.
> 2. **El Paso 9 depende de un RPM bajo para funcionar como está escrito.** Con el límite más
> alto de Flash-Lite, el `for` de 20 llamadas podría no alcanzar a disparar el error 429
> dentro del mismo minuto, y habría que recalcular el número de iteraciones.
>
> Si en una futura edición del curso se actualizan también las diapositivas a
> `gemini-3.5-flash-lite`, este `.md` debe migrarse junto con ellas — nombre del modelo y
> número de iteraciones del Paso 9 incluidos.

Necesitas tu proyecto de la Clase 1 (`curso-mcp-<tu-usuario>`) con Python 3.12 y `uv`
funcionando.

---

## Paso 1 — Consigue tu clave de Gemini

Entra a [aistudio.google.com/apikey](https://aistudio.google.com/apikey), inicia sesión con
tu cuenta de Google, y genera una API key nueva.

En la raíz de tu proyecto, crea (o edita) `.env`:

```dotenv
GEMINI_API_KEY=pega-aqui-tu-clave-real
```

Y agrega esta línea a tu `.env.example` existente (sin el valor real):

```dotenv
GEMINI_API_KEY=
```

Confirma que Git no la ve:

```bash
git status --short
```

`.env` **no debe aparecer** en la lista.

---

## Paso 2 — Instala el SDK de Gemini

```bash
uv add google-genai python-dotenv
```

---

## Paso 3 — El request mínimo y la anatomía de la respuesta

### Por qué empezamos así

Antes de pensar en roles o memoria, confirma que la cadena completa funciona, y acostúmbrate
desde ya a mirar más que `response.text` — eso es lo que cuesta y lo que te dice si la
respuesta vino completa.

Crea `gemini_client.py` **en la raíz del proyecto**:

```python
"""First real call to Gemini: minimal request, full response anatomy."""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODEL = "gemini-2.5-flash"


def main() -> None:
    response = client.models.generate_content(
        model=MODEL,
        contents=[
            {"role": "user", "parts": [{"text": "¿Qué es una API?"}]},
        ],
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=200,
        ),
    )

    print(response.text)

    u = response.usage_metadata
    print(f"prompt    : {u.prompt_token_count}")
    print(f"respuesta : {u.candidates_token_count}")
    print(f"TOTAL     : {u.total_token_count}")
    print(f"finish    : {response.candidates[0].finish_reason}")


if __name__ == "__main__":
    main()
```

Ejecuta:

```bash
uv run python gemini_client.py
```

**Fíjate en `finish`.** Si dice `STOP`, el modelo terminó solo. Si alguna vez dice
`MAX_TOKENS`, la respuesta viene cortada por el `max_output_tokens` que pusiste — y aun así
pagaste por ella completa. Es el campo que la mayoría ignora y que hoy no vas a ignorar.

**Nota sobre `contents`:** es una lista de diccionarios planos — sin magia, es JSON que viaja
por HTTP. Ahí está la semilla de la memoria que van a construir más adelante.

---

## Paso 4 — Los tres roles y el system prompt

### Los roles

Gemini usa `user` y `model` (no `assistant`, como sí usan OpenAI y Anthropic — si escribes
`assistant` aquí, falla). El tercer rol, `system`, no va dentro de `contents`: va aparte, en
`system_instruction`.

Modifica `gemini_client.py`:

```python
"""Calls Gemini with a system instruction and explicit generation parameters."""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODEL = "gemini-2.5-flash"

SYSTEM_INSTRUCTION = (
    "Eres un instructor de programación para principiantes. "
    "Respondes en español, máximo 3 frases. "
    "Sin jerga sin explicar, sin inventar funciones."
)


def ask(prompt: str, temperature: float = 0.7) -> tuple[str, str]:
    """Returns (text, finish_reason)."""
    response = client.models.generate_content(
        model=MODEL,
        contents=[{"role": "user", "parts": [{"text": prompt}]}],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=temperature,
            max_output_tokens=200,
        ),
    )
    finish_reason = str(response.candidates[0].finish_reason)
    if "MAX_TOKENS" in finish_reason:
        print("[warning] La respuesta viene truncada por max_output_tokens.")
    return response.text, finish_reason


def main() -> None:
    text, _ = ask("¿Qué opinas de var en JS?")
    print(text)


if __name__ == "__main__":
    main()
```

Ejecuta de nuevo. El `system_instruction` **no se pierde** cuando más adelante recortes el
historial — vive en la config, no en `contents`.

### Experimento rápido (2 min)

Cambia `temperature` a `0.1` y luego a `1.3` en la misma pregunta y compara. Este parámetro,
junto con `max_output_tokens` y `top_p`, son los tres que de verdad vas a tocar — el resto se
queda como está por defecto.

---

## Paso 5 — El token, ahora como presupuesto

### La idea nueva

Ya saben qué es un token (Clase 1). Lo nuevo: es un **presupuesto**, no solo un costo — y se
puede medir *antes* de gastarlo, con `count_tokens`.

Agrega esto a `gemini_client.py`:

```python
CONTEXT_WINDOW_LIMIT = 1_048_576  # gemini-2.5-flash


def print_budget(contents: list[dict]) -> None:
    tokens = client.models.count_tokens(model=MODEL, contents=contents)
    used_ratio = tokens.total_tokens / CONTEXT_WINDOW_LIMIT
    print(f"Historial: {tokens.total_tokens} tokens ({used_ratio:.4%} de la ventana)")
```

Pruébalo con cualquier lista de `contents` que ya tengas. Este es el chequeo que vas a volver
a usar cuando el historial empiece a crecer, en el Paso 7.

---

## Paso 6 — Autopsia: el modelo no recuerda

### El experimento

Al final de `gemini_client.py`, reemplaza `main()`:

```python
def main() -> None:
    r1_text, _ = ask("Hola, me llamo Valeria.")
    print("BOT:", r1_text)

    r2_text, _ = ask("¿Cómo me llamo?")
    print("BOT:", r2_text)


if __name__ == "__main__":
    main()
```

Ejecuta:

```bash
uv run python gemini_client.py
```

El modelo va a decir que no sabe tu nombre. **No es un bug tuyo ni falta de memoria del
modelo** — cada llamada a `generate_content` es una petición HTTP independiente, sin ningún
estado compartido con la anterior. Antes de seguir, discute con tu compañero: ¿por qué pasa
esto? Recojan una hipótesis antes de pasar al siguiente paso.

---

## Paso 7 — Construye la memoria

### La idea

Si el modelo no recuerda, tú se lo repites: reenvías **todo el historial** en cada llamada.

Crea `conversation.py` en la raíz del proyecto:

```python
"""In-memory conversation history — the model 'remembers' because we resend it."""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODEL = "gemini-2.5-flash"
SYSTEM_INSTRUCTION = "Eres un asistente breve. Respondes en español."

# List of plain dicts, same shape as `contents` — nothing hidden here.
history: list[dict] = []


def send(message: str) -> str:
    history.append({"role": "user", "parts": [{"text": message}]})

    response = client.models.generate_content(
        model=MODEL,
        contents=history,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
    )

    history.append({"role": "model", "parts": [{"text": response.text}]})
    return response.text


def main() -> None:
    # 8 turns: the fact goes in turn 1, and gets asked back at turn 8.
    print(send("Me llamo Alex y mi color favorito es el verde."))
    print(send("¿Qué framework de Python vimos en la Clase 1?"))
    print(send("Dame un ejemplo de dato que no cabe en un int."))
    print(send("¿Qué hace el comando uv init?"))
    print(send("Explica en una frase qué es un token."))
    print(send("¿Qué significa que una API sea stateless?"))
    print(send("¿Para qué sirve un archivo .env?"))
    print(send("¿Cómo me llamo y cuál es mi color favorito?"))


if __name__ == "__main__":
    main()
```

Ejecuta:

```bash
uv run python conversation.py
```

En el turno 8, el modelo debe recordar tanto tu nombre como tu color favorito — porque
`send()` reenvía `history` completo cada vez. El modelo no cambió entre el Paso 6 y este; lo
que cambió es lo que le mandas.

---

## Paso 8 — La ventana deslizante (y su límite)

### Recorta el historial

Agrega esto a `conversation.py`, antes de `def send`:

```python
MAX_TURNS = 10  # keeps the last 10 user/model exchanges (20 entries)


def trim_history() -> None:
    max_entries = MAX_TURNS * 2
    if len(history) > max_entries:
        del history[:-max_entries]
```

Y llama a `trim_history()` al inicio de `send()`, antes de agregar el nuevo mensaje:

```python
def send(message: str) -> str:
    trim_history()
    history.append({"role": "user", "parts": [{"text": message}]})
    ...
```

Con `MAX_TURNS = 10`, tu conversación de 8 turnos del Paso 7 cabe completa — nada se pierde
todavía.

### Ahora, el trade-off (demo, no se entrega)

La ventana deslizante **sí pierde el principio de la conversación** cuando la charla es más
larga que `MAX_TURNS`. Compruébalo con un experimento aparte, sin tocar tu conversación
calificada:

```python
def demo_forgetting() -> None:
    """Standalone demo: a short window forgets the beginning. Not part of the graded run."""
    global history, MAX_TURNS
    history = []
    original_max = MAX_TURNS
    MAX_TURNS = 3  # small on purpose, to force forgetting

    print(send("Mi mascota se llama Rocko."))
    for i in range(1, 7):
        print(send(f"Pregunta de relleno número {i}."))
    print(send("¿Cómo se llama mi mascota?"))  # already dropped from the window

    MAX_TURNS = original_max
    history = []
```

Corre `demo_forgetting()` desde una consola de Python o un `if` temporal. Vas a ver que esta
vez el modelo **sí** olvida, porque `MAX_TURNS=3` es demasiado pequeño para una charla de 8
turnos. Esa es exactamente la fila "En contra" de la tabla de estrategias que vieron en la
teoría: barata, pero pierde el principio si la conversación crece.

---

## Paso 9 — Cuando el proveedor dice "ya no más"

### Provócalo a propósito

En el tier gratuito no hay "gasto" — hay un **límite de solicitudes por minuto (RPM)**.
Agrega esto al final de `conversation.py`:

```python
def trigger_rate_limit() -> None:
    """Sends several requests back to back to hit the free tier's requests-per-minute cap."""
    global history
    history = []
    for i in range(1, 21):
        print(f"Request {i}: {send(f'Cuenta hasta {i}.')}")
```

Ejecútalo. En algún punto de las 20 llamadas vas a ver un error con `RESOURCE_EXHAUSTED` o
`429`. Es el proveedor diciéndote "ya recibí todas las solicitudes que te tocan este minuto"
— no es un bug tuyo.

### Maneja el error correctamente

Un detalle importante: `429` técnicamente es un `ClientError` (4xx), pero **sí se reintenta**
— a diferencia de un `400` por un request mal armado, que no tiene caso reintentar tal cual.
Envuelve la llamada dentro de `send()`:

```python
import time

from google.genai import errors


def send(message: str, _retries: int = 0) -> str:
    trim_history()
    history.append({"role": "user", "parts": [{"text": message}]})

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=history,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
        )
    except errors.ClientError as exc:
        if exc.code == 429 and _retries < 3:
            wait = 2 ** _retries
            print(f"[429] Límite de RPM alcanzado. Reintentando en {wait}s...")
            time.sleep(wait)
            history.pop()  # avoid duplicating the same user turn
            return send(message, _retries=_retries + 1)
        history.pop()
        return f"Error del cliente ({exc.code}): {exc.message}. No se reintenta."
    except errors.ServerError as exc:
        if _retries < 3:
            wait = 2 ** _retries
            print(f"[{exc.code}] Error del servidor. Reintentando en {wait}s...")
            time.sleep(wait)
            history.pop()
            return send(message, _retries=_retries + 1)
        history.pop()
        return f"El servicio no respondió tras varios intentos ({exc.code})."

    finish_reason = str(response.candidates[0].finish_reason)
    if "MAX_TOKENS" in finish_reason:
        print("[warning] Respuesta truncada por max_output_tokens.")

    history.append({"role": "model", "parts": [{"text": response.text}]})
    return response.text
```

**Regla que queda implementada:** `ClientError` con código `429` → reintenta con backoff
exponencial. Cualquier otro `ClientError` (400, 401, 403) → no se reintenta, se reporta.
`ServerError` (5xx) → reintenta igual que el 429.

---

## Guía de entrega

Misma convención que la Clase 1: una carpeta de evidencia por sesión, un README que documenta
lo que pasó, y un commit con mensaje claro. Nada de plataformas externas — el repositorio de
GitHub es la entrega.

### Paso A — Crea la carpeta de evidencia de esta sesión

```bash
mkdir -p entregas/s02/evidencia
```

En Windows con PowerShell:
```powershell
New-Item -ItemType Directory -Force -Path entregas/s02/evidencia
```

### Paso B — Guarda la evidencia de ejecución

Dentro de `entregas/s02/evidencia`, guarda:

1. **Una captura de pantalla (o el texto copiado) de la corrida completa de `conversation.py`**
del Paso 7 — los 8 turnos, mostrando que el modelo recordó el nombre y el color en el
turno 8. Nómbrala `memoria.png` (o `.txt` si prefieres pegar el texto).
2. **Una captura del error 429 del Paso 9**, mostrando el mensaje `RESOURCE_EXHAUSTED` y que
tu código lo manejó sin caerse (el `print` de "Reintentando en...", o el mensaje final si se
agotaron los reintentos). Nómbrala `rate_limit.png` (o `.txt`).

No hace falta nada más en esta carpeta — dos evidencias, una por cada fallo que la sesión
pidió provocar.

### Paso C — Documenta en el README

Agrega esta sección a tu `README.md` (debajo de la de la Clase 1, no la reemplaces):

```markdown
## Clase 2 — APIs de IA Generativa y memoria conversacional

### Conversación de 8 turnos (Paso 7)

Ver evidencia en `entregas/s02/evidencia/memoria.png`.

<pega aquí también el texto de la salida, aunque ya esté en la captura>

### Por qué elegí ventana deslizante

<explica en 2-3 líneas por qué esta estrategia y no resumen progresivo,
memoria selectiva o almacenamiento externo, para este caso>

### Límite de solicitudes provocado (Paso 9)

Ver evidencia en `entregas/s02/evidencia/rate_limit.png`.

<una línea confirmando que el error se manejó sin que el programa se cayera>
```

### Paso D — Commit y push

Revisa antes de commitear, como en la Clase 1:

```bash
git status --short
```

Confirma que **no aparece `.env`**. Si todo se ve bien:

```bash
git add .
git commit -m "Class 2: Gemini client with conversation memory and rate-limit handling"
git push
```

Refresca tu repositorio en GitHub y confirma que `entregas/s02/evidencia` y el README
actualizado quedaron publicados — ese es tu comprobante de entrega.

---

## Checklist de entrega

*(Idéntico al criterio de aceptación de la sesión — no lo simplifiques.)*

- [ ] El script llama a Gemini con `system_instruction`, `temperature` y `max_output_tokens`
explícitos.
- [ ] Mantiene una conversación de al menos 8 turnos y el modelo recuerda un dato del turno 1.
- [ ] Implementa una estrategia de memoria y el README justifica por qué esa y no otra.
- [ ] Registra en consola el `total_token_count` de cada llamada.
- [ ] Verifica `finish_reason` y avisa cuando la respuesta viene truncada.
- [ ] Captura `ClientError` y `ServerError` por separado, con reintento en 429 y en 5xx.
- [ ] La API key se lee de una variable de entorno: no aparece en el código ni en el repo.
- [ ] `entregas/s02/evidencia` contiene la captura de la conversación de 8 turnos y la del 429.
- [ ] El README tiene la sección "Clase 2" completa, con la justificación de la estrategia.
- [ ] Commit y push hechos; el repositorio en GitHub refleja todo lo anterior.

---

## Si algo falla

| Síntoma | Causa habitual | Qué hacer |
|---|---|---|
| `KeyError: 'GEMINI_API_KEY'` | `.env` no existe o no está en la raíz | Confirma que `.env` está junto a `gemini_client.py` |
| `PermissionDenied` o `401` | Clave inválida o con espacios | Regenera la clave y pégala sin comillas ni espacios |
| `404` al llamar al modelo | Nombre de modelo obsoleto (p. ej. `gemini-2.0-flash`, dado de baja) | Usa exactamente `gemini-2.5-flash` |
| `RESOURCE_EXHAUSTED` o `429` | Límite de solicitudes **por minuto** del tier gratuito — esperado en el Paso 9 | Espera 60 segundos; no es un bug ni un tema de gasto |
| `ModuleNotFoundError: google` | Ejecutaste sin `uv run`, o falta `uv add` | Usa siempre `uv run python ...` |
| El Paso 7 no recuerda el color en el turno 8 | `trim_history()` se llamó con un `MAX_TURNS` menor a 8 | Confirma que `MAX_TURNS = 10` en la conversación calificada |
| `git status --short` muestra `.env` | El `.gitignore` no tiene la línea `.env` | Agrega la línea; si ya hiciste commit: `git rm --cached .env` y **rota la clave** |

Cualquier otro caso: consúltalo con tu docente en la sesión, con la captura completa del error.
