import math
import streamlit as st
import pandas as pd
from shor_engine.orchestrator import run_shor_pipeline
from components.distribution_chart import render_measurement_chart
from components.cycle_visual import render_cycle_visual


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
    "effective_counting_qubits": "Phase bits used",
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

RSA_MODULUS = 15
RSA_PUBLIC_EXPONENT = 3
FACTOR_EXAMPLES = {
    "15 = 3 × 5 · base 7 · Qiskit circuit": (15, 7),
    "21 = 3 × 7 · base 2 · emulated": (21, 2),
    "35 = 5 × 7 · base 2 · emulated": (35, 2),
    "55 = 5 × 11 · base 2 · emulated": (55, 2),
    "77 = 7 × 11 · base 2 · emulated": (77, 2),
    "91 = 7 × 13 · base 3 · emulated": (91, 3),
}


def _load_factor_example():
    """Fill the practical factorizer with a known-good example and base."""
    selected = st.session_state.get("factor_example")
    if selected in FACTOR_EXAMPLES:
        number, base = FACTOR_EXAMPLES[selected]
        st.session_state["factor_N"] = number
        st.session_state["factor_base_mode"] = "I want to choose a base"
        st.session_state["factor_a"] = base

tab_rsa, tab_factor, tab_flow, tab_circuit, tab_measurements, tab_period, tab_notes = st.tabs([
    "🔐 RSA Lock Story",
    "🧮 Factor a Number",
    "📋 Data Flow",
    "⚛️ Quantum Circuit",
    "📊 Measurements",
    "🔄 Period Recovery",
    "📑 About this Demo",
])

with tab_rsa:
    st.subheader("A tiny locked message")
    st.write(
        "Imagine Bob shares a lock anyone can use, but keeps the key that opens it. "
        "RSA builds that lock from two secret prime numbers. Shor's algorithm could find those primes by finding a repeating pattern."
    )

    public_col, message_col, cipher_col = st.columns(3)
    public_col.metric("Bob's public lock", f"N = {RSA_MODULUS}, e = {RSA_PUBLIC_EXPONENT}")
    with st.form("rsa_story_form"):
        toy_message = st.number_input("Alice's tiny message", min_value=1, max_value=RSA_MODULUS - 1, value=2, step=1)
        unlock_clicked = st.form_submit_button("Try to open the lock", type="primary", use_container_width=True)

    if unlock_clicked:
        with st.spinner("Following the lock's number trail…"):
            rsa_result = run_shor_pipeline(
                N=RSA_MODULUS, a=7, num_counting_qubits=4, shots=2048,
            )
        st.session_state["rsa_story_result"] = rsa_result
        st.session_state["rsa_story_message"] = int(toy_message)
        st.session_state["shor_result"] = rsa_result

    rsa_result = st.session_state.get("rsa_story_result")
    rsa_message = st.session_state.get("rsa_story_message", int(toy_message))
    ciphertext = pow(rsa_message, RSA_PUBLIC_EXPONENT, RSA_MODULUS)
    message_col.metric("Message before locking", rsa_message)
    cipher_col.metric("Locked message", ciphertext)

    flow_cols = st.columns(5)
    flow_cols[0].markdown("#### 1. Public lock\nAnyone can see **15**")
    flow_cols[1].markdown(f"#### 2. Lock message\n`{rsa_message}` becomes **{ciphertext}**")
    flow_cols[2].markdown("#### 3. Find secret pieces\nShor finds **3** and **5**")
    flow_cols[3].markdown("#### 4. Rebuild key\nPrivate key number is **3**")
    flow_cols[4].markdown(f"#### 5. Unlock\n`{ciphertext}` opens back to **{rsa_message}**")

    if rsa_result is None:
        st.info("Press **Try to open the lock** to run the Shor demonstrator on this tiny public number.")
    elif rsa_result.success:
        p, q = rsa_result.factors
        phi = (p - 1) * (q - 1)
        private_exponent = pow(RSA_PUBLIC_EXPONENT, -1, phi)
        unlocked = pow(ciphertext, private_exponent, RSA_MODULUS)
        st.markdown("### The lock opens, one small step at a time")
        key_cols = st.columns(4)
        key_cols[0].metric("Hidden prime pieces", f"{p} × {q}")
        key_cols[1].metric("Number of possible key steps", phi)
        key_cols[2].metric("Private key number", private_exponent)
        key_cols[3].metric("Message after unlocking", unlocked)
        st.success(
            f"The public lock was **({RSA_MODULUS}, {RSA_PUBLIC_EXPONENT})**. "
            f"Factoring {RSA_MODULUS} gave {p} and {q}; that let us rebuild the private key and recover **{unlocked}**."
        )
        st.caption(
            "In this app, N = 15 runs in a Qiskit simulator. The message and key are toy numbers, "
            "and small numbers are easy to factor classically too. This is a lesson about a possible future risk, not a real security attack."
        )
    else:
        st.warning(f"This run did not recover factors: {rsa_result.message}. Press the button to try the simulated run again.")

    st.markdown(
        "[Why RSA is considered quantum-vulnerable](https://www.nist.gov/cybersecurity-and-privacy/what-post-quantum-cryptography)"
    )

