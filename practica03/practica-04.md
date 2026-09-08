# Guía Práctica — Pruebas, Cobertura y Seguridad (con Skills, Agentes y Hooks)
## Sesión 5 · Jueves · Programación de Backend y MCP en Python para IA Generativa

**Duración de la práctica:** 75 minutos, después de la teoría.
**Punto de partida:** el código del miércoles (`s4/mi-proyecto-speckit/`).

**Novedad de hoy:** van a construir una pequeña jerarquía de agentes especializados sobre la base que ya dejó Spec Kit el miércoles.

## La arquitectura (léela antes de empezar)

```
SKILLS  →  son capacidades puntuales (una tarea, sin criterio propio)
AGENTES →  tienen un rol y un criterio; usan skills específicas para cumplirlo
TÚ (vía agy) → orquestas, invocando a cada agente en el momento correcto
```

Un agente **no es** una skill — un agente **llama** a una o varias skills, con un criterio propio sobre cuándo y cómo usarlas. Hoy van a construir:

- 6 **skills** (`qa-unit`, `qa-integration`, `qa-coverage`, `qa-security`, `qa-report`, `qa-orchestrate`) — escritas a mano, para que entiendan exactamente qué le piden a cada una.
- 3 **agentes** (`tester-agent`, `security-agent`, `report-agent`) — cada uno con acceso *solo* a las skills que necesita (mínimo privilegio, igual que en el diseño de la Agencia de Agentes).
- Ustedes, invocando a cada agente en secuencia, hacen de orquestador.

### Cómo se invoca cada cosa (importante, no se mezclan)

| Qué es | Cómo se invoca | Confirmado en la práctica |
|---|---|---|
| Skill | `/nombre-de-la-skill` | ✅ Sí (así funcionó `/speckit-specify` el miércoles) |
| Agente | Lenguaje natural: *"Usa el agente nombre-agente para..."* | ⚠️ No confirmado — puede que también acepte `/nombre-agente`, pruébalo antes de clase |

Las skills usan `/` porque así lo comprobaste con Spec Kit. Los agentes se invocan distinto porque son un concepto de otra capa (un rol con reglas, no un comando suelto) — si `agy` también acepta `/tester-agent`, mejor, pero no lo des por hecho sin probarlo primero.

## Cronograma

| Bloque | Tiempo | Acumulado |
|---|---|---|
| Setup — spec de tests + skills + agentes + órdenes de trabajo | 27 min | 27 min |
| A — Invocar al `tester-agent` (con orden de trabajo) | 5 min | 32 min |
| Descanso | 5 min | 37 min |
| B — Provocar fallo, ver el hook bloquear, corregir | 10 min | 47 min |
| C — Invocar al `security-agent` (con orden de trabajo) | 5 min | 52 min |
| D — Invocar al `report-agent` (con orden de trabajo) | 4 min | 56 min |
| E — Automatizar todo: `/qa-orchestrate` | 10 min | 66 min |
| Reflexión sobre la orquestación | 5 min | 71 min |
| Cierre | 5 min | 76 min |

> 🧑‍🏫 **Nota de tiempo:** esta versión completa (manual + automática) corre ~81 min, un poco por encima del bloque de práctica habitual. Si vas corto de tiempo, la opción más limpia es **saltar los Bloques C y D manuales** (invocar security-agent y report-agent uno por uno) e ir directo del Bloque B al Bloque E — la orquestación automática ya los ejecuta a ambos, así que no se pierde contenido, solo la demostración paso a paso de cada uno por separado.

## Antes de empezar

- [ ] Tu carpeta `s4/mi-proyecto-speckit/` del miércoles con código funcionando.
- [ ] `agy` instalado y autenticado.
- [ ] Instala dependencias:
  ```bash
  cd s4/mi-proyecto-speckit
  uv pip install pytest pytest-cov pytest-json-report
  ```

---

## Setup — Construir la estructura completa (15 min)

### Paso 1 — Confirmar que tu código corre (2 min)

```bash
python -c "import [tu_modulo]"
```

### Paso 2 — Explorar lo que Spec Kit ya dejó (2 min)

```bash
ls .agents/skills/
```

Ya deberías ver las carpetas de Spec Kit del miércoles (`speckit-specify`, `speckit-plan`, etc.). Hoy agregamos **más skills propias** dentro de esa misma estructura, y por primera vez, una carpeta nueva: `.agents/agents/`.

### Paso 3 — Escribir la spec de las pruebas, ANTES de generar nada (5 min)

Aquí está el punto que evita el vibe coding en las pruebas: si le piden al agente "genera tests" sin más, él decide qué probar — y puede improvisar, igual que el lunes. En vez de eso, ustedes definen primero **qué debe verificar cada test**, en un archivo corto.

Crea `test-spec.md`:

```markdown
## Qué deben verificar los tests unitarios
- [ ] [función 1]: dado [entrada], debe devolver [salida esperada]
- [ ] [función 1]: con [caso borde de tu spec_manual.md], debe [comportamiento esperado]
- [ ] [función 2]: ...

## Qué debe verificar el test de integración
- [ ] El flujo completo, desde [entrada inicial] hasta [salida final], debe [resultado esperado]
```

**Ejemplo (conversor de temperatura):**
```markdown
## Qué deben verificar los tests unitarios
- [ ] convertir_temperatura: dado 25°C, debe devolver 77°F
- [ ] convertir_temperatura: con texto en vez de número, debe dar error claro, no excepción
- [ ] convertir_temperatura: con Kelvin negativo, debe rechazarlo

## Qué debe verificar el test de integración
- [ ] El flujo completo (pedir conversión → validar entrada → devolver resultado) debe funcionar de punta a punta con una entrada válida
```

Esta es literalmente la misma spec del lunes, aplicada a las pruebas en vez de al código.

### Paso 4 — Crear las 6 skills de QA, explicadas una por una (10 min)

Vas a escribir cada `SKILL.md` a mano — esto es intencional: cada archivo es corto, y entender exactamente qué le estás pidiendo a la skill es más valioso hoy que generarlas automáticamente.

```bash
mkdir -p .agents/skills/qa-unit .agents/skills/qa-integration .agents/skills/qa-coverage .agents/skills/qa-security .agents/skills/qa-report .agents/skills/qa-orchestrate
```

**`.agents/skills/qa-unit/SKILL.md`**
```markdown
---
name: qa-unit
description: Genera tests unitarios siguiendo estrictamente lo definido en test-spec.md, sin improvisar qué probar.
---
# Instrucciones
1. Lee `test-spec.md`. Si no existe, DETENTE y pide al usuario que lo cree primero — no inventes criterios propios.
2. Para cada punto de "Qué deben verificar los tests unitarios", genera un test con assert real que lo cumpla exactamente.
3. No agregues tests para casos que no estén en `test-spec.md` — si crees que falta algo importante, sugiérelo al final, no lo generes por tu cuenta.
4. Guarda en `tests/test_unitario.py`. Corre `pytest tests/test_unitario.py -v` y reporta cuántos pasaron.
```

**`.agents/skills/qa-integration/SKILL.md`**
```markdown
---
name: qa-integration
description: Genera un test de integración siguiendo lo definido en test-spec.md, sin improvisar el flujo a probar.
---
# Instrucciones
1. Lee `test-spec.md`, sección "Qué debe verificar el test de integración". Si no existe, DETENTE y pide que se cree primero.
2. Genera un test que verifique exactamente ese flujo, de punta a punta.
3. Guarda en `tests/test_integracion.py`. Corre `pytest tests/test_integracion.py -v` y reporta el resultado.
```

**`.agents/skills/qa-coverage/SKILL.md`**
```markdown
---
name: qa-coverage
description: Ejecuta y resume el reporte de cobertura de tests del proyecto, señalando líneas sin probar.
---
# Instrucciones
1. Corre `pytest --cov=. --cov-report=term-missing`.
2. Resume: porcentaje total, y qué líneas "Missing" son casos borde olvidados vs. código no usado.
3. No agregues tests automáticamente — solo diagnostica.
```

