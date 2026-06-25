"""
CLI argument parser y seleccion interactiva de agentes para el Concilio de Salamanca.

Define todos los flags de linea de comandos: proveedores, modelos, agentes,
modos de salida, y subcomandos (license, bme, audit, dashboard).
"""

from __future__ import annotations

import argparse
from typing import List


def prompt_agents_interactive() -> List[str]:
    from concilio_salamanca.agents import AGENT_REGISTRY, AGENT_GROUPS

    print("\nSelecciona los agentes que participaran en el Concilio:")
    print("  - Escribe las claves separadas por comas (ej: promotor,linus,stallman)")
    print("  - O usa un grupo predefinido (ej: escolasticos, pragmaticos, todos)")
    print()
    print("Grupos disponibles:")
    for group, members in AGENT_GROUPS.items():
        print(f"  {group:15s} = {', '.join(members)}")
    print()
    print("Agentes disponibles:")
    for key, (label, _) in AGENT_REGISTRY.items():
        print(f"  {key:15s} - {label}")
    print()
    print("Default: promotor,defensor,doctor,larouche,leon_xiii")
    print()

    try:
        raw = input("Agentes > ").strip()
    except (EOFError, KeyboardInterrupt):
        return ["promotor", "defensor", "doctor", "larouche", "leon_xiii"]

    if not raw:
        return ["promotor", "defensor", "doctor", "larouche", "leon_xiii"]

    return [a.strip() for a in raw.split(",") if a.strip()]


