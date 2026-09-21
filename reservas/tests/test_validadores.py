from datetime import date

from app.utils.validadores import (
    validar_fecha_futura_o_presente,
    validar_formato_fecha,
    validar_formato_hora,
    validar_orden_horas,
    verificar_solapamiento_intervalos,
)


def test_validadores_formatos_temporales():
    # 1. Validación de formato de fecha
    assert validar_formato_fecha("2026-10-15") is True
    assert validar_formato_fecha("2024-02-29") is True  # Año bisiesto
    assert validar_formato_fecha("2023-02-29") is False  # No bisiesto
    assert validar_formato_fecha("15-10-2026") is False
    assert validar_formato_fecha("2026/10/15") is False
    assert validar_formato_fecha("invalido") is False
    assert validar_formato_fecha("") is False
    assert validar_formato_fecha(None) is False

    # 2. Validación de formato de hora (24h)
    assert validar_formato_hora("00:00") is True
    assert validar_formato_hora("09:30") is True
    assert validar_formato_hora("23:59") is True
    assert validar_formato_hora("24:00") is False  # 24:00 no es hora válida
    assert validar_formato_hora("12:60") is False
    assert validar_formato_hora("9:30") is False  # Requiere dos dígitos
    assert validar_formato_hora("invalido") is False
    assert validar_formato_hora("") is False
    assert validar_formato_hora(None) is False

    # 3. Validación de orden de horas
    assert validar_orden_horas("09:00", "10:00") is True
    assert validar_orden_horas("10:00", "10:00") is False  # Horas iguales
    assert validar_orden_horas("11:00", "10:00") is False  # Fin menor que inicio
    assert validar_orden_horas("09:00", "invalido") is False
    assert validar_orden_horas("invalido", "10:00") is False

    # 4. Validación de fecha futura o presente
    ref = date(2026, 10, 15)
    assert validar_fecha_futura_o_presente("2026-10-15", fecha_referencia=ref) is True  # Hoy
    assert validar_fecha_futura_o_presente("2026-10-16", fecha_referencia=ref) is True  # Mañana
    assert validar_fecha_futura_o_presente("2026-10-14", fecha_referencia=ref) is False  # Ayer
    assert validar_fecha_futura_o_presente("invalido", fecha_referencia=ref) is False

    # 5. Detección matemática de solapamiento
    # Caso A: Solapamiento parcial (A termina después de que B empieza)
    assert verificar_solapamiento_intervalos("10:00", "12:00", "11:00", "13:00") is True
    # Caso B: Solapamiento idéntico
    assert verificar_solapamiento_intervalos("10:00", "12:00", "10:00", "12:00") is True
    # Caso C: Contención total (B dentro de A)
    assert verificar_solapamiento_intervalos("09:00", "15:00", "10:00", "12:00") is True
    # Caso D: Contigüidad exacta (permitido, NO solapa)
    assert verificar_solapamiento_intervalos("10:00", "11:00", "11:00", "12:00") is False
    assert verificar_solapamiento_intervalos("11:00", "12:00", "10:00", "11:00") is False
    # Caso E: Disjuntos separados en el tiempo
    assert verificar_solapamiento_intervalos("08:00", "09:00", "11:00", "12:00") is False
