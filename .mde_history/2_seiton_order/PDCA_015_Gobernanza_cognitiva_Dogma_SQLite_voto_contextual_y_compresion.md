# PDCA 015 — Gobernanza cognitiva

## Plan

Hacer funcional la deliberacion del Concilio con un voto contextual auditable, reducir
contexto entre rondas, persistir Dogmas y memoria en SQLite, y convertir estas capacidades
en herramientas MCP deterministas.

## Do

- Sustituir el conteo textual por un colegio electoral de un voto final por agente.
- Ponderar competencia contextual, silogismo estructurado, PnC y reserva prudencial.
- Comprimir argumentos a `V | PM | Pm | C | F` bajo presupuesto configurable.
- Crear `CouncilStore` con WAL, claves foraneas, FTS5, BM25 y grafo local.
- Bloquear la convocatoria si las ordenes tienen polaridad opuesta sobre la misma proposicion.
- Exponer Dogma, casuistica y grafo mediante MCP.
- Documentar el contrato en `reference/gobernanza_cognitiva.md`.

## Check

- Suite heredada: 80 pruebas.
- Pruebas nuevas: voto no duplicado, peso contextual, penalizacion PnC, contradiccion y
  resolucion de Dogma, recuperacion multi-salto, presupuesto de compresion y catalogo MCP.
- Resultado esperado: 86 pruebas aprobadas y Ruff sin hallazgos en archivos modificados.

## Act

Mantener el umbral y los pesos como politica explicita. En una fase posterior, migrar los
precedentes JSON existentes a SQLite con una herramienta de importacion idempotente, sin
romper el formato heredado.
