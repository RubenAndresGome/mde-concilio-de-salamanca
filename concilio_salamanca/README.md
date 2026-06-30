# MDE Politeia Conciliar de Salamanca — Auditoria de Codigo por Meta Dialectica Escolastica

> *"Ninguna linea de codigo sera desplegada sin haber sido sometida al tribunal de la razon."*

Sistema multi-agente de auditoria de codigo basado en logica aristotelico-tomista. **39 agentes IA** especializados debaten usando silogismos formales, logica de predicados y teoria de conjuntos. Multi-proveedor LLM con ranking automatico calidad-precio-disponibilidad vía ModelRanker.

[![CI](https://github.com/anomalyco/opencode/actions/workflows/ci.yml/badge.svg)](https://github.com/anomalyco/opencode/actions)
[![Python 3.11+](https://img.shields.io/pypi/pyversions/concilio-salamanca)](https://pypi.org/project/concilio-salamanca/)
[![License: RNS 5.0](https://img.shields.io/badge/License-Rerum_Novarum_5.0-purple.svg)](LICENSE)

---

## Instalacion

```bash
pip install concilio-salamanca

# Con proveedores adicionales:
pip install concilio-salamanca[all]
pip install concilio-salamanca[anthropic,groq,ollama]
```

## Plataformas soportadas

| Plataforma | Metodo |
|---|---|
| **CLI** | `concilio --file app.js` (o `py -m concilio_salamanca.main`) |
| **PyPI** | `pip install concilio-salamanca` |
| **opencode** | Skill auto-detectada al pedir "auditar", "revisar codigo", "code review" |
| **Open-Design** | `od mcp install opencode` — prototipos visuales |
| **CBMM** | `codebase-memory-mcp install` — grafo de conocimiento |
| **Spec-Kit** | `specify init` — flujo SDD integrado |
| **OpenRouter** | `OPENROUTER_API_KEY` — 339+ modelos |
| **CI/CD** | `--output json` para pipelines |

## Proveedores LLM

| Proveedor | Variable de entorno | Modelo default | Costo |
|---|---|---|---|
| Ollama (local) | — | `deepseek-r1:8b` | **Gratis** |
| Meta Llama | via OpenRouter | `llama-3.3-70b` | $0.10/MTok |
| DeepSeek | `DEEPSEEK_API_KEY` | `deepseek-chat` | $0.09/MTok |
| Qwen (Alibaba) | via OpenRouter | `qwen3-32b` | $0.08/MTok |
| MiniMax | via OpenRouter | `minimax-m2.5` | $0.12/MTok |
| GLM (Z.ai) | via OpenRouter | `glm-4.7-flash` | $0.06/MTok |
| OpenAI | `OPENAI_API_KEY` | `gpt-4o` | $2.50/MTok |
| Anthropic | `ANTHROPIC_API_KEY` | `claude-sonnet-4` | $3.00/MTok |
| **OpenRouter** | `OPENROUTER_API_KEY` | `deepseek/deepseek-v4-flash` | **339+ modelos** |
| Groq | `GROQ_API_KEY` | `llama-3.3-70b` | Gratis (limitado) |

El **ModelRanker** selecciona automaticamente el mejor modelo calidad-precio-disponibilidad. Usa `--list-model-prices` para ver la tabla completa.

### Enrutamiento Cognitivo

```bash
concilio --file app.js \
  --provider-obreros deepseek --model-obreros deepseek-chat \
  --provider-magister openai --model-magister gpt-4o
```

---

## Uso rapido

### Auditoria basica (escolastica)

```bash
concilio --file app.js --agents escolasticos
```

### Auditoria ejecutiva (informe reducido)

```bash
concilio --file app.tsx --mode ejecutivo --agents pragmaticos
```

### Auditoria de seguridad

```bash
concilio --file server.js --agents seguridad,promotor --rounds 3
```

### Auditoria Clean Code (SOLID)

```bash
concilio --file app.py --agents clean_code
```

### Auditoria de coherencia ontologica (OckhamDev + CBMM)

```bash
concilio --file app.py --agents logici --ockham
```

### Escaneo rapido de anti-patrones (sin LLM, gratuito)

```bash
concilio audit --file app.js --domain seguridad
```

---

## Agentes del Concilio (39)

### Escolasticos (tribunal clasico)

| Clave | Agente | Especialidad |
|---|---|---|
| `promotor` | Promotor Fidei | Acusador: busca vulnerabilidades, fallos, privaciones del ser |
| `defensor` | Defensor Causae Finalis | Defiende el codigo por su causa final y estructura formal |
| `doctor` | Doctor Materiae | Analiza datos, tipos, estructuras, flujo de informacion |
| `larouche` | Arquitecto LaRouche | Economia fisica: eficiencia termodinamica, complejidad |
| `leon_xiii` | Defensor Leonis XIII | Justicia conmutativa, anti-usura tecnica, licencias |

### Pragmaticos (ingenieria pura)

| Clave | Agente | Filosofia |
|---|---|---|
| `linus` | Linus Torvalds | "Good taste", zero BS, que funcione |
| `wozniak` | Steve Wozniak | Minimalismo HW/SW, hacer mas con menos |
| `thompson` | Ken Thompson | Unix: do one thing well, "worse is better" |

### Eticos + Algoritmicos

| Clave | Agente | Filosofia |
|---|---|---|
| `stallman` | Richard Stallman | 4 libertades, anti-tivoizacion, copyleft |
| `stroustrup` | Bjarne Stroustrup | Zero-overhead abstraction, type safety, RAII |
| `korotkevich` | Gennady Korotkevich | Optimalidad algoritmica, edge cases, complejidad |

### Tecnicos especializados

| Clave | Agente | Especialidad |
|---|---|---|
| `auditor_dl` | Auditor Profundi | Deep Learning: tensores, GPU, arquitectura |
| `seguridad` | Custos Securitatis | Red-team: prompt injection, adversarial, sandbox |
| `mlops` | Architectus Pipeline | CI/CD, versionado, drift, observabilidad |
| `datos` | Purgator Datorum | Schemas, outliers, encoding, calidad de datos |
| `sistemas` | Architectus Systematis | Escalabilidad, CAP, backpressure, idempotencia |
| `iot` | Architectus Siliconis | Firmware, RTOS, BLE/LoRa, power profiling |

### Dialecticos, Metodologia y Logica

| Clave | Agente | Enfoque |
|---|---|---|
| `socrates` | Socrates | Mayeutica: interrogacion destructiva de supuestos |
| `scrum` | Scrum Master | DoD, velocidad, retrospectivas, empirismo agil |
| `sixsigma` | Six Sigma | DMAIC, Poka-Yoke, control de calidad |
| `llull` | Ramon Llull | Grafos logicos, logica combinatoria (*Ars Magna*) |
| `bacon` | Roger Bacon | Empirismo radical, validacion experimental |
| `vitoria` | Francisco de Vitoria | Ius Gentium, derechos del usuario, WCAG |
| `ratio` | Ratio Studiorum | Pedagogia del codigo, legibilidad |
| **`ockham`** | **OckhamDev** | **Navaja de la No-Contradiccion: operaciones de conjunto, silogismos, PNC** |

### Clean Code, Diseno y Proceso

| Clave | Agente | Enfoque |
|---|---|---|
| `arquimedes` | Arquimedes (Magister Artis) | SOLID, Clean Code, Boy Scout Rule |
| `custos_impacti` | Custos Impacti | Analisis de impacto, refactorizacion segura |
| `magister_processus` | Magister Processus Integri | PDCA + SDD (Spec-Diven), mediciones |
| `magister_delineationis` | Magister Delineationis | Arquitecto Visual: prototipos Open-Design, DESIGN.md |

### Meta-Agentes (Token Optimizers)

| Clave | Agente | Rol |
|---|---|---|
| `ponytail` | Ponytail/YAGNI | Escalera de la Pereza, evitar codigo innecesario |
| `graphify` | Graphify | Deteccion de acoplamientos, god nodes |
| `rtk` | RTK | Filtrado de ruido contextual en refutaciones |
| `telemetry` | Telemetry | Medicion de consumo de tokens y llamadas a API |

### Seguridad Ofensiva + Filosofia Aplicada

| Clave | Agente | Rol |
|---|---|---|
| `redteam` | Red Team Coordinator | Planificador de cadenas de ataque |
| `pentest` | PenTest+ Auditor | Metodologias PTES, CompTIA |
| `abuser` | Abuser Story Generator | Historias de abuso desde perspectiva del atacante |
| `causas` | Analista Causal Aristotelico | 4 causas de cada vulnerabilidad |
| `leibniz` | Optimista Leibniziano | Principio de razon suficiente |
| `nietzsche` | Vitalista Nietzscheano | Anti-dogma, transvaloracion tecnica |

### Grupos predefinidos

```bash
--agents escolasticos    # El tribunal clasico (5)
--agents pragmaticos     # Ingenieria pura (3)
--agents tecnicos        # Especialistas (6)
--agents clean_code      # SOLID + Impacto + Proceso (3)
--agents logici          # Ockham + Socrates + Bacon + Leibniz (4)
--agents delineatio      # Diseno Visual + Derechos + Pedagogia (3)
--agents red_team        # Seguridad ofensiva (4)
--agents ia_produccion   # Auditoria de produccion IA (6)
--agents seguridad_completa  # Seguridad completa (6)
--agents embebidos       # IoT/Embebidos (4)
--agents token_optimizers    # Optimizacion de tokens (4)
--agents todos           # Los 39 agentes
```

---

## Comandos

| Comando | Descripcion |
|---|---|
| `--file`, `-f` | Archivo a auditar |
| `--code`, `-c` | Codigo directo como string |
| `--agents`, `-a` | Agentes (claves o grupo) |
| `--provider` | Proveedor LLM (openai, deepseek, anthropic, groq, ollama, openrouter) |
| `--model`, `-m` | Modelo especifico |
| `--provider-magister` | Proveedor para el Juez (ej. `openai`) |
| `--model-magister` | Modelo para el Juez (ej. `gpt-4o`) |
| `--provider-obreros` | Proveedor para los debatientes (ej. `deepseek`) |
| `--model-obreros` | Modelo para los debatientes (ej. `deepseek-chat`) |
| `--rounds`, `-r` | Rondas de debate (default: 2) |
| `--mode` | `escolastico`, `ejecutivo`, `sdd`, `pdca`, `auto` |
| `--output`, `-o` | `text`, `json`, `markdown`, `mermaid` |
| `--verbose`, `-v` | Reporte trinivel de silogismos |
| `--no-pnc` | Deshabilitar validacion PnC |
| `--ockham` | Activar OckhamDev + CBMM (logica de conjuntos) |
| `--no-ockham` | Desactivar OckhamDev |
| `--list-model-prices` | Tabla de precios de modelos |
| `--check-tools` | Detectar herramientas externas |
| `--config` | Archivo de configuracion YAML |

### Subcomandos

```bash
# Auditoria de anti-patrones (sin LLM)
concilio audit --file app.js --domain seguridad

# Licencia Rerum Novarum Statuto v4.1
concilio license --country MX --dev "Nombre" --project "Proyecto" --repo github.com/...
concilio license --country MX --dev "Nombre" --project "Proyecto" --jubilee 2024 --std
concilio license --register --name "Proyecto" --repo "https://github.com/..."
concilio license --bula --dev "Empresa" --project "Proyecto" --revenue 5000000
concilio license --pay --dev "Empresa" --project "Proyecto" --amount 2500

# Precio justo (Big Mac Index)
concilio bme --income 3000 --residence MX --income-country US

# Listados
concilio --list-agents
concilio --list-providers
concilio --list-anti-patrones
concilio --list-model-prices
concilio --check-tools
```

---

## Licencia Rerum Novarum Statuto v4.1

El proyecto se distribuye bajo el **Rerum Novarum Statuto** (RNS v4.1), una licencia de commons compensado con 17 articulos basada en el Decalogo, la Doctrina Social de la Iglesia y la Escuela de Salamanca.

**Articulos esenciales (17):**
1. Definiciones — Margen Bruto Operativo, prorrateo por importancia, kWE
2. Open Source gratuito para individuos y PYMEs
3. Salario, no limosna — 3 opciones de contratacion
4. Diezmo Tecnologico (1%-10%) sobre Margen Bruto Operativo + tabla plana corporativa
5. Auditoria CI + sistema de recompensas (30% de la multa al delator)
6. Anti-Parasitaria — pro-trabajo humano (Exodo 20:15)
7. Retroactividad Modelo WinRAR — negociacion asistida
8. Excomunion Digital
9. Compatibilidad — RNS no busca OSI approval
10. No-Remuneracion = No-Soporte
11. Jubileo del Codigo cada 7 anos
12. Liberacion por Abandono si soporte cae <50%
13. Gobernanza STD por consenso del 60%
14. Bulas — 1 por proyecto, precio = % ingresos de division, 7 anos
15. Fundacion RNS — sede en Sur Global, hermana FSF, voto por meritos, SCRUM
16. Mediacion → Arbitraje → Tribunales (3 pasos)
17. Disposiciones Finales — articulos irrenunciables

```bash
concilio license --help
```

---

## Compresor Trinivel de Silogismos

Cada silogismo emitido por los agentes se reduce a tres paradigmas formales:

| Nivel | Paradigma | Ejemplo |
|---|---|---|
| 1. Escolastico | Mnemotecnia A/E/I/O | `AAA-1` = Barbara |
| 2. Conjuntos | Algebra de Boole | `S ⊂ P`, `s(1-p)=0` |
| 3. Predicados | Logica de primer orden | `∀x. S(x) → P(x)` |

---

## Estructura del proyecto

```
concilio_salamanca/
├── __init__.py                 # Package init (v1.0.0)
├── SKILL.md                    # Skill definition for opencode
├── README.md                   # Project documentation
├── config.yaml                 # Configuration (provider, model, rounds, weights, budget)
├── main.py                     # CLI entry point
├── cli.py                      # Argument parser
├── license_generator.py        # RNS v4.1 generator (BME, Bulas, Registry)
├── schemas.py                  # Pydantic models + DebateState
│
├── agents/                     # Dynamic agent registry (39 agents)
│   ├── __init__.py             # AGENT_DEFS, AGENT_GROUPS, resolve_agents()
│   ├── base.py                 # AgentFromPrompt, cache integration
│   └── magister_determinans.py # Magister judge + parse_determinatio()
│
├── debate/                     # Orchestration, providers, logic
│   ├── orchestrator.py         # DebateOrchestrator (sync + async, CBMM, Ockham)
│   ├── providers.py            # Multi-provider factory + ModelRanker
│   ├── ockham_engine.py        # OckhamDev: set operations, PNC, silogisms
│   ├── model_pricing.py        # 22 model catalog + price table
│   ├── rns_registry.py         # RNS Registry (projects, Bulas, payments)
│   ├── send_graph.py           # LangGraph parallel debate
│   ├── validator_pnc.py        # PnC formal validation
│   ├── formal_verification.py  # Z3 SMT solver integration
│   ├── street_solver           # Syllogism cache (trinivel compression)
│   ├── static_analysis.py      # Tree-sitter AST + regex fallback
│   ├── checks.py               # Socratic/Murphy checks
│   ├── git_history.py          # Git log + .mde_history reader
│   ├── mcp_design_client.py    # Open-Design MCP client
│   ├── tool_detection.py       # External tool detection (CBMM, Spec-Kit, OD)
│   ├── formatters.py, voting.py, precedents.py
│   ├── loop_invariants.py, mcp_client.py
│   └── syllogism_cache.json   # Runtime cache
│
├── prompts/                    # 36+ system prompts
│   ├── system_prompts.py       # All agent prompts (OCKHAMDEV, MAGISTER_DELINEATIONIS, ...)
│   └── __init__.py             # Re-exports
│
├── reference/                  # Reference materials
│   ├── anti_patrones.py        # 15 anti-patterns catalog
│   ├── componentes.py          # Component reference specs
│   ├── determinatio_template.py # Output templates
│   ├── genesis_iberoamerica_extract.md  # Universal concepts
│   └── arquitectura_maestria_software.md # Clean Code treatise
│
├── templates/
│   └── DESIGN.md               # Brand contract for Magister Delineationis
│
├── dashboard/app.py            # Streamlit web dashboard
├── scripts/                    # Utility scripts
├── tests/                      # 75 tests (unit + integration)
└── docs/historial_markdowns/   # Archived documentation
```

---

## Tests

```bash
py -m pytest concilio_salamanca/tests/ -v
# 75 passed
```
