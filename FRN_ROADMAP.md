# 🏛️ Fundación Rerum Novarum (FRN) — Manifiesto y Roadmap

## Politeia de Desarrolladores — Un Gobierno de los que Construyen

### El Problema

La **Free Software Foundation** (FSF, 1985) defendió el código abierto como derecho moral. Durante 40 años, logró que el software libre fuera una fuerza imparable. Pero **no resolvió el hambre de los mantenedores**. Hoy, proyectos que sostienen internet (OpenSSL, curl, FFmpeg) son mantenidos por una o dos personas que no reciben salario, mientras empresas que valen más que naciones enteras construyen sus imperios sobre ese trabajo gratuito.

La **Linux Foundation** financia infraestructura crítica. Pero no fiscaliza quién extrae valor sin retornar. Las empresas pagan membresías voluntarias. Las que no quieren pagar, no pagan.

La **Fundación Rerum Novarum** (FRN) resuelve el vacío que queda entre ambas: **un sistema de commons compensado con enforcement real**.

### Principios de la Politeia

| Principio | Origen | Aplicación FRN |
|---|---|---|
| **Gobierno de los virtuosos** | Aristóteles, *Política* | Voto ponderado por méritos: quien más contribuye, más decide |
| **El trabajo merece su salario** | Lucas 10:7, León XIII, *Rerum Novarum* | Diezmo Tecnológico obligatorio para uso comercial |
| **No robarás** | Exodo 20:15 | Montaje sin fork = robo acreditable (Art. 5.4 RNS) |
| **Destino universal de los bienes** | Juan Pablo II, *Centesimus Annus* | Jubileo del Código cada 7 años (Art. 11 RNS) |
| **Subsidiariedad** | Pío XI, *Quadragesimo Anno* | Gobernanza local: cada proyecto decide su pricing dentro del marco RNS |

### ¿En qué se diferencia de la FSF y la Linux Foundation?

| | FSF | Linux Foundation | **FRN** |
|---|---|---|---|
| **Propósito** | Defender el software libre como derecho | Financiar infraestructura crítica | **Remunerar a los mantenedores** |
| **Modelo económico** | Donaciones voluntarias | Membresías corporativas | **Diezmo obligatorio (1%-10%) + Bulas (7 años)** |
| **Enforcement** | Ninguno (solo defensa legal de GPL) | Ninguno | **Crawler público + recompensas (30% al delator) + arbitraje ICC** |
| **Gobernanza** | Junta directiva designada | Junta corporativa | **Politeia: voto ponderado por méritos** |
| **Sede** | Boston (Norte Global) | San Francisco (Norte Global) | **Sur Global (Uruguay / Costa Rica / India)** |
| **Licencia** | GPL (copyleft) | Apache/MIT (permisiva) | **RNS (commons compensado)** |

---

## Roadmap

### Fase 1 — Constitución Legal (2025-2026)

| Hito | Estado | Detalle |
|---|---|---|
| Sede legal | 📋 Planificado | Uruguay o Costa Rica: estabilidad jurídica, baja carga fiscal, tradición de derecho civil |
| Estatutos | 📋 Planificado | Reflejar Artículo 15 del Statuto RNS: comité de 10 miembros (5 electos por mérito, 3 por interés, 2 fundadores) |
| Cuenta bancaria | 📋 Planificado | Para el Fondo de Sostenibilidad |
| Convenio FSF | 📋 Planificado | Hermandad con FSF para interoperabilidad de licencias |
| Abogados PI | 📋 Planificado | 1-2 abogados para revisión final de RNS y enforcement |

### Fase 2 — Infraestructura Técnica (2026)

| Hito | Estado | Detalle |
|---|---|---|
| Crawler de fingerprinting | 📋 Planificado | Bot que escanea GitHub/GitLab buscando firmas de código RNS. Cruza con registro de pagos. |
| Registro público | ✅ Implementado | `concilio license --register` — `rns_registry.py` |
| Pasarela de pago | 📋 Planificado | Integración con Stripe para pagos recurrentes |
| Badge "RNS Licensed" | ✅ Implementado | Generado automáticamente por `rns_registry.py` |
| Smart contracts (Bulas NFT) | 📋 Planificado | Bulas como tokens no transferibles en blockchain para trazabilidad inmutable |

### Fase 3 — Primeros Casos de Enforcement (2026-2027)

| Hito | Estado | Detalle |
|---|---|---|
| Proyecto piloto | 📋 Planificado | Un proyecto open source de alto perfil migra a RNS (ej: curl, FFmpeg, SQLite) |
| Primera mediación | 📋 Planificado | Mediación comunitaria exitosa (Art. 16) como precedente |
| Primer arbitraje | 📋 Planificado | Laudo ICC ejecutable en 170+ países (Convención de Nueva York) |
| Jurisprudencia RNS | 📋 Planificado | Primer caso público de enforcement |

### Fase 4 — Autonomía Financiera (2027+)

| Hito | Estado | Detalle |
|---|---|---|
| 5+ mantenedores full-time | 📋 Planificado | Salarios pagados por el Fondo de Sostenibilidad |
| Elecciones del Comité | 📋 Planificado | Cada 2 años, voto ponderado por méritos |
| Distribución SCRUM | 📋 Planificado | Sprints trimestrales de distribución del Fondo |
| 100+ proyectos RNS | 📋 Planificado | Masa crítica de adopción |

---

## Cómo Contribuir

### Si eres Desarrollador
- Adopta RNS como licencia de tu proyecto: `concilio license --country MX --dev "Tu Nombre" --project "Tu Proyecto" --std`
- Registra tu proyecto: `concilio license --register --name "Tu Proyecto" --repo "https://github.com/..."`
- Reporta uso no declarado al crawler de la FRN

### Si eres Empresa
- Paga el Diezmo sin Compliance (Art. 4.0): 0.5%-3% auto-declarado, sin contrato
- Adquiere una Bula (Art. 14) para mantener tu código cerrado 7 años
- Haz fork público para compliance documentado: el fork es tu prueba de buena fe

### Si eres Abogado o Jurista
- Revisa el Statuto RNS y propón mejoras a las cláusulas de enforcement
- Ayuda a constituir legalmente la FRN en tu jurisdicción
- Participa en el arbitraje comunitario como mediador certificado

---

*"El trabajador merece su salario" (Lucas 10:7) — no como limosna, sino como derecho.*
*La Politeia de Desarrolladores no pide permiso: construye su propio gobierno.*
