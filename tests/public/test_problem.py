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

def test_problem_keeps_supplied_objects():
    case = supplied_case()
    settings = PlanningSettings()
    problem = ParametricPlanningProblem(**case, settings=settings)
    assert problem.path is case["path"] and problem.settings is settings
    assert problem.start.dimension == 2
    assert problem.path.length() == 8.0


@pytest.mark.parametrize("field", ["start", "goal", "bounds", "obstacle", "path", "settings"])
def test_problem_reject_wrong_object_type(field):
    case = dict(supplied_case(), settings=PlanningSettings())
    case[field] = None
    with pytest.raises(PlanningModelError):
        ParametricPlanningProblem(**case)


@pytest.mark.parametrize("field", ["start", "goal", "bounds", "path"])
def test_problem_reject_three_dimensions(field):
    case = dict(supplied_case(), settings=PlanningSettings())
    if field == "bounds":
        case[field] = ConfigurationBounds(Configuration((-1, -1, -1)), Configuration((5, 3, 1)))
    elif field == "path":
        case[field] = Path([Configuration((0, 0, 0)), Configuration((4, 0, 0))])
    else:
        case[field] = Configuration((0, 0, 0))
    with pytest.raises(PlanningModelError):
        ParametricPlanningProblem(**case)


@pytest.mark.parametrize("field,value", [("start", (0, 1)), ("goal", (4, 1))])
def test_problem_reject_endpoint_mismatch(field, value):
    case = dict(supplied_case(), settings=PlanningSettings())
    case[field] = Configuration(value)
    with pytest.raises(PlanningModelError):
        ParametricPlanningProblem(**case)


def test_problem_accepts_inclusive_workspace_boundary():
    problem = make_problem(coordinates=[(-1, -1), (5, 3)])
    assert problem.path.start.values == (-1.0, -1.0)


@pytest.mark.parametrize("coordinates", [
    [(0, 0), (0, 3.1), (4, 0)],
    [(-1.1, 0), (4, 0)],
    [(0, 0), (5.1, 0)],
])
def test_problem_rejects_out_of_bounds(coordinates):
    with pytest.raises(PlanningModelError):
        make_problem(coordinates=coordinates)


def test_problem_rejects_consecutive_duplicates():
    with pytest.raises(PlanningModelError):
        make_problem(coordinates=[(0, 0), (0, 0), (4, 0)])


def test_problem_accepts_nondegenerate_closed_loop():
    problem = make_problem(coordinates=[(0, 0), (0, 2), (4, 2), (0, 0)])
    assert problem.start == problem.goal


def test_problem_accepts_32_waypoints_but_rejects_33():
    problem = make_problem(coordinates=[(index / 10, 1) for index in range(32)])
    assert len(problem.path.waypoints) == 32
    with pytest.raises(PlanningModelError):
        make_problem(coordinates=[(index / 10, 1) for index in range(33)])
