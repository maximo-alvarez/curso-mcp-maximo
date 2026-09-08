# Resultados de Pruebas — Bloque 3.A (Spec a mano)

## Implementación
- **Archivo de especificación:** `spec_manual.md`
- **Código fuente:** `conversor.py`
- **Suite de pruebas:** `test_conversor.py`

---

## Casos de Prueba Evaluados

| Tipo de caso | Entrada / Comando | Resultado Esperado | Resultado Obtenido | Estado |
|---|---|---|---|:---:|
| **Caso normal** (Uso típico y esperado) | `100` de `C` a `F` | `212.0` | `212.0` | ✅ Exitoso |
| **Caso borde de la spec** (Regla explícita: Kelvin < 0) | `-10` de `K` a `C` | Rechazo con error claro controlado sin excepción descontrolada | `Error: Temperatura en Kelvin inválida (-10.0 K). Kelvin no puede ser menor a 0 (cero absoluto).` (código de salida 1) | ✅ Exitoso |
| **Caso borde de la spec** (Entrada no numérica) | `"abc"` de `C` a `F` | Error claro sin traceback | `Error: El valor 'abc' no es un número válido. Ingrese un valor numérico (ej. 25, -10.5).` | ✅ Exitoso |
| **Caso no contemplado** (Temperatura bajo el cero absoluto en Celsius o escala no soportada) | `-300` de `C` a `K` | La spec no definió explícitamente qué hacer con valores < 0 K originados en Celsius | El conversor validó la escala destino física: `Error: El resultado equivale a -26.85 K, lo cual es menor a 0 K (por debajo del cero absoluto).` | ✅ Manejado con seguridad |

---

## Verificación de Criterios de Aceptación de `spec_manual.md`

- [x] **Convierte correctamente de Celsius a Fahrenheit y viceversa:** Probado con 0°C → 32°F, 100°C → 212°F, 32°F → 0°C, 212°F → 100°C.
- [x] **Convierte correctamente de Celsius a Kelvin y viceversa:** Probado con 0°C → 273.15 K, 100°C → 373.15 K, 273.15 K → 0°C.
- [x] **Redondea el resultado a 2 decimales:** 100°F → 37.78°C, 1°F → -17.22°C.
- [x] **Rechaza una temperatura en Kelvin menor a 0:** Rechaza entradas negativas en K con mensaje descriptivo.

---

## Casos Borde de `spec_manual.md`

- [x] **Valor no numérico como entrada (ej. "abc"):** Capturado y controlado emitiendo mensaje descriptivo sin caída abrupta ni traceback.
- [x] **Mismo valor de entrada y salida (ej. Celsius a Celsius):** Devuelve el mismo valor numérico con el redondeo estándar (ej. 25.55 C a C → 25.55).
- [x] **Números negativos válidos en Celsius/Fahrenheit:** -40°C = -40°F evaluado correctamente.
