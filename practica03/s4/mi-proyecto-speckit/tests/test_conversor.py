"""
Pruebas unitarias para el conversor de temperatura.
"""

import unittest
from io import StringIO
from unittest.mock import patch
from conversor import convertir_temperatura, ConversionError, main


class TestConversorTemperatura(unittest.TestCase):

    # --- User Story 1: Celsius y Fahrenheit ---

    def test_celsius_a_fahrenheit(self):
        self.assertEqual(convertir_temperatura(0, "C", "F"), 32.0)
        self.assertEqual(convertir_temperatura(100, "C", "F"), 212.0)
        self.assertEqual(convertir_temperatura(37, "C", "F"), 98.6)

    def test_fahrenheit_a_celsius(self):
        self.assertEqual(convertir_temperatura(32, "F", "C"), 0.0)
        self.assertEqual(convertir_temperatura(212, "F", "C"), 100.0)
        self.assertEqual(convertir_temperatura(1, "F", "C"), -17.22)

    def test_temperaturas_negativas_c_y_f(self):
        self.assertEqual(convertir_temperatura(-40, "C", "F"), -40.0)
        self.assertEqual(convertir_temperatura(-40, "F", "C"), -40.0)

    def test_redondeo_dos_decimales_us1(self):
        self.assertEqual(convertir_temperatura(35.555, "C", "F"), 96.0)
        self.assertEqual(convertir_temperatura(100, "F", "C"), 37.78)

    # --- User Story 2: Celsius y Kelvin ---

    def test_celsius_a_kelvin(self):
        self.assertEqual(convertir_temperatura(0, "C", "K"), 273.15)
        self.assertEqual(convertir_temperatura(100, "C", "K"), 373.15)
        self.assertEqual(convertir_temperatura(-273.15, "C", "K"), 0.0)

    def test_kelvin_a_celsius(self):
        self.assertEqual(convertir_temperatura(273.15, "K", "C"), 0.0)
        self.assertEqual(convertir_temperatura(373.15, "K", "C"), 100.0)
        self.assertEqual(convertir_temperatura(0, "K", "C"), -273.15)

    def test_rechazo_kelvin_menor_a_cero(self):
        with self.assertRaises(ConversionError) as ctx:
            convertir_temperatura(-1, "K", "C")
        self.assertIn("Kelvin no puede ser menor a 0", str(ctx.exception))

        with self.assertRaises(ConversionError) as ctx:
            convertir_temperatura(-0.01, "K", "F")
        self.assertIn("Kelvin no puede ser menor a 0", str(ctx.exception))

    # --- User Story 3: Fahrenheit ↔ Kelvin y Misma Unidad ---

    def test_fahrenheit_a_kelvin_y_viceversa(self):
        self.assertEqual(convertir_temperatura(32, "F", "K"), 273.15)
        self.assertEqual(convertir_temperatura(212, "F", "K"), 373.15)
        self.assertEqual(convertir_temperatura(273.15, "K", "F"), 32.0)

    def test_caso_borde_mismo_origen_y_destino(self):
        self.assertEqual(convertir_temperatura(25.456, "C", "C"), 25.46)
        self.assertEqual(convertir_temperatura(32.0, "F", "F"), 32.0)
        self.assertEqual(convertir_temperatura(100, "K", "K"), 100.0)

    def test_caso_borde_valor_no_numerico(self):
        valores_invalidos = ["abc", "12a", "", " ", None, True, False, [10]]
        for val in valores_invalidos:
            with self.subTest(val=val):
                with self.assertRaises(ConversionError):
                    convertir_temperatura(val, "C", "F")

    def test_normalizacion_escalas_y_formato_coma(self):
        self.assertEqual(convertir_temperatura("25,5", "celsius", "FAHRENHEIT"), 77.9)
        with self.assertRaises(ConversionError):
            convertir_temperatura(10, "Rankine", "C")

    # --- CLI Main & Arguments ---

    @patch("sys.argv", ["conversor.py", "100", "C", "F"])
    def test_cli_argumentos_exito(self):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            exit_code = main()
            self.assertEqual(exit_code, 0)
            self.assertEqual(fake_out.getvalue().strip(), "212.0")

    @patch("sys.argv", ["conversor.py", "-10", "K", "C"])
    def test_cli_argumentos_error(self):
        with patch("sys.stderr", new=StringIO()) as fake_err:
            exit_code = main()
            self.assertEqual(exit_code, 1)
            self.assertIn("Kelvin no puede ser menor a 0", fake_err.getvalue())

    @patch("sys.argv", ["conversor.py", "100", "C"])
    def test_cli_argumentos_insuficientes(self):
        with patch("sys.stderr", new=StringIO()) as fake_err:
            exit_code = main()
            self.assertEqual(exit_code, 1)
            self.assertIn("Uso: python conversor.py", fake_err.getvalue())


if __name__ == "__main__":
    unittest.main()