def setup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Concilio de Salamanca - Auditoria MDE de Codigo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--code", "-c", type=str, help="Codigo a analizar (string directo)"
    )
    parser.add_argument("--file", "-f", type=str, help="Archivo de codigo a analizar")
    parser.add_argument(
        "--model", "-m", type=str, default=None, help="Modelo LLM a usar (aplica a todos si no se divide)"
    )
    parser.add_argument(
        "--provider",
        type=str,
        default=None,
        choices=["openai", "deepseek", "anthropic", "groq", "ollama", "opencode", "openrouter"],
        help="Proveedor LLM global (openai, deepseek, anthropic, groq, ollama, opencode, openrouter)",
    )
    parser.add_argument(
        "--provider-magister",
        type=str,
        default=None,
        choices=["openai", "deepseek", "anthropic", "groq", "ollama", "opencode", "openrouter"],
        help="Proveedor LLM exclusivo para el Magister Determinans (Deluxe)",
    )
    parser.add_argument(
        "--model-magister", type=str, default=None, help="Modelo especifico para el Magister (ej. gpt-4o)"
    )
    parser.add_argument(
        "--provider-obreros",
        type=str,
        default=None,
        choices=["openai", "deepseek", "anthropic", "groq", "ollama", "opencode", "openrouter"],
        help="Proveedor LLM exclusivo para el foro de agentes obreros",
    )
    parser.add_argument(
        "--model-obreros", type=str, default=None, help="Modelo especifico para los agentes obreros (ej. deepseek-chat)"
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="URL base del endpoint (para proxies o self-hosted)",
    )
    parser.add_argument(
        "--list-providers",
        action="store_true",
        help="Listar proveedores LLM soportados y salir",
    )
    parser.add_argument(
        "--rounds", "-r", type=int, default=None, help="Rondas de debate"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="text",
        choices=["text", "json", "markdown", "mermaid", "sarif"],
        help="Formato de salida",
    )
    parser.add_argument(
        "--agents",
        "-a",
        type=str,
        default=None,
        help="Agentes del debate (claves separadas por comas o nombre de grupo). Usa --list-agents para ver opciones.",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="auto",
        choices=["escolastico", "ejecutivo", "sdd", "pdca", "auto"],
        help="Modo de salida/operacion: escolastico, ejecutivo, sdd (Spec-Driven), pdca, auto",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Mostrar reporte trinivel de silogismos (escolastico, conjuntos, predicados)",
    )
    parser.add_argument(
        "--refine-design",
        action="store_true",
        default=False,
        help="Refinar prototipos visuales con modelo premium (Claude) al final del PDCA",
    )
    parser.add_argument(
        "--check-tools",
        action="store_true",
        help="Detectar herramientas externas (Spec-Kit, Open-Design) y salir",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Seleccion interactiva de agentes",
    )
    parser.add_argument(
        "--list-agents",
        action="store_true",
        help="Listar agentes y grupos disponibles y salir",
    )
    parser.add_argument(
        "--list-anti-patrones",
        action="store_true",
        help="Listar catalogo de anti-patrones y salir",
    )
    parser.add_argument(
        "--list-componentes",
        action="store_true",
        help="Listar ejemplos de componentes de referencia y salir",
    )
    parser.add_argument(
        "--no-pnc",
        action="store_true",
        help="Deshabilitar validacion del Principio de No Contradiccion",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Modo rapido para CI/CD: 2 agentes, 1 ronda, ejecucion en paralelo",
    )
    parser.add_argument(
        "--config", type=str, default=None, help="Archivo de configuracion YAML"
    )
    parser.add_argument("--api-key", type=str, default=None, help="API key de OpenAI")
    parser.add_argument(
        "--save", "-s", type=str, default=None, help="Guardar veredicto en archivo"
    )
    parser.add_argument(
        "--model-weights",
        type=str,
        default=None,
        help="Ruta a JSON/YAML con pesos de modelos (opcional, sobreescribe config.yaml)",
    )
    parser.add_argument(
        "--list-model-prices",
        action="store_true",
        help="Listar tabla de precios de modelos (calidad-precio-disponibilidad) y salir",
    )
    parser.add_argument(
        "--prefer-local",
        action="store_true",
        default=True,
        help="Priorizar modelos locales (Ollama) sobre APIs cloud",
    )
    parser.add_argument(
        "--cache-stats",
        action="store_true",
        help="Mostrar estadisticas del cache de silogismos",
    )

    subparsers = parser.add_subparsers(dest="command", help="Comandos adicionales")

    license_parser = subparsers.add_parser(
        "license", help="Generar Licencia Rerum Novarum"
    )
    license_parser.add_argument(
        "--country", type=str, default="US", help="Codigo de pais para umbrales PPA"
    )
    license_parser.add_argument(
        "--dev", type=str, default="", help="Nombre del desarrollador"
    )
    license_parser.add_argument(
        "--project", type=str, default="", help="Nombre del proyecto"
    )
    license_parser.add_argument(
        "--repo",
        type=str,
        default="",
        help="URL del repositorio GitHub (para clausula Auto-Favorito)",
    )
    license_parser.add_argument(
        "--save", "-s", type=str, default=None, help="Guardar licencia en archivo"
    )
    license_parser.add_argument(
        "--list-countries",
        action="store_true",
        help="Listar paises con soporte PPA",
    )
    license_parser.add_argument(
        "--jubilee",
        type=int,
        default=None,
        help="Ano de la ultima version major para activar clausula de Jubileo (ej: 2026)",
    )
    license_parser.add_argument(
        "--std",
        action="store_true",
        default=False,
        help="Marcar esta licencia como version STD (Estandar Comunitaria)",
    )
    license_parser.add_argument(
        "--register",
        action="store_true",
        default=False,
        help="Registrar un proyecto en el RNS Registry",
    )
    license_parser.add_argument(
        "--pay",
        action="store_true",
        default=False,
        help="Registrar un pago de licencia",
    )
    license_parser.add_argument(
        "--bula",
        action="store_true",
        default=False,
        help="Emitir una Bula de 7 anos para un proyecto",
    )
    license_parser.add_argument(
        "--list-registry",
        action="store_true",
        default=False,
        help="Listar el RNS Registry (proyectos, bulas, pagos)",
    )
    license_parser.add_argument(
        "--revenue",
        type=float,
        default=None,
        help="Facturacion anual en USD (para calculo de precio de Bula)",
    )
    license_parser.add_argument(
        "--amount",
        type=float,
        default=None,
        help="Monto del pago en USD (para --pay)",
    )

    bme_parser = subparsers.add_parser(
        "bme", help="Calcular Big Mac Equivalents (Precio Justo)"
    )
    bme_parser.add_argument(
        "--income", type=float, required=True, help="Ingreso bruto mensual en USD"
    )
    bme_parser.add_argument(
        "--residence", type=str, required=True, help="Pais de residencia (codigo ISO)"
    )
    bme_parser.add_argument(
        "--income-country",
        type=str,
        default=None,
        help="Pais de origen del ingreso (si es distinto al de residencia, activa geo-arbitraje)",
    )

    audit_parser = subparsers.add_parser(
        "audit", help="Escanear codigo en busca de anti-patrones conocidos (sin LLM)"
    )
    audit_parser.add_argument(
        "--file", "-f", type=str, required=True, help="Archivo a escanear"
    )
    audit_parser.add_argument(
        "--domain",
        type=str,
        default=None,
        choices=[
            "frontend",
            "backend",
            "seguridad",
            "rendimiento",
            "datos",
            "fullstack",
        ],
        help="Filtrar por dominio",
    )

    dashboard_parser = subparsers.add_parser(
        "dashboard", help="Lanzar el dashboard web en Streamlit"
    )

    return parser
