---
name: concilio-salamanca
description: >
  Auditar y revisar código con un colegio electoral de agentes, Dogma objetivo,
  voto contextual, PnC, memoria SQLite y presupuestos estrictos. Usar para code
  review, seguridad, debugging, testing, arquitectura, optimización de contexto,
  contradicciones entre órdenes, selección económica de modelos y auditorías CI/MCP.
---

# Concilio de Salamanca

Aplicar este orden:

1. Constituir el Dogma con `propose_dogma` si hay varias órdenes. Si hay contradicción, mostrar las órdenes incompatibles y detenerse hasta que el usuario elija; no inventar precedencia.
2. Elegir el nivel mínimo que pueda preservar hallazgos críticos: `0` estático, `1` económico, `2` normal, `3` pleno. En CI/MCP usar `1`; `--fast` equivale a `1`.
3. Tamizar el contexto y activar sólo los módulos necesarios.
4. Ejecutar `run_audit` o el CLI. No elegir modelos frontera sin una aprobación individual y explícita.
5. Entregar veredicto, evidencia, voto, preguntas bloqueantes, consumo, caché y causa de parada. No mostrar el protocolo cavernícola interno.

## Comandos

```bash
# Cero llamadas LLM
concilio --file <archivo> --audit-level 0

# Dos agentes, dos llamadas como máximo
concilio --file <archivo> --audit-level 1 --compute-policy auto --priority cost

# Auditoría normal con presupuesto total
concilio --file <archivo> --audit-level 2 --token-budget 6000

# Cloud económico explícito (DeepSeek V4 Flash)
concilio --file <archivo> --compute-policy cloud --priority cost

# Modelo/proveedor explícitos conservan compatibilidad
concilio --file <archivo> --provider ollama --model qwen2.5-coder:7b
```

## Router de módulos

Leer sólo la referencia activada:

- Código o repositorio grande: [context-sieve.md](reference/context-sieve.md).
- Debate entre agentes o serialización compacta: [cave-protocol.md](reference/cave-protocol.md).
- Silogismos, conjuntos, empate o PnC: [syllogism-boolean.md](reference/syllogism-boolean.md).
- Cambio de código que requiere pruebas: [test-impact.md](reference/test-impact.md).
- Bug, excepción o traza: [debug-evidence.md](reference/debug-evidence.md).
- Diff con autenticación, red, secretos, SQL, procesos o archivos: [security-diff.md](reference/security-diff.md).
- Arquitectura, dependencias o precedentes: [architecture-graph.md](reference/architecture-graph.md).
- Presupuesto, caché, costo o escalamiento: [token-accountant.md](reference/token-accountant.md).
- Gobierno del Dogma y voto contextual: [gobernanza_cognitiva.md](reference/gobernanza_cognitiva.md).

## Contratos

- Un agente conserva un voto: el último válido. Ponderar competencia contextual, forma silogística y PnC.
- Detener rondas al llegar a 67% y no existir contradicción bloqueante.
- Limitar preguntas por categoría: dos en nivel 1, tres en niveles 2–3.
- Mantener prefijo estable hasta el código; colocar rol y pregunta específica después.
- En ausencia de `DEEPSEEK_API_KEY`, probar DeepSeek/Qwen Coder en Ollama y luego nivel 0 con `RESERVA`.
- En MCP/CI devolver `requires_user_decision` para frontera; no gastar antes de recibir `decision_id`, candidato y aprobación.
