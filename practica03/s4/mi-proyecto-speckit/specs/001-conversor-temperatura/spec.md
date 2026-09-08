# Feature Specification: Conversor de Temperatura

**Feature Branch**: `001-conversor-temperatura`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "Implementa el proyecto Conversor siguiendo esta spec: @spec_manual.md"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Conversión entre Celsius y Fahrenheit (Priority: P1)

Como usuario que necesita convertir temperaturas de uso cotidiano o meteorológico, quiero convertir valores entre Celsius y Fahrenheit de manera bidireccional para interpretar la temperatura en mi escala de preferencia.

**Why this priority**: Representa el caso de uso más habitual y común de conversión térmica a nivel global. Provee un producto mínimo viable (MVP) completamente funcional y de valor inmediato.

**Independent Test**: Se puede verificar de forma independiente ingresando temperaturas conocidas (ej. 0 °C → 32.00 °F, 100 °C → 212.00 °F, 98.6 °F → 37.00 °C) y validando la exactitud y redondeo a dos decimales.

**Acceptance Scenarios**:

1. **Given** una temperatura en Celsius de 0, **When** el usuario solicita la conversión a Fahrenheit, **Then** el sistema entrega un resultado de 32.00 °F.
2. **Given** una temperatura en Fahrenheit de 212, **When** el usuario solicita la conversión a Celsius, **Then** el sistema entrega un resultado de 100.00 °C.
3. **Given** una temperatura en Celsius de -40, **When** el usuario solicita la conversión a Fahrenheit, **Then** el sistema entrega un resultado de -40.00 °F.
4. **Given** una temperatura en Fahrenheit de 98.6, **When** el usuario solicita la conversión a Celsius, **Then** el sistema entrega 37.00 °C redondeado a dos decimales.

---

### User Story 2 - Conversión entre Celsius y Kelvin (Priority: P2)

Como estudiante, docente o profesional científico, quiero convertir temperaturas entre la escala Celsius y la escala termodinámica Kelvin para realizar cálculos científicos y académicos.

**Why this priority**: Complementa el sistema con soporte para la unidad base del Sistema Internacional (SI) y permite validar las restricciones físicas de la escala absoluta.

**Independent Test**: Se puede probar independientemente realizando conversiones directas de Celsius a Kelvin y viceversa, verificando tanto valores de referencia (0 °C = 273.15 K) como el rechazo estricto de temperaturas inferiores al cero absoluto (Kelvin < 0).

**Acceptance Scenarios**:

1. **Given** una temperatura en Celsius de 25, **When** el usuario solicita la conversión a Kelvin, **Then** el sistema entrega 298.15 K.
2. **Given** una temperatura en Kelvin de 300, **When** el usuario solicita la conversión a Celsius, **Then** el sistema entrega 26.85 °C.
3. **Given** una temperatura en Celsius de -273.15, **When** el usuario solicita la conversión a Kelvin, **Then** el sistema entrega 0.00 K.
4. **Given** una temperatura en Kelvin con valor negativo (ej. -5 K), **When** el usuario solicita una conversión, **Then** el sistema rechaza la operación informando que Kelvin no admite valores menores a 0.

---

### User Story 3 - Conversión entre Fahrenheit y Kelvin, y conversiones a la misma unidad (Priority: P3)

Como usuario, quiero poder convertir directamente entre Fahrenheit y Kelvin sin pasos intermedios manuales, y obtener una respuesta coherente cuando la unidad de origen y destino coincidan.

**Why this priority**: Cierra el grafo completo de conversiones de las tres unidades soportadas y garantiza consistencia operativa ante solicitudes reflexivas o directas.

**Independent Test**: Se puede verificar convirtiendo 32 °F a Kelvin (obteniendo 273.15 K), convirtiendo 0 K a Fahrenheit (obteniendo -459.67 °F), o solicitando convertir 50 °C a Celsius y recibiendo 50.00 °C.

**Acceptance Scenarios**:

1. **Given** una temperatura en Fahrenheit de 32, **When** el usuario solicita la conversión a Kelvin, **Then** el sistema entrega 273.15 K.
2. **Given** una temperatura en Kelvin de 273.15, **When** el usuario solicita la conversión a Fahrenheit, **Then** el sistema entrega 32.00 °F.
3. **Given** una temperatura de entrada con la misma unidad de origen y de destino (ej. 18.5 °C a Celsius), **When** el usuario ejecuta la conversión, **Then** el sistema entrega el mismo valor numérico con formato estándar de dos decimales (18.50 °C).

