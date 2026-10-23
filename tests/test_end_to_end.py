import pytest
from shor_engine.orchestrator import run_shor_pipeline

def test_even_number_early_exit():
    res = run_shor_pipeline(N=14)
    assert res.success is True
    assert set(res.factors) == {2, 7}
    assert res.is_quantum_executed is False

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

def test_gcd_trivial_factor():
    res = run_shor_pipeline(N=15, a=6)
    assert res.success is True
    assert set(res.factors) == {3, 5}
    assert res.trivial_factor_found is True