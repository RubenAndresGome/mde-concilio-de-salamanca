# Concilio de Salamanca — Auditoria de Codigo por Meta Dialectica Escolastica

> *"Ninguna linea de codigo sera desplegada sin haber sido sometida al tribunal de la razon."*

Sistema multi-agente de auditoria de codigo basado en logica aristotelico-tomista. **38 agentes IA** especializados debaten usando silogismos formales y emiten un veredicto estructurado bajo el Principio de No Contradiccion. Multi-proveedor LLM con ranking automatico calidad-precio-disponibilidad.

[![CI](https://github.com/anomalyco/opencode/actions/workflows/ci.yml/badge.svg)](https://github.com/anomalyco/opencode/actions)
[![PyPI version](https://img.shields.io/pypi/v/concilio-salamanca)](https://pypi.org/project/concilio-salamanca/)
[![Python 3.11+](https://img.shields.io/pypi/pyversions/concilio-salamanca)](https://pypi.org/project/concilio-salamanca/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Instalación

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

### Enrutamiento Cognitivo (Economía Física Cognitiva)
Para proyectos grandes, es financieramente insostenible correr agentes debatiendo en modelos Deluxe. 
El Concilio soporta la división del trabajo, asignando modelos locales/baratos para el debate (la Potencia) y modelos de alto razonamiento para el veredicto (el Acto):
```bash
python concilio_salamanca/main.py --file app.js \
  --provider-obreros deepseek --model-obreros deepseek-chat \
  --provider-magister openai --model-magister gpt-4o
```

---

## Instalacion

```bash
git clone <repo>
cd "MDE Skill Modulos"
pip install -r concilio_salamanca/requirements.txt
```

Configurar API key (elige un proveedor):

```powershell
# OpenAI
setx OPENAI_API_KEY "sk-..."

# DeepSeek
setx DEEPSEEK_API_KEY "sk-..."

# Ollama (local, sin key)
ollama pull llama3
```

---

## Uso rapido

### Auditoria basica

```bash
python concilio_salamanca/main.py --file app.js --agents escolasticos
```

### Auditoria ejecutiva (informe reducido)

```bash
python concilio_salamanca/main.py --file app.tsx --mode ejecutivo --agents pragmaticales
```

### Auditoria de seguridad

```bash
python concilio_salamanca/main.py --file server.js --agents seguridad,promotor --rounds 3
```

### Escaneo rapido de anti-patrones (sin LLM)

```bash
python concilio_salamanca/main.py audit --file app.js
```

### Con DeepSeek

```bash
python concilio_salamanca/main.py --file app.py --provider deepseek --model deepseek-chat --agents escolasticos
```

### Con Ollama local (gratis)

```bash
python concilio_salamanca/main.py --file app.py --provider ollama --model llama3 --agents pragmaticos
```

---

## Agentes del Concilio (28)

### Escolasticos (tribunal clasico)

| Clave | Agente | Especialidad / Rol |
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

### Dialécticos, Metodologías y Nuevos Agentes

| Clave | Agente | Enfoque / Filosofía |
|---|---|---|
| `socrates` | Socrates | Mayeútica, interrogación destructiva de supuestos |
| `scrum` | Scrum Master | DoD, velocidad de entrega, retrospectivas y empirismo ágil |
| `sixsigma` | Six Sigma | Control de calidad DMAIC, Poka-Yoke, reducción de varianza |
| `llull` | Ramon Llull | Grafos lógicos, lógica combinatoria (*Ars Magna*) |
| `bacon` | Roger Bacon | Empirismo radical, validación experimental |
| `vitoria` | Francisco de Vitoria | Ius Gentium, derechos del usuario, accesibilidad (WCAG) |
| `ratio` | Ratio Studiorum | Pedagogía del código, legibilidad y estructura limpia |

### Meta-Agentes (Optimizadores de Token)

| Clave | Agente | Rol Metodológico |
|---|---|---|
| `ponytail` | Ponytail/YAGNI | Escalera de la Pereza, evitar código innecesario |
| `graphify` | Graphify | Detección de acoplamientos, god nodes y dependencias |
| `rtk` | RTK | Filtrado de ruido contextual en refutaciones cruzadas |
| `telemetry` | Telemetry | Medición e informe del consumo de tokens y llamadas a la API |

### Grupos predefinidos

```bash
# Todos los escolasticos
--agents escolasticos

# Pragmaticos
--agents pragmaticos

# Tecnicos especializados
--agents tecnicos

# Auditoria de produccion IA
--agents ia_produccion

# Seguridad completa
--agents seguridad_completa

# Embebidos/IoT
--agents embebidos

# Todos (28 agentes)
--agents todos

# Combinacion personalizada
--agents promotor,seguridad,linus,korotkevich
```

---

## Comandos

| Comando | Descripcion |
|---|---|
| `--file`, `-f` | Archivo a auditar |
| `--code`, `-c` | Codigo directo como string |
| `--agents`, `-a` | Agentes (claves o grupo) |
| `--provider` | Proveedor LLM |
| `--model`, `-m` | Modelo especifico |
| `--provider-magister` | Proveedor para el Juez (ej. `openai`) |
| `--model-magister` | Modelo para el Juez (ej. `gpt-4o`) |
| `--provider-obreros` | Proveedor para los debatientes (ej. `ollama`) |
| `--model-obreros` | Modelo para los debatientes (ej. `llama3`) |
| `--rounds`, `-r` | Rondas de debate (default: 2) |
| `--mode` | `escolastico` (default) o `ejecutivo` |
| `--output`, `-o` | `text` (default), `json`, `markdown` |
| `--verbose`, `-v` | Reporte trinivel de silogismos |
| `--no-pnc` | Deshabilitar validacion PnC |

### Subcomandos

```bash
# Escaneo rapido de anti-patrones (sin LLM, gratuito)
python main.py audit --file app.js --domain seguridad

# Generar licencia Rerum Novarum
python main.py license --country MX --dev "Nombre" --project "Proyecto" --repo github.com/...

# Calcular precio justo (Big Mac Index)
python main.py bme --income 3000 --residence MX --income-country US

# Listar agentes
python main.py --list-agents

# Listar proveedores LLM
python main.py --list-providers

# Listar anti-patrones
python main.py --list-anti-patrones
```

---

## Formato de salida

### Escolastico (default)

```
QUAESTIO: Planteamiento formal del problema
VIDETUR: Argumentos que favorecen al codigo
SED CONTRA: Argumentos que condenan al codigo
RESPONDEO: Sintesis razonada del Magister
DETERMINATIO CODICI: Veredicto final y codigo corregido
```

### Ejecutivo (`--mode ejecutivo`)

Informe tecnico con tabla de metricas: veredicto, agentes participantes, rondas, contradicciones detectadas.

### JSON (`--output json`)

Para integracion con CI/CD, GitHub Actions, o sistemas automatizados.

---

## Anti-patrones

El sistema detecta automaticamente 15 anti-patrones (AP-001 a AP-015):

| ID | Anti-patron | Dominio |
|---|---|---|
| AP-001 | XSS por innerHTML sin sanitizar | Seguridad |
| AP-002 | SQL Injection por concatenacion | Seguridad |
| AP-003 | useEffect sin dependencias / bucles | Frontend |
| AP-004 | Prop drilling excesivo | Frontend |
| AP-005 | Estado derivado sin memoizacion | Rendimiento |
| AP-006 | Callback hell / Pyramid of Doom | Backend |
| AP-007 | API sin rate limiting | Seguridad |
| AP-008 | Modal con z-index hardcodeado | Frontend |
| AP-009 | N+1 queries en ORMs | Rendimiento |
| AP-010 | Manejo de errores con catch vacio | Backend |
| AP-011 | Tabla sin paginacion | Rendimiento |
| AP-012 | Dashboard con polling sin debounce | Frontend |
| AP-013 | Secrets en codigo fuente | Seguridad |
| AP-014 | Botones sin estado de carga | Frontend |
| AP-015 | useState para estado derivable | Frontend |

---

## Compresor Trinivel de Silogismos

Cada silogismo emitido por los agentes se reduce a tres paradigmas formales:

| Nivel | Paradigma | Ejemplo | Fuente |
|---|---|---|---|
| 1. Escolastico | Mnemotecnia A/E/I/O | `AAA-1` = Barbara | Aristoteles, Primeros Analiticos |
| 2. Conjuntos | Algebra de Boole | `S SUBSET P`, `s(1-p)=0` | Boole, Laws of Thought |
| 3. Predicados | Logica de primer orden | `forall x. S(x) -> P(x)` | Frege, Begriffsschrift |

Esto permite cachear conclusiones y detectar silogismos equivalentes aunque usen terminos distintos, ahorrando tokens de LLM.

---

## Licencia Rerum Novarum v2.0

El proyecto incluye su propia licencia de software basada en el indice Big Mac:

- **Devs pobres** (< 20,000 MXN/mes): **gratis**, solo pide estrella en GitHub
- **Open source**: gratis
- **Escala 1% a 10%** segun poder adquisitivo real medido en Big Macs
- **Geo-arbitraje**: si ganas en USD y vives en MX, pagas mas
- **Auto-Favorito**: dar estrella en GitHub es el diezmo digital minimo

Generar: `python main.py license --country MX --dev "Tu Nombre" --repo github.com/...`

---

## VS Code

El proyecto incluye `.vscode/tasks.json` con 7 tareas:

- `Ctrl+Shift+P` > `Tasks: Run Task`
- Concilio: Auditar archivo abierto (Escolastico)
- Concilio: Auditar archivo abierto (Ejecutivo rapido)
- Concilio: Auditar archivo abierto (Seguridad)
- Concilio: Escaneo rapido de anti-patrones
- Concilio: Auditar con DeepSeek
- Concilio: Listar agentes disponibles

---

## Estructura del proyecto

```
concilio_salamanca/
├── SKILL.md                     # Definicion para opencode/Antigravity
├── config.yaml                  # Configuracion (proveedor, modelo, rondas)
├── main.py                      # CLI principal simplificado
├── cli.py                       # Definición de argumentos de CLI
├── license_generator.py         # Generador LPRN v2.0 (Big Mac Index)
├── schemas.py                   # Modelos Pydantic
├── agents/                      # Agentes dinámicos (base y cargador virtual)
├── debate/                      # Orquestador, PnC, cache, formatters, voting, providers
├── prompts/                     # 18 system prompts
├── reference/                   # Anti-patrones, componentes, templates
└── tests/                       # 68 tests (unitarios e integración)
```

---

## Tests

```bash
py -m pytest
# 68 passed
```