**`.agents/skills/qa-security/SKILL.md`**
```markdown
---
name: qa-security
description: Revisa el proyecto en busca de secretos expuestos, validación de entradas insuficiente y manejo de excepciones riesgoso.
---
# Instrucciones
1. Busca claves/contraseñas escritas directamente en el código.
2. Revisa validación de entradas (tipo, formato, longitud, rango).
3. Busca `except:` genérico o `except: pass`.
4. Reporta en esta tabla:

| Caso | Lo que se encontró | Corrección sugerida |
|---|---|---|
| 🔑 Secreto expuesto | [hallazgo o "sin hallazgos"] | [sugerencia] |
| 🧪 Validación de entradas | [hallazgo o "sin hallazgos"] | [sugerencia] |
| 🚪 Manejo de excepciones | [hallazgo o "sin hallazgos"] | [sugerencia] |

5. No corrijas automáticamente — solo diagnostica.
```

**`.agents/skills/qa-report/SKILL.md`**
```markdown
---
name: qa-report
description: Ejecuta el script de reporte de calidad y genera reporte-qa.html.
---
# Instrucciones
1. Corre: `python .agents/skills/qa-report/generar_reporte.py`
2. Abre `reporte-qa.html` y reporta solo el veredicto final y un resumen de una línea.
3. Si "REQUIERE CORRECCIÓN", lista los 2-3 problemas más importantes.
```

Guarda también el script `.agents/skills/qa-report/generar_reporte.py` (genera tests, cobertura y seguridad en un HTML consolidado con Python puro, sin gastar tokens de IA en redactarlo).

**`.agents/skills/qa-orchestrate/SKILL.md`** *(esta es especial — no la usen todavía, la activan en el Bloque E)*
```markdown
---
name: qa-orchestrate
description: Ejecuta el flujo completo de calidad invocando en orden a tester-agent, security-agent y report-agent, sin pedir confirmación entre cada uno.
---
# Instrucciones
1. Verifica que exista `test-spec.md` y `ordenes-agentes.md`. Si falta alguno, detente y pide que se cree.
2. Invoca al agente tester-agent siguiendo la orden en ordenes-agentes.md. Espera a que termine por completo.
3. Invoca al agente security-agent siguiendo la orden en ordenes-agentes.md. Espera a que termine por completo.
4. Invoca al agente report-agent siguiendo la orden en ordenes-agentes.md.
5. Presenta al usuario el veredicto final, con un resumen de 1 línea de qué hizo cada agente en el camino.

No pidas confirmación entre fase y fase — este es un flujo automático de punta a punta.
```

> 🧑‍🏫 **Al explicar cada skill, señala el patrón repetido:** frontmatter (`name` + `description`) → sección de Instrucciones numeradas → un paso final que dice qué reportar. Una vez que ven ese patrón en la primera skill, las siguientes 5 se explican solas.

> Nota la diferencia: `qa-orchestrate` **no es un agente** — no tiene rol propio ni "personalidad". Es una receta de secuencia que la sesión principal de `agy` sigue, delegando el trabajo real a los 3 agentes especializados.

### Paso 5 — Crear los 3 agentes que USAN esas skills (5 min)

> ⚠️ **Verificar antes de clase:** la ubicación (`.agents/agents/`) y el formato exacto de un agente en `agy` no están confirmados — sigue la convención de Claude Code. Corre `agy --help agents` o revisa su documentación para confirmar antes de comprometerte con esto en vivo.

```bash
mkdir -p .agents/agents
```

**`.agents/agents/tester-agent.md`**
```markdown
---
name: tester-agent
description: Especialista en calidad funcional. Úsalo para generar o correr tests unitarios, de integración, y medir cobertura.
tools: qa-unit, qa-integration, qa-coverage
---

Eres el Tester-Agent. Tu única responsabilidad es la calidad funcional del código:
que existan tests, que pasen, y que la cobertura sea razonable.

Nunca improvises qué probar. Siempre exige que exista `test-spec.md` antes de generar tests —
si no existe, detente y pide que se cree primero. No te ocupes de seguridad — eso lo hace otro agente.
No generes el reporte final — eso también es de otro agente.

Cuando te invoquen:
1. Verifica que exista `test-spec.md`.
2. Usa la skill qa-unit.
3. Usa la skill qa-integration.
4. Usa la skill qa-coverage.
5. Resume tus hallazgos en 3-4 líneas, sin extenderte.
```

