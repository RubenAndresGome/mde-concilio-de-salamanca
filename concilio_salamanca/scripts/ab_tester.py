"""
Script para realizar pruebas A/B de la eficacia del formato silogístico.
Evalúa el rendimiento de los agentes con formato estricto vs prompt libre.
"""

import json
import time
from pathlib import Path
from concilio_salamanca.debate.orchestrator import DebateOrchestrator, DebateConfig
from concilio_salamanca.debate.providers import create_model

# Configuracion de la prueba A/B
DATASET_DIR = Path(__file__).parent.parent.parent / "dataset_ab_test"
RESULT_DIR = Path(__file__).parent.parent.parent / "results_ab_test"


def run_ab_test():
    if not DATASET_DIR.exists():
        print(
            f"No se encontró el dataset en {DATASET_DIR}. Por favor, crea este directorio con 100 archivos de muestra."
        )
        return

    RESULT_DIR.mkdir(exist_ok=True)

    files = list(DATASET_DIR.glob("*.*"))[:100]
    print(f"Iniciando prueba A/B en {len(files)} archivos...")

    results = []

    model_name = "gpt-4o-mini"
    provider = "openai"

    for i, file_path in enumerate(files):
        print(f"Procesando [{i + 1}/{len(files)}]: {file_path.name}")

        try:
            code = file_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error leyendo {file_path}: {e}")
            continue

        # Variante A: Formato Silogístico Estricto (Por defecto)
        config_a = DebateConfig(
            max_rounds=1, include_pnc_validation=True, parallel=True
        )
        model_a = create_model(provider, model_name)
        orchestrator_a = DebateOrchestrator(model_a, config_a)

        start_a = time.time()
        res_a = orchestrator_a.run_debate(code)
        end_a = time.time()

        # Variante B: Prompt Libre (Modificamos temporalmente el schema del AgenteBase)
        # Nota: en una implementación real, se inyectaría un "FreePromptAgent" en vez de parchear
        config_b = DebateConfig(
            max_rounds=1, include_pnc_validation=False, parallel=True
        )
        model_b = create_model(provider, model_name)
        orchestrator_b = DebateOrchestrator(model_b, config_b)

        # Hack para Variante B: remover instrucción JSON
        for agent in orchestrator_b._agent_instances.values():
            agent.json_schema_instruction = "Responde libremente con tus observaciones técnicas. No uses formato silogístico."

        start_b = time.time()
        res_b = orchestrator_b.run_debate(code)
        end_b = time.time()

        # Almacenar métricas
        results.append(
            {
                "file": file_path.name,
                "silogistico": {
                    "time_sec": end_a - start_a,
                    "contradictions": len(res_a.get("pnc_validation").contradicciones)
                    if res_a.get("pnc_validation")
                    else 0,
                    "veredicto": res_a["determinatio"].veredicto_final.value
                    if res_a.get("determinatio")
                    else "ERROR",
                },
                "libre": {
                    "time_sec": end_b - start_b,
                    "veredicto": res_b["determinatio"].veredicto_final.value
                    if res_b.get("determinatio")
                    else "ERROR",
                },
            }
        )

        # Guardar resultados incrementales
        with open(RESULT_DIR / "ab_test_metrics.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

    print(f"Prueba A/B finalizada. Resultados guardados en {RESULT_DIR}")


if __name__ == "__main__":
    run_ab_test()
