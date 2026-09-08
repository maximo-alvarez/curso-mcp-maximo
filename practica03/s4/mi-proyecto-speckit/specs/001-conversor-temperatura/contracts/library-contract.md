# Library Contract: Conversor de Temperatura

**Feature**: `001-conversor-temperatura`

## 1. Signaturas Públicas

```python
from typing import Union

class ConversionError(ValueError):
    """Excepción lanzada cuando los datos de entrada o parámetros de escala violan las reglas del dominio."""
    pass

def convertir_temperatura(
    valor: Union[int, float, str],
    origen: str,
    destino: str,
) -> float:
    """
    Convierte un valor de temperatura entre las escalas Celsius (C), Fahrenheit (F) y Kelvin (K).

    Parámetros:
        valor: Valor numérico a convertir (admisible int, float o str representativo).
        origen: Unidad o símbolo de partida ('C', 'F', 'K' o equivalentes como 'CELSIUS').
        destino: Unidad o símbolo objetivo ('C', 'F', 'K' o equivalentes).

    Retorno:
        float: Valor resultante redondeado a dos cifras decimales.

    Lanza:
        ConversionError: Si el valor no es numérico, es None/booleano, contiene una escala
                         desconocida, o se viola el límite físico del cero absoluto (< 0 K).
    """
    ...
```
