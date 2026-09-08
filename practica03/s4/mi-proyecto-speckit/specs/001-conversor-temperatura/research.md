# Technical Research: Conversor de Temperatura

**Feature**: `001-conversor-temperatura`
**Status**: Completed

## 1. Runtime y Lenguaje

- **Decision**: Python 3 (versión 3.9+) empleando únicamente la biblioteca estándar (`sys`, `typing`, `unittest`).
- **Rationale**: 
  - Disponibilidad nativa en el entorno de ejecución (`Python 3.9.6`).
  - Cero dependencias externas requeridas, facilitando reproducibilidad inmediata sin gestores de paquetes adicionales (`pip`, `poetry`).
  - Tipado estático con `typing` y suite de pruebas nativa con `unittest`.
- **Alternatives considered**:
  - *Node.js / TypeScript*: Descartado por requerir `package.json`, compilación/transpilación y dependencias de testing (`jest`/`vitest`).
  - *C/Rust/Go*: Descartado por requerir cadenas de compilación pesadas innecesarias para una herramienta educativa de conversión.

---

## 2. Patrón de Arquitectura

- **Decision**: Diseño **Library-First** con interfaz CLI desacoplada.
  - Módulo principal (`src/conversor.py` o raíz del proyecto) exponiendo la función pura `convertir_temperatura(valor, origen, destino)` y la excepción tipada `ConversionError`.
  - Punto de entrada CLI (`main()`) con soporte para modo por argumentos de línea de comando (`python conversor.py <valor> <origen> <destino>`) y modo interactivo.
  - Pruebas unitarias completas bajo `tests/test_conversor.py` con `unittest`.
- **Rationale**:
  - Satisface el principio de modularidad e independencia de pruebas.
  - Facilita la automatización y scripting mediante CLI, manteniendo la lógica reutilizable como biblioteca.
- **Alternatives considered**:
  - *CLI monolítica sin biblioteca expuesta*: Descartada por dificultar las pruebas unitarias automatizadas y la reutilización.

---

## 3. Modelo Matemático de Conversión

- **Decision**: Conversión mediante pivote canónico en **Celsius** ($O \rightarrow C \rightarrow D$) con optimización de cortocircuito para unidades idénticas ($O == D$).
  - Si $Origen == Destino$: Devolver el valor con redondeo estándar a 2 decimales.
  - Paso 1 ($Origen \rightarrow Celsius$):
    - $C \rightarrow C$: $C$
    - $F \rightarrow C$: $(F - 32) \times \frac{5}{9}$
    - $K \rightarrow C$: $K - 273.15$
  - Paso 2 ($Celsius \rightarrow Destino$):
    - $C \rightarrow C$: $C$
    - $F$: $(C \times \frac{9}{5}) + 32$
    - $K$: $C + 273.15$
  - Tratamiento especial para signo cero negativo: convertir `-0.0` a `0.0`.
- **Rationale**:
  - Reduce la complejidad combinatoria y la duplicación de código de $N \times (N-1)$ funciones a $2 \times N$ transformaciones.
  - Precisión numérica suficiente: el error residual de coma flotante de 64 bits en conversiones lineales simples queda completamente absorbido al redondear a 2 decimales.
- **Alternatives considered**:
  - *6 funciones independientes de conversión directa*: Descartado por mayor código repetitivo sin beneficio de rendimiento para operaciones $O(1)$.

---

## 4. Validación de Entradas y Casos Borde

- **Decision**: Validación estricta con excepción controlada `ConversionError` (hereda de `ValueError`).
  - Rechazar tipos `None`, booleanos y valores no numéricos (`"abc"`, `""`, etc.) con mensajes explicativos claros.
  - Soportar cadenas con coma o punto decimal (ej. `"25,5"` o `"25.5"`).
  - Normalizar escalas de temperatura a su letra representativa en mayúsculas (`"C"`, `"F"`, `"K"`), tolerando nombres completos (`"CELSIUS"`, `"FAHRENHEIT"`, `"KELVIN"`).
  - Rechazar cualquier temperatura en Kelvin inferior a 0 K ($< 0$), así como resultados convertidos que caigan por debajo del cero absoluto ($< 0\text{ K}$).
- **Rationale**:
  - Cumple estrictamente con los criterios de aceptación y casos borde de `spec_manual.md`.
  - Evita fallos no controlados (`uncaught exceptions`) en tiempo de ejecución.
- **Alternatives considered**:
  - *Trunking o ajuste silencioso al cero absoluto*: Descartado porque la especificación exige rechazo explícito con error descriptivo.
