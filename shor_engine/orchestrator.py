from typing import Optional
from .schemas import ShorExecutionResult, ShorStageResult
from .classical_preprocessor import classical_precheck
from .quantum_circuits import build_shor_circuit_n15, simulate_circuit
from .period_recovery import recover_period_from_counts, extract_factors_from_period

def run_shor_pipeline(
    N: int, 
    a: Optional[int] = None, 
    num_counting_qubits: int = 4, 
    shots: int = 2048
) -> ShorExecutionResult:
    stages = []

    # 1. Classical Precheck
    handled, message, resolved_a, trivial_factors = classical_precheck(N, a)
    
    if handled:
        stages.append(ShorStageResult(
            stage_name="Stage 1: Classical Precheck",
            status="SUCCESS" if trivial_factors else "INFO",
            summary=message,
            details={"trivial_factors": trivial_factors}
        ))
        return ShorExecutionResult(
            N=N, a=resolved_a if resolved_a else 0,
            num_counting_qubits=num_counting_qubits,
            shots=shots,
            is_quantum_executed=False,
            stages=stages,
            trivial_factor_found=trivial_factors is not None,
            factors=list(trivial_factors) if trivial_factors else [],
            success=trivial_factors is not None,
            message=message
        )

    stages.append(ShorStageResult(
        stage_name="Stage 1: Classical Precheck",
        status="SUCCESS",
        summary=f"N={N} is composite, non-prime-power, and coprime with base a={resolved_a}.",
        details={"a": resolved_a}
    ))

    # 2. Quantum Circuit Construction & Simulation
    if N == 15:
        qc = build_shor_circuit_n15(resolved_a, num_counting_qubits)
        counts = simulate_circuit(qc, shots=shots)
        total_shots = sum(counts.values())
        probabilities = {k: v / total_shots for k, v in counts.items()}
        circuit_str = qc.draw(output="text").single_string()

        stages.append(ShorStageResult(
            stage_name="Stage 2: Quantum Period Finding (QPE + QFT†)",
            status="SUCCESS",
            summary=f"Constructed & simulated Shor's circuit for N=15, a={resolved_a}.",
            details={"qubits": qc.num_qubits, "shots": shots, "outcomes": len(counts)}
        ))
    else:
        # Analytical Quantum Emulation for non-15 composites
        r_actual = 1
        while pow(resolved_a, r_actual, N) != 1:
            r_actual += 1

        total_states = 2 ** num_counting_qubits
        counts = {}
        for s in range(r_actual):
            phase = s / r_actual
            bin_idx = int(round(phase * total_states)) % total_states
            bitstr = f"{bin_idx:0{num_counting_qubits}b}"
            counts[bitstr] = counts.get(bitstr, 0) + (shots // r_actual)

        probabilities = {k: v / shots for k, v in counts.items()}
        circuit_str = f"[Quantum Circuit Emulation for N={N}, a={resolved_a}]\n(Full gate compilation for N > 15 abstracted for local hardware capacity)"
        
        stages.append(ShorStageResult(
            stage_name="Stage 2: Quantum Period Finding (Emulated)",
            status="SUCCESS",
            summary=f"Emulated Quantum Phase Estimation for N={N}, base={resolved_a}.",
            details={"shots": shots}
        ))

    # 3. Period Recovery (Continued Fractions)
    cf_steps, periods = recover_period_from_counts(counts, num_counting_qubits, N, resolved_a)

    stages.append(ShorStageResult(
        stage_name="Stage 3: Period Recovery via Continued Fractions",
        status="SUCCESS" if periods else "FAILED",
        summary=f"Found candidate period(s): {periods}" if periods else "No valid period satisfied modular equivalence.",
        details={"recovered_periods": periods}
    ))

    # 4. Factor Extraction
    final_factors = []
    overall_success = False
    extraction_message = "No factors derived."

    for r in periods:
        succ, facts, msg = extract_factors_from_period(r, resolved_a, N)
        if succ:
            final_factors = list(facts)
            overall_success = True
            extraction_message = msg
            break

    stages.append(ShorStageResult(
        stage_name="Stage 4: Factor Extraction via GCD",
        status="SUCCESS" if overall_success else "FAILED",
        summary=extraction_message,
        details={"factors": final_factors}
    ))

    return ShorExecutionResult(
        N=N,
        a=resolved_a,
        num_counting_qubits=num_counting_qubits,
        shots=shots,
        is_quantum_executed=(N == 15),
        stages=stages,
        trivial_factor_found=False,
        factors=final_factors,
        circuit_ascii=circuit_str,
        measurement_counts=counts,
        probabilities=probabilities,
        cf_steps=cf_steps,
        recovered_period=periods[0] if periods else None,
        period_found=len(periods) > 0,
        success=overall_success,
        message=extraction_message
    )