import pytest
from conversor import convertir_temperatura, ConversionError


def test_convertir_temperatura_25c_a_77f():
    resultado = convertir_temperatura(25, "C", "F")
    assert resultado == 77.0


def test_convertir_temperatura_texto_error_claro():
    with pytest.raises(ConversionError) as exc_info:
        convertir_temperatura("texto", "C", "F")
    assert "no es un número válido" in str(exc_info.value)


def test_convertir_temperatura_kelvin_negativo_rechazado():
    with pytest.raises(ConversionError) as exc_info:
        convertir_temperatura(-10, "K", "C")
    assert "Kelvin no puede ser menor a 0" in str(exc_info.value)
