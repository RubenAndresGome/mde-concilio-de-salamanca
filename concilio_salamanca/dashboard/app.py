import streamlit as st
import os
import sys

# Agregar al path para que encuentre concilio_salamanca si se lanza desde el subdirectorio
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from concilio_salamanca.debate.orchestrator import DebateOrchestrator, DebateConfig
from concilio_salamanca.debate.providers import create_model

st.set_page_config(page_title="Concilio de Salamanca", page_icon="⚖️", layout="wide")

st.title("🏛️ Concilio de Salamanca — Web Dashboard")
st.markdown("Dashboard interactivo para auditoría adversarial de código fuente.")

# Sidebar config
st.sidebar.header("Configuración del Debate")
provider = st.sidebar.selectbox(
    "Proveedor LLM", ["openai", "deepseek", "anthropic", "groq", "ollama", "opencode"]
)
model_name = st.sidebar.text_input("Modelo", "gpt-4o-mini")
rounds = st.sidebar.slider("Rondas de Debate", 1, 5, 2)
use_pnc = st.sidebar.checkbox("Usar Validación Z3 / PnC", value=True)
parallel = st.sidebar.checkbox("Ejecución Paralela", value=True)

# Main area
code_input = st.text_area(
    "Código Fuente a Analizar", height=300, placeholder="Pega tu código aquí..."
)

if st.button("Convocar al Concilio", type="primary"):
    if not code_input.strip():
        st.error("Por favor, introduce código fuente para analizar.")
    else:
        with st.spinner("Instanciando Magister Determinans y el modelo..."):
            try:
                llm = create_model(provider, model_name)
                config = DebateConfig(
                    max_rounds=rounds, include_pnc_validation=use_pnc, parallel=parallel
                )
                orchestrator = DebateOrchestrator(model=llm, config=config)

                st.info("El debate ha comenzado. Esperando los veredictos...")

                # Para evitar problemas con el event loop en Streamlit
                if parallel:
                    # En streamlit, usar asyncio a veces es problemático, fallback a sincrono
                    config.parallel = False
                    orchestrator = DebateOrchestrator(model=llm, config=config)

                result = orchestrator.run_debate(code_input, "auto")

                determinatio = result["determinatio"]

                st.success("¡Debate concluido!")

                st.subheader("📜 Determinatio Final")
                st.markdown(f"**Quaestio:** {determinatio.quaestio}")
                st.markdown("### Videtur quod (Argumentos a favor del código):")
                st.markdown(determinatio.videtur)
                st.markdown("### Sed Contra (Argumentos en contra):")
                st.markdown(determinatio.sed_contra)
                st.markdown("### Respondeo (Juicio Final):")
                st.markdown(determinatio.respondeo)

                if determinatio.pnc_validation:
                    st.subheader("🔍 Validación PnC y Z3")
                    st.write(
                        f"**Contradicciones detectadas:** {determinatio.pnc_validation.hay_contradicciones}"
                    )
                    st.write(determinatio.pnc_validation.resumen)

            except Exception as e:
                st.error(f"Error durante el debate: {e}")
