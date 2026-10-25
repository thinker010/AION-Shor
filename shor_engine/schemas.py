from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

@dataclass
class ContinuedFractionStep:
    convergent_fraction: str
    phase_estimate: float
    candidate_r: int
    is_valid_period: bool
    explanation: str

@dataclass
class ShorStageResult:
    stage_name: str
    status: str  # "SUCCESS", "SKIPPED", "FAILED", "INFO"
    summary: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ShorExecutionResult:
    # Input parameters
    N: int
    a: int
    num_counting_qubits: int
    shots: int
    is_quantum_executed: bool

    # Stage-by-stage diagnostics
    stages: List[ShorStageResult] = field(default_factory=list)

    # Classical preprocessing
    trivial_factor_found: bool = False
    factors: List[int] = field(default_factory=list)

    # Quantum circuit & measurement
    circuit_ascii: str = ""
    measurement_counts: Dict[str, int] = field(default_factory=dict)
    probabilities: Dict[str, float] = field(default_factory=dict)

    # Post-processing / Continued fractions
    cf_steps: List[ContinuedFractionStep] = field(default_factory=list)
    recovered_period: Optional[int] = None
    period_found: bool = False

    # Execution summary
    success: bool = False
    message: str = ""
