---
name: qa-security
description: Revisa el proyecto en busca de secretos expuestos, validación de entradas insuficiente y manejo de excepciones riesgoso.
---
# Instrucciones
1. Busca claves/contraseñas escritas directamente en el código.
2. Revisa validación de entradas (tipo, formato, longitud, rango).
3. Busca `except:` genérico o `except: pass`.
4. Reporta en esta tabla:

| Caso | Lo que se encontró | Corrección sugerida |
|---|---|---|
| 🔑 Secreto expuesto | [hallazgo o "sin hallazgos"] | [sugerencia] |
| 🧪 Validación de entradas | [hallazgo o "sin hallazgos"] | [sugerencia] |
| 🚪 Manejo de excepciones | [hallazgo o "sin hallazgos"] | [sugerencia] |

5. No corrijas automáticamente — solo diagnostica.
