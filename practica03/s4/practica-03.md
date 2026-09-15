# Guía Práctica — Spec Sencilla + Spec Kit
## Sesión 4 · Miércoles · Programación de Backend y MCP en Python para IA Generativa

**Duración de la práctica:** 75 minutos, después de la teoría.

## Cronograma

| Bloque | Tiempo | Acumulado |
|---|---|---|
| 3.A — Spec a mano | 30 min | 30 min |
| Descanso | 5 min | 35 min |
| 3.B — Spec Kit | 30 min | 65 min |
| Comparar resultados | 5 min | 70 min |
| Cierre | 5 min | 75 min |

## Antes de empezar

- [ ] Python 3.12 y `uv` instalados.
- [ ] `agy` instalado y autenticado.
- [ ] Carpeta de trabajo: `mkdir s4 && cd s4`

---

## BLOQUE 3.A — Spec a mano (30 min)

### Paso 1 — Elegir proyecto (3 min)

Crea la subcarpeta de este bloque: `mkdir clase-sdd && cd clase-sdd`

Elige un dominio simple, distinto al de contraseñas del lunes:

- Conversor de unidades (temperatura, longitud, peso)
- Calculadora de propina y división de cuenta
- Generador de códigos de descuento
- Validador de formato de placa vehicular

Si no decides en 1 minuto, toma el conversor de temperatura.

### Paso 2 — Escribir la spec, guiado sección por sección (15 min)

Crea el archivo `spec_manual.md`. Vas a llenarlo en tres pasadas, respondiendo una pregunta a la vez — no escribas todo de corrido, sigue el orden.

#### 2.1 — Objetivo (3 min)

Responde en una sola frase: **¿qué hace tu programa?**

Guíate con esta estructura: *"[Verbo en infinitivo] + [qué] + [para quién o con qué propósito, si aplica]."*

Ejemplo (conversor de temperatura):
> Convertir una temperatura entre Celsius, Fahrenheit y Kelvin.

Escribe la tuya:
```markdown
## Objetivo
[tu frase aquí]
```

#### 2.2 — Criterios de aceptación (6 min)

Ahora responde: **¿cómo sé que mi programa está bien?** Escribe entre 3 y 5 criterios. Para cada uno, hazte esta pregunta de control: *¿esto se puede marcar como ✅ o ❌ sin discusión?*

Preguntas guía para generarlos:
- ¿Qué transformación exacta debe hacer? (ej. "convierte X a Y correctamente")
- ¿Hay algún formato de salida específico? (ej. "redondea a 2 decimales")
- ¿Hay algún límite o regla de negocio? (ej. "rechaza valores menores a X")

Ejemplo:
```markdown
## Criterios de aceptación
- [ ] Convierte correctamente de Celsius a Fahrenheit y viceversa
- [ ] Convierte correctamente de Celsius a Kelvin y viceversa
- [ ] Redondea el resultado a 2 decimales
- [ ] Rechaza una temperatura en Kelvin menor a 0
```

Escribe los tuyos ahora, usando las 3 preguntas guía de arriba.

**Antes de seguir, revisa cada criterio que escribiste:** si alguno dice algo como "que sea rápido" o "que sea fácil de usar", bórralo y vuelve a escribirlo con un número o condición concreta.

#### 2.3 — Casos borde (6 min)

Responde: **¿qué pasa cuando algo sale raro?** Escribe entre 2 y 4 casos borde. Usa estas 4 preguntas guía, una por una:

1. ¿Qué pasa si el usuario no manda ningún dato (vacío)?
2. ¿Qué pasa si manda un tipo de dato que no esperabas (texto en vez de número, por ejemplo)?
3. ¿Qué pasa si manda un valor válido pero extremo (muy grande, negativo, en el límite)?
4. ¿Qué pasa si manda el mismo dato dos veces, o algo repetido/redundante?

No necesitas responder las 4 — elige las 2-4 que apliquen mejor a tu proyecto.

Ejemplo:
```markdown
## Casos borde
- Valor no numérico como entrada (ej. "abc") → error claro, no una excepción sin control
- Mismo valor de entrada y salida (ej. Celsius a Celsius) → debe devolver el mismo número
- Números negativos válidos en Celsius/Fahrenheit → deben procesarse sin problema
```

Escribe los tuyos ahora.

**Checkpoint del Paso 2:** tu `spec_manual.md` debe tener las tres secciones completas: Objetivo (1 frase), Criterios de aceptación (3-5 bullets verificables), Casos borde (2-4 situaciones límite).

### Paso 3 — Implementar con `agy` (12 min)

Pega tu spec completa en el pedido:

```
> Implementa [nombre del proyecto] siguiendo esta spec: [pegar contenido completo de spec_manual.md]
```

Mientras corre, define tus 3 casos de prueba:

| Tipo de caso | Qué es |
|---|---|
| Caso normal | Un uso típico y esperado |
| Caso borde de tu spec | Uno de los que escribiste en 2.3 |
| Caso no contemplado | Algo que NO pusiste en la spec — observa qué hace el agente aquí |

Prueba los 3 casos y anota el resultado de cada uno. El caso "no contemplado" es el más interesante — muestra qué hace el agente cuando se queda sin instrucciones.

