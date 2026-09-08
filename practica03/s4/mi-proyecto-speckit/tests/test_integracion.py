import sys
from conversor import main


def test_flujo_completo_conversion_punta_a_punta(monkeypatch, capsys):
    # Simula el flujo interactivo de punta a punta: pedir conversión -> validar entrada -> devolver resultado
    entradas = iter(["25", "C", "F"])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))
    monkeypatch.setattr(sys, "argv", ["conversor.py"])

    codigo_salida = main()
    salida = capsys.readouterr().out

    assert codigo_salida == 0
    assert "Resultado: 77.0 F" in salida
