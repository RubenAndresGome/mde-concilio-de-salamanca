# Gobernanza cognitiva

## Ruta de ejecucion

1. Convertir las ordenes del usuario en proposiciones normalizadas.
2. Detener la auditoria si dos ordenes tienen la misma proposicion y polaridad opuesta.
3. Pedir al usuario que elija que orden conserva; no resolver su contradiccion por inferencia.
4. Persistir el Dogma objetivo, sus ordenes y relaciones en SQLite.
5. Convocar agentes y comprimir cada argumento previo a `V | PM | Pm | C | F`.
6. Emitir un voto final por agente y ponderarlo por competencia contextual y calidad formal.
7. Dar al Magister la tabla auditable antes de su `Determinatio`.

## Colegio electoral contextual

El peso no representa dignidad personal ni autoridad absoluta. Representa competencia para
el caso concreto:

```text
peso = (1 + competencia_contextual) * calidad_silogismo * PnC * reserva
```

- Competencia contextual: `+0.5` por dominio coincidente, hasta `+1.5`.
- Silogismo estructurado: `1.15`; texto no estructurado: `0.85`.
- Violacion del principio de no contradiccion: factor `0.5`.
- Reserva prudencial: factor `0.8`.
- Consenso: al menos `67%` del peso emitido, configurable por API.
- Cada agente aparece una sola vez aunque el debate tenga varias rondas.

La salida conserva `votos` y `mayoria` por compatibilidad, y agrega `votos_ponderados`,
`cuota_mayoria`, `contexto`, `formula` y el desglose por agente.

## Economia de tokens

- Mantener el codigo fuente intacto; acotar analisis, precedentes, historial y grafo.
- En rondas posteriores pasar el silogismo comprimido, no toda la prosa del agente.
- Deduplicar argumentos semanticamente identicos antes de construir el prompt.
- Usar recuperacion local FTS5 y vecindarios de 0 a 3 saltos; evitar cargar el grafo global.
- Registrar estimaciones antes/despues en `state.token_metrics`.
- Formular preguntas casuisticas por clase de riesgo y con limite; no repetir variantes
  lexicas de la misma pregunta.

Esta decision sigue el enfoque de presupuesto coarse-to-fine de
[LLMLingua](https://arxiv.org/abs/2310.05736), la compresion en hechos atomicos de
[Telegraph English](https://arxiv.org/abs/2605.04426), y la separacion local/global de
[Microsoft GraphRAG](https://microsoft.github.io/graphrag/query/overview/). Para busqueda
lexica se usa [SQLite FTS5 y BM25](https://www.sqlite.org/fts5.html), sin un servicio de
vectores obligatorio.

## SQLite y grafo

`CouncilStore` usa WAL, claves foraneas, `busy_timeout`, FTS5 y limites duros. Los nodos
pueden representar dogmas, ordenes, precedentes o hechos; las aristas llevan relacion y
peso. `graph_context` recupera semillas por BM25 y expande solo el vecindario solicitado.

La ubicacion por defecto es el directorio de datos local del usuario. Definir
`CONCILIO_DB_PATH` para aislar proyectos, CI o pruebas.

## Contrato de Dogma

Estados:

- `PROPUESTO`: transitorio durante la transaccion.
- `CONTRADICTORIO`: bloquear agentes y devolver pares incompatibles al usuario.
- `OBJETIVO`: ordenes coherentes o contradiccion resuelta expresamente.

No ejecutar `run_audit` con ordenes contradictorias. Invocar `resolve_dogma` con los IDs
que el usuario decida conservar y un objetivo explicito.
