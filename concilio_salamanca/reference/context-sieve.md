# Context sieve

Ejecutar antes de toda llamada sobre entradas grandes. Preferir diff, símbolos tocados, diagnósticos y vecinos directos. Conservar líneas de riesgo con dos líneas de entorno. No incluir archivos generados, vendorizados, secretos ni logs completos. Registrar `omitted_chars`; si la omisión impide verificar un hallazgo crítico, emitir `RESERVA` y pedir el fragmento concreto.

Herramienta MCP: `context_sieve`. Módulo: `debate.context_sieve.sift_context`.

