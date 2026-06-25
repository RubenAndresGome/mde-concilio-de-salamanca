---
name: concilio-salamanca
description: >
  Auditoria de codigo por silogismos ontologicos. Usa esta skill cuando necesites
  auditar, revisar, analizar o juzgar codigo fuente para detectar vulnerabilidades,
  anti-patrones, ineficiencias o fallos de diseno. El Concilio de Salamanca convoca
  un tribunal de 28 agentes IA especializados que debaten usando logica aristotelico-tomista
  y emiten un veredicto estructurado (Quaestio, Videtur, Sed Contra, Respondeo,
  Determinatio Codici). Soporta OpenAI, DeepSeek, Anthropic, Groq y Ollama.
  Activar con: auditar, revisar, analizar codigo, code review, encontrar bugs,
  revisar seguridad, optimizar codigo, anti-patrones, buenas practicas.
---

# Concilio de Salamanca: Auditoria de Codigo por Meta Dialectica Escolastica

> *"Ninguna linea de codigo sera desplegada sin haber sido sometida al tribunal de la razon."*

> **v4.0 — Lanzamiento Open Source**: 38 agentes, PyPI (`pip install concilio-salamanca`), CI/CD integrado, Spec-Kit + Open-Design, ranking calidad-precio.

## Cuando usar esta skill

Activa esta skill cuando el usuario pida:
- Revisar o auditar codigo
- Encontrar vulnerabilidades o bugs
- Evaluar calidad de codigo
- Optimizar rendimiento
- Revisar seguridad
- Validar buenas practicas
- Analizar arquitectura de software

## Como usar el sistema

El Concilio expone un CLI completo. NO es necesario escribir Python. La skill ejecuta comandos directamente:

### Comandos principales

```bash
# Auditoria basica (escolastica)
py concilio_salamanca/main.py --file <archivo> --agents escolasticos

# Auditoria ejecutiva (informe tecnico reducido)
py concilio_salamanca/main.py --file <archivo> --mode ejecutivo --agents pragmaticos

# Auditoria de seguridad
py concilio_salamanca/main.py --file <archivo> --agents seguridad,promotor --rounds 2

# Auditoria de IoT/embebidos
py concilio_salamanca/main.py --file <archivo> --agents embebidos

# Auditoria con Enrutamiento Cognitivo (Obreros baratos + Magister Deluxe)
py concilio_salamanca/main.py --file <archivo> --provider-obreros deepseek --model-obreros deepseek-chat --provider-magister openai --model-magister gpt-4o
```

### Comandos auxiliares

```bash
# Escaneo rapido de anti-patrones (sin LLM)
py concilio_salamanca/main.py audit --file <archivo>

# Listar agentes disponibles
py concilio_salamanca/main.py --list-agents

# Listar proveedores LLM
py concilio_salamanca/main.py --list-providers

# Generar licencia Rerum Novarum
py concilio_salamanca/main.py license --country MX --dev "Nombre" --project "Proyecto" --repo "github.com/..."
```

## Agentes disponibles (37)

| Grupo | Agentes | Clave |
|---|---|---|
| Escolasticos | Promotor, Defensor, Doctor, LaRouche, Leon XIII | `escolasticos` |
| Pragmaticos | Linus Torvalds, Steve Wozniak, Ken Thompson | `pragmaticos` |
| Tecnicos | DL, Seguridad, MLOps, Datos, Sistemas, IoT | `tecnicos` |
| Eticos | Stallman, Stroustrup | `eticos` |
| Algoritmicos | Korotkevich | `algoritmicos` |
| Dialécticos/Nuevos | Socrates, Scrum Master, Six Sigma, Llull, Bacon, Vitoria, Ratio | `dialecticos`, `metodologia`, `empiristas`, `ius_gentium` |
| Token Optimizadores | Ponytail, Graphify, RTK, Telemetry | `token_optimizers` |
| Embebidos | IoT, Wozniak, Thompson, Sistemas | `embebidos` |
| **Clean Code** | **Arquimedes, Custos Impacti, Magister Processus** | **`clean_code`** |
| **Proceso** | **Scrum Master, Six Sigma, Magister Processus** | **`proceso`** |
| Seguridad Ofensiva | Red Team, Pentest, Abuser, Seguridad | `red_team` |
| Filosofos Aplicados | Leibniz, Nietzsche, Socrates, Causas | `filosofos_aplicados` |
| Todos | Los 37 | `todos` |

## Configuración Multi-Modelo (v3.0)

Ahora puedes definir **pesos** para cada proveedor LLM en `config.yaml`. El modelo con mayor peso se usa como Ejecutor (obreros), y el `director_strategy` como Magister (razonamiento profundo).

```yaml
model_weights:
  deepseek: 1
  openai: 0
  anthropic: 0

roles:
  ejecutor: "deepseek"
  director_strategy: "openai"
```

Los pesos se resuelven automaticamente si no se especifica `--provider` por CLI.

## Proveedores LLM soportados

| Proveedor | Flag | Variable de entorno |
|---|---|---|
| OpenAI | `--provider openai` | `OPENAI_API_KEY` |
| DeepSeek | `--provider deepseek` | `DEEPSEEK_API_KEY` |
| Anthropic | `--provider anthropic` | `ANTHROPIC_API_KEY` |
| Groq | `--provider groq` | `GROQ_API_KEY` |
| Ollama (local) | `--provider ollama` | (ninguna) |

## Formato de salida

El sistema produce tres formatos:

1. **Escolastico** (default): Quaestio, Videtur, Sed Contra, Respondeo, Determinatio Codici
2. **Ejecutivo** (`--mode ejecutivo`): Informe tecnico con tabla de metricas
3. **JSON** (`--output json`): Estructurado para integracion con CI/CD

## Anti-patrones integrados

El sistema conoce 15 anti-patrones (AP-001 a AP-015) y los agentes los referencian
automaticamente en sus silogismos. Ver referencia completa en `reference/anti_patrones.py`.

## Referencias

- `reference/anti_patrones.py` - Catalogo de 15 anti-patrones
- `reference/componentes.py` - 4 componentes de referencia con checklist
- `reference/determinatio_template.py` - Plantillas de salida

## Reglas de uso

1. Siempre ejecuta la auditoria desde la raiz del proyecto (`D:\DocumentosWin\MDE Skill Modulos`)
2. Si el usuario no especifica agentes, usa `--agents escolasticos` por defecto
3. Si el usuario pide algo rapido, usa `--mode ejecutivo`
4. Si no hay API key configurada, sugiere usar `--provider ollama` (local, gratis)
5. **Economia Fisica Cognitiva**: Si la tarea es larga/costosa, sugiere dividir la carga usando `--provider-obreros ollama --provider-magister openai`.
6. Despues de la auditoria, resume los hallazgos principales en 2-3 lineas
7. Si el codigo es frontend (React/HTML/CSS), sugiere usar ademas la skill `mde-frontend`
