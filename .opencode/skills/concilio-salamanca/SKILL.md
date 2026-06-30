---
name: concilio-salamanca
description: >
  Auditoria de codigo por silogismos ontologicos. Usa esta skill cuando necesites
  auditar, revisar, analizar o juzgar codigo fuente para detectar vulnerabilidades,
  anti-patrones, ineficiencias o fallos de diseno. El Concilio de Salamanca convoca
  un tribunal de 39 agentes IA especializados que debaten usando logica aristotelico-tomista
  y emiten un veredicto estructurado (Quaestio, Videtur, Sed Contra, Respondeo,
  Determinatio Codici). Soporta OpenAI, DeepSeek, Anthropic, Groq, Ollama, OpenRouter,
  Codebase Memory MCP y Open-Design.
  Activar con: auditar, revisar, analizar codigo, code review, encontrar bugs,
  revisar seguridad, optimizar codigo, anti-patrones, buenas practicas.
---

# MDE Politeia Conciliar de Salamanca — Auditoria de Codigo por Meta Dialectica Escolastica

> *"Ninguna linea de codigo sera desplegada sin haber sido sometida al tribunal de la razon."*

> **v5.0** — 39 agentes · Grafo de Conocimiento (CBMM) · Logica de Conjuntos · OckhamDev · RNS v5.0 · `pip install concilio-salamanca`

## Cuando usar esta skill

Activa esta skill cuando el usuario pida:
- Revisar o auditar codigo
- Encontrar vulnerabilidades o bugs
- Evaluar calidad de codigo
- Optimizar rendimiento
- Revisar seguridad
- Validar buenas practicas
- Analizar arquitectura de software
- **Nuevo**: Analisis de coherencia ontologica (OckhamDev: entes definidos vs invocados)
- **Nuevo**: Generar licencia Rerum Novarum Statuto con Bula y Jubileo

## Como usar el sistema

El Concilio expone un CLI completo. NO es necesario escribir Python.

### Comandos principales

```bash
# Auditoria basica (escolastica)
py concilio_salamanca/main.py --file <archivo> --agents escolasticos

# Auditoria con OckhamDev (logica de conjuntos vía CBMM)
py concilio_salamanca/main.py --file <archivo> --agents logici --ockham

# Auditoria ejecutiva (informe tecnico reducido)
py concilio_salamanca/main.py --file <archivo> --mode ejecutivo --agents pragmaticos

# Auditoria de seguridad
py concilio_salamanca/main.py --file <archivo> --agents seguridad,promotor --rounds 2

# Auditoria Clean Code (SOLID)
py concilio_salamanca/main.py --file <archivo> --agents clean_code

# Auditoria con Enrutamiento Cognitivo (Obreros baratos + Magister Deluxe)
py concilio_salamanca/main.py --file <archivo> --provider-obreros deepseek --model-obreros deepseek-chat --provider-magister openai --model-magister gpt-4o

# Auditoria con OpenRouter (339+ modelos, auto-seleccion calidad-precio)
py concilio_salamanca/main.py --file <archivo> --provider openrouter --agents escolasticos
```

### Comandos auxiliares

```bash
# Escaneo rapido de anti-patrones (sin LLM)
py concilio_salamanca/main.py audit --file <archivo>

# Listar agentes disponibles
py concilio_salamanca/main.py --list-agents

# Listar proveedores LLM
py concilio_salamanca/main.py --list-providers

# Listar precios de modelos (tabla calidad-precio)
py concilio_salamanca/main.py --list-model-prices

# Verificar herramientas externas (CBMM, Spec-Kit, Open-Design)
py concilio_salamanca/main.py --check-tools

# Generar licencia Rerum Novarum Statuto (RNS)
py concilio_salamanca/main.py license --country MX --dev "Nombre" --project "Proyecto" --repo "github.com/..." --jubilee 2024 --std

# Registrar proyecto en RNS Registry + emitir Bula
py concilio_salamanca/main.py license --register --project "Proyecto" --repo "github.com/..."
py concilio_salamanca/main.py license --bula --dev "Empresa" --project "Proyecto" --revenue 5000000
py concilio_salamanca/main.py license --pay --dev "Empresa" --project "Proyecto" --amount 2500

# Calcular precio justo (Big Mac Index)
py concilio_salamanca/main.py bme --income 3000 --residence MX

# Modo SDD (Spec-Driven Development con Spec-Kit)
py concilio_salamanca/main.py --file <archivo> --mode sdd --agents proceso
```

## Agentes disponibles (39)

| Grupo | Agentes | Clave |
|---|---|---|
| Escolasticos | Promotor, Defensor, Doctor, LaRouche, Leon XIII | `escolasticos` |
| Pragmaticos | Linus Torvalds, Steve Wozniak, Ken Thompson | `pragmaticos` |
| Tecnicos | DL, Seguridad, MLOps, Datos, Sistemas, IoT | `tecnicos` |
| Eticos | Stallman, Stroustrup | `eticos` |
| Algoritmicos | Korotkevich | `algoritmicos` |
| Dialecticos | Socrates, Scrum Master, Six Sigma, Llull, Bacon, Vitoria, Ratio | `dialecticos`, `metodologia`, `empiristas`, `ius_gentium` |
| Token Optimizadores | Ponytail, Graphify, RTK, Telemetry | `token_optimizers` |
| Embebidos | IoT, Wozniak, Thompson, Sistemas | `embebidos` |
| **Clean Code** | **Arquimedes, Custos Impacti, Magister Processus** | **`clean_code`** |
| **Proceso (SDD+PDCA)** | **Scrum Master, Six Sigma, Magister Processus** | **`proceso`** |
| **Logica (Conjuntos)** | **OckhamDev, Socrates, Bacon, Leibniz** | **`logici`** |
| **Diseno Visual** | **Magister Delineationis, Vitoria, Ratio** | **`delineatio`** |
| Seguridad Ofensiva | Red Team, Pentest, Abuser, Seguridad | `red_team` |
| Filosofos Aplicados | Leibniz, Nietzsche, Socrates, Causas | `filosofos_aplicados` |
| Todos | **Los 39** | `todos` |

## Configuracion Multi-Modelo (ModelRanker)

Ahora puedes definir **pesos** por proveedor en `config.yaml`. El ModelRanker selecciona automaticamente el mejor modelo calidad-precio-disponibilidad.

```yaml
model_weights:
  ollama: 10       # Siempre prioritario si disponible (local, gratis)
  meta-llama: 2
  deepseek: 1
  qwen: 1
  minimax: 1
  openai: 0
  anthropic: 0     # Claude = techo, solo si se necesita

roles:
  ejecutor: "auto"           # ModelRanker decide (rango 1-3)
  director_strategy: "auto"  # ModelRanker decide (rango 4-6)

budget:
  max_per_debate_usd: 0.50   # Limite opcional
  warn_at_usd: 0.10
```

El sistema detecta modelos locales de Ollama automaticamente y los prioriza. Usa `--list-model-prices` para ver la tabla completa.

## Proveedores LLM soportados

| Proveedor | Flag | Variable de entorno | Modelo default |
|---|---|---|---|
| Ollama (local) | `--provider ollama` | (ninguna) | `deepseek-r1:8b` |
| OpenRouter (339+) | `--provider openrouter` | `OPENROUTER_API_KEY` | `deepseek/deepseek-v4-flash` |
| DeepSeek | `--provider deepseek` | `DEEPSEEK_API_KEY` | `deepseek-chat` |
| OpenAI | `--provider openai` | `OPENAI_API_KEY` | `gpt-4o` |
| Anthropic | `--provider anthropic` | `ANTHROPIC_API_KEY` | `claude-sonnet-4` |
| Groq | `--provider groq` | `GROQ_API_KEY` | `llama-3.3-70b` |

## Herramientas integradas

| Herramienta | Instalacion | Uso |
|---|---|---|
| **Codebase Memory MCP** | Auto-instalacion via `--check-tools` | Grafo de conocimiento del codebase (OckhamDev) |
| **Spec-Kit** | Auto-instalacion via `uv tool install` | Flujo SDD (--mode sdd) |
| **Open-Design** | `od mcp install opencode` | Prototipos visuales (Magister Delineationis) |
| **MarkItDown** | `pip install markitdown[pdf]` | Extraccion de contenido para licencia RNS |

## Licencia Rerum Novarum Statuto v4.1

El Concilio incluye su propia licencia de commons compensado con 17 articulos:

- **Open Source para individuos, estudiantes y PYMEs**
- **Bulas**: propiedad privada temporal de 7 anos, maximo 1 por proyecto (anti-Disney)
- **Diezmo Tecnologico**: 1%-10% sobre Margen Bruto Operativo (tabla plana desde $0 a $50K/ano)
- **Jubileo del Codigo**: cada 7 anos se libera como STD
- **Fundacion RNS**: sede en Sur Global, hermana de FSF, votacion por meritos
- **No-Remuneracion = No-Soporte**: quien no paga no exige SLA
- **Decalogo y Doctrina Social Catolica** como fuentes doctrinales

```bash
concilio license --country MX --dev "Mi Nombre" --project "Mi App" --jubilee 2024 --std
concilio license --register --name "Proyecto" --repo "https://github.com/..."
```

## Formato de salida

1. **Escolastico** (default): Quaestio, Videtur, Sed Contra, Respondeo, Determinatio Codici
2. **Ejecutivo** (`--mode ejecutivo`): Informe tecnico con tabla de metricas
3. **JSON** (`--output json`): Estructurado para integracion con CI/CD
4. **Mermaid** (`--output mermaid`): Diagrama de grafo de debate

## Anti-patrones integrados

El sistema conoce 15 anti-patrones (AP-001 a AP-015) y los agentes los referencian automaticamente en sus silogismos.

## Referencias

- `reference/anti_patrones.py` — Catalogo de 15 anti-patrones
- `reference/componentes.py` — Componentes de referencia con checklist
- `reference/determinatio_template.py` — Plantillas de salida
- `reference/arquitectura_maestria_software.md` — Tratado de Clean Code, SOLID y 15 lenguajes
- `reference/genesis_iberoamerica_extract.md` — Conceptos universales de justicia distributiva
- `templates/DESIGN.md` — Brand contract para Magister Delineationis
- `scripts/validador_kpi.py` y `scripts/generador_paleta.py` — MDE Frontend

## Reglas de uso

1. Siempre ejecuta la auditoria desde la raiz del proyecto
2. Si el usuario no especifica agentes, usa `--agents escolasticos` por defecto
3. Si el usuario pide algo rapido, usa `--mode ejecutivo`
4. Si no hay API key, sugiere `--provider ollama` (local, gratis) o `--provider openrouter`
5. **Economia Fisica Cognitiva**: divide la carga con `--provider-obreros ollama --provider-magister openai`
6. Despues de la auditoria, resume los hallazgos principales en 3-4 lineas
7. Si el codigo es frontend (React/HTML/CSS), sugiere usar ademas la skill `mde-frontend`
8. Para analisis de coherencia ontologica, usa `--agents logici --ockham`
9. Para licencias de software, usa `concilio license --help`