**`.agents/agents/security-agent.md`**
```markdown
---
name: security-agent
description: Especialista en seguridad básica. Úsalo para revisar secretos expuestos, validación de entradas y manejo de excepciones.
tools: qa-security
---

Eres el Security-Agent. Tu única responsabilidad es encontrar riesgos de seguridad básicos.
No te importa si los tests pasan o no — eso es del Tester-Agent.

Cuando te invoquen:
1. Usa la skill qa-security.
2. Presenta la tabla de 3 filas tal como la generó la skill, sin resumirla de más.
```

**`.agents/agents/report-agent.md`**
```markdown
---
name: report-agent
description: Consolida resultados de calidad en un reporte final. Úsalo al final del proceso, después del Tester y Security.
tools: qa-report
---

Eres el Report-Agent. Solo consolidas — no vuelves a analizar nada por tu cuenta,
confías en lo que ya hicieron el Tester-Agent y el Security-Agent.

Cuando te invoquen:
1. Usa la skill qa-report.
2. Presenta el veredicto final de forma clara y breve.
```

### Paso 6 — Escribir la orden de trabajo de cada agente (5 min)

Aquí cierra el círculo anti-vibe-coding: invocar a un agente con un prompt suelto ("revisa la calidad") es tan vago como pedirle código sin spec el lunes. Antes de invocar a cada agente, escriben una **orden de trabajo** — la misma disciplina de siempre (tarea + criterios de aceptación + entregable esperado), aplicada ahora a qué le piden al agente.

Crea `ordenes-agentes.md`:

```markdown
## Orden: tester-agent
**Tarea:** Verificar la calidad funcional de este proyecto.
**Criterios de aceptación de esta tarea:**
- [ ] Genera y corre tests unitarios según test-spec.md
- [ ] Genera y corre el test de integración según test-spec.md
- [ ] Reporta el % de cobertura y qué líneas quedaron sin probar
**Entregable esperado:** resumen de 3-4 líneas, sin código completo pegado en el chat.

## Orden: security-agent
**Tarea:** Revisar riesgos de seguridad básicos en este proyecto.
**Criterios de aceptación de esta tarea:**
- [ ] Revisa secretos expuestos, validación de entradas, manejo de excepciones
- [ ] Reporta en la tabla de exactamente 3 filas
**Entregable esperado:** la tabla, sin agregar hallazgos fuera de esas 3 categorías.

## Orden: report-agent
**Tarea:** Generar el veredicto final de calidad.
**Criterios de aceptación de esta tarea:**
- [ ] Ejecuta el script de reporte (no redacta el reporte con IA)
- [ ] Presenta el veredicto y, si aplica, los 2-3 problemas más importantes
**Entregable esperado:** veredicto + resumen de una línea, no el HTML completo pegado en el chat.
```

De ahora en adelante, cuando invoques a un agente, referencia su orden en vez de improvisar el pedido:

```
> Usa el agente tester-agent siguiendo la orden de trabajo en ordenes-agentes.md, sección "tester-agent".
```

> 🧑‍🏫 **Por qué esto importa más de lo que parece:** sin esta orden, dos alumnos que invocan "al mismo" tester-agent con distintas frases sueltas pueden obtener resultados distintos — exactamente el mismo problema del lunes, pero un nivel más arriba en la cadena. La orden de trabajo es lo que hace que invocar un agente sea reproducible, no una conversación improvisada.


> ⚠️ **Verificar antes de clase:** la ubicación (`.agents/agents/`) y el formato exacto de un agente en `agy` no están confirmados — sigue la convención de Claude Code. Corre `agy --help agents` o revisa su documentación para confirmar antes de comprometerte con esto en vivo.

```bash
mkdir -p .agents/agents
```

**`.agents/agents/tester-agent.md`**
```markdown
---
name: tester-agent
description: Especialista en calidad funcional. Úsalo para generar o correr tests unitarios, de integración, y medir cobertura.
tools: qa-unit, qa-integration, qa-coverage
---

Eres el Tester-Agent. Tu única responsabilidad es la calidad funcional del código:
que existan tests, que pasen, y que la cobertura sea razonable.

Nunca improvises qué probar. Siempre exige que exista `test-spec.md` antes de generar tests —
si no existe, detente y pide que se cree primero. No te ocupes de seguridad — eso lo hace otro agente.
No generes el reporte final — eso también es de otro agente.

Cuando te invoquen:
1. Verifica que exista `test-spec.md`.
2. Usa la skill qa-unit.
3. Usa la skill qa-integration.
4. Usa la skill qa-coverage.
5. Resume tus hallazgos en 3-4 líneas, sin extenderte.
```

