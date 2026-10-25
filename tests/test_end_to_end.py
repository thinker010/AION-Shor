import pytest
from shor_engine.orchestrator import run_shor_pipeline

def test_even_number_early_exit():
    res = run_shor_pipeline(N=14)
    assert res.success is True
    assert set(res.factors) == {2, 7}
    assert res.is_quantum_executed is False
    assert [stage.status for stage in res.stages] == ["SUCCESS", "SKIPPED", "SKIPPED", "SKIPPED"]
    assert res.stages[0].outputs["factors"] == [2, 7]

def test_prime_input():
    res = run_shor_pipeline(N=17)
    assert res.success is False
    assert "prime" in res.message.lower()

def test_prime_power():
    res = run_shor_pipeline(N=9)
    assert res.success is True
    assert 3 in res.factors

def test_canonical_n15_factorization():
    res = run_shor_pipeline(N=15, a=7, num_counting_qubits=4, shots=2048)
    assert res.success is True
    assert set(res.factors) == {3, 5}
    assert res.recovered_period == 4
    assert res.is_quantum_executed is True
    assert [stage.stage_name for stage in res.stages] == [
        "Stage 1: Classical Precheck",
        "Stage 2: Quantum Period Finding",
        "Stage 3: Period Recovery via Continued Fractions",
        "Stage 4: Factor Extraction via GCD",
    ]
    assert res.stages[1].outputs["execution_mode"] == "qiskit_aer"
    assert res.stages[1].outputs["measurement_counts"] == res.measurement_counts
    assert res.stages[2].inputs["measurement_counts"] == res.measurement_counts
    assert res.stages[2].outputs["candidate_periods"] == [4]
    assert res.stages[3].inputs["candidate_periods"] == [4]
    assert res.stages[3].outputs["verified"] is True
    assert res.factors[0] * res.factors[1] == res.N

def test_emulated_measurement_trace_is_normalized():
    res = run_shor_pipeline(N=21, a=2, num_counting_qubits=4, shots=10)
    measurement_stage = res.stages[1]
    assert measurement_stage.outputs["execution_mode"] == "analytical_emulation"
    assert sum(measurement_stage.outputs["measurement_counts"].values()) == 10
    assert sum(measurement_stage.outputs["probabilities"].values()) == pytest.approx(1.0)

def test_gcd_trivial_factor():
    res = run_shor_pipeline(N=15, a=6)
    assert res.success is True
    assert set(res.factors) == {3, 5}
    assert res.trivial_factor_found is True
