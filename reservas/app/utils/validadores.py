"""Funciones puras para validación de fechas, horas e intervalos temporales.

Cumple con el Artículo I.4 de la Constitución: funciones puras, mismo input -> mismo output,
sin efectos secundarios y sin dependencias de services, routers ni repositories.
"""
from datetime import date, datetime


def validar_formato_fecha(fecha: str) -> bool:
    """Valida que la fecha tenga el formato ISO YYYY-MM-DD y sea una fecha de calendario real."""
    if not isinstance(fecha, str) or len(fecha) != 10:
        return False
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validar_formato_hora(hora: str) -> bool:
    """Valida que la hora tenga el formato HH:MM en rango de 24 horas (00:00 - 23:59)."""
    if not isinstance(hora, str) or len(hora) != 5:
        return False
    try:
        datetime.strptime(hora, "%H:%M")
        return True
    except ValueError:
        return False


def validar_orden_horas(hora_inicio: str, hora_fin: str) -> bool:
    """Valida que los formatos sean correctos y que hora_fin sea estrictamente posterior a hora_inicio."""
    if not validar_formato_hora(hora_inicio) or not validar_formato_hora(hora_fin):
        return False
    return hora_fin > hora_inicio


def validar_fecha_futura_o_presente(fecha: str, fecha_referencia: date | None = None) -> bool:
    """Valida que la fecha especificada sea igual o posterior a la fecha de referencia (hoy por defecto)."""
    if not validar_formato_fecha(fecha):
        return False
    try:
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        return False

    referencia = fecha_referencia if fecha_referencia is not None else date.today()
    return fecha_obj >= referencia


def verificar_solapamiento_intervalos(inicio1: str, fin1: str, inicio2: str, fin2: str) -> bool:
    """Determina si dos intervalos temporales semiabiertos [inicio, fin) se solapan.

    Condición matemática: (inicio1 < fin2) and (fin1 > inicio2).
    Si un intervalo termina exactamente donde inicia el otro (inicio2 == fin1 o inicio1 == fin2),
    son contiguos y NO se solapan (retorna False).
    """
    return (inicio1 < fin2) and (fin1 > inicio2)