with tab_factor:
    st.subheader("Try factoring an integer")
    st.write("Enter a number and run the demonstrator. You can let it choose a base or provide one yourself.")
    st.caption(
        "Ready-to-try examples (all have distinct prime factors): 15, 21, 35, 55, 77, and 91. "
        "Only 15 runs the Qiskit circuit; the others use emulated measurements."
    )
    st.selectbox(
        "Quick example — choose one to fill in the controls",
        ["Choose an example…", *FACTOR_EXAMPLES.keys()],
        key="factor_example",
        on_change=_load_factor_example,
    )

    with st.form("factor_number_form"):
        input_col, base_col = st.columns(2)
        with input_col:
            N = st.number_input("Integer to factor", min_value=2, max_value=99, value=15, step=1, key="factor_N")
        with base_col:
            base_mode = st.selectbox(
                "Base selection", ["Choose automatically", "I want to choose a base"],
                key="factor_base_mode",
            )
            a_val = None
            if base_mode == "I want to choose a base" and N >= 3:
                a_val = st.number_input("Base a", min_value=2, max_value=int(N) - 1,
                                        value=min(7, int(N) - 1), step=1, key="factor_a")
            elif base_mode == "I want to choose a base":
                st.caption("A base is not needed for this input.")

        with st.expander("Simulation settings"):
            setting_col1, setting_col2 = st.columns(2)
            with setting_col1:
                counting_qubits = st.slider("Counting qubits", min_value=2, max_value=6, value=4)
            with setting_col2:
                shots = st.select_slider("Measurements", options=[512, 1024, 2048, 4096], value=2048)

        run_btn = st.form_submit_button("Factor this number", type="primary", use_container_width=True)

    if run_btn:
        with st.spinner("Running the factorisation steps…"):
            st.session_state["shor_result"] = run_shor_pipeline(
                N=int(N), a=int(a_val) if a_val is not None else None,
                num_counting_qubits=counting_qubits, shots=shots,
            )

    result = st.session_state.get("shor_result")
    if result is None:
        st.info("Your result and explanation will appear here after you run a factorisation.")
    elif result.success:
        st.success(f"{result.N} = {result.factors[0]} × {result.factors[1]}")
        result_col1, result_col2 = st.columns(2)
        result_col1.metric("First factor", result.factors[0])
        result_col2.metric("Second factor", result.factors[1])
        st.caption("Check: the two factors multiply back to the number you entered.")
        st.write("Want to see how it got there? Open the Data Flow, Measurements, and Period Recovery tabs.")
    elif "prime number" in result.message.lower():
        st.info(result.message)
    else:
        st.warning(result.message)

    if result is not None:
        if result.is_quantum_executed:
            st.caption("This run used a Qiskit Aer circuit simulation.")
        elif result.stages[1].outputs.get("execution_mode") == "analytical_emulation":
            st.caption("This run used analytical emulation; no quantum circuit was executed.")
            requested_bits = result.stages[1].details.get("requested_counting_qubits", result.num_counting_qubits)
            if result.num_counting_qubits > requested_bits:
                st.info(
                    f"For a clear period result, the emulation increased the virtual phase bits "
                    f"from {requested_bits} to {result.num_counting_qubits}. This is still a classical emulation, not a quantum run."
                )
        else:
            st.caption("This number was handled by the classical precheck; no quantum circuit was executed.")

result = st.session_state.get("shor_result")

