---
name: qa-coverage
description: Ejecuta y resume el reporte de cobertura de tests del proyecto, señalando líneas sin probar.
---
# Instrucciones
1. Corre `pytest --cov=. --cov-report=term-missing`.
2. Resume: porcentaje total, y qué líneas "Missing" son casos borde olvidados vs. código no usado.
3. No agregues tests automáticamente — solo diagnostica.
