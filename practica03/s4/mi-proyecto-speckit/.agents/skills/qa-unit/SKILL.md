---
name: qa-unit
description: Genera tests unitarios siguiendo estrictamente lo definido en test-spec.md, sin improvisar qué probar.
---
# Instrucciones
1. Lee `test-spec.md`. Si no existe, DETENTE y pide al usuario que lo cree primero — no inventes criterios propios.
2. Para cada punto de "Qué deben verificar los tests unitarios", genera un test con assert real que lo cumpla exactamente.
3. No agregues tests para casos que no estén en `test-spec.md` — si crees que falta algo importante, sugiérelo al final, no lo generes por tu cuenta.
4. Guarda en `tests/test_unitario.py`. Corre `pytest tests/test_unitario.py -v` y reporta cuántos pasaron.
