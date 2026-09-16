# Sesión 9 — Práctica: Reconstruyendo "Gastos" con Spec-Driven Development (Spec Kit + IA)

**Duración de la práctica:** ~180 minutos (versión "con todas las de ley" — constitution, spec con `/speckit-clarify`, plan, tasks con `/speckit-analyze`, testing y seguridad detallados), +10 min opcionales por el reto de escritura de specs del Paso 4, +25-30 min opcionales si incluyes el anexo de subagentes/hooks/skills.
**Punto de partida:** el proyecto **"Gastos"** completo de las Sesiones 6-8 — arquitectura en capas, OAuth2+JWT, SQLAlchemy+Alembic, MCP reutilizando `services/`. Ábrelo en otra ventana, lo vas a usar como referencia y como criterio de aceptación.
**Novedad de hoy:** en vez de escribir código, escribes **cuatro documentos** (`constitution.md`, `spec.md`, `plan.md`, `tasks.md`) con el nivel de detalle suficiente para que un agente de IA construya el sistema completo — arquitectura, endpoints, seguridad, MCP y pruebas — sin que tengas que corregirle cada decisión sobre la marcha.

> **Principio de hoy:** un prompt vago produce código vago. Si tu `constitution.md` dice "sigue buenas prácticas de seguridad", el agente decide qué es "bueno". Si dice "hashea con bcrypt, JWT con HS256, expiración de 30 minutos, nunca acepta `usuario_id` del cliente", el agente no tiene margen de interpretación. Hoy escribimos del segundo tipo.

## El mapa completo de artefactos

```
constitution.md   → reglas NO NEGOCIABLES: arquitectura, SOLID, seguridad, MCP, testing
spec.md           → QUÉ hace el sistema: entidades, reglas de negocio, tabla de endpoints
plan.md           → CÓMO se construye: stack técnico + cómo se cumple cada artículo de la constitución
tasks.md          → tareas atómicas, cada una con su "definition of done" (código + test + verde)
prompt de /speckit-implement → cómo le pides al agente que ejecute tasks.md sin saltarse la constitución
```

## Cronograma

| Paso | Tiempo | Acumulado |
|---|---|---|
| 1 — Instalar Spec Kit y elegir agente | 10 min | 10 min |
| 2 — Inicializar el proyecto | 5 min | 15 min |
| 3 — `constitution.md` completa (arquitectura, SOLID, seguridad, MCP, testing) | 35 min | 50 min |
| 4 — `spec.md` completa (entidades, reglas de negocio, tabla de endpoints, `/speckit-clarify`) | 35 min | 85 min |
| **Reto opcional (Paso 4) — spec bien escrito vs. mal escrito** | +10 min | 95 min |
| 5 — `plan.md` completo (stack + cómo cumple cada artículo) | 20 min | 115 min |
| 6 — `tasks.md` con test y cobertura por tarea, más `/speckit-analyze` | 25 min | 140 min |
| 7 — El prompt correcto para `/speckit-implement` | 10 min | 150 min |
| 8 — Implementar de forma incremental y verificar cobertura | 20 min | 170 min |
| 9 — Reflexión y cierre | 10 min | 180 min |
| **Anexo (opcional) — Subagentes, hooks y skills para ahorrar tokens** | 25-30 min | 205-210 min |

## Antes de empezar

- [ ] Python 3.12, `uv`, `git`
- [ ] Google Antigravity (`agy`) **v1.20.5 o superior** instalado y autenticado — esta práctica está construida sobre esta integración de Spec Kit, que desde esa versión usa el layout `.agents/skills/` (plural); si usas otro agente (Copilot, Claude Code, Gemini CLI), la mecánica es la misma pero el Anexo de subagentes/hooks/skills no aplica tal cual
- [ ] `pytest-cov` disponible (`uv add --dev pytest-cov` una vez inicializado el proyecto)
- [ ] Los tests de `practica_05.md`, `practica_06.md`, `practica_07.md` a la mano
- [ ] Node.js instalado si vas a validar MCP con MCP Inspector (igual que en la Sesión 8)

---

## 0 — Antes de escribir: lo que la constitución da por sentado

El Paso 3 te va a dar los 8 artículos de la constitución ya redactados, listos para pegar. Antes de hacerlo, conviene entender el porqué de tres de ellos — para no pegarlos sin criterio, y para poder defenderlos cuando el agente proponga algo distinto.

### MCP: la constitución no inventa reglas nuevas, nombra las que ya aplicaron

- **Toda tool reutiliza `services/`, nunca al revés** (Artículo VI.1). Ya lo hicieron en la Sesión 8: `registrar_gasto` como tool y `POST /gastos/` como router llaman a la misma función de `services/`. Hoy esa costumbre se vuelve una regla escrita que el agente no puede ignorar.
- **La confirmación de una acción destructiva vive en el servidor** (Artículo VI.5), no en que el modelo "decida preguntar". Si `eliminar_gasto` dependiera de que el modelo fuera prudente, un prompt malicioso o un modelo distinto podría saltárselo sin que nadie lo note.
- **`stdio` no siempre puede propagar identidad real de usuario** (Artículo VI.4) — y la constitución no finge que sí. Si el transporte de hoy no puede llevar un JWT real hasta la tool, se documenta como *simplificación consciente* en el código.

🧑‍🏫 **Por qué importa nombrarlo así:** un agente de IA no distingue entre "no lo hice porque no aplicaba" y "no lo hice porque se me olvidó" a menos que el código (o un comentario) lo diga explícitamente.

### Testing: por qué el Artículo VII prohíbe `unittest.mock`

Si ya inyectan el repository por parámetro con un valor por defecto (DIP, Artículo II.3, Sesión 6), mockear en los tests unitarios de `services/` es reintroducir el acoplamiento que ese diseño ya resolvió. Por eso la constitución exige un repositorio falso que cumpla el mismo contrato que el real, no un mock — es la diferencia entre *simular* el comportamiento del repository y *reemplazarlo* por uno igual de válido.

La cobertura tampoco es aspiracional: **90% en `services/`, 80% global**, y — más importante que el porcentaje — **cobertura de reglas de negocio, no solo de líneas**. Cada regla explícita de `spec.md` necesita su propio test identificable. De hecho, son los mismos 5 casos de error que vas a escribir en el Paso 4: monto inválido, categoría inexistente, límite excedido, sin token, gasto de otro usuario. `spec.md` y `tasks.md` deberían poder leerse uno contra el otro y encontrar la misma lista.

### Gobernanza: el agente declara la desviación, no decide en silencio

La línea final de la constitución (sección "Gobernanza") es quizás el artículo más fácil de pasar por alto y el más importante de vigilar durante `/speckit-implement`: *si el agente necesita desviarse de un artículo, debe señalarlo explícitamente y esperar aprobación antes de continuar*.

Ejemplo del tipo de desviación que vas a ver hoy: al implementar `services/`, el agente decide "simplificar" validando la categoría directo en el router. Sin esta regla, ese cambio pasa silencioso. Con ella, el agente está obligado a decir "esto se sale del Artículo I.1, ¿lo permito?" — y decides tú, no él.

Guárdate esta pregunta para el Paso 9: **¿qué artículo terminaste "defendiendo" activamente hoy?**

