# Guía Práctica — Vibe Coding: El Experimento Guiado

**Sesión 3 · Lunes · Programación de Backend y MCP en Python para IA Generativa**
**Duración total:** 45 minutos
**Formato:** el instructor va pidiendo en voz alta y ejecutando en pantalla; cada alumno predice antes de ver el resultado y ejecuta en paralelo en su propia máquina.

## De qué se trata

Vas a seguir al instructor paso a paso: antes de que él corra cada pedido, tú vas a predecir qué crees que va a pasar. Después lo vas a correr tú también, en tu propia máquina, y vas a comparar tres cosas: tu predicción, el resultado del instructor, y tu propio resultado. El objetivo es sentir que el mismo pedido, sin spec, no siempre produce lo mismo — ni siquiera es 100% predecible para quien lo pide.

No hay entrega de proyecto en esta guía — es desechable a propósito. Lo que entregas es tu reflexión y tus capturas.

## Antes de empezar

- [ ] Tener **Python 3.12** instalado.
- [ ] Tener **uv** instalado (gestor de entornos y paquetes de Python que se usará durante todo el curso).
- [ ] Tener `agy` instalado y autenticado con tu propia cuenta.
- [ ] Crear tu carpeta de trabajo e inicializar el entorno con `uv`:
  ```bash
  mkdir vibe-coding && cd vibe-coding
  uv init --python 3.12
  ```
- [ ] Tener un archivo `notas.md` abierto para tus predicciones y observaciones.
- [ ] Estar atento a la pantalla del instructor durante cada ronda — vas un paso "detrás" de él a propósito.

---

## Ronda 1 — Validador de contraseñas (10 min)

### Paso 1 — Predicción (1 min, ANTES de correr nada)

El instructor va a anunciar este pedido:
```
> hazme un validador de contraseñas
```

**Antes de que lo corra**, escribe en tu `notas.md` tu predicción:
- ¿Cuántos caracteres mínimos crees que va a exigir?
- ¿Va a pedir mayúsculas, números o símbolos?
- ¿Qué crees que pasa si le mandas una contraseña vacía?

### Paso 2 — Ejecución en paralelo (4 min)

1. Corre exactamente el mismo pedido en tu propia máquina:
   ```bash
   agy
   ```
   ```
   > hazme un validador de contraseñas
   ```
2. Prueba con estos 3 casos:
   - `12345`
   - `password`
   - `` (vacía)

### Paso 3 — Comparación (5 min, en grupo)

Cuando el instructor lo indique, compara en tu `notas.md`:

| Pregunta | Tu predicción | Tu resultado real | ¿Coincide con lo del instructor? |
|---|---|---|---|
| Longitud mínima exigida | | | |
| ¿Pidió símbolo/mayúscula/número? | | | |
| ¿Qué pasó con la contraseña vacía? | | | |

Levanta la mano si tu resultado fue **distinto** al del instructor con el mismo pedido exacto — eso es parte del punto de la ronda.

---

## Ronda 2 — Agregar validación de email (10 min)

### Paso 1 — Predicción (1 min)

El instructor va a pedir, sobre el código anterior:
```
> agrégale que también valide un formato de email
```

Antes de que lo corra, predice:
- ¿Crees que el agente va a mantener el mismo estilo de respuesta que en la Ronda 1, o lo va a cambiar?
- ¿Qué crees que hace con un email mal escrito como `ana@`?

### Paso 2 — Ejecución en paralelo (4 min)

1. Corre el mismo pedido en tu código.
2. Prueba con:
   - Un email válido (ej. `ana@correo.com`)
   - Un email mal formado (ej. `ana@`)
   - Un email vacío

### Paso 3 — Comparación (5 min, en grupo)

| Pregunta | Tu predicción | Tu resultado real |
|---|---|---|
| ¿Mantuvo el mismo formato de respuesta de la Ronda 1? | | |
| ¿Qué hizo con el email mal formado? | | |

Pregunta para el grupo: ¿a alguien el agente le reescribió también la parte de la contraseña, sin que se lo pidieran?

---

## Ronda 3 — Lista de varios usuarios (10 min)

### Paso 1 — Predicción (1 min)

El instructor va a pedir:
```
> ahora que maneje una lista de varios usuarios, cada uno con su contraseña y su email
```

Antes de correrlo, predice:
- ¿Crees que algo de lo que ya funcionaba en la Ronda 1 o 2 se va a romper con este cambio?
- ¿Cómo crees que va a estructurar la lista de usuarios (diccionario, lista de objetos, archivo)?

### Paso 2 — Ejecución en paralelo (4 min)

1. Corre el mismo pedido.
2. Agrega 2 usuarios distintos y pide la lista completa.

### Paso 3 — Comparación (5 min, en grupo)

| Pregunta | Tu predicción | Tu resultado real |
|---|---|---|
| ¿Se rompió algo que ya funcionaba? ¿Qué? | | |
| ¿Cómo estructuró la lista de usuarios? | | |

---

## Bloque de cierre — Provocar la falla en vivo (10 min)

### Paso 1 — El instructor narra y provoca (3 min)

El instructor va a pedir algo que probablemente cause un problema:
```
> ahora que la validación de contraseña sea opcional para usuarios administradores
```
Antes de que lo corra, anota en `notas.md`: ¿qué crees que puede salir mal con este cambio?

### Paso 2 — Corres el mismo pedido (4 min)

Ejecuta lo mismo en tu código y revisa: ¿algo que ya funcionaba dejó de tener sentido o se comporta raro ahora?

### Paso 3 — Reporte rápido en voz alta (3 min)

Cuando el instructor lo pida, comparte en una frase: ¿qué se rompió o qué quedó inconsistente en tu código después de este último pedido?

---

## Reflexión final (5 min — escríbela en tu `notas.md`)

Responde estas preguntas antes de terminar la sesión:

1. ¿En qué ronda tu predicción se alejó más de lo que realmente pasó? ¿Por qué crees que fallaste esa predicción?
2. ¿Tu resultado fue exactamente igual al del instructor en todas las rondas, o hubo diferencias con el mismo pedido? ¿Qué te dice eso sobre pedir cosas sin spec?
3. Completa la frase: *"Si yo tuviera que darle este código a otra persona mañana, tendría que explicarle ______ porque eso no está escrito en ningún lado."*

> Guarda esa última respuesta — es el punto de partida exacto de lo que vas a hacer el miércoles: escribir eso que "no está escrito en ningún lado" como una spec de verdad.

---

## Entregable de la sesión

- Captura de pantalla de al menos 2 de las 3 rondas (tu predicción + tu resultado real).
- Captura del bloque de cierre (el pedido que provocó la falla).
- Tus 3 respuestas de la reflexión final.

Sube esto en el **Informe de Entrega en PDF** (plantilla del AVAC, disponible en Contenido → Inicio). No hace falta repositorio de código para esta sesión — este código es desechable a propósito, es el punto de la clase.
