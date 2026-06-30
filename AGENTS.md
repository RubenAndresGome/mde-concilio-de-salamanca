# AGENTS.md — MDE Politeia Conciliar de Salamanca

> Instrucciones para agentes de IA (GitHub Copilot, Claude Code, Codex, OpenCode, etc.)

## Estructura del Proyecto

```
concilio-salamanca/           # Repo GitHub (kebab-case)
├── concilio_salamanca/       # Paquete Python (snake_case)
│   ├── main.py               # CLI entry point
│   ├── cli.py                # Argument parser
│   ├── license_generator.py  # RNS v5.0 (17 artículos)
│   ├── agents/               # 39 agentes IA
│   ├── debate/               # Orquestador, proveedores, lógica
│   ├── prompts/              # System prompts (36+)
│   └── tests/                # 75 tests
├── FRN_ROADMAP.md            # Manifiesto Fundación Rerum Novarum
├── .mde_history/             # Historial PDCA (5S)
└── LICENSE.md                # Statuto RNS v5.0
```

## Convenciones

- **Nombres**: kebab-case para archivos, snake_case para Python, PascalCase para agentes
- **Licencia**: RNS v5.0 (commons compensado, no MIT)
- **Tests**: `pytest concilio_salamanca/tests/` — 75 tests, deben pasar
- **CLI**: `concilio --file app.js --agents escolasticos`
- **Historial**: `.mde_history/` con estructura 5S y archivos PDCA

## Agentes disponibles (39)

```bash
concilio --list-agents
```

Grupos: `escolasticos`, `pragmaticos`, `clean_code`, `logici`, `red_team`, `delineatio`, `token_optimizers`, `todos`

## Ejecutar el Concilio

```bash
pip install concilio-salamanca
concilio --file app.js --agents escolasticos
concilio --file app.js --mode ejecutivo --agents pragmaticos
concilio license --country MX --dev "Nombre" --project "Proyecto"
```

## Antes de modificar código

1. `pytest concilio_salamanca/tests/` — asegurar 75/75
2. Si añades un agente: `prompts/system_prompts.py` + `agents/__init__.py` + `prompts/__init__.py`
3. Si modificas la licencia: regenerar `LICENSE.md`: `concilio license --country MX --dev X --project Y --std`
4. Documentar en `.mde_history/2_seiton_order/PDCA_NNN.md`

## Archivos clave para entender el proyecto

| Archivo | Propósito |
|---|---|
| `concilio_salamanca/SKILL.md` | Definición de la skill para OpenCode |
| `concilio_salamanca/README.md` | Documentación del proyecto |
| `FRN_ROADMAP.md` | Manifiesto Fundación Rerum Novarum |
| `concilio_salamanca/debate/orchestrator.py` | Orquestador del debate |
| `concilio_salamanca/debate/providers.py` | Proveedores LLM + ModelRanker |
| `concilio_salamanca/prompts/system_prompts.py` | Todos los prompts (884+ líneas) |
| `concilio_salamanca/license_generator.py` | Generador de licencia RNS v5.0 |
| `concilio_salamanca/reference/mde_arquitectura_supervisor.md` | Manifiesto fundacional: arquitectura neurosimbólica, 4 Causas, Zonificación Crítica |
