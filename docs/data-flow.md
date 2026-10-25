# Data flow and run trace

Each click on **Execute Factorization** calls `run_shor_pipeline` once. That call returns one `ShorExecutionResult`; the stage cards, circuit panel, measurement chart, continued-fraction table, and final status all read from that same result. `ShorStageResult.inputs` and `.outputs` make the handoff between stages explicit. `.details` holds diagnostics for display, not values that downstream stages need.

## Flow

| Stage | Inputs | Outputs passed forward | UI view |
|---|---|---|---|
| 1. Classical precheck | `N`, requested base `a` (optional) | Whether classical handling is complete, resolved base, any immediate factors | Stage card |
| 2. Quantum period finding | `N`, resolved `a`, counting qubits, requested shots | Execution mode, measurement counts, total shots, probabilities | Stage card, circuit tab, distribution tab |
| 3. Period recovery | Measurement counts, counting-qubit count, `N`, `a` | Candidate periods and continued-fraction steps | Stage card and period-recovery tab |
| 4. Factor extraction | `N`, `a`, candidate periods | Factors and a product verification flag | Stage card and final status |

For even numbers, primes, prime powers, invalid inputs, and bases that already share a factor with `N`, stage 1 handles the case. Stages 2–4 are recorded as `SKIPPED` so the trace shows why quantum work did not happen.

## Reading a run

1. Start with the requested input and the base returned by stage 1. A randomly chosen base is recorded as `resolved_base`; downstream stages must use that returned value, not choose another one.
2. Stage 2's `measurement_counts` are the source for the chart and for stage 3. `probabilities` are derived from those counts and normalize to 1. `execution_mode` distinguishes `qiskit_aer` from `analytical_emulation`.
3. Stage 3 parses the measured bit strings as phase-bin values, approximates each phase with continued fractions, and checks candidate orders against `pow(a, r, N) == 1`. Its steps include the fraction, candidate, and explanation shown in the table.
4. Stage 4 tries each accepted period, applies the GCD extraction, and reports factors only when they are non-trivial. `verified` confirms that two returned factors multiply back to `N`.

## Execution modes and limitations

The current implementation executes the gate-level Qiskit/Aer circuit only for `N = 15`. Other accepted odd composites use analytically generated phase bins based on a classically computed order. Those runs are useful for demonstrating the later data-processing steps, but are not quantum circuit executions. The UI should keep this distinction visible.

The analytical histogram distributes shots across bins and assigns any integer remainder to its first bin so the recorded counts sum exactly to the requested shots. Qiskit counts are the simulator's observed counts and may vary by run. Shor factor extraction can also fail for a valid period when it is odd or produces the `-1 mod N` outcome; the trace records the failed extraction instead of claiming success.

## Contract for changes

- Keep stage inputs and outputs JSON-serializable so Streamlit can display them directly.
- Keep `ShorExecutionResult` as the single result object shared by backend and UI.
- If a field name changes, update the backend, UI, and tests together.
- Add a stage record for a new processing step, including its inputs, outputs, status, and reason when skipped or failed.