> ⏱️ A los 12 minutos, corta aquí aunque no hayas terminado de probar todo.

> 🧑‍🏫 **Qué esperar:** en pruebas reales, `agy` a veces genera tests propios por iniciativa (sin que se le pidan) al implementar la spec — es normal, déjalo pasar sin explicarlo hoy. Guarda tus 3 casos de prueba en un archivo `resultados-3a.md` para poder compararlos después con la Parte B.

---

## 🔄 DESCANSO (5 min)

---

## BLOQUE 3.B — Mismo proyecto con Spec Kit (30 min)

### Paso 1 — Instalar Spec Kit (5 min)

```bash
cd ..
mkdir mi-proyecto-speckit && cd mi-proyecto-speckit
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
specify init . --integration agy
```

Si `agy` no aparece soportado oficialmente:
```bash
specify init . --integration generic --ai-commands-dir .agy/commands/
```

Este comando instala Spec Kit como un conjunto de **skills** dentro de `.agents/skills/` (verás carpetas como `speckit-specify`, `speckit-plan`, `speckit-tasks`, `speckit-implement`, entre otras). Se invocan como comandos con `/`, igual que antes.

### Paso 2 — Correr el flujo, comando por comando (20 min)

No corras los 4 comandos seguidos sin mirar — después de cada uno, haz la pausa indicada.

#### 2.1 — `/speckit-specify` (5 min)

```
/speckit-specify
[describe el MISMO proyecto de la Parte A — usa palabras parecidas a tu spec_manual.md]
```

**Pausa de comparación (30 seg):** abre el archivo `spec.md` que se generó dentro de `specs/`. Compáralo con tu `spec_manual.md`. ¿Tiene alguna sección o detalle que tú no habías pensado? Anótalo mentalmente, lo vas a usar en la comparación final.

#### 2.2 — `/speckit-plan` (3 min)

```
/speckit-plan
```

Este comando decide cómo se va a estructurar el código (qué archivos, qué arquitectura). No hace falta leerlo a fondo — solo confirma que terminó sin errores.

#### 2.3 — `/speckit-tasks` (3 min)

```
/speckit-tasks
```

**Pausa de comparación (30 seg):** mira la lista de tareas generadas en `tasks.md`. Puede ser una lista larga (en pruebas reales llegó a 27 tareas) — no hace falta leerlas todas, solo nota si el orden se parece a como tú lo hubieras construido.

#### 2.4 — `/speckit-implement` (9 min)

```
/speckit-implement
```

Deja que corra hasta terminar.

> ⏱️ Si a los 20 minutos totales de este paso no terminaste, completa `/speckit-implement` como tarea antes del jueves. No te apures a costa de no entender qué hizo cada comando.

> 🧑‍🏫 **Qué esperar:** en pruebas reales, `/speckit-implement` generó automáticamente decenas de tests (llegó a 88 en un caso) sin que nadie los pidiera explícitamente — es parte de cómo trabaja el framework. No te detengas a explicarlos hoy; es un buen gancho para mencionar de pasada: "esto que generó solo, mañana lo vamos a examinar a fondo."

### Paso 3 — Probar el resultado (5 min)

Usa los **mismos 3 casos** del Bloque 3.A:

| Caso | Resultado spec a mano | Resultado Spec Kit |
|---|---|---|
| Caso normal | | |
| Caso borde de tu spec | | |
| Caso no contemplado | | |

Guarda este resultado en `resultados-3b.md`.

---

## COMPARAR RESULTADOS (5 min)

Completa esta tabla final en un archivo `comparacion.md` (fuera de ambas carpetas, a nivel de `s4/`):

| Aspecto | Spec a mano | Spec Kit |
|---|---|---|
| ¿Cubrió los mismos casos borde? | | |
| ¿Qué generó Spec Kit que tú no habías escrito? | | |
| ¿Qué se sintió más rápido de arrancar? | | |
| ¿Cuál te generó más confianza en el resultado? | | |

En ese mismo archivo `comparacion.md`, deja también la tabla de los 3 casos de ambos bloques lado a lado, y la frase de cierre del siguiente paso.

---

## CIERRE (5 min)

Completa en una frase:
> "La próxima vez que tenga un proyecto de tamaño [pequeño/mediano/grande], elegiría [spec a mano / Spec Kit] porque ______."

**Guarda todo el trabajo de hoy** — el jueves retomas este mismo código para agregarle tests reales y una revisión de seguridad básica. No empiezas un proyecto nuevo.

---

## Entregable de la sesión

Estructura de carpetas esperada al final:

```
s4/
├── clase-sdd/              (Bloque 3.A)
│   ├── spec_manual.md
│   ├── [código implementado]
│   └── resultados-3a.md
├── mi-proyecto-speckit/     (Bloque 3.B)
│   ├── [carpeta generada por specify init]
│   └── resultados-3b.md
└── comparacion.md
```

- Repositorio con ambas versiones completas.
- **Informe de Entrega en PDF** (plantilla del AVAC, Contenido → Inicio) con: breve explicación, captura de la spec a mano funcionando, captura del flujo `/speckit-specify → /speckit-implement`, la tabla comparativa, y el enlace al repositorio.
