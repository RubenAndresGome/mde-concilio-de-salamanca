# Manual de Usuario — MDE Politeia Conciliar de Salamanca

> Guía paso a paso para instalar, configurar y ejecutar auditorías de código con 39 agentes IA usando lógica escolástica.

---

## Índice

1. [Instalación](#1-instalacion)
2. [Primera Auditoría](#2-primera-auditoria)
3. [Selección de Agentes](#3-seleccion-de-agentes)
4. [Proveedores LLM](#4-proveedores-llm)
5. [Auditoría Avanzada](#5-auditoria-avanzada)
6. [Licencia RNS v5.0](#6-licencia-rns-v50)
7. [Herramientas Externas](#7-herramientas-externas)
8. [Historial y Documentación](#8-historial-y-documentacion)

---

## 1. Instalación

### Requisitos
- Python 3.11+
- API key de al menos un proveedor LLM (OpenAI, DeepSeek, Anthropic, etc.)
- Opcional: Ollama para modelos locales gratuitos

### Instalación

```bash
pip install concilio-salamanca

# Con todos los proveedores:
pip install concilio-salamanca[all]
```

### Verificar instalación

```bash
concilio --list-agents     # 39 agentes disponibles
concilio --list-providers  # 6 proveedores LLM
```

### Configurar API key

```bash
# Windows
setx OPENAI_API_KEY "sk-..."
# o
setx DEEPSEEK_API_KEY "sk-..."

# Linux/macOS
export OPENAI_API_KEY="sk-..."
```

---

## 2. Primera Auditoría

### Crear un archivo de prueba

```javascript
// app.js
function login(username, password) {
    const query = "SELECT * FROM users WHERE user = '" + username + "'";
    db.execute(query);
    return true;
}
```

### Ejecutar auditoría escolástica

```bash
concilio --file app.js --agents escolasticos
```

### Salida esperada (formato escolástico)

```
╔══════════════════════════════════════════════════════════╗
║             DETERMINATIO MAGISTRALIS                     ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  QUAESTIO: ¿Es el código app.js seguro para producción?   ║
║                                                          ║
║  VIDETUR: La función login cumple su causa final          ║
║           (autenticar usuarios).                          ║
║                                                          ║
║  SED CONTRA: El Promotor Fidei detecta SQL Injection     ║
║              en línea 3 (AP-002). Contradicción lógica:   ║
║              el código protege Y expone simultáneamente.  ║
║                                                          ║
║  RESPONDEO: El código es funcional pero inseguro.         ║
║            Debe usar consultas parametrizadas.            ║
║                                                          ║
║  DETERMINATIO CODICI: CONDENNATIO.                        ║
║  Reemplazar concatenación por parámetros.                 ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

### Diagrama de flujo básico

```
┌──────────┐     ┌───────────────┐     ┌──────────────────┐     ┌──────────────┐
│ Código   │────▶│ Orquestador    │────▶│ 39 agentes IA    │────▶│ Magister     │
│ fuente   │     │ run_debate()   │     │ debaten en rondas│     │ Determinans  │
└──────────┘     └───────────────┘     └──────────────────┘     └──────┬───────┘
                                                                        │
                                                          ┌─────────────▼─────────────┐
                                                          │  DETERMINATIO CODICI      │
                                                          │  Quaestio + Videtur +     │
                                                          │  Sed Contra + Respondeo   │
                                                          └───────────────────────────┘
```

---

## 3. Selección de Agentes

### Por grupo

```bash
concilio --file app.py --agents escolasticos     # Tribunal clásico (5 agentes)
concilio --file app.py --agents clean_code       # SOLID + Impacto (3 agentes)
concilio --file app.py --agents logici           # OckhamDev + Socrates + Bacon + Leibniz
concilio --file app.py --agents red_team         # Seguridad ofensiva (4 agentes)
concilio --file app.py --agents todos            # Los 39 agentes (máximo rigor)
```

### Por agente individual

```bash
concilio --file app.py --agents promotor,seguridad,ockham,arquimedes
```

### Modo rápido (CI/CD)

```bash
concilio --file app.js --fast  # alias de nivel 1: 2 agentes, 1 ronda, máximo 2 llamadas
```

### Diagrama de agentes por capa

```
┌──────────────────────────────────────────────────────────────────┐
│                    39 AGENTES DEL CONCILIO                       │
├────────────┬────────────┬────────────┬────────────┬─────────────┤
│ ESCOLÁSTICO│ CLEAN CODE │  LÓGICA    │  DISEÑO    │ SEGURIDAD   │
│  Promotor  │ Arquímedes │ OckhamDev  │MagisterDel.│  RedTeam    │
│  Defensor  │  CustosImp.│ Sócrates   │  Vitoria   │  Pentest    │
│  Doctor    │ MagisterPr.│  Bacon     │  Ratio     │  Abuser     │
│  LaRouche  │            │  Leibniz   │            │  Seguridad  │
│  León XIII │            │            │            │             │
├────────────┼────────────┼────────────┼────────────┼─────────────┤
│ PRAGMÁTICO │  TÉCNICO   │   ÉTICO    │   TOKEN    │ FILOSOFÍA   │
│   Linus    │ Auditor DL │  Stallman  │  Ponytail  │   Causas    │
│  Wozniak   │  MLOps     │ Stroustrup │  Graphify  │  Nietzsche  │
│  Thompson  │  Datos     │            │    RTK     │             │
│  Korotk.   │  Sistemas  │            │ Telemetry  │             │
│            │    IoT     │            │            │             │
└────────────┴────────────┴────────────┴────────────┴─────────────┘
```

---

## 4. Proveedores LLM

### Tabla de proveedores y costos

| Proveedor | Modelo default | Costo $/MTok | Comando |
|---|---|---|---|
| **Ollama** (local) | `deepseek-r1:8b` | **Gratis** | `--provider ollama` |
| **DeepSeek** | `deepseek-v4-flash` | $0.14 entrada miss / $0.28 salida | `--provider deepseek` |
| **OpenRouter** | `deepseek/deepseek-v4-flash` | $0.09 | `--provider openrouter` |
| **OpenAI** | `gpt-4o` | $2.50 | `--provider openai` |
| **Anthropic** | `claude-sonnet-4` | $3.00 | `--provider anthropic` |
| **Groq** | `llama-3.3-70b` | Gratis* | `--provider groq` |

### Enrutamiento Cognitivo (obreros baratos + Magister Deluxe)

```bash
concilio --file app.js \
  --provider-obreros deepseek \
  --model-obreros deepseek-v4-flash \
  --provider-magister openai \
  --model-magister gpt-4o
```

### Diagrama de enrutamiento

```
                    ┌─────────────────────────┐
                    │   ModelRanker (auto)     │
                    │  rank_by_cost_quality()  │
                    └──────────┬──────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  OllamaLocal  │    │   OpenRouterHub   │    │  DirectProviders │
│  (gratis)     │    │  (339 modelos)    │    │  (OpenAI,Anthro) │
│  deepseek-r1  │    │  deepseek/qwen/   │    │  Claude = techo  │
│  qwen-coder   │    │  minimax/meta/    │    │  max expense     │
└──────────────┘    └──────────────────┘    └──────────────────┘
```

---

## 5. Auditoría Avanzada

### Con OckhamDev (lógica de conjuntos + CBMM)

```bash
# Requiere CBMM instalado: curl -fsSL https://.../install.sh | bash
concilio --file app.py --agents logici --ockham
```

### Modo Spec-Driven Development (SDD)

```bash
# Requiere Spec-Kit: uv tool install specify-cli
concilio --file app.py --mode sdd --agents proceso
```

### Modo PDCA

```bash
concilio --file app.py --mode pdca --agents proceso
```

### Con historial automático

```bash
concilio --file app.js --save-history --agents escolasticos
# Pregunta al final: "¿Guardar en .mde_history? [S/N/A]"
```

---

## 6. Licencia RNS v5.0

### Generar licencia

```bash
concilio license --country MX --dev "Tu Nombre" --project "Tu Proyecto" --repo "github.com/..."
```

### Con Jubileo (7 años desde major)

```bash
concilio license --country MX --dev "Autor" --project "Proyecto" --jubilee 2024 --std
```

### Registrar proyecto en el RNS Registry

```bash
concilio license --register --name "Mi Proyecto" --repo "https://github.com/user/project"
```

### Emitir Bula (propiedad privada 7 años)

```bash
concilio license --bula --dev "Acme Corp" --project "mi-proyecto" --revenue 5000000
```

### Pagar diezmo

```bash
concilio license --pay --dev "Acme Corp" --project "mi-proyecto" --amount 2500
```

---

## 7. Herramientas Externas

### Verificar herramientas disponibles

```bash
concilio --check-tools
```

```
=== Verificacion de herramientas externas ===
  Spec-Kit CLI:    ✓ disponible
  Open-Design CLI: ✗ no encontrado
  CBMM (grafo):    ✓ disponible
  ...
```

### Instalar Codebase Memory MCP (grafo de conocimiento)

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh | bash

# O desde el Concilio
concilio --check-tools  # intenta instalar automáticamente
```

### Instalar Open-Design (prototipos visuales)

```bash
# Desde open-design.ai
od mcp install opencode
```

---

## 8. Historial y Documentación

### Ver estadísticas del historial

```bash
concilio --history-stats
```

```
=== .mde_history Stats ===
Proyecto:       concilio-salamanca
Sesiones doc:   12 (con PDCA markdown)
PDCA generados: 13 archivos
```

### Estructura del historial

```
.mde_history/
├── 1_seiri_sort/       # Material archivado
├── 2_seiton_order/     # PDCA_001 ... PDCA_NNN.md
├── 3_seiso_shine/      # Diffs y archivos afectados
├── 4_seiketsu_std/     # Instrucciones y convenciones
└── 5_shitsuke_sustain/ # Colas de tareas y métricas
```

---

## Referencias rápidas

| Comando | Descripción |
|---|---|
| `concilio --list-agents` | 39 agentes y 24 grupos |
| `concilio --list-providers` | 6 proveedores LLM |
| `concilio --list-model-prices` | Tabla calidad-precio 22 modelos |
| `concilio --check-tools` | Verificar + instalar herramientas |
| `concilio --history-stats` | Estadísticas .mde_history |
| `concilio audit --file app.js` | Antipatrones sin LLM |
| `concilio license --help` | Licencia RNS v5.0 |
| `concilio bme --income 3000 --residence MX` | Precio justo Big Mac |
