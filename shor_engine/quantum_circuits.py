import numpy as np
import math
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

def create_modular_exp_n15(a: int) -> QuantumCircuit:
    """Returns the unitary circuit for f(x) = a^x mod 15 on 4 target qubits."""
    qc = QuantumCircuit(4, name=f"{a}_mod_15")
    if a in [2, 13]:
        qc.swap(0, 1)
        qc.swap(1, 2)
        qc.swap(2, 3)
        if a == 13:
            qc.x([0, 1, 2, 3])
    elif a in [7, 8]:
        qc.swap(2, 3)
        qc.swap(1, 2)
        qc.swap(0, 1)
        if a == 7:
            qc.x([0, 1, 2, 3])
    elif a in [4, 11]:
        qc.swap(0, 2)
        qc.swap(1, 3)
        if a == 11:
            qc.x([0, 1, 2, 3])
    elif a == 14:
        qc.x([0, 1, 2, 3])
    return qc

def build_qft_dagger(n: int) -> QuantumCircuit:
    """Constructs Inverse QFT on n qubits."""
    qc = QuantumCircuit(n, name="QFT_dagger")
    for j in range(n // 2):
        qc.swap(j, n - j - 1)
    for j in range(n):
        for m in range(j):
            qc.cp(-np.pi / float(2 ** (j - m)), m, j)
        qc.h(j)
    return qc

def build_shor_circuit_n15(a: int, num_counting_qubits: int = 4) -> QuantumCircuit:
    """Assembles complete Shor's order finding circuit for N = 15."""
    n_count = num_counting_qubits
    qc = QuantumCircuit(n_count + 4, n_count)

    # 1. Superposition on counting register
    for q in range(n_count):
        qc.h(q)

    # 2. Target register initialized to |1> (qubit index n_count corresponds to target qubit 0)
    qc.x(n_count)

    # 3. Controlled Modular Exponentiation
    for q in range(n_count):
        power = 2 ** q
        mod_exp_gate = create_modular_exp_n15(pow(a, power, 15)).to_gate()
        mod_exp_gate.name = f"{a}^{power}_mod15"
        c_mod_exp = mod_exp_gate.control(1)
        qc.append(c_mod_exp, [q] + list(range(n_count, n_count + 4)))

    qc.barrier()

    # 4. Inverse QFT
    qft_dag = build_qft_dagger(n_count)
    qc.append(qft_dag, range(n_count))

    qc.barrier()

    # 5. Measure counting register
    qc.measure(range(n_count), range(n_count))
    return qc

def simulate_circuit(qc: QuantumCircuit, shots: int = 2048) -> dict:
    """
    Decomposes/transpiles composite gates into simulator primitives
    and executes using AerSimulator.
    """
    simulator = AerSimulator()
    # Decompose custom gates into basis gates so Aer can assemble them
    transpiled_qc = transpile(qc, simulator)
    job = simulator.run(transpiled_qc, shots=shots)
    result = job.result()
    return result.get_counts()