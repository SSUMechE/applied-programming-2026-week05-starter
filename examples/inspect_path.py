"""Run before editing TODOs: python examples/inspect_path.py from repository root."""
from ap_week05 import (
    supplied_case, sample_path, path_metrics, constraint_margins,
)

MIN_CLEARANCE_M = 0.5
MAX_LENGTH_M = 9.0
RESOLUTION_M = 0.5
METHOD = "interpolated"

case = supplied_case()
samples = sample_path(
    case["path"], resolution_m=RESOLUTION_M, method=METHOD,
)
metrics = path_metrics(case["path"], samples, case["obstacle"])
margins = constraint_margins(
    metrics["length_m"], metrics["clearance_m"],
    MIN_CLEARANCE_M, MAX_LENGTH_M,
)
for name, value in metrics.items():
    print(f"{name}: {value:.6f}")
for name, value in margins.items():
    print(f"{name}: {value:.6f}")
print("feasible:", all(value >= 0.0 for value in margins.values()))
print("sample_count:", len(samples))