**`.agents/agents/security-agent.md`**
```markdown
---
name: security-agent
description: Especialista en seguridad básica. Úsalo para revisar secretos expuestos, validación de entradas y manejo de excepciones.
tools: qa-security
---

Eres el Security-Agent. Tu única responsabilidad es encontrar riesgos de seguridad básicos.
No te importa si los tests pasan o no — eso es del Tester-Agent.

Cuando te invoquen:
1. Usa la skill qa-security.
2. Presenta la tabla de 3 filas tal como la generó la skill, sin resumirla de más.
```

**`.agents/agents/report-agent.md`**
```markdown
---
name: report-agent
description: Consolida resultados de calidad en un reporte final. Úsalo al final del proceso, después del Tester y Security.
tools: qa-report
---

Eres el Report-Agent. Solo consolidas — no vuelves a analizar nada por tu cuenta,
confías en lo que ya hicieron el Tester-Agent y el Security-Agent.

Cuando te invoquen:
1. Usa la skill qa-report.
2. Presenta el veredicto final de forma clara y breve.
```

---

## BLOQUE A — Invocar al `tester-agent` (12 min)

```
> Usa el agente tester-agent siguiendo la orden de trabajo en ordenes-agentes.md, sección "tester-agent".
```

**Observa mientras corre:** ¿el agente se comportó distinto a cuando invocaban skills sueltas? ¿Explicó su rol antes de actuar?

**Checkpoint:** `tests/test_unitario.py` y `tests/test_integracion.py` existen, cada test corresponde a un punto de tu `test-spec.md` (no hay tests "de más" que ustedes no pidieron), y tienes un resumen de cobertura.

> 🧑‍🏫 **Si `agy` no reconoce la sintaxis de agentes:** ten como plan B invocar las 3 skills directamente (`/qa-unit`, `/qa-integration`, `/qa-coverage`) y explicar verbalmente el concepto de agente/rol sin depender de que la mecánica funcione en vivo.

---

## 🔄 DESCANSO (5 min)

---

## BLOQUE B — Provocar un fallo y ver el hook actuar (15 min)

### Paso 1 — Instalar el hook de bloqueo (5 min)

Crea `.agents/hooks/gate-tests.sh`:
```bash
#!/bin/bash
pytest --tb=no -q
if [ $? -ne 0 ]; then
  echo "BLOQUEADO: hay tests fallando. Corrige antes de continuar." >&2
  exit 2
fi
exit 0
```
```bash
chmod +x .agents/hooks/gate-tests.sh
```

