#!/usr/bin/env python3
"""
Script de reporte de calidad automatizado.
Ejecuta pruebas, mide cobertura, analiza seguridad y genera reporte-qa.html.
"""

import os
import re
import subprocess
import sys
from pathlib import Path


def correr_comando(cmd, cwd):
    env = os.environ.copy()
    venv_bin = Path("/Volumes/data/_cursos/_cedia_2026_programacion_mcp/proyecto01/practica03/.venv/bin")
    if venv_bin.exists():
        env["PATH"] = f"{venv_bin}:{env.get('PATH', '')}"
    
    res = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )
    return res.returncode, res.stdout


def analizar_seguridad(proyecto_dir):
    hallazgos = []
    conversor_file = proyecto_dir / "conversor.py"
    
    if conversor_file.exists():
        content = conversor_file.read_text(encoding="utf-8")
        
        # 1. Secretos
        secret_pattern = re.compile(r"(api[_-]?key|secret|token|password)\s*=\s*['\"][^'\"]+['\"]", re.I)
        if secret_pattern.search(content):
            hallazgos.append(("🔑 Secretos expuestos", "Posible credencial hardcodeada detectada"))
        else:
            hallazgos.append(("🔑 Secretos expuestos", "Sin hallazgos"))
            
        # 2. Validación de entradas
        if "temp < 0" in content and "-273.15" not in content:
            hallazgos.append((
                "🧪 Validación de entradas",
                "Falta validación de límite físico del cero absoluto en origen para Celsius (< -273.15 °C) y Fahrenheit (< -459.67 °F)"
            ))
        else:
            hallazgos.append(("🧪 Validación de entradas", "Sin hallazgos"))
            
        # 3. Excepciones genéricas
        bare_except = re.compile(r"except\s*:\s*(pass)?")
        if bare_except.search(content):
            hallazgos.append(("🚪 Manejo de excepciones", "Bloque except genérico o except: pass detectado"))
        else:
            hallazgos.append(("🚪 Manejo de excepciones", "Sin hallazgos (todas las excepciones son específicas)"))
    else:
        hallazgos.append(("Archivo", "conversor.py no encontrado"))
        
    return hallazgos


def main():
    script_dir = Path(__file__).resolve().parent
    # El proyecto está 3 niveles arriba: .agents/skills/qa-report -> .agents/skills -> .agents -> mi-proyecto-speckit
    proyecto_dir = script_dir.parents[2]
    
    # 1. Correr pytest con cobertura
    cmd = [sys.executable, "-m", "pytest", "--cov=conversor", "--cov-report=term-missing", "-v"]
    # Si pytest no está en sys.executable, usar pytest directamente
    ret, out = correr_comando(["pytest", "--cov=conversor", "--cov-report=term-missing", "-v"], proyecto_dir)
    
    tests_pasaron = (ret == 0)
    
    # Extraer métricas
    passed_match = re.search(r"(\d+)\s+passed", out)
    tests_count = passed_match.group(1) if passed_match else "0"
    
    cov_match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", out)
    if not cov_match:
        cov_match = re.search(r"conversor(?:\.py)?\s+\d+\s+\d+\s+(\d+)%", out)
    cobertura_pct = cov_match.group(1) if cov_match else "N/A"
    
    missing_match = re.search(r"conversor(?:\.py)?\s+\d+\s+\d+\s+\d+%\s+([0-9,\s-]+)", out)
    missing_lines = missing_match.group(1).strip() if missing_match else "Ninguna"

    # 2. Analizar seguridad
    hallazgos_sec = analizar_seguridad(proyecto_dir)
    problemas_seguridad = [h for h in hallazgos_sec if "Sin hallazgos" not in h[1]]

    # 3. Veredicto
    # Si tests pasan y cobertura >= 80% y no hay secretos expuestos
    tiene_secretos = any("🔑" in h[0] and "Sin hallazgos" not in h[1] for h in hallazgos_sec)
    
    if tests_pasaron and not tiene_secretos:
        if problemas_seguridad:
            veredicto = "APROBADO CON OBSERVACIONES"
            clase_veredicto = "warning"
        else:
            veredicto = "APROBADO"
            clase_veredicto = "success"
    else:
        veredicto = "REQUIERE CORRECCIÓN"
        clase_veredicto = "danger"

    # 4. Generar HTML
    filas_sec = "".join(f"<tr><td>{h[0]}</td><td>{h[1]}</td></tr>" for h in hallazgos_sec)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Reporte de Calidad QA</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; background: #f8fafc; color: #1e293b; }}
        .card {{ background: white; border-radius: 8px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); padding: 24px; margin-bottom: 24px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 16px; margin-bottom: 20px; }}
        .badge {{ padding: 6px 14px; border-radius: 9999px; font-weight: 700; font-size: 0.95rem; text-transform: uppercase; }}
        .badge.success {{ background: #dcfce7; color: #15803d; }}
        .badge.warning {{ background: #fef9c3; color: #854d0e; }}
        .badge.danger {{ background: #fee2e2; color: #b91c1c; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
        th {{ background: #f1f5f9; font-weight: 600; }}
        pre {{ background: #0f172a; color: #f8fafc; padding: 16px; border-radius: 6px; overflow-x: auto; font-size: 0.85rem; }}
        .metric {{ font-size: 2rem; font-weight: bold; color: #0f172a; }}
        .metric-label {{ font-size: 0.875rem; color: #64748b; }}
        .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <div>
                <h1 style="margin: 0; font-size: 1.5rem;">Reporte Consolidado de Calidad QA</h1>
                <p style="margin: 4px 0 0; color: #64748b;">Proyecto: Conversor de Temperatura (Spec Kit)</p>
            </div>
            <div>
                <span class="badge {clase_veredicto}">{veredicto}</span>
            </div>
        </div>

        <div class="grid">
            <div style="background: #f8fafc; padding: 16px; border-radius: 6px; text-align: center;">
                <div class="metric">{tests_count}</div>
                <div class="metric-label">Tests Pasados</div>
            </div>
            <div style="background: #f8fafc; padding: 16px; border-radius: 6px; text-align: center;">
                <div class="metric">{cobertura_pct}%</div>
                <div class="metric-label">Cobertura de Código</div>
            </div>
            <div style="background: #f8fafc; padding: 16px; border-radius: 6px; text-align: center;">
                <div class="metric">{len(problemas_seguridad)}</div>
                <div class="metric-label">Hallazgos de Seguridad</div>
            </div>
        </div>
    </div>

    <div class="card">
        <h2>Revisión de Seguridad Básica</h2>
        <table>
            <thead>
                <tr><th>Categoría</th><th>Estado / Hallazgo</th></tr>
            </thead>
            <tbody>
                {filas_sec}
            </tbody>
        </table>
    </div>

    <div class="card">
        <h2>Salida de Cobertura y Pruebas</h2>
        <p><strong>Líneas no cubiertas:</strong> {missing_lines}</p>
        <pre><code>{out}</code></pre>
    </div>
</body>
</html>
"""

    reporte_path = proyecto_dir / "reporte-qa.html"
    reporte_path.write_text(html, encoding="utf-8")
    
    print(f"Reporte generado exitosamente en: {reporte_path}")
    print(f"Veredicto: {veredicto}")
    if problemas_seguridad:
        print("Problemas/Observaciones destacadas:")
        for cat, obs in problemas_seguridad:
            print(f"- {cat}: {obs}")


if __name__ == "__main__":
    main()
