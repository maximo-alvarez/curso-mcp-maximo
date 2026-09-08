"""
Conversor de Temperatura (Celsius, Fahrenheit, Kelvin)
Implementado siguiendo spec_manual.md
"""

import sys
from typing import Union


class ConversionError(ValueError):
    """Excepción para errores de validación y conversión controlados."""
    pass


NORMALIZACION_ESCALAS = {
    "C": "C",
    "CELSIUS": "C",
    "F": "F",
    "FAHRENHEIT": "F",
    "K": "K",
    "KELVIN": "K",
}


def _normalizar_escala(escala: str) -> str:
    """Normaliza y valida la escala recibida."""
    if not isinstance(escala, str):
        raise ConversionError(f"Error: La unidad debe ser un texto, se recibió {type(escala).__name__}.")
    
    limpia = escala.strip().upper()
    if limpia in NORMALIZACION_ESCALAS:
        return NORMALIZACION_ESCALAS[limpia]
    
    raise ConversionError(
        f"Error: Escala '{escala}' no reconocida. Opciones válidas: Celsius (C), Fahrenheit (F), Kelvin (K)."
    )


def convertir_temperatura(
    valor: Union[int, float, str],
    origen: str,
    destino: str,
) -> float:
    """
    Convierte una temperatura entre Celsius, Fahrenheit y Kelvin.

    Criterios de aceptación:
    - Convierte correctamente de Celsius a Fahrenheit y viceversa.
    - Convierte correctamente de Celsius a Kelvin y viceversa.
    - Redondea el resultado a 2 decimales.
    - Rechaza una temperatura en Kelvin menor a 0.

    Casos borde:
    - Valor no numérico como entrada -> error claro controlado.
    - Mismo valor de entrada y salida -> devuelve el mismo número (redondeado a 2 decimales).
    - Números negativos válidos en Celsius/Fahrenheit -> procesados sin problema.
    """
    # 1. Validación de valor no numérico
    if valor is None:
        raise ConversionError("Error: El valor de temperatura no puede ser nulo.")
    
    if isinstance(valor, bool):  # bool es subclase de int en Python (True == 1)
        raise ConversionError("Error: El valor de temperatura no puede ser booleano.")

    try:
        if isinstance(valor, str):
            # Limpieza básica de espacios
            valor_str = valor.strip()
            # Soporte amigable para coma decimal si viene de entrada en español
            if "," in valor_str and "." not in valor_str:
                valor_str = valor_str.replace(",", ".")
            temp = float(valor_str)
        else:
            temp = float(valor)
    except (ValueError, TypeError):
        raise ConversionError(
            f"Error: El valor '{valor}' no es un número válido. Ingrese un valor numérico (ej. 25, -10.5)."
        )

    # 2. Normalización de escalas
    escala_origen = _normalizar_escala(origen)
    escala_destino = _normalizar_escala(destino)

    # 3. Validación de límite físico: Rechaza temperatura en Kelvin menor a 0
    if escala_origen == "K" and temp < 0:
        raise ConversionError(
            f"Error: Temperatura en Kelvin inválida ({temp} K). Kelvin no puede ser menor a 0 (cero absoluto)."
        )

    # 4. Mismo valor de entrada y salida
    if escala_origen == escala_destino:
        resultado = round(temp, 2)
        return 0.0 if resultado == -0.0 else resultado

    # 5. Conversión a Celsius como escala intermedia
    if escala_origen == "C":
        temp_celsius = temp
    elif escala_origen == "F":
        temp_celsius = (temp - 32.0) * (5.0 / 9.0)
    elif escala_origen == "K":
        temp_celsius = temp - 273.15
    else:
        raise ConversionError(f"Error: Escala de origen '{origen}' no soportada.")

    # 6. Conversión desde Celsius hacia escala destino
    if escala_destino == "C":
        resultado = temp_celsius
    elif escala_destino == "F":
        resultado = (temp_celsius * (9.0 / 5.0)) + 32.0
    elif escala_destino == "K":
        temp_kelvin = temp_celsius + 273.15
        if temp_kelvin < 0:
            raise ConversionError(
                f"Error: El resultado equivale a {round(temp_kelvin, 2)} K, lo cual es menor a 0 K (por debajo del cero absoluto)."
            )
        resultado = temp_kelvin
    else:
        raise ConversionError(f"Error: Escala de destino '{destino}' no soportada.")

    resultado_redondeado = round(resultado, 2)
    return 0.0 if resultado_redondeado == -0.0 else resultado_redondeado


def main() -> int:
    """Punto de entrada CLI para ejecución interactiva o por argumentos."""
    args = sys.argv[1:]
    
    if len(args) == 0:
        print("=== Conversor de Temperatura ===")
        try:
            val_input = input("Ingrese la temperatura: ")
            orig_input = input("Escala de origen (C, F, K): ")
            dest_input = input("Escala de destino (C, F, K): ")
            res = convertir_temperatura(val_input, orig_input, dest_input)
            print(f"Resultado: {res} {_normalizar_escala(dest_input)}")
            return 0
        except ConversionError as e:
            print(f"{e}", file=sys.stderr)
            return 1
        except (KeyboardInterrupt, EOFError):
            print("\nOperación cancelada.")
            return 0

    if len(args) == 3:
        valor_raw, origen_raw, destino_raw = args
        try:
            res = convertir_temperatura(valor_raw, origen_raw, destino_raw)
            print(f"{res}")
            return 0
        except ConversionError as e:
            print(f"{e}", file=sys.stderr)
            return 1

    print("Uso: python conversor.py <valor> <origen: C|F|K> <destino: C|F|K>", file=sys.stderr)
    print("Ejemplo: python conversor.py 100 C F", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
