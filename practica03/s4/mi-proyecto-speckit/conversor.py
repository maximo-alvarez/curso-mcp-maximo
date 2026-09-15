"""
Conversor de Temperatura (Celsius, Fahrenheit, Kelvin)
Implementación siguiendo la especificación y diseño de Spec Kit.
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


def _validar_y_parsear_numero(valor: Union[int, float, str]) -> float:
    """Valida y convierte el valor de entrada a tipo flotante."""
    if valor is None:
        raise ConversionError("Error: El valor de temperatura no puede ser nulo.")
    
    if isinstance(valor, bool):
        raise ConversionError("Error: El valor de temperatura no puede ser booleano.")

    try:
        if isinstance(valor, str):
            valor_str = valor.strip()
            if "," in valor_str and "." not in valor_str:
                valor_str = valor_str.replace(",", ".")
            return float(valor_str)
        return float(valor)
    except (ValueError, TypeError):
        raise ConversionError(
            f"Error: El valor '{valor}' no es un número válido. Ingrese un valor numérico (ej. 25, -10.5)."
        )


def convertir_temperatura(
    valor: Union[int, float, str],
    origen: str,
    destino: str,
) -> float:
    """
    Convierte una temperatura entre Celsius, Fahrenheit y Kelvin.
    """
    temp = _validar_y_parsear_numero(valor)
    escala_origen = _normalizar_escala(origen)
    escala_destino = _normalizar_escala(destino)

    # Validación de límite físico: Rechazar temperaturas por debajo del cero absoluto
    if escala_origen == "K" and temp < 0:
        raise ConversionError(
            f"Error: Temperatura en Kelvin inválida ({temp} K). Kelvin no puede ser menor a 0 (cero absoluto)."
        )
    if escala_origen == "C" and temp < -273.15:
        raise ConversionError(
            f"Error: Temperatura en Celsius inválida ({temp} °C). No puede ser menor a -273.15 °C (cero absoluto)."
        )
    if escala_origen == "F" and temp < -459.67:
        raise ConversionError(
            f"Error: Temperatura en Fahrenheit inválida ({temp} °F). No puede ser menor a -459.67 °F (cero absoluto)."
        )

    # Caso borde: Mismo valor de origen y destino
    if escala_origen == escala_destino:
        resultado = round(temp, 2)
        return 0.0 if resultado == -0.0 else resultado

    # Conversión a Celsius como escala intermedia
    if escala_origen == "C":
        temp_celsius = temp
    elif escala_origen == "F":
        temp_celsius = (temp - 32.0) * (5.0 / 9.0)
    elif escala_origen == "K":
        temp_celsius = temp - 273.15
    else:
        raise ConversionError(f"Error: Escala de origen '{origen}' no soportada.")

    # Conversión desde Celsius a escala destino
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