### Sobre el Anexo (subagentes, hooks y skills)

Más adelante, el Anexo opcional explica cómo evitar pagar tokens de más releyendo tareas ya resueltas — con subagentes de contexto acotado, hooks que verifican mecánicamente sin gastar razonamiento del modelo, y skills que se cargan solo cuando hacen falta. No hace falta entenderlo ahora; solo ten presente que existe como salida si `/speckit-implement` se vuelve lento o repetitivo en un proyecto tuyo más grande que "Gastos".

---

## Paso 1 — Instalar Spec Kit (10 min)

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
specify --help
```

Las plantillas de `/speckit-constitution`, `/speckit-specify`, `/speckit-plan`, etc. ya vienen empaquetadas dentro de `specify-cli` — `specify init` no necesita red para generarlas.

**Checkpoint:** `specify --help` lista los comandos sin error.

---

## Paso 2 — Inicializar el proyecto (5 min)

```bash
specify init proyecto-curso-speckit --integration agy
cd proyecto-curso-speckit
```

⚠️ La bandera es `--integration`, no `--ai` (versiones antiguas de la documentación de Spec Kit usaban `--ai`; el CLI actual la rechaza).

Antigravity es una **integración basada en skills**: Spec Kit no instala archivos de prompt sueltos, instala `/speckit-constitution`, `/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-implement` (y los opcionales `/speckit-clarify`, `/speckit-analyze`, `/speckit-checklist`) como Agent Skills en `.agents/skills/speckit-<nombre>/SKILL.md` (con **s** — `.agents/`, no `.agent/`) que Antigravity carga solo cuando la tarea lo amerita — el mismo principio de "carga bajo demanda" del que habla el Anexo más abajo, aplicado desde el primer comando. Al iniciar verás una advertencia si tu versión de Antigravity es anterior a la v1.20.5, que es la que introdujo este layout.

**Checkpoint:** el directorio `.agents/skills/` existe con una carpeta `speckit-<nombre>/` por comando (podés listarlas con `ls .agents/skills/`), y esos comandos —con el prefijo `speckit-`— aparecen disponibles en Antigravity. `specify check` es útil para confirmar qué agentes de IA están instalados en tu máquina, pero no valida nada del proyecto ya inicializado; no lo uses como el checkpoint de este paso.

---

## Paso 3 — `constitution.md` completa (35 min)

No le pidas al agente "una buena constitución". Escríbela tú, artículo por artículo, basada en lo que ya viviste en las Sesiones 6-8. Ejecuta `/speckit-constitution` pegando (y adaptando) esto:

```markdown
# Constitución — Proyecto Control de Gastos

## Artículo I — Arquitectura en capas
1. `routers/` reciben la solicitud HTTP, delegan al service correspondiente y
   traducen su resultado (o excepción) a una respuesta HTTP. Un router NUNCA
   valida reglas de negocio (ej. "el monto debe ser positivo") — esa lógica
   vive en `services/`.
2. `services/` contienen toda la lógica de negocio. Un service NUNCA importa
   SQLAlchemy, `Session`, ni ningún detalle de persistencia directamente.
3. `repositories/` son la única capa autorizada a leer o escribir en la base
   de datos. Un repository no contiene reglas de negocio, solo operaciones
   de persistencia (guardar, listar, buscar, sumar).
4. `utils/` son funciones puras (mismo input → mismo output, sin efectos
   secundarios), sin importar nada de `services/`, `routers/` ni `repositories/`.
5. `mcp/tools/` NUNCA reimplementan lógica de `services/`. Si una tool de MCP
   y un router necesitan la misma regla, ambos llaman al mismo service.

## Artículo II — SOLID aplicado (no teórico)
1. **SRP**: cada función de `services/` hace una sola cosa. La validación
   (`_validar_x`) está separada de la orquestación (`registrar_x`).
2. **OCP**: agregar una categoría, un tipo de gasto o una regla nueva se hace
   agregando un valor a una constante o `Enum`, nunca reescribiendo un `if`
   ya existente.
3. **DIP**: todo service que necesite un repository lo recibe como parámetro
   con un valor por defecto (`def registrar_gasto(..., repo=gastos_repo)`),
   nunca lo importa fijo dentro del cuerpo de la función. Esto es innegociable:
   es lo que permite testear sin `unittest.mock`.
4. No se fuerza LSP ni ISP si el proyecto no tiene jerarquías de clases ni
   interfaces formales — no agregar complejidad artificial para cumplir un
   principio que no aplica todavía.

## Artículo III — Persistencia
1. SQLAlchemy como ORM, Alembic para migraciones. Ninguna sentencia SQL cruda
   concatenada con strings.
2. SQLite en desarrollo; el código de `database.py` debe funcionar contra
   Postgres sin tocar `services/` ni `routers/` (usar `connect_args`
   condicional solo para SQLite).
3. Cada modelo con datos de usuario incluye `usuario_id` como FK. Ninguna
   consulta de datos de usuario puede omitir el filtro por `usuario_id`.

## Artículo IV — Seguridad (no negociable)
1. Contraseñas: hash con `passlib[bcrypt]`. Nunca se guarda ni se loguea una
   contraseña en texto plano.
2. Autenticación: OAuth2 password flow + JWT firmado con HS256.
   `ACCESS_TOKEN_EXPIRE_MINUTES` configurable, nunca infinito.
3. `SECRET_KEY` y `DATABASE_URL` viven solo en `.env` (nunca versionado).
   `.env.example` documenta las variables necesarias sin valores reales.
   `SECRET_KEY` se genera con `openssl rand -hex 32` o equivalente
   criptográficamente seguro, nunca escrito a mano.
4. Autorización: el `usuario_id` para filtrar, crear o modificar un gasto
   SIEMPRE sale del token JWT decodificado (`get_current_user`), NUNCA de un
   parámetro de la URL, del body, ni de un query param. Esto aplica también
   a recursos ya existentes, no solo a la creación: cualquier operación sobre
   un gasto por `id` (leer, actualizar, eliminar) primero verifica que ese
   gasto pertenece al usuario autenticado, antes de tocarlo.
5. Un error no controlado (`Exception` genérica) devuelve `500` con
   `{"detail": "Error interno del servidor"}` — nunca un stack trace ni el
   mensaje de la excepción original al cliente. El detalle sí se loguea
   internamente.
6. Toda entrada de usuario se valida con schemas Pydantic antes de llegar a
   `services/`.

## Artículo V — Diseño de endpoints REST
1. Convención de verbos y códigos: `POST` crea (`201`), `GET` lista/lee
   (`200`), fallo de autenticación (`401`), recurso no encontrado (`404`),
   error de validación de schema (`422`), error de regla de negocio conocido
   (`400` con `{"detail": "..."}`). `403` se reserva para cuando el recurso
   solicitado existe pero pertenece a otro usuario y la operación lo
   identifica por `id` explícito en la ruta (ej. `PATCH /gastos/{id}`); un
   listado (`GET /gastos/`) NUNCA devuelve `403` — simplemente filtra por el
   `usuario_id` del JWT y nunca expone ni acepta el de otro usuario.
