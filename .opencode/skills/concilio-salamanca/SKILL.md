---
name: concilio-salamanca
description: >
  Auditoria de codigo por silogismos ontologicos. Usa esta skill cuando necesites
  auditar, revisar, analizar o juzgar codigo fuente para detectar vulnerabilidades,
  anti-patrones, ineficiencias o fallos de diseno. El Concilio de Salamanca convoca
  un tribunal de 17 agentes IA especializados que debaten usando logica aristotelica
  y emiten un veredicto estructurado (Quaestio, Videtur, Sed Contra, Respondeo,
  Determinatio Codici). Soporta OpenAI, DeepSeek, Anthropic, Groq y Ollama.
  Activar con: auditar, revisar, analizar codigo, code review, encontrar bugs,
  revisar seguridad, optimizar codigo, anti-patrones.
---

# Concilio de Salamanca: Auditoria de Codigo MDE

> *"Ninguna linea de codigo sera desplegada sin haber sido sometida al tribunal de la razon."*

## Cuando usar esta skill

Activa esta skill cuando se pida:
- Revisar o auditar codigo
- Encontrar vulnerabilidades o bugs
- Evaluar calidad de codigo
- Optimizar rendimiento
- Revisar seguridad
- Validar buenas practicas
- Analizar arquitectura de software

## Como ejecutar la auditoria

NO escribas Python. Ejecuta comandos CLI directamente desde la raiz del proyecto:

```bash
# Auditoria basica (escolastica)
py concilio_salamanca/main.py --file <archivo> --agents escolasticos

# Auditoria ejecutiva (informe reducido)
py concilio_salamanca/main.py --file <archivo> --mode ejecutivo --agents pragmaticos

# Auditoria de seguridad
py concilio_salamanca/main.py --file <archivo> --agents seguridad,promotor --rounds 2

# Escaneo rapido de anti-patrones (sin LLM, gratuito)
py concilio_salamanca/main.py audit --file <archivo>
```

## Agentes (17 disponibles)

| Grupo | Clave | Agentes incluidos |
|---|---|---|
| Escolasticos (default) | `escolasticos` | Promotor, Defensor, Doctor, LaRouche, Leon XIII |
| Pragmaticos | `pragmaticos` | Linus Torvalds, Steve Wozniak, Ken Thompson |
| Tecnicos | `tecnicos` | DL, Seguridad, MLOps, Datos, Sistemas, IoT |
| Metodologia | `metodologia` | Scrum Master, Six Sigma |
| Calidad | `calidad` | Six Sigma, Scrum, MLOps, Datos |
| Dialecticos | `dialecticos` | Socrates, Promotor, Defensor |
| Empiristas | `empiristas` | Roger Bacon, Linus, Thompson |
| Ius Gentium | `ius_gentium` | Vitoria, Stallman, Leon XIII |
| Pedagogicos | `pedagogicos` | Ratio Studiorum, Socrates |
| Embebidos | `embebidos` | IoT, Wozniak, Thompson, Sistemas |
| Todos | `todos` | Los 24 agentes |

## Proveedores LLM

| Proveedor | Flag | Variable de entorno |
|---|---|---|
| OpenAI | `--provider openai` | `OPENAI_API_KEY` |
| DeepSeek | `--provider deepseek` | `DEEPSEEK_API_KEY` |
| Ollama (local) | `--provider ollama` | ninguna |

Ejemplo: `--provider deepseek --model deepseek-chat`

## Modos de salida

- **Escolastico** (default): Quaestio, Videtur, Sed Contra, Respondeo, Determinatio
- **Ejecutivo** (`--mode ejecutivo`): Informe reducido con tabla de metricas
- **JSON** (`--output json`): Para CI/CD

## Reglas

1. Ejecuta comandos desde la raiz: `D:\DocumentosWin\MDE Skill Modulos`
2. Si no se especifican agentes, usa `--agents escolasticos`
3. Para revisiones rapidas usa `--mode ejecutivo`
4. Si no hay API key, sugiere `--provider ollama` (local, gratis)
5. Resume hallazgos principales en 2-3 lineas al final
6. Si el codigo es frontend (React/HTML/CSS), sugiere tambien usar la skill `mde-frontend`

## Anti-patrones integrados

El sistema detecta 15 anti-patrones (AP-001 a AP-015): XSS, SQL Injection, useEffect mal usado, prop drilling, N+1 queries, secrets en codigo, botones sin loading, y mas.

Ver catalogo completo con: `py concilio_salamanca/main.py --list-anti-patrones`
