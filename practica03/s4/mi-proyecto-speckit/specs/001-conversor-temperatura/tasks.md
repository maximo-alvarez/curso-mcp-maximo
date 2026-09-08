# Tasks: Conversor de Temperatura

**Feature**: `001-conversor-temperatura` | **Spec**: [spec.md](file:///Volumes/data/_cursos/_cedia_2026_programacion_mcp/proyecto01/practica03/s4/mi-proyecto-speckit/specs/001-conversor-temperatura/spec.md) | **Plan**: [plan.md](file:///Volumes/data/_cursos/_cedia_2026_programacion_mcp/proyecto01/practica03/s4/mi-proyecto-speckit/specs/001-conversor-temperatura/plan.md)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inicialización del proyecto y estructura base de directorios y pruebas.

- [X] T001 Create project test directory structure in tests/
- [X] T002 Initialize package testing configuration in tests/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestructura central de dominio, normalización y tipos de error que bloquea la implementación de las historias de usuario.

**⚠️ CRITICAL**: Ninguna historia de usuario puede implementarse hasta completar esta fase.

- [X] T003 Define ConversionError domain exception and module docstrings in conversor.py
- [X] T004 Implement scale normalization dictionary and validation helper _normalizar_escala in conversor.py
- [X] T005 Implement input numeric validation and float parsing with comma support in conversor.py

**Checkpoint**: Base de validación y errores lista. El desarrollo de las historias de usuario puede comenzar.

---

## Phase 3: User Story 1 - Conversión entre Celsius y Fahrenheit (Priority: P1) 🎯 MVP

**Goal**: Permitir la conversión bidireccional exacta entre Celsius y Fahrenheit con redondeo a 2 decimales y soporte de negativos válidos.

**Independent Test**: Ejecutar `python3 -m unittest tests/test_conversor.py` verificando conversiones como `0 C -> 32.0 F`, `212 F -> 100.0 C` y `-40 C -> -40.0 F`.

### Tests for User Story 1 (Test-First / TDD) ⚠️

> **NOTE: Escribir estas pruebas PRIMERO y verificar que fallen antes de implementar.**

- [X] T006 [P] [US1] Add unit tests for bidirectional Celsius and Fahrenheit conversions in tests/test_conversor.py
- [X] T007 [P] [US1] Add unit tests for negative temperatures in C and F, and 2-decimal rounding in tests/test_conversor.py

### Implementation for User Story 1

- [X] T008 [US1] Implement Celsius to Fahrenheit and Fahrenheit to Celsius conversion formulas in conversor.py
- [X] T009 [US1] Implement 2-decimal rounding and negative zero normalization in conversor.py

**Checkpoint**: User Story 1 (MVP) completamente funcional e independientemente verificable.

---

## Phase 4: User Story 2 - Conversión entre Celsius y Kelvin (Priority: P2)

**Goal**: Permitir la conversión bidireccional entre Celsius y Kelvin, garantizando el rechazo de temperaturas inferiores al cero absoluto (Kelvin < 0).

**Independent Test**: Verificar conversiones como `0 C -> 273.15 K`, `300 K -> 26.85 C`, y el lanzamiento de `ConversionError` ante `Kelvin < 0`.

### Tests for User Story 2 (Test-First / TDD) ⚠️

- [X] T010 [P] [US2] Add unit tests for Celsius to Kelvin and Kelvin to Celsius conversions in tests/test_conversor.py
- [X] T011 [P] [US2] Add unit tests for Kelvin < 0 boundary validation and error rejection in tests/test_conversor.py

### Implementation for User Story 2

- [X] T012 [US2] Implement Celsius to Kelvin and Kelvin to Celsius conversion formulas in conversor.py
- [X] T013 [US2] Implement physical boundary validation rejecting Kelvin < 0 with descriptive error in conversor.py

**Checkpoint**: User Story 1 y User Story 2 son plenamente operativas de forma individual y conjunta.

---

## Phase 5: User Story 3 - Conversión Fahrenheit ↔ Kelvin y Misma Unidad (Priority: P3)

**Goal**: Permitir conversiones directas entre Fahrenheit y Kelvin, y gestionar de forma optimizada conversiones donde origen y destino coinciden.

**Independent Test**: Verificar `32 F -> 273.15 K`, `273.15 K -> 32.0 F`, y `25.456 C -> 25.46 C`.

### Tests for User Story 3 (Test-First / TDD) ⚠️

- [X] T014 [P] [US3] Add unit tests for direct Fahrenheit and Kelvin conversions in tests/test_conversor.py
- [X] T015 [P] [US3] Add unit tests for identical source and destination scale short-circuiting in tests/test_conversor.py
- [X] T016 [P] [US3] Add unit tests for non-numeric input rejection (strings, None, booleans) in tests/test_conversor.py

### Implementation for User Story 3

- [X] T017 [US3] Implement Fahrenheit to Kelvin and Kelvin to Fahrenheit conversion path in conversor.py
- [X] T018 [US3] Implement identical source-destination unit bypass returning rounded input in conversor.py

**Checkpoint**: Cobertura total de conversiones y casos borde especificados en el modelo de datos.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Interfaz de línea de comandos (CLI), modo interactivo y validación de extremo a extremo.

- [X] T019 Implement CLI command-line arguments parsing with sys.argv and stdout/stderr handling in conversor.py
- [X] T020 Implement CLI interactive input fallback when run without arguments in conversor.py
- [X] T021 Execute validation scenarios defined in specs/001-conversor-temperatura/quickstart.md
- [X] T022 [P] Run full unittest suite ensuring 100% pass rate in tests/test_conversor.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias, inicia de inmediato.
- **Foundational (Phase 2)**: Depende de Phase 1 completada. Bloquea todas las historias de usuario.
- **User Stories (Phase 3+)**: Dependen de Phase 2.
  - US1 (Phase 3) se implementa primero (MVP).
  - US2 (Phase 4) se implementa a continuación.
  - US3 (Phase 5) cierra el grafo de conversiones.
- **Polish (Phase 6)**: Depende de que las historias US1, US2 y US3 estén implementadas en la librería base.

### Within Each User Story

1. Pruebas unitarias escritas primero (deben fallar antes de implementar la funcionalidad).
2. Lógica de conversión y validaciones asociadas.
3. Validación y verificación en verde del checkpoint de la historia.

### Parallel Opportunities

- T006 y T007 pueden redactarse en paralelo dentro de tests/test_conversor.py.
- T010 y T011 pueden redactarse en paralelo dentro de tests/test_conversor.py.
- T014, T015 y T016 pueden redactarse en paralelo.
- T022 puede ejecutarse de manera concurrente con la validación de documentación.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Setup (T001-T002) y Foundational (T003-T005).
2. Escribir pruebas para US1 (T006-T007).
3. Implementar lógica C↔F y redondeo (T008-T009).
4. **Validar MVP**: Correr pruebas y verificar entrega funcional inmediata.

### Incremental Delivery

1. MVP listo (Celsius ↔ Fahrenheit).
2. Agregar US2 (Celsius ↔ Kelvin y validación Kelvin >= 0).
3. Agregar US3 (Fahrenheit ↔ Kelvin y optimización misma escala).
4. Incorporar interfaz CLI interactiva y por argumentos (T019-T020).
5. Certificación completa contra quickstart.md (T021-T022).