---

### Edge Cases

- **Entrada no numérica**: Si el usuario ingresa texto no numérico, caracteres especiales o valores vacíos (ej. `"abc"`, `""`), el sistema debe responder con un mensaje de error claro y comprensible sin fallos inesperados.
- **Valores por debajo del cero absoluto**: Si se ingresa una temperatura en Kelvin inferior a 0 (o equivalente por debajo de 0 K), el sistema debe rechazar la solicitud y emitir un mensaje indicando que no existen temperaturas inferiores al cero absoluto.
- **Misma unidad de origen y destino**: Si la unidad inicial y final son idénticas, el sistema debe retornar el valor de entrada formateado a 2 decimales sin introducir errores de redondeo o procesamiento.
- **Temperaturas negativas válidas**: Temperaturas bajo cero en Celsius y Fahrenheit (como -40 °C o -10 °F) deben procesarse con total exactitud y conservar su signo correspondiente.
- **Redondeo de decimales recurrentes o inexactos**: Conversiones que generen decimales continuos (ej. 1 °F a Celsius) deben redondearse estrictamente a 2 decimales usando aproximación estándar.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE soportar conversiones de temperatura entre las unidades Celsius, Fahrenheit y Kelvin.
- **FR-002**: El sistema DEBE convertir de forma bidireccional y precisa entre Celsius y Fahrenheit.
- **FR-003**: El sistema DEBE convertir de forma bidireccional y precisa entre Celsius y Kelvin.
- **FR-004**: El sistema DEBE convertir de forma bidireccional y precisa entre Fahrenheit y Kelvin.
- **FR-005**: El sistema DEBE redondear el resultado numérico de toda conversión a exactamente dos (2) cifras decimales.
- **FR-006**: El sistema DEBE rechazar cualquier valor de temperatura en Kelvin que sea menor a 0 (cero absoluto) y mostrar un mensaje de error explicativo.
- **FR-007**: El sistema DEBE validar que el valor de temperatura ingresado sea numérico, rechazando entradas alfanuméricas o vacías mediante un mensaje informativo sin interrupciones abruptas.
- **FR-008**: El sistema DEBE devolver el mismo valor numérico con el redondeo establecido cuando la unidad de origen y la unidad de destino sean idénticas.
- **FR-009**: El sistema DEBE procesar correctamente valores numéricos negativos válidos en Celsius y Fahrenheit.

### Key Entities *(include if feature involves data)*

- **Medida de Temperatura**: Representa una magnitud escalar térmica definida por un valor numérico y su escala de medida asociada.
- **Escala de Temperatura**: Define el conjunto de unidades termométricas permitidas por el sistema: Celsius (°C), Fahrenheit (°F) y Kelvin (K).
- **Resultado de Conversión**: Representa la salida entregada al usuario, compuesta por el valor numérico transformado redondeado a dos decimales, la unidad de destino y, en caso de fallo, el mensaje descriptivo del motivo del error.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de las conversiones con entradas válidas entre cualquier combinación de las tres escalas entrega resultados matemáticamente exactos redondeados a 2 decimales.
- **SC-002**: El 100% de los intentos de conversión con valores no numéricos son capturados e informados con mensajes de error comprensibles sin excepciones no controladas.
- **SC-003**: El 100% de las solicitudes con valores de temperatura en Kelvin menores a 0 K son rechazadas con una advertencia clara sobre el cero absoluto.
- **SC-004**: El tiempo de resolución de cualquier conversión individual es inmediato para el usuario.
- **SC-005**: Las solicitudes de conversión idéntica (misma unidad de entrada y salida) entregan exactamente el mismo valor ingresado preservando el formato de 2 decimales en el 100% de los casos.

## Assumptions

- Las tres únicas escalas térmicas contempladas en el alcance de esta especificación son Celsius, Fahrenheit y Kelvin.
- Las equivalencias termodinámicas estándar aplicadas son:
  - De Celsius a Fahrenheit: $(C \times 9/5) + 32$
  - De Fahrenheit a Celsius: $(F - 32) \times 5/9$
  - De Celsius a Kelvin: $C + 273.15$
  - De Kelvin a Celsius: $K - 273.15$
- Toda salida numérica válida se presenta con dos lugares decimales.
- La interfaz de interacción específica (línea de comandos, biblioteca o servicio) será determinada en la fase de planificación técnica, manteniéndose esta especificación agnóstica a la tecnología.