with tab_flow:
    if result is None:
        st.info("Run a factorisation in the Factor a Number tab to see its data flow.")
    else:
        st.subheader("First, watch the number trail")
        st.write(
            "Imagine making groups of the number you entered. Multiply by the base, "
            "keep the leftovers, and do it again. The colored trail shows when those leftovers return to 1."
        )
        if result.a > 1 and math.gcd(result.a, result.N) == 1:
            cycle_period = render_cycle_visual(result.N, result.a)
            st.caption(
                f"Each stop is the leftover after multiplying by {result.a} and grouping by {result.N}. "
                f"The trail comes back to 1 after {cycle_period} steps."
            )
            if result.is_quantum_executed:
                st.info("For this N = 15 run, the Qiskit circuit's measurements are used to recover the period. The trail above is a picture to help explain the repeating pattern.")
            else:
                st.info("This trail is an ordinary-math picture of the pattern. For this input, the app uses emulated measurements rather than executing a quantum circuit.")

            factor_stage = next((stage for stage in reversed(result.stages)
                                 if stage.stage_name.startswith("Stage 4:")), None)
            period_used = factor_stage.outputs.get("period_used") if factor_stage else None
            if result.success and period_used is not None and period_used % 2 == 0:
                half_power = pow(result.a, period_used // 2, result.N)
                left_gcd = math.gcd(half_power - 1, result.N)
                right_gcd = math.gcd(half_power + 1, result.N)
                st.subheader("Then, see how the clues reveal the factors")
                st.markdown(f"The trail repeats after **{period_used} jumps**. Halfway is **{period_used // 2} jumps**.")
                st.caption(f"So {result.a} to the power {period_used // 2}, after grouping by {result.N}, leaves {half_power}.")
                clue_left, clue_right = st.columns(2)
                clue_left.metric("One less: shared divisor", f"gcd({half_power - 1}, {result.N}) = {left_gcd}")
                clue_right.metric("One more: shared divisor", f"gcd({half_power + 1}, {result.N}) = {right_gcd}")
                st.success(f"Those two clues give the factors **{result.factors[0]} × {result.factors[1]} = {result.N}**.")
        else:
            st.info("The chosen base already shares a factor with this number, so the app can find a factor directly. It does not need to search for a repeating trail.")

        st.divider()
        st.subheader("Now follow the values through the algorithm")
        for stage in result.stages:
            status_icon = {
                "SUCCESS": "✅", "INFO": "ℹ️", "SKIPPED": "⏭️", "FAILED": "⚠️",
            }.get(stage.status, "⚠️")
            with st.expander(f"{status_icon} {stage.stage_name}", expanded=True):
                st.write(stage.summary)
                _render_trace_fields(stage.inputs, section="What went into this step")
                _render_trace_fields(stage.outputs, section="What came out of this step")
                if stage.details:
                    _render_trace_fields(stage.details, section="Extra notes")

with tab_circuit:
    if result is None:
        st.info("Run a factorisation first to see its circuit view.")
    else:
        st.subheader("Quantum phase-estimation circuit")
        if result.is_quantum_executed:
            st.info("This run used direct Qiskit gate-level simulation.")
        else:
            st.warning("This run did not execute a quantum circuit. The view is an explanation or emulation placeholder.")
        st.code(result.circuit_ascii or "No circuit was needed for this input.", language="text")

with tab_measurements:
    if result is None:
        st.info("Run a factorisation first to see its measurement results.")
    elif result.probabilities:
        st.subheader("Measured phase probabilities")
        fig = render_measurement_chart(result.probabilities)
        st.plotly_chart(fig, use_container_width=True)
        df_counts = pd.DataFrame([
            {"State |x⟩": k, "Decimal": int(k, 2), "Counts": result.measurement_counts[k], "Probability": f"{v:.4f}"}
            for k, v in result.probabilities.items()
        ])
        st.dataframe(df_counts, use_container_width=True)
    else:
        st.info("There were no quantum measurements for this input.")

with tab_period:
    if result is None:
        st.info("Run a factorisation first to see how the period was recovered.")
    elif result.cf_steps:
        st.subheader("Continued fractions and order finding ($a^r \\equiv 1 \\pmod N$)")
        cf_data = [{
            "Phase": step.phase_estimate,
            "Fraction": step.convergent_fraction,
            "Candidate r": step.candidate_r,
            "Valid period?": "✅ Yes" if step.is_valid_period else "❌ No",
            "Explanation": step.explanation,
        } for step in result.cf_steps]
        st.dataframe(pd.DataFrame(cf_data), hide_index=True, use_container_width=True)
    else:
        st.info("This run had no quantum measurements to process.")

with tab_notes:
    st.markdown("""
    ### What this demonstrator does
    Shor's method uses quantum period finding as one step in integer factorisation. The app shows the input checks, measurement results, period candidates, and classical factor extraction for each run.

    ### Scope of this demo
    The gate-level Qiskit/Aer circuit runs for **N = 15**. Other accepted odd composites use analytical phase-bin emulation based on a classically computed order, so those examples do not represent quantum circuit execution. Even numbers, primes, and prime powers can be handled by the classical precheck.

    A period only yields factors when it is even and the half-period does not give the `-1 mod N` outcome. If factor extraction fails, try a different base or run again.
    """)
