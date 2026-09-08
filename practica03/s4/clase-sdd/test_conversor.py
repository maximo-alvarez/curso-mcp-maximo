"""
Pruebas unitarias para el conversor de temperatura.
Verifica todos los criterios de aceptación y casos borde de spec_manual.md.
"""

import unittest
from conversor import convertir_temperatura, ConversionError


class TestConversorTemperatura(unittest.TestCase):

    # --- Criterios de aceptación ---

    def test_celsius_a_fahrenheit(self):
        self.assertEqual(convertir_temperatura(0, "C", "F"), 32.0)
        self.assertEqual(convertir_temperatura(100, "C", "F"), 212.0)
        self.assertEqual(convertir_temperatura(37, "C", "F"), 98.6)

    def test_fahrenheit_a_celsius(self):
        self.assertEqual(convertir_temperatura(32, "F", "C"), 0.0)
        self.assertEqual(convertir_temperatura(212, "F", "C"), 100.0)
        # Redondeo de -17.2222... a 2 decimales
        self.assertEqual(convertir_temperatura(1, "F", "C"), -17.22)

    def test_celsius_a_kelvin(self):
        self.assertEqual(convertir_temperatura(0, "C", "K"), 273.15)
        self.assertEqual(convertir_temperatura(100, "C", "K"), 373.15)
        self.assertEqual(convertir_temperatura(-273.15, "C", "K"), 0.0)

    def test_kelvin_a_celsius(self):
        self.assertEqual(convertir_temperatura(273.15, "K", "C"), 0.0)
        self.assertEqual(convertir_temperatura(373.15, "K", "C"), 100.0)
        self.assertEqual(convertir_temperatura(0, "K", "C"), -273.15)

    def test_fahrenheit_a_kelvin_y_viceversa(self):
        self.assertEqual(convertir_temperatura(32, "F", "K"), 273.15)
        self.assertEqual(convertir_temperatura(212, "F", "K"), 373.15)
        self.assertEqual(convertir_temperatura(273.15, "K", "F"), 32.0)

    def test_redondeo_dos_decimales(self):
        # 25 Celsius a Fahrenheit es 77.0
        self.assertEqual(convertir_temperatura(25, "C", "F"), 77.0)
        # 35.555 Celsius a Fahrenheit = 96.0
        self.assertEqual(convertir_temperatura(35.555, "C", "F"), 96.0)
        # 100 Fahrenheit a Celsius: (100 - 32) * 5/9 = 37.7777... -> 37.78
        self.assertEqual(convertir_temperatura(100, "F", "C"), 37.78)

    def test_rechazo_kelvin_menor_a_cero(self):
        with self.assertRaises(ConversionError) as ctx:
            convertir_temperatura(-1, "K", "C")
        self.assertIn("Kelvin no puede ser menor a 0", str(ctx.exception))

        with self.assertRaises(ConversionError) as ctx:
            convertir_temperatura(-0.01, "K", "F")
        self.assertIn("Kelvin no puede ser menor a 0", str(ctx.exception))

    # --- Casos borde especificados en spec_manual.md ---

    def test_caso_borde_valor_no_numerico(self):
        valores_invalidos = ["abc", "12a", "", " ", None, True, [10]]
        for val in valores_invalidos:
            with self.subTest(val=val):
                with self.assertRaises(ConversionError):
                    convertir_temperatura(val, "C", "F")

    def test_caso_borde_mismo_origen_y_destino(self):
        self.assertEqual(convertir_temperatura(25.456, "C", "C"), 25.46)
        self.assertEqual(convertir_temperatura(32.0, "F", "F"), 32.0)
        self.assertEqual(convertir_temperatura(100, "K", "K"), 100.0)

    def test_caso_borde_negativos_validos(self):
        # -40 es el punto de cruce donde C == F
        self.assertEqual(convertir_temperatura(-40, "C", "F"), -40.0)
        self.assertEqual(convertir_temperatura(-40, "F", "C"), -40.0)
        # Negativos válidos en Celsius que superan el cero absoluto
        self.assertEqual(convertir_temperatura(-200, "C", "K"), 73.15)


if __name__ == "__main__":
    unittest.main()