2. Toda lista paginada expone `skip` y `limit` como query params, con
   valores por defecto razonables (ej. `skip=0, limit=20`); valores
   inválidos (negativos, no numéricos) son error de schema (`422`).
3. Los schemas de entrada y salida son distintos (`GastoCreate` vs
   `GastoOut`) — nunca se expone el modelo de SQLAlchemy directamente.

## Artículo VI — MCP: tools y reutilización
1. Cada tool de MCP llama a una función de `services/`, punto. Si una tool
   necesita lógica que no existe en `services/`, esa lógica se agrega en
   `services/` primero, y la tool la reutiliza — nunca al revés.
2. La descripción de cada tool es específica y accionable (ej. "Registra un
   gasto con descripción, monto y categoría, validando el límite mensual por
   categoría"), nunca genérica ("maneja gastos").
3. Errores de negocio se devuelven como una estructura clara
   (`{"error": "..."}`), nunca como una excepción sin controlar que rompa
   la sesión del cliente MCP.
4. Si el transporte es `stdio` y no hay forma de propagar identidad real de
   usuario, se documenta explícitamente en el código como simplificación
   consciente (comentario), nunca como un olvido silencioso. Si el
   transporte es `streamable-http` y hay un token verificado, la tool DEBE
   usar la identidad de ese token (nunca un usuario demo hardcodeado) — el
   usuario demo es solo el fallback legítimo cuando no hay ningún token
   disponible.
5. Cualquier tool con efecto destructivo (ej. `eliminar_gasto`) debe pedir
   confirmación explícita gestionada por el servidor, nunca depender de que
   el modelo decida preguntar por su cuenta.

## Artículo VII — Testing y cobertura
1. Pirámide de pruebas obligatoria: unitarias (mayoría) → integración → API/E2E (minoría).
2. Tests unitarios de `services/` inyectan un repositorio falso (que cumple
   el mismo contrato que el real) como parámetro — está PROHIBIDO usar
   `unittest.mock` para esto, porque el diseño con DIP ya lo hace innecesario.
3. Cobertura mínima exigida:
   - 100% de las reglas de negocio explícitas de `spec.md` cubiertas por al
     menos un test unitario cada una (ej. categoría inválida, límite
     excedido, monto inválido) — cobertura de *reglas*, no solo de líneas.
   - Cobertura de líneas de `services/` ≥ 90%.
   - Cobertura de líneas del conjunto `services/ + repositories/ + routers/ +
     utils/` ≥ 80%, medida con `pytest --cov=app --cov-report=term-missing`.
     Este umbral NO exige cubrir el arranque de la app (`main.py`: lifespan,
     montaje ASGI de MCP, middleware de logging), el servidor MCP en sí
     (`mcp/server.py`, `mcp/auth.py`) ni `logging_config.py` — son
     infraestructura de arranque, no lógica de negocio, y su exclusión se
     declara explícitamente en `[tool.coverage.run] omit` de
     `pyproject.toml`, nunca como una omisión silenciosa.
4. Tests de integración corren contra una base de datos real (SQLite en
   memoria como mínimo), nunca contra el repositorio falso.
5. Tests de API usan `app.dependency_overrides` de FastAPI para sustituir
   `get_db`, `get_gastos_repo` y `get_current_user` — nunca levantan un
   servidor real ni golpean la base de datos de desarrollo.
6. Toda tool de MCP tiene al menos dos tests: un caso exitoso y un caso de
   error de negocio, verificados directamente o vía MCP Inspector.
7. Ninguna tarea de `tasks.md` se considera terminada sin su test
   correspondiente en verde.

## Artículo VIII — Compatibilidad con el proyecto de referencia
1. Este proyecto reconstruye el sistema "Gastos" de las Sesiones 6-8, cuya
   suite de tests (`test_gastos.py`, `test_integracion_gastos.py`,
   `test_api_gastos.py`) se copia sin modificar sus aserciones. Los módulos,
   funciones, parámetros (nombre y orden) y excepciones que esos tests
   importan son un contrato fijo, no una sugerencia — se documentan en una
   sección "Contrato de compatibilidad" de `spec.md` (ver Paso 4) y ninguna
   tarea de `tasks.md` puede renombrar, reordenar o eliminar un símbolo de
   esa lista.
2. `repositories/gastos.py` y `repositories/usuarios.py` son módulos con
   funciones sueltas, no clases — el contrato de compatibilidad así lo fija.
   Un repository devuelve estructuras simples (`dict`, o el objeto de
   dominio ya existente), nunca expone el objeto de sesión de SQLAlchemy al
   llamador.

## Gobernanza
Esta constitución tiene prioridad sobre cualquier decisión tomada durante
`/speckit-implement`. Si el agente necesita desviarse de un artículo, debe
señalarlo explícitamente y esperar aprobación antes de continuar, no
decidir en silencio.
```

> 🧑‍🏫 **Por qué es tan larga:** cada artículo de arriba es una decisión que ya tomaste — a veces por las malas — en las Sesiones 6-8 (el warning de Pydantic v1, el `passlib`/`bcrypt` que falló en runtime, el `usuario_id` que no debe venir de la URL). Una constitución corta es una constitución que no aprendió nada de lo que ya te costó tiempo resolver.

**Checkpoint:** `.specify/memory/constitution.md` contiene los 8 artículos de arriba (o tu versión adaptada), cada uno verificable — es decir, alguien podría leer el código generado y decir con certeza "esto cumple/no cumple el Artículo IV.4".

---

## Paso 4 — `spec.md` completa, con tabla de endpoints y `/speckit-clarify` (35 min)

`/speckit-specify` describe **qué** hace el sistema — comportamiento y contrato, no tecnología. Incluye explícitamente la tabla de endpoints, porque "endpoints" es contrato observable, no implementación.

```markdown
Sistema de control de gastos personales.

## Entidades
- Usuario: email (único), contraseña (nunca expuesta en respuestas).
- Gasto: descripción, monto (> 0), categoría, pertenece a un usuario.

## Reglas de negocio
- Categorías válidas: comida, transporte, entretenimiento, otros.
  Cualquier otra categoría es un error de negocio, no una excepción genérica.
- El monto de un gasto debe ser mayor a cero; una descripción vacía también
  es inválida.
- Un gasto no puede hacer que el total acumulado de su categoría supere 500.
- Un usuario solo puede ver y crear gastos propios; nunca los de otro usuario,
  sin importar qué identificador se pase en la solicitud.

## Contrato de la API (REST)

| Método | Ruta              | Auth | Request                          | Éxito         | Errores esperados                          |
|--------|-------------------|------|-----------------------------------|---------------|---------------------------------------------|
| POST   | /usuarios/        | No   | email, password                   | 201 Usuario   | 400 email duplicado, 422 validación         |
| POST   | /usuarios/token   | No   | username, password (form)         | 200 token JWT | 401 credenciales inválidas                  |
| POST   | /gastos/          | Sí   | descripcion, monto, categoria     | 201 Gasto     | 400 categoría inválida, 400 límite excedido, 401, 422 |
| GET    | /gastos/          | Sí   | query: skip, limit                | 200 lista     | 401, 422 (skip/limit inválidos)             |

## Contrato equivalente por MCP
- Tool `registrar_gasto(descripcion, monto, categoria)`: mismo comportamiento
  y mismas reglas que POST /gastos/, devolviendo el gasto creado o un error
  de negocio estructurado.
- Tool `listar_gastos(skip=0, limit=20)`: mismo comportamiento que GET /gastos/.
- Ambas tools operan siempre sobre el usuario autenticado de la sesión MCP
  (identidad resuelta desde el token verificado cuando el transporte es
  streamable-http; usuario demo de `.env` solo como fallback documentado
  cuando el transporte es stdio sin identidad propagable), nunca sobre un
  usuario indicado como parámetro.

## Contrato de compatibilidad (no negociable)

Los tests de las Sesiones 6-8 se copian sin modificar. Fijan estas firmas —
sin esta sección, un agente que solo lea las reglas de negocio de arriba
tiene total libertad para inventar otras firmas, y los tres archivos de
tests fallan al importar:

- `app/services/gastos.py`: `CategoriaInvalidaError`, `LimiteExcedidoError`,
  `LIMITE_POR_CATEGORIA = 500.0`,
  `registrar_gasto(db, usuario_id, descripcion, monto, categoria, repo=gastos_repository) -> dict`,
  `listar_gastos(db, usuario_id, skip=0, limit=20, repo=gastos_repository) -> list[dict]`
  — orden posicional exacto, `repo` es keyword con default (DIP).
- `app/repositories/gastos.py` — módulo con funciones, NO clase:
  `guardar(db, usuario_id, descripcion, monto, categoria) -> dict`,
  `listar(db, usuario_id, skip=0, limit=20) -> list[dict]`,
  `total_por_categoria(db, usuario_id, categoria) -> float`. Devuelven
  `dict`, nunca objetos ORM.
- `app/repositories/usuarios.py`: `obtener_por_email(db, email) -> Usuario | None`,
  `guardar(db, email, hashed_password) -> Usuario`.
- `app.database.get_db`, `app.dependencies.get_current_user`,
  `app.dependencies.get_gastos_repo`, `app.models.usuario.Usuario(id=, email=,
  hashed_password=)` — los tests copiados los importan directamente.
- `tests/__init__.py` debe existir: `test_api_gastos.py` hace
  `from tests.test_gastos import RepositorioFalso`.

## Casos de error explícitos que deben tener test
1. Registrar gasto con monto negativo o cero.
2. Registrar gasto con categoría inexistente.
3. Registrar gasto que excede el límite de 500 en su categoría.
4. Listar o registrar gastos sin token → 401.
5. Listar gastos de otro usuario pasando su ID manualmente → debe ignorarse,
   nunca debe filtrar por ese ID.
```

> ⚠️ **Los tests de S6-S8 no cubren los 5 casos por sí solos.** Si revisás `test_gastos.py`, `test_integracion_gastos.py` y `test_api_gastos.py`, vas a ver que cubren los casos 1-3 (monto inválido, categoría inválida, límite excedido) pero **no** los casos 4 y 5 (401 sin token, `usuario_id` ajeno ignorado) — esos dos nunca se probaron en la Sesión 7-8. Vas a necesitar escribir tests nuevos para esos dos casos en `tasks.md`; no asumas que "copiar los tests de antes" alcanza para marcar los 5 casos de error como cubiertos.

**Checkpoint:** `specs/001-control-de-gastos/spec.md` tiene la tabla de endpoints, el contrato de compatibilidad y los 5 casos de error explícitos — estos 5 casos son los que después vas a exigir como tests en `tasks.md`.

### Por qué esto cabe en un solo `spec.md`, y qué no cabría

Todo lo de arriba — usuarios, gastos, REST, MCP — es **una sola funcionalidad** (control de gastos), aunque toque varias capas del backend. La regla de spec-kit no es "una spec por capa", es **una spec por feature**: si más adelante agregan algo que no es una extensión directa de esto (por ejemplo, "reportes mensuales exportables a PDF" o "notificaciones por correo"), eso merece su propio ciclo `/speckit-specify → /speckit-plan → /speckit-tasks → /speckit-implement`, no ampliar este mismo `spec.md` hasta que se vuelva ilegible.

🧑‍🏫 **Cómo distinguir "una feature grande" de "dos features en un spec":** si al leer `spec.md` alguien pregunta "¿pero esto qué tiene que ver con lo otro?", son dos specs. Si todo lo que hay adentro responde a una sola pregunta de negocio ("¿cómo controla sus gastos un usuario?"), es una sola spec, sin importar cuántas capas toque para construirse.

### Reto opcional: distinguir un criterio verificable de uno que no lo es (10 min)

Antes de dar por buena tu `spec.md`, practica con un caso chico. Supón que agregan esta funcionalidad más adelante: **"permitir que un usuario corrija la categoría de un gasto ya registrado."**

Una primera versión, tentadora pero mala, diría algo así:

> *"Mejora el manejo de gastos, que sea más seguro y fácil de usar."*

Suena razonable, pero no define comportamiento ni resultado comprobable — nadie puede escribir un test contra esto. La versión que sí sirve como spec da **criterios de aceptación**, no adjetivos:

```markdown
## actualizar_categoria(gasto_id, nueva_categoria)
- DUEÑO: solo el usuario dueño del gasto puede actualizarlo → 403 si no lo es.
- VALIDACIÓN: nueva_categoria debe ser una de las categorías válidas → 400 si no.
- LOG: cada cambio registra usuario, gasto y categoría anterior.
```

Tres criterios, tres tests posibles antes de escribir una sola línea de código. Si tu propio `spec.md` tiene alguna regla escrita como la primera versión (una intención sin forma de verificarla), corrígela ahora — es más barato aquí que después de `/speckit-implement`.

### `/speckit-clarify`: la pregunta que evita que el agente adivine

Antes de pasar a `/speckit-plan`, corre:

```
/speckit-clarify
```

Con la spec de arriba, una buena pregunta de `/speckit-clarify` sería: *"¿puede un usuario con algún rol especial (ej. administrador) actualizar la categoría de un gasto que no es suyo?"* Si `spec.md` no lo dice, el agente tiene dos caminos: preguntarte (lo correcto) o decidirlo solo (el riesgo). `/speckit-clarify` fuerza el primero antes de que exista una sola línea de plan.

**Checkpoint adicional:** si `/speckit-clarify` no te hizo ninguna pregunta, revisa si tu `spec.md` es realmente inequívoco o si el agente se está guardando su interpretación para más adelante.

---

## Paso 5 — `plan.md`: cómo se cumple cada artículo (20 min)

`/speckit-plan` traduce la spec a stack técnico, pero además — y esto es lo que casi todos se saltan — **explica cómo cada decisión técnica satisface un artículo específico de la constitución**. Eso obliga al agente (y a ti) a razonar la conexión, no solo listar librerías.

```markdown
Stack: FastAPI, uvicorn[standard], SQLAlchemy + Alembic, pyjwt,
passlib[bcrypt], bcrypt<4.1, pydantic-settings, email-validator,
python-multipart, SDK oficial "mcp" montado vía streamable-http, pytest +
pytest-cov + httpx.

Trazabilidad plan → constitución:
- La separación routers/services/repositories/utils (Artículo I) se
  implementa como paquetes Python separados bajo app/, sin imports cruzados
  que violen la dirección de dependencia.
- DIP (Artículo II.3) se implementa con parámetros por defecto en las
  funciones de services/, no con un contenedor de inyección de dependencias
  externo — mantenerlo simple.
- Seguridad (Artículo IV) se implementa con `pyjwt` para JWT (una sola
  librería, no "pyjwt o python-jose" — dar a elegir reintroduce la ambigüedad
  que la constitución existe para eliminar; además python-jose está sin
  mantenimiento), `passlib.context.CryptContext(schemes=["bcrypt"])` para
  hashing (con `bcrypt<4.1` fijado — passlib 1.7.4 rompe en runtime con
  versiones más nuevas de bcrypt), y `pydantic_settings.BaseSettings`
  leyendo `.env` para SECRET_KEY y DATABASE_URL. `email-validator` y
  `python-multipart` son dependencias transitivas obligatorias de
  `pydantic.EmailStr` y `OAuth2PasswordRequestForm` respectivamente — sin
  ellas la app ni siquiera arranca.
- Autorización (Artículo IV.4): toda ruta y tool que opera sobre gastos
  depende de `get_current_user` (o su equivalente MCP) para obtener
  `usuario_id`; ningún endpoint acepta `usuario_id` como parámetro de
  entrada.
- Testing (Artículo VII) se implementa con fixtures de pytest para DB en
  memoria, `app.dependency_overrides` para tests de API (`httpx` como
  dependencia de `TestClient`), y `pytest-cov` con el umbral del Artículo
  VII.3 verificado como último paso de `/speckit-implement`, no como una
  tarea opcional.
- MCP (Artículo VI) se monta dentro de la misma app FastAPI
  (`streamable-http`), reutilizando `get_current_user` adaptado para
  extraer el JWT del header Authorization de la sesión MCP.
```

**Checkpoint:** `plan.md` no es solo una lista de librerías — cada bullet conecta explícitamente con un artículo de la constitución (verifica que puedas señalar, para cada artículo, en qué parte del plan se resuelve).

---

## Paso 6 — `tasks.md`: cada tarea con su "definition of done", más `/speckit-analyze` (25 min)

```
/speckit-tasks
```

Antes de aceptar la lista generada, revisa que **cada tarea de código tenga una tarea de test emparejada**, y que las tareas cubran los 5 casos de error del Paso 4. Si el agente generó tareas sin esa correspondencia, pide explícitamente:

```
Reorganiza tasks.md para que cada tarea de implementación tenga como
"definition of done": (1) código escrito, (2) test correspondiente escrito
y en verde, (3) no viola ningún artículo de la constitución. Agrega una
tarea final dedicada exclusivamente a correr pytest --cov=app y confirmar
que se cumple el umbral de cobertura del Artículo VII.3.
```

**Checkpoint:** `tasks.md` tiene una tarea final explícita de verificación de cobertura, y ninguna tarea de código "suelta" sin su test.

### Referencia rápida: qué exige `tasks.md` según la capa

No es un spec por capa — es lo que ya exige el Artículo VII: ninguna tarea se da por terminada sin su test y sin cumplir el artículo que le aplica. Úsala para revisar `tasks.md` antes de correr `/speckit-implement`:

| Capa | Qué valida esa tarea antes de darse por terminada |
|---|---|
| Models | schemas de entrada/salida separados; relación `usuario_id` declarada |
| Repositories | solo persiste, no valida nada; recibe la sesión por parámetro |
| Services | DIP con repo por defecto; reglas de negocio explícitas; excepción propia por regla |
| Routers | `usuario_id` siempre desde `get_current_user`; traduce excepción → código HTTP |
| MCP/Tools | reutiliza `services/`, nunca reimplementa; `ToolError` para errores de dominio |

### `/speckit-analyze`: revisa el plan antes de que exista código

Antes de `/speckit-implement`, corre:

```
/speckit-analyze
```

`/speckit-analyze` compara `plan.md` y `tasks.md` contra `constitution.md` — y vale la pena ver un ejemplo de lo que detecta. Toma el plan de `actualizar_categoria` del reto del Paso 4:

**Plan original:**
```
1. recibir gasto_id + nueva_categoria
2. validar categoría
3. guardar cambio
4. registrar auditoría
```

**`analyze` señala:** ningún paso verifica que el gasto pertenece al usuario autenticado. Sin eso, cualquiera podría cambiar la categoría de un gasto ajeno con solo conocer su `id` — viola el Artículo IV.4 (`usuario_id` siempre desde el JWT), aplicado aquí a un gasto ya existente, no solo al crearlo.

**Plan corregido:**
```
1. recibir gasto_id + nueva_categoria
2. verificar que el gasto pertenece al usuario autenticado  ← paso agregado
3. validar categoría
4. guardar cambio
5. registrar auditoría
```

Corregir un paso en el plan cuesta una línea; corregir la misma falla en código ya escrito e implementado cuesta un incidente de seguridad. Por eso `/speckit-analyze` va antes de `/speckit-implement`, no después.

**Checkpoint adicional:** si `/speckit-analyze` no marcó ninguna observación, revisa manualmente que cada tarea que toca datos de usuario tenga su verificación de dueño explícita — no todas las violaciones son detectadas automáticamente. Un ejemplo real de esta misma práctica: los tests de S6-S8 copiados en el Paso 8 no cubren los casos de error 4 y 5 de `spec.md` (ver la advertencia del Paso 4) — un `/speckit-analyze` atento a "cobertura de reglas, no solo de líneas" (Artículo VII.3) debería marcarlo; si no lo hace, sos vos quien tiene que notarlo antes de dar `tasks.md` por bueno.

---

## Paso 7 — El prompt correcto para `/speckit-implement` (10 min)

Este es el paso que más se salta la gente, y es el que evita que `/speckit-implement` genere 40 archivos de una vez que después nadie revisó. Usa este patrón de prompt (basado en buenas prácticas de prompting: instrucciones claras, paso a paso, formato explícito de verificación):

```
Ejecuta tasks.md en orden, UNA tarea a la vez. Para cada tarea:
1. Muestra qué archivo(s) vas a crear o modificar antes de escribir el código.
2. Escribe el código y su test correspondiente en el mismo turno.
3. Corre los tests de esa tarea y muestra el resultado (verde o rojo).
4. Antes de pasar a la siguiente tarea, indica explícitamente si esta tarea
   cumple todos los artículos de la constitución que le aplican. Si hay
   alguna desviación, decláralo y espera mi confirmación antes de continuar.

No implementes dos capas (por ejemplo, repository y router) en el mismo
paso si dependen una de la otra — hazlo en el orden que respeta la
dirección de dependencia del Artículo I.

Al terminar todas las tareas, corre `pytest --cov=app --cov-report=term-missing`
y reporta explícitamente si se cumple el umbral del Artículo VII.3. Si no
se cumple, indica qué archivos o funciones quedaron sin cubrir antes de
darlo por terminado.
```

> 🧑‍🏫 **Por qué "una tarea a la vez" y no "hazlo todo":** es la misma razón por la que en la Sesión 6-8 avanzaron paso a paso con checkpoints, en vez de escribir el proyecto entero y probar al final. Un agente que genera 15 archivos de un jalón y falla en el archivo 12 te deja sin saber si los 11 anteriores están bien. Pedir verificación por tarea es el equivalente a los "Checkpoint" de tus prácticas anteriores, aplicado al agente.

**Checkpoint:** tienes claro el prompt de arriba (o tu adaptación) antes de correr `/speckit-implement` — no se improvisa en el momento.

---

## Paso 8 — Implementar de forma incremental y verificar cobertura (20 min)

```
/speckit-implement
```

Sigue el prompt del Paso 7. Después de cada tarea:
- Revisa el código generado contra el artículo de constitución que le aplica (no todos, el que corresponde a esa tarea).
- Si el agente se desvía, corrígelo con un prompt puntual antes de seguir — no acumules desviaciones para "arreglarlas al final".

Al terminar, copia los tests de las Sesiones 6-8 y corre todo junto. Ajusta `RUTA_PROYECTO_S6_S8` a donde tengas tu proyecto de esa sesión — normalmente **no** es `../proyecto-curso` (esa ruta asume una estructura de carpetas que rara vez coincide; verificá la tuya con `ls` antes de copiar):

```bash
uv add --dev pytest-cov
RUTA_PROYECTO_S6_S8="ruta/a/tu/proyecto/de/la/sesion/8"
mkdir -p tests
cp "$RUTA_PROYECTO_S6_S8/tests/__init__.py" tests/
cp "$RUTA_PROYECTO_S6_S8/tests/test_gastos.py" tests/
cp "$RUTA_PROYECTO_S6_S8/tests/test_integracion_gastos.py" tests/
cp "$RUTA_PROYECTO_S6_S8/tests/test_api_gastos.py" tests/
uv run pytest --cov=app --cov-report=term-missing -v
```

⚠️ No te olvides de `tests/__init__.py` — sin él, `test_api_gastos.py` falla al hacer `from tests.test_gastos import RepositorioFalso` (es un import de paquete, no un import relativo).

**Checkpoint:**
- Todos los tests (los copiados y los generados hoy) pasan en verde.
- La cobertura reportada cumple el Artículo VII.3 (services ≥90%, conjunto services+repositories+routers+utils ≥80%).
- Los 5 casos de error del Paso 4 tienen, cada uno, un test identificable — recordá que los 3 archivos copiados de S6-S8 solo cubren los casos 1-3; los casos 4 y 5 necesitan tests nuevos que `tasks.md` debería haber generado (ver advertencia del Paso 4).

---

## Anexo — Orquestación con subagentes, hooks y skills en Antigravity (para no pagar tokens de más) — 25-30 min

### El problema que esto resuelve

Todo lo hecho en los Pasos 3-8 asumió una sola conversación larga: constitución + spec + plan + tasks + cada una de las ~25 tareas de `/speckit-implement`, todo acumulándose en el mismo contexto. Funciona, pero tiene un costo real — para una tarea de la Fase 8 (MCP) de `tasks.md`, el agente está releyendo (y pagando tokens por) las ~20 tareas anteriores completas, aunque esa tarea solo necesite el Artículo VI y dos archivos concretos.

Skills y subagentes son mecanismos nativos de Antigravity (no un añadido de Spec Kit). Hooks es más matizado — hay un hook nativo del agente, un hook propio de Spec Kit, y el hook de Git de toda la vida; la sección 3 de abajo explica cuál da la garantía real de "sin depender de que el modelo lo recuerde":

| Mecanismo | Qué resuelve | Dónde vive |
|---|---|---|
| **Skills** | Evita cargar SIEMPRE el contenido completo de un comando/checklist; se carga solo cuando hace falta (discovery → carga bajo demanda) | Antigravity: `.agents/skills/<nombre>/SKILL.md` |
| **Subagentes** | Aíslan el contexto por responsabilidad: cada uno arranca limpio, no hereda el historial completo de tareas anteriores; corren en paralelo | Antigravity: agentes con nombre, invocados como "en un subagente: ..." |
| **Hooks** | Verificación mecánica (correr tests, bloquear un secreto hardcodeado) sin gastar tokens del modelo "recordando" hacerlo | Antigravity (nativo, formato propio), Spec Kit (`.specify/extensions.yml`, no cableado para `agy` en esta versión), o Git (`.git/hooks/pre-commit`, universal) |

### 1. Spec Kit ya instala sus comandos como Skills en Antigravity

```bash
specify init proyecto-curso-speckit --integration agy
```

No hace falta ninguna bandera adicional aparte de `--integration agy` (no `--ai`, ver Paso 2): la integración `agy` de Spec Kit es **skills-based por definición** — `/speckit-constitution`, `/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-implement` quedan instalados en `.agents/skills/` (plural), y Antigravity solo carga el contenido de cada uno cuando decide que la tarea actual lo amerita (modelo de *progressive disclosure*: primero ve nombre y descripción de cada skill, y recién carga el resto si aplica). Es el mismo principio de "carga bajo demanda" con el que yo, como asistente, reviso un `SKILL.md` solo si la tarea lo amerita, no en cada respuesta.

### 2. Subagentes por capa, no un solo hilo gigante

En vez de que un único agente ejecute las ~25 tareas de `tasks.md` una tras otra acumulando todo el historial, se delega por capa a subagentes. Cada uno arranca con **su propio contexto**, acotado al artículo de la constitución que le aplica — no a la constitución completa ni a las tareas ya hechas. La pregunta que decide "¿esto merece un subagente aparte?" es siempre la misma: *¿esta tarea necesita releer decisiones de una capa distinta para hacerse bien?* Si no, aislarla no pierde nada y ahorra tokens.

Para "Gastos" (25 tareas en 9 fases, ver `tasks.md` del Paso 6), un reparto razonable son 4 subagentes, cada uno con un artículo primario y un límite explícito de qué NO debe tocar:

| Subagente | Tareas de `tasks.md` | Artículo primario | Límite explícito |
|---|---|---|---|
| Repositories | Fase 2 (repos) | I.3, III | No escribe reglas de negocio — eso es de `services/` |
| Services | Fase 4 (lógica de negocio) | I.2, II.1, II.3, VIII.1 | Recibe el repo por parámetro (DIP); no importa SQLAlchemy |
| Routers + auth | Fase 6 (dependencies, routers) | IV.4, V | `usuario_id` sale siempre de `get_current_user`, nunca de un parámetro |
| MCP | Fase 8 (tools, server) | VI.1, VI.4 | Reutiliza `services/`; identidad del token verificado, no usuario demo por defecto |

En Antigravity, esto se pide de forma conversacional, dirigiéndote a un subagente explícitamente:

```
En un subagente: construye los repositories de app/repositories/ siguiendo
los Artículos I.3 y III de la constitución. No escribas lógica de negocio
(eso es de services/, Artículo I.2). Todo query que involucre datos de
usuario filtra por usuario_id (Artículo III.3). Al terminar, corre
`uv run pytest tests/test_integracion_gastos.py -q` y reporta el resultado.
```

```
En un subagente distinto: revisa el código de autenticación, JWT, hashing
y secretos contra el Artículo IV. Verifica hashing con bcrypt (nunca
sha256/md5 ni texto plano), SECRET_KEY leído desde settings (nunca
hardcoded), usuario_id siempre desde el JWT decodificado. Si encuentras
una violación, repórtala puntualmente — no apruebes código "porque funciona".
```

```
En un subagente distinto: implementa app/mcp/tools/gastos.py siguiendo el
Artículo VI. Cada tool llama a una función de services/gastos.py que ya
existe — no reimplementes la validación de categoría ni el límite de 500
adentro de la tool. Resuelve la identidad del usuario desde el token
verificado (get_access_token().subject) cuando lo haya; usa el usuario demo
de settings SOLO si no hay ningún token (documentalo con un comentario,
Artículo VI.4). Al terminar, corre los tests de tests/test_mcp_gastos.py.
```

Los tres corren con contexto aislado (Antigravity gestiona el worktree de cada uno automáticamente) y pueden trabajar en paralelo cuando no dependen entre sí — Repositories y Services sí tienen dependencia estricta (Services necesita que Repositories exista primero), pero Routers+auth y MCP pueden avanzar en paralelo una vez que Services está listo. El agente principal actúa como **orquestador**: lee `tasks.md`, delega cada fase al subagente que corresponde, y usa el panel de agentes de Antigravity para monitorear su estado (el nombre exacto del comando puede variar entre versiones — confirmalo en tu instalación en vez de asumir un nombre) en vez de ejecutar las ~25 tareas él mismo en una sola conversación. Así, la tarea de la Fase 8 no paga el costo de contexto de las 20 tareas anteriores.

> 🧑‍🏫 **Cuándo vale la pena y cuándo no:** para un proyecto del tamaño de "Gastos" (2 entidades, ~25 tareas), la ganancia de tokens es real pero modesta — el valor de hoy es sobre todo pedagógico. Donde esto se vuelve indispensable es en tu proyecto evaluado con una idea propia más grande: ahí sí vas a notar la diferencia entre una conversación de 200 turnos y varios subagentes de 20 turnos cada uno.
>
> ⚠️ **Un subagente con contexto acotado no ve las decisiones de otras capas** — si el subagente de Routers no sabe que `services/gastos.py` ya define `CategoriaInvalidaError`, puede terminar creando su propia excepción duplicada. La mitigación no es "dale más contexto" (eso anula el ahorro) sino ser explícito en el prompt sobre qué símbolos ya existen y debe reutilizar — como se ve en el ejemplo de MCP de arriba, que nombra `services/gastos.py` en vez de asumir que el subagente lo va a descubrir solo.

### 3. Hooks: reglas que se verifican solas, sin gastar tokens del modelo

Algunas reglas de la constitución no necesitan que el modelo las "razone" cada vez — son verificaciones mecánicas. Antes de elegir dónde poner el hook, hay que ser precisos con qué tipo de hook es cada cosa, porque no todos dan la misma garantía:

- **Hook nativo del agente** (el que trae Antigravity: scripts disparados antes/después de una llamada a tool, antes/después de una llamada al modelo, o al llegar a una condición de parada). Es el más flexible, pero su JSON exacto (ubicación global vs. workspace, nombres de evento) está en la documentación oficial de Hooks de Antigravity — revísala antes de escribir el tuyo, porque el formato difiere del que usan Claude Code u otros agentes aunque el concepto sea el mismo. **Este documento no puede darte ese JSON exacto sin acceso a Antigravity para verificarlo** — no copies un ejemplo de "hooks de Claude Code" esperando que funcione igual en Antigravity.
- **Hook de Spec Kit** (`.specify/extensions.yml`, eventos como `before_implement`/`after_specify`): existe y ya lo estás usando sin saberlo — es el mecanismo que hace que la extensión de git (Paso 1) cree una rama antes de `/speckit-specify`. Pero ojo: en la versión de `specify-cli` de este curso, la ejecución *automática* de esos hooks (sin que el modelo tenga que acordarse de revisarlos) solo está cableada para algunos agentes — verificalo con `specify integration list` antes de asumir que tu integración la soporta. Cuando no está cableada nativamente, el propio `SKILL.md` de cada comando igual le indica al modelo "revisá `.specify/extensions.yml` antes de continuar" — funciona, pero ahí sí depende de que el modelo lea y seros esa instrucción, no es 100% mecánico.
- **Git hook estándar** (`.git/hooks/pre-commit`): no es específico de ningún agente ni de Spec Kit — es una función de Git que corre siempre, la escriba quien la escriba, y bloquea el `commit` si el script sale con código distinto de cero. **Es la opción que da la garantía real de "sin depender de que el modelo lo recuerde"**, porque ni el agente ni vos podés saltarla sin pasar `--no-verify` explícitamente. Para el alcance de hoy es la más práctica de implementar y verificar, y funciona igual si mañana cambiás de agente.

Ejemplo funcional (probado: bloquea el commit si los tests de `services/` fallan, y si detecta un `SECRET_KEY` hardcodeado fuera de `.env`):

```bash
# .git/hooks/pre-commit (dar permiso de ejecución: chmod +x .git/hooks/pre-commit)
#!/usr/bin/env bash
set -euo pipefail

staged=$(git diff --cached --name-only --diff-filter=ACM)

# Artículo VII.7: si cambió algo en app/services/, los tests de services
# tienen que estar en verde ANTES de que el commit exista — no después.
if echo "$staged" | grep -q '^app/services/'; then
  echo "[pre-commit] app/services/ cambió -> corriendo tests de services..."
  if ! uv run pytest tests/test_gastos.py tests/test_gastos_service_extra.py \
       tests/test_usuarios_service.py -q; then
    echo "[pre-commit] BLOQUEADO: tests de services en rojo." >&2
    exit 1
  fi
fi

# Artículo IV.3: SECRET_KEY nunca se escribe a mano en código versionado.
secret_hit=0
while IFS= read -r f; do
  [ -z "$f" ] && continue
  case "$f" in .env|.env.example) continue ;; esac
  if git show ":$f" 2>/dev/null | grep -Eq 'SECRET_KEY\s*=\s*["'"'"'][^"'"'"']+["'"'"']'; then
    echo "[pre-commit] BLOQUEADO: $f tiene un SECRET_KEY hardcodeado." >&2
    secret_hit=1
  fi
