# CLI Contract: Conversor de Temperatura

**Feature**: `001-conversor-temperatura`

## 1. Modos de Ejecución

### Modo Directo por Argumentos

```bash
python3 conversor.py <valor> <origen> <destino>
```

#### Parámetros Posicionales
- `<valor>`: Expresión numérica a convertir (ej. `100`, `32.5`, `-40`).
- `<origen>`: Escala origen (`C`, `F`, `K` o nombres completos equivalentes).
- `<destino>`: Escala destino (`C`, `F`, `K` o nombres completos equivalentes).

#### Salida Estándar (stdout)
- En caso de éxito: Imprime el valor numérico transformado redondeado a 2 decimales seguido de salto de línea.
  ```text
  212.0
  ```

#### Salida de Error (stderr) y Códigos de Salida (Exit Codes)
- Si los argumentos son insuficientes o incorrectos:
  - Salida (`stderr`):
    ```text
    Uso: python conversor.py <valor> <origen: C|F|K> <destino: C|F|K>
    Ejemplo: python conversor.py 100 C F
    ```
  - Código de salida: `1`
- Si ocurre un error de validación o conversión (`ConversionError`):
  - Salida (`stderr`): Mensaje descriptivo del error (ej. `Error: Kelvin no puede ser menor a 0 (cero absoluto).`)
  - Código de salida: `1`
- Si la ejecución es exitosa:
  - Código de salida: `0`

---

### Modo Interactivo

Si se invoca sin argumentos:
```bash
python3 conversor.py
```

#### Flujo Interactivo
1. Mensaje de bienvenida: `=== Conversor de Temperatura ===`
2. Solicitud 1: `Ingrese la temperatura: `
3. Solicitud 2: `Escala de origen (C, F, K): `
4. Solicitud 3: `Escala de destino (C, F, K): `
5. Salida en stdout: `Resultado: <valor> <unidad>` (ej. `Resultado: 212.0 F`) con exit code `0`.
6. En caso de error de entrada: Imprime mensaje en stderr y finaliza con exit code `1`.
