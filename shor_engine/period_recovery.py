import math
from fractions import Fraction
from typing import List, Tuple, Dict
from .schemas import ContinuedFractionStep

def recover_period_from_counts(
    counts: Dict[str, int], 
    num_counting_qubits: int, 
    N: int, 
    a: int
) -> Tuple[List[ContinuedFractionStep], List[int]]:
    """
    Analyzes measurement states to extract candidate periods using continued fractions.
    """
    total_states = 2 ** num_counting_qubits
    steps = []
    viable_periods = set()

    # Sort measurement states by frequency
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    for bitstring, count in sorted_counts:
        decimal_val = int(bitstring, 2)
        phase = decimal_val / total_states

        frac = Fraction(phase).limit_denominator(N)
        candidate_r = frac.denominator

        is_valid = False
        explanation = ""

        if candidate_r == 0 or candidate_r == 1:
            explanation = f"Measured state |{bitstring}⟩ = {decimal_val}. Phase {phase:.4f} gave denominator {candidate_r} (trivial)."
        elif pow(a, candidate_r, N) == 1:
            is_valid = True
            viable_periods.add(candidate_r)
            explanation = f"Success! {a}^{candidate_r} ≡ 1 (mod {N}). Valid period: r = {candidate_r}."
        elif pow(a, candidate_r * 2, N) == 1:
            is_valid = True
            viable_periods.add(candidate_r * 2)
            explanation = f"Multiplied candidate: {a}^{candidate_r*2} ≡ 1 (mod {N}). Valid period: r = {candidate_r * 2}."
        else:
            explanation = f"Rejected: {a}^{candidate_r} mod {N} = {pow(a, candidate_r, N)} ≠ 1."

        steps.append(ContinuedFractionStep(
            convergent_fraction=f"{frac.numerator}/{frac.denominator}",
            phase_estimate=round(phase, 4),
            candidate_r=candidate_r,
            is_valid_period=is_valid,
            explanation=explanation
        ))

    return steps, sorted(list(viable_periods))

def extract_factors_from_period(r: int, a: int, N: int) -> Tuple[bool, tuple | None, str]:
    """
    Computes gcd(a^(r/2) ± 1, N).
    """
    if r % 2 != 0:
        return False, None, f"Period r = {r} is odd; factor extraction condition fails."

    val = pow(a, r // 2, N)
    if val == N - 1:
        return False, None, f"Trivial outcome: a^(r/2) ≡ -1 (mod {N}). No non-trivial factors extracted."

    f1 = math.gcd(val - 1, N)
    f2 = math.gcd(val + 1, N)

    valid_factors = [f for f in (f1, f2) if 1 < f < N]

    if valid_factors:
        p = valid_factors[0]
        q = N // p
        return True, (min(p, q), max(p, q)), f"Success: Extracted non-trivial factors: {min(p, q)} and {max(p, q)}."

    return False, None, "Extracted factors were trivial (1 or N)."