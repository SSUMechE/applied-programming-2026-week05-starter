"""Compute the Assignment result. This entry point never renders or writes files."""
from . import ParametricPlanningProblem, PlanningSettings, supplied_case


def main():
    case = supplied_case()
    problem = ParametricPlanningProblem(
        start=case["start"],
        goal=case["goal"],
        bounds=case["bounds"],
        obstacle=case["obstacle"],
        path=case["path"],
        settings=PlanningSettings(),
    )
    result = problem.evaluate()
    print(f"length_m: {result.length_m:.6f}")
    print(f"clearance_m: {result.clearance_m:.6f}")
    print(f"total_turn_rad: {result.total_turn_rad:.6f}")
    print(f"clearance_margin_m: {result.clearance_margin_m:.6f}")
    print(f"length_margin_m: {result.length_margin_m:.6f}")
    print(f"feasible: {result.feasible}")
    print(f"method: {result.method}")
    print(f"sample_count: {result.sample_count}")


if __name__ == "__main__":
    main()
