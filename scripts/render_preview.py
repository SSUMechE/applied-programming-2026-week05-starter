"""Optional inspection only. Run after TODOs 1 and 2, independently of evaluate."""
from ap_week05 import ParametricPlanningProblem, PlanningSettings, supplied_case
from ap_week05.visualization import write_svg

problem = ParametricPlanningProblem(**supplied_case(), settings=PlanningSettings())
output = write_svg(problem.to_plot_data(), "artifacts/path_preview.svg")
print("Wrote", output.as_posix())
