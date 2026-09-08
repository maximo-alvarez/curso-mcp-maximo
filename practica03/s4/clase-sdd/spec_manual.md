## Objetivo
Convertir una temperatura entre Celsius, Fahrenheit y Kelvin.

## Criterios de aceptación
- [x] Convierte correctamente de Celsius a Fahrenheit y viceversa
- [x] Convierte correctamente de Celsius a Kelvin y viceversa
- [x] Redondea el resultado a 2 decimales
- [x] Rechaza una temperatura en Kelvin menor a 0

## Casos borde
- Valor no numérico como entrada (ej. "abc") → error claro, no una excepción sin control
- Mismo valor de entrada y salida (ej. Celsius a Celsius) → debe devolver el mismo número
- Números negativos válidos en Celsius/Fahrenheit → deben procesarse sin problema
