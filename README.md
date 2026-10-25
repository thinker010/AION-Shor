# ⚛️ Shor's Algorithm Interactive Demonstrator
**AION-IA Quantum Computing Internship — Task 04**

An interactive, end-to-end demonstrator of Peter Shor's quantum integer factorization algorithm using Python, Qiskit, and Streamlit.

---

## 👥 Team Members & Responsibilities
* **Rakshith (Task Lead & Backend):** Algorithm architecture, Qiskit quantum circuit design, classical preprocessor, and orchestration pipeline.
* **Samanvi (UI/UX & Frontend):** Streamlit user interface, visual layout, interactive dashboards, and design hierarchy.
* **Punith (Data Flow, Visualisation & Testing):** Pipeline tracing, test case suite, documentation, and limitations analysis.

---

## 🚀 Key Features
* **Classical Preprocessing:** Handles evens, primes, and prime powers before quantum execution.
* **Qiskit Aer Quantum Circuit:** Native gate-level simulation for canonical composite $N = 15$ with controlled modular exponentiation unitaries and Inverse QFT ($\text{QFT}^\dagger$).
* **Quantum Phase Estimation (QPE):** Measures counting register phase states.
* **Continued Fractions Algorithm:** Recovers candidate orders $r$ from quantum phase measurements.
* **Classical Factor Extraction:** Computes $\gcd(a^{r/2} \pm 1, N)$ to extract non-trivial factors.
* **Interactive Probability Visualisation:** Dynamic Plotly distribution of measured phase states.

## 🔄 Data Flow Trace

Each run returns one `ShorExecutionResult`. Its ordered stage records expose the inputs and outputs passed between classical precheck, period finding, continued-fraction recovery, and factor extraction. The Streamlit stage view renders those handoffs, and the circuit, chart, period table, and final factors use data from that same run. See [docs/data-flow.md](docs/data-flow.md) for the stage contract and execution-mode limitations.

---

## 📦 Setup & Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/thinker010/AION-Shor.git](https://github.com/thinker010/AION-Shor.git)
cd AION-Shor
