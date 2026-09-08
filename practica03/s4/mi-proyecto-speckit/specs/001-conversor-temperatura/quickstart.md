# Quickstart: Validación del Conversor de Temperatura

**Feature**: `001-conversor-temperatura`

Esta guía describe los pasos para validar el funcionamiento del Conversor de Temperatura de principio a fin una vez implementado.

## Prerrequisitos

- Python 3.9 o superior instalado (`python3 --version`).
- No requiere dependencias externas ni instalación de paquetes mediante `pip`.

---

## Ejecución de la Suite de Pruebas Automatizadas

Para validar todos los criterios de aceptación y casos de borde de la especificación:

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```
o directamente:
```bash
python3 -m unittest tests/test_conversor.py -v
```

**Resultado esperado**:
- Todas las pruebas deben pasar con estado `OK`.
- Cobertura completa de conversiones C↔F, C↔K, F↔K, idénticos, redondeos a 2 decimales y rechazo de errores.

---

## Escenarios de Validación por CLI

### 1. Conversión Celsius a Fahrenheit (Escenario P1)
```bash
python3 conversor.py 100 C F
```
**Salida esperada**:
```text
212.0
```

### 2. Conversión Fahrenheit a Celsius con redondeo
```bash
python3 conversor.py 1 F C
```
**Salida esperada**:
```text
-17.22
```

### 3. Conversión Celsius a Kelvin (Escenario P2)
```bash
python3 conversor.py 0 C K
```
**Salida esperada**:
```text
273.15
```

### 4. Rechazo de Kelvin menor a cero (Límite físico)
```bash
python3 conversor.py -10 K C
```
**Salida esperada en stderr**:
```text
Error: ... Kelvin no puede ser menor a 0 ...
```
**Código de retorno**: `1`

### 5. Rechazo de valor no numérico (Caso borde)
```bash
python3 conversor.py "abc" C F
```
**Salida esperada en stderr**:
```text
Error: El valor 'abc' no es un número válido. Ingrese un valor numérico ...
```
**Código de retorno**: `1`

### 6. Conversión a la misma unidad
```bash
python3 conversor.py 25.456 C C
```
**Salida esperada**:
```text
25.46
```
