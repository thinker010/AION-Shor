import streamlit as st
import pandas as pd
from shor_engine.orchestrator import run_shor_pipeline
from components.distribution_chart import render_measurement_chart


TRACE_LABELS = {
    "N": "Number to factor",
    "requested_base": "Base requested",
    "resolved_base": "Base used",
    "a": "Base used",
    "counting_qubits": "Counting qubits",
    "requested_shots": "Requested measurements",
    "total_shots": "Measurements recorded",
    "handled_classically": "Solved in the classical check",
    "quantum_stages_skipped": "Quantum steps skipped",
    "execution_mode": "How the period was found",
    "candidate_periods": "Candidate periods",
    "factors": "Factors found",
    "verified": "Factor check passed",
    "executed": "This step ran",
    "measurement_counts": "Measurement results",
    "probabilities": "Measurement probabilities",
    "continued_fraction_steps": "Period-finding calculations",
}


def _trace_text(value):
    """Turn trace values into short, readable labels for the stage cards."""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if value is None:
        return "Not set"
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) if value else "None"
    if value == "qiskit_aer":
        return "Qiskit Aer circuit simulation"
    if value == "analytical_emulation":
        return "Analytical emulation (no circuit executed)"
    return str(value)


def _render_trace_fields(fields, *, section, omit=()):
    """Render stage inputs/outputs as labeled UI rows, never as raw JSON."""
    visible = [(key, value) for key, value in fields.items() if key not in omit]
    if not visible:
        return

    st.markdown(f"**{section}**")
    for key, value in visible:
        label = TRACE_LABELS.get(key, key.replace("_", " ").capitalize())
        if key == "measurement_counts" and value:
            rows = [
                {"Measured state": f"|{state}⟩", "Times seen": count}
                for state, count in sorted(value.items(), key=lambda item: item[1], reverse=True)
            ]
            st.caption(label)
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
        elif key == "probabilities":
            st.caption("The probability chart in the Measurement Distribution tab visualizes these results.")
        elif key == "continued_fraction_steps":
            st.caption("The Period Recovery tab shows each continued-fraction calculation.")
        else:
            st.markdown(f"- **{label}:** {_trace_text(value)}")

st.set_page_config(
    page_title="Shor's Algorithm Demonstrator | AION-IA",
    page_icon="⚛️",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1E222A;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #2E3440;
    }
    .stAlert {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚛️ Shor's Algorithm Interactive Demonstrator")
st.caption("Quantum Integer Factorization Engine — AION-IA Internship Task 04")

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Configuration")
    N = st.number_input("Target Integer (N)", min_value=3, max_value=99, value=15, step=2)
    
    custom_a = st.checkbox("Specify Coprime Base (a)", value=False)
    a_val = None
    if custom_a:
        a_val = st.number_input("Base (a)", min_value=2, max_value=N-1, value=7)
    
    st.divider()
    st.subheader("Quantum Parameters")
    counting_qubits = st.slider("Counting Qubits", min_value=2, max_value=6, value=4)
    shots = st.select_slider("Simulation Shots", options=[512, 1024, 2048, 4096], value=2048)
    
    run_btn = st.button("🚀 Execute Factorization", type="primary", use_container_width=True)

# Main Stage Display
if run_btn:
    with st.spinner("Processing Shor's Pipeline..."):
        result = run_shor_pipeline(N=N, a=a_val, num_counting_qubits=counting_qubits, shots=shots)

    # Top Status Bar
    if result.success:
        st.success(f"### 🎉 Factorization Successful: {N} = {result.factors[0]} × {result.factors[1]}")
    else:
        st.error(f"### ❌ Factorization Incomplete: {result.message}")

    # Tabs for Data Flow Stages
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Stages & Data Flow", 
        "⚛️ Quantum Circuit", 
        "📊 Measurement Distribution", 
        "🔄 Period Recovery (C.F.)",
        "📑 Technical Notes"
    ])

    with tab1:
        st.subheader("Algorithm Step-by-Step Execution")
        for stage in result.stages:
            status_icon = {
                "SUCCESS": "✅",
                "INFO": "ℹ️",
                "SKIPPED": "⏭️",
                "FAILED": "⚠️",
            }.get(stage.status, "⚠️")
            with st.expander(f"{status_icon} {stage.stage_name}", expanded=True):
                st.write(stage.summary)
                _render_trace_fields(stage.inputs, section="What went into this step")
                _render_trace_fields(stage.outputs, section="What came out of this step")
                if stage.details:
                    _render_trace_fields(stage.details, section="Extra notes")

    with tab2:
        st.subheader("Quantum Phase Estimation Circuit")
        if result.is_quantum_executed:
            st.info("Direct Qiskit gate-level execution with modular exponentiation unitaries:")
            st.code(result.circuit_ascii, language="text")
        else:
            st.warning("Quantum Circuit visualization bypassed (Handled classically or via QPE emulator).")
            st.code(result.circuit_ascii, language="text")

    with tab3:
        st.subheader("Measured Phase Probabilities")
        if result.probabilities:
            fig = render_measurement_chart(result.probabilities)
            st.plotly_chart(fig, use_container_width=True)
            
            df_counts = pd.DataFrame([
                {"State |x⟩": k, "Decimal": int(k, 2), "Counts": result.measurement_counts[k], "Probability": f"{v:.4f}"}
                for k, v in result.probabilities.items()
            ])
            st.dataframe(df_counts, use_container_width=True)

    with tab4:
        st.subheader("Continued Fractions & Order Finding ($a^r \\equiv 1 \\pmod N$)")
        if result.cf_steps:
            cf_data = []
            for s in result.cf_steps:
                cf_data.append({
                    "Phase": s.phase_estimate,
                    "Fraction": s.convergent_fraction,
                    "Candidate r": s.candidate_r,
                    "Valid Period?": "✅ Yes" if s.is_valid_period else "❌ No",
                    "Status": s.explanation
                })
            st.table(pd.DataFrame(cf_data))
        else:
            st.write("No quantum measurements to process.")

    with tab5:
        st.markdown("""
        ### Physical & Mathematical Limitations
        1. **Quantum Memory Constraints:** Compiling arbitrary $a^x \\pmod N$ circuits on NISQ simulators requires $\\mathcal{O}(n^3)$ gates and significant ancillary registers. $N=15$ runs natively at gate-level; larger composites use phase-bin emulation.
        2. **Even Periods Requirement:** Shor's method succeeds when the recovered order $r$ is even and $a^{r/2} \\not\\equiv -1 \\pmod N$. If not met, pick another coprime $a$.
        """)
