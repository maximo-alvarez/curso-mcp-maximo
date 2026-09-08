# Data Model: Conversor de Temperatura

**Feature**: `001-conversor-temperatura`
**Status**: Approved

## 1. Entidades Principales

### EscalaTermica (Enumeración / Valor Canónico)

Representa las unidades de medida de temperatura admitidas en el sistema.

| Símbolo | Nombre Completo | Cero Absoluto |
|---------|-----------------|---------------|
| `C`     | Celsius         | -273.15 °C    |
| `F`     | Fahrenheit      | -459.67 °F    |
| `K`     | Kelvin          | 0.00 K        |

- **Normalización**:
  - `C`, `CELSIUS` $\rightarrow$ `C`
  - `F`, `FAHRENHEIT` $\rightarrow$ `F`
  - `K`, `KELVIN` $\rightarrow$ `K`

---

### SolicitudConversion

Representa los datos requeridos para ejecutar una operación de conversión.

| Campo | Tipo | Requerido | Restricciones / Reglas |
|---|---|:---:|---|
| `valor` | `float` / `int` / `str` | Sí | Debe ser convertible a número flotante real. No puede ser booleano, nulo ni texto alfanumérico no convertible. |
| `origen` | `str` | Sí | Debe coincidir con una de las escalas válidas (`C`, `F`, `K`). Si `origen == 'K'`, `valor >= 0.0`. |
| `destino` | `str` | Sí | Debe coincidir con una de las escalas válidas (`C`, `F`, `K`). |

---

### ResultadoConversion

Representa la respuesta entregada por el sistema tras procesar una `SolicitudConversion`.

| Campo | Tipo | Descripción |
|---|---|---|
| `valor` | `float` | Valor numérico transformado, redondeado a 2 lugares decimales. Si el redondeo produce `-0.0`, se normaliza a `0.0`. |
| `unidad` | `str` | Símbolo canónico de la escala de destino (`C`, `F`, `K`). |

---

### ErrorConversion (Excepción de Dominio)

Representa una condición inválida detectada durante la validación o el cómputo.

| Atributo | Tipo | Descripción |
|---|---|---|
| `mensaje` | `str` | Explicación legible y orientada al usuario del error detectado. |
| `tipo` | `class` | Hereda de `ValueError` (`ConversionError`). |

---

## 2. Reglas de Validación

1. **RV-01 (Tipo numérico)**: El valor no puede ser nulo, booleano ni contener caracteres alfanuméricos incompatibles.
2. **RV-02 (Cero absoluto en origen)**: Si la escala de origen es Kelvin (`K`), el valor debe ser estrictamente $\ge 0.0$.
3. **RV-03 (Cero absoluto en resultado)**: Si el valor convertido resultante en Kelvin es $< 0.0$, la operación debe ser rechazada.
4. **RV-04 (Escalas admitidas)**: Las escalas de origen y destino deben pertenecer exclusivamente al conjunto `{C, F, K}`.
5. **RV-05 (Redondeo)**: Todo valor devuelto debe redondearse a 2 cifras decimales (`round(resultado, 2)`).