Y `.agents/hooks/hooks.json`:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "edit_file|write_file",
        "hooks": [{ "type": "command", "command": "bash .agents/hooks/gate-tests.sh" }]
      }
    ]
  }
}
```

### Paso 2 — Provocar el fallo (4 min)

```
> Modifica [una función de tu proyecto] para que tenga un bug sutil, sin decirme cuál es.
```

### Paso 3 — Observar el bloqueo y corregir (6 min)

```
> Este test está fallando: [pega el nombre del test y el mensaje de error completo]
> Corrige el código para que pase.
```

> 🧑‍🏫 **Si el hook no funciona:** sigue el bloque manualmente (`pytest -v`, identifica, corrige) y retómalo como ejercicio de investigación fuera de clase.

---

## BLOQUE C — Invocar al `security-agent` (10 min)

```
> Usa el agente security-agent siguiendo la orden de trabajo en ordenes-agentes.md, sección "security-agent".
```

Para cada fila con hallazgo real, corrige:
```
> Corrige [hallazgo específico].
```

**Nota de arquitectura:** fíjate que el `security-agent` solo tiene acceso a `qa-security` — no podría, aunque quisiera, tocar tus tests. Eso es mínimo privilegio aplicado a agentes, el mismo principio de la Agencia de Agentes.

---

## BLOQUE D — Invocar al `report-agent` (8 min)

```
> Usa el agente report-agent siguiendo la orden de trabajo en ordenes-agentes.md, sección "report-agent".
```

Abre `reporte-qa.html` y revisa el veredicto.

---

## BLOQUE E — Automatizar todo: `/qa-orchestrate` (12 min)

### Qué vas a hacer y por qué

Ya invocaste a los 3 agentes a mano, uno por uno, y viste cómo se conectan por archivos. Ahora vas a activar la skill orquestadora para que ese mismo trabajo ocurra con **un solo comando**, sin que tú decidas el orden cada vez.

### Paso 1 — Provocar un problema nuevo (3 min)

Para que la corrida de hoy no muestre "todo ya está bien" (poco interesante), rompe algo de nuevo:
```
> Modifica [otra función] para que tenga un bug distinto al de antes.
```

### Paso 2 — Correr todo con un solo comando (7 min)

```
/qa-orchestrate
```

Observa: el `tester-agent` corre, encuentra el fallo (o el hook lo bloquea), el `security-agent` corre después, y al final el `report-agent` te da el veredicto — todo sin que tú tengas que invocar cada uno por separado.

### Paso 3 — Comparar la experiencia (2 min)

Responde:
- ¿Qué se sintió distinto entre invocar cada agente a mano (Bloques A, C, D) y usar `/qa-orchestrate`?
- ¿Perdiste algo de control, o solo perdiste pasos repetitivos?

> 🧑‍🏫 **Si el hook bloquea a mitad de la orquestación:** es el comportamiento correcto — el `tester-agent` no puede avanzar con tests rotos, así que la cadena se detiene ahí hasta que se corrija. Es una buena oportunidad para señalar que "automático" no significa "sin control".

---

## Cómo se conectan los 3 agentes (léelo antes de la reflexión)

No hay comunicación directa entre agentes — cada uno deja su resultado en un **archivo**, y el siguiente lo lee de ahí. Así de simple:

```
tester-agent    → escribe → tests/test_*.py, resultado de cobertura
security-agent  → escribe → tabla de hallazgos (la reportas tú, o la guardas)
report-agent    → LEE      → corre pytest + cobertura + busca hallazgos de nuevo
                → escribe → reporte-qa.html (veredicto final)
```

El `report-agent` no necesita que le "pasen" nada explícitamente — su skill (`qa-report`) vuelve a correr todo por su cuenta (tests, cobertura, seguridad) y arma el HTML. Por eso el orden importa: si lo invocas antes de que el `tester-agent` haya generado tests, el reporte va a mostrar 0 tests, no un error.

**Esa es toda la "orquestación" de hoy:** tú decides el orden (Tester → Security → Report) porque el resultado de uno le da sentido al siguiente, no porque haya una conexión mágica entre ellos.

## Reflexión sobre la orquestación (5 min)

Responde:
1. ¿En qué se sintió distinto invocar "agentes" comparado con invocar "skills" sueltas?
2. ¿Qué pasaría si el `security-agent` intentara modificar tus tests? ¿Podría, con la configuración que armaron?
3. Tú fuiste el orquestador hoy — invocando a cada agente en el momento correcto. ¿Cómo sería si otro agente (no ustedes) decidiera ese orden?

> Esa última pregunta es exactamente el paso que sigue: un orquestador automático, no ustedes a mano. Es la Agencia de Agentes.

---

## CIERRE (5 min)

En `resultados-jueves.md`, pega la tabla de seguridad y responde:
1. ¿Cuál fue el veredicto final?
2. Completa: *"El inspector encontró ______ que el cocinero no había visto."*

**Guarda todo tu trabajo**, incluidas las skills, los agentes y el hook — son la base directa del proyecto que viene.

---

## Entregable de la sesión

```
mi-proyecto-speckit/
├── [código corregido hoy]
├── test-spec.md
├── ordenes-agentes.md
├── .agents/
│   ├── skills/qa-unit, qa-integration, qa-coverage, qa-security, qa-report, qa-orchestrate/
│   ├── agents/tester-agent.md, security-agent.md, report-agent.md
│   └── hooks/gate-tests.sh + hooks.json
├── tests/test_unitario.py + test_integracion.py
├── reporte-qa.html
├── .env.example
├── .gitignore
└── resultados-jueves.md
```

- Repositorio con todo lo anterior.
- **Informe de Entrega en PDF** con: captura del hook bloqueando, captura de `reporte-qa.html`, breve explicación de la arquitectura skills→agentes, y enlace al repositorio.
