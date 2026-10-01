"""Published Week 5 contract tests. Provided, do not edit."""
from dataclasses import FrozenInstanceError, replace
import json
import math
import numpy as np
import pytest
from ap_week05 import (
    Configuration, ConfigurationBounds, Path, Obstacle, PlanningModelError,
    PlanningSettings, ParametricPlanningProblem, EvaluationResult,
    supplied_case, sample_path, path_metrics, constraint_margins,
)


from .helpers import make_problem

def test_provided_support_runs_before_student_todos():
    case = supplied_case()
    samples = sample_path(case["path"], 0.5, "interpolated")
    metrics = path_metrics(case["path"], samples, case["obstacle"])
    assert metrics["length_m"] == 8.0 and metrics["clearance_m"] == 1.5
    assert constraint_margins(8.0, 1.5, 0.5, 9.0) == {"clearance_margin_m": 1.0, "length_margin_m": 1.0}


def test_provided_values_own_their_input_and_arrays():
    values = [0.0, 0.0]
    first = Configuration(values)
    points = [first, Configuration((1, 0))]
    path = Path(points)
    values[0] = 50.0
    points.clear()
    returned = path.as_array()
    returned[0, 0] = 60.0
    assert first.values == (0.0, 0.0) and len(path.waypoints) == 2