done <<< "$staged"

[ "$secret_hit" -eq 0 ] || exit 1
```

Ajustá la lista de archivos de test del primer bloque a los tuyos (`tasks.md` te dice cuáles son). Probalo antes de confiar en él: hacé un commit que solo cambie `app/services/` con un test roto a propósito y confirmá que Git lo rechaza (`git commit` debe salir con código 1 y el mensaje `BLOQUEADO`); después arreglá el test y confirmá que si pasa.

**Checkpoint del hook:** `git commit --no-verify` es la única forma de saltarlo — si alguien del equipo lo usa para esquivar un test roto, tiene que quedar explícito en el mensaje del commit, no en silencio.

### 4. Skills locales, en vez de repetir el mismo checklist en cada prompt

⚠️ **Nombrala sin el prefijo `speckit-`.** Ese prefijo lo usa Spec Kit para sus propios comandos (`speckit-implement`, `speckit-analyze`, etc. — ver Paso 2); una skill tuya llamada `speckit-algo` puede colisionar con una futura actualización de Spec Kit que agregue un comando con ese mismo nombre. `constitution-check`, `mcp-tool-check`, etc. — nombres propios del proyecto, no del namespace de la herramienta.

**Skill 1 — chequeo de constitución**, para correr al final de cada tarea de `tasks.md`:

`.agents/skills/constitution-check/SKILL.md`:
```markdown
---
name: constitution-check
description: Usa esta skill al finalizar cualquier tarea de tasks.md, para verificar cumplimiento con la constitución antes de marcarla como terminada.
---
Verifica, en este orden: (1) capas respetadas, (2) DIP con parámetro por
defecto, (3) si toca datos de usuario, filtro por usuario_id desde JWT,
(4) test correspondiente en verde, (5) si toca MCP, reutiliza services/.
```

**Skill 2 — chequeo específico de tools MCP**, más angosta que la anterior a propósito: solo se carga cuando la tarea es de la Fase 8 (`tasks.md`), no en cada tarea del proyecto — el punto de tener dos skills separadas, en vez de una sola larga, es que el agente cargue únicamente la que aplica.

`.agents/skills/mcp-tool-check/SKILL.md`:
```markdown
---
name: mcp-tool-check
description: Usa esta skill después de escribir o modificar cualquier tool en app/mcp/tools/, antes de darla por terminada.
---
Verifica, en este orden: (1) la tool llama a una función de services/, no
reimplementa la regla adentro (Artículo VI.1); (2) la descripción de la tool
es específica y accionable, no genérica (Artículo VI.2); (3) un error de
negocio se devuelve como {"error": "..."}, nunca como excepción sin
controlar (Artículo VI.3); (4) la identidad del usuario sale del token
verificado cuando lo hay, el usuario demo es solo el fallback documentado
para stdio sin token (Artículo VI.4); (5) existen al menos dos tests para
la tool: un caso exitoso y un caso de error de negocio (Artículo VII.6).
```

Ninguna de las dos se envía en cada turno de la conversación — Antigravity las lee bajo demanda, cuando el agente decide que la tarea actual amerita ese chequeo puntual (mira nombre + `description` de cada skill primero, y solo carga el cuerpo completo si aplica). Es el mismo mecanismo de *progressive disclosure* por el que un asistente con varias skills disponibles no carga todas sus instrucciones en cada respuesta, solo las relevantes a la tarea que tiene enfrente — la Skill 2 existe separada de la Skill 1 precisamente para que una tarea de `repositories/` no pague el costo de leer el checklist de MCP.

### Checklist adicional del anexo

- [ ] `specify init --integration agy` confirmado — los comandos de Spec Kit ya viven como skills en `.agents/skills/`, sin bandera adicional
- [ ] Al menos 2 subagentes usados durante `/speckit-implement` (idealmente los 4 de la tabla: repositories, services, routers+auth, MCP), cada uno con contexto acotado al artículo que le aplica y un límite explícito de qué NO debe tocar
- [ ] El `.git/hooks/pre-commit` probado dos veces: bloquea un commit con un test de `services/` roto, y deja pasar uno limpio — no basta con haberlo escrito, hay que confirmar que efectivamente bloquea
- [ ] Al menos 2 skills locales (`constitution-check` y `mcp-tool-check`, o tus propios nombres — sin el prefijo `speckit-`) en `.agents/skills/`, cada una angosta a su propio chequeo en vez de una sola larga que se cargue siempre
- [ ] El orquestador delega tareas a subagentes en vez de ejecutar las ~25 tareas de `tasks.md` dentro de una sola conversación continua

---

## Paso 9 — Reflexión y cierre (10 min)

1. ¿Qué artículo de la constitución tuviste que "defender" activamente durante `/speckit-implement` — es decir, dónde el agente propuso algo que lo violaba y tuviste que corregirlo? (Un candidato típico: el Artículo VI.4 — es fácil que las tools de MCP usen siempre el usuario demo "por simplicidad" incluso cuando sí hay un token verificado disponible.)
2. Compara el tiempo que tomó escribir `constitution.md` + `spec.md` + `plan.md` hoy contra el tiempo que tomó escribir el código a mano en las Sesiones 6-8. ¿Dónde se fue el tiempo distinto: pensando, o escribiendo?
3. Si el umbral de cobertura del Artículo VII.3 no se hubiera puesto por escrito, ¿crees que el agente se habría detenido en un 60% de cobertura sin decírtelo?

> "Hoy la especificación reemplazó al código como fuente de verdad. Lo comprobé cuando ______, y el artículo de la constitución que más me costó defender fue ______."

---

## Checklist de autoverificación (versión completa)

- [ ] `constitution.md` tiene los 8 artículos (arquitectura, SOLID, persistencia, seguridad, endpoints, MCP, testing, compatibilidad), cada uno verificable en el código, no aspiracional
- [ ] `spec.md` incluye la tabla de endpoints REST, su equivalente MCP, el contrato de compatibilidad y los 5 casos de error explícitos
- [ ] Corriste `/speckit-clarify` después de `/speckit-specify` y resolviste al menos una ambigüedad antes de pasar a `/speckit-plan`
- [ ] `plan.md` conecta cada decisión técnica con el artículo de la constitución que satisface
- [ ] `tasks.md` no tiene ninguna tarea de código sin su test emparejado, y tiene una tarea final de verificación de cobertura
- [ ] Corriste `/speckit-analyze` antes de `/speckit-implement` y revisaste manualmente que cada tarea que toca datos de usuario verifique el dueño explícitamente
- [ ] Usaste el prompt de `/speckit-implement` que pide verificación tarea por tarea, no "hazlo todo de una vez"
- [ ] Corregiste al menos una desviación de la constitución durante `/speckit-implement` (si el agente no se desvió nunca, revisa si de verdad estabas verificando cada tarea)
- [ ] `pytest --cov=app --cov-report=term-missing` cumple el umbral del Artículo VII.3 (services ≥90%, conjunto services+repositories+routers+utils ≥80%)
- [ ] Los 5 casos de error de `spec.md` tienen cada uno un test identificable — incluidos los casos 4 y 5, que los tests copiados de S6-S8 NO cubren por sí solos
- [ ] Los tests de `test_gastos.py`, `test_integracion_gastos.py` y `test_api_gastos.py` (Sesiones 6-8) pasan sin modificar su lógica de aserciones
- [ ] Las tools de MCP reutilizan `services/gastos.py`, tienen descripciones específicas (no genéricas), y usan la identidad del token verificado cuando lo hay — nunca el usuario demo por defecto
- [ ] La autorización nunca acepta `usuario_id` desde el cliente (verificado con el caso de error 5)
- [ ] (Si hiciste el reto opcional del Paso 4) el criterio "solo el dueño puede actualizar" quedó escrito con código de respuesta HTTP, no como una intención vaga

---

## Conexión con la próxima sesión

Este mismo conjunto de artefactos —`constitution.md`, `spec.md`, `plan.md`, `tasks.md` y el prompt de `/speckit-implement` con verificación incremental— es la plantilla que vas a llevar a tu propia idea. La constitución probablemente cambie poco (la arquitectura en capas y la seguridad se mantienen); lo que sí cambia por completo es `spec.md`. Guarda esta práctica como referencia de "cuánto detalle es suficiente detalle".
