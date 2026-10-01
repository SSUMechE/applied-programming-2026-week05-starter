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

def test_evaluation_shared_detour_returns_all_fields():
    result = make_problem().evaluate()
    assert isinstance(result, EvaluationResult)
    assert result.length_m == 8.0 and result.clearance_m == 1.5
    assert result.total_turn_rad == pytest.approx(math.pi)
    assert result.clearance_margin_m == 1.0 and result.length_margin_m == 1.0
    assert result.feasible is True
    assert result.method == "interpolated" and result.sample_count == 17


def test_evaluation_zero_margins_are_feasible():
    result = make_problem(PlanningSettings(1.5, 8.0)).evaluate()
    assert result.clearance_margin_m == 0.0 and result.length_margin_m == 0.0
    assert result.feasible is True


@pytest.mark.parametrize("settings,negative_field", [
    (dict(min_clearance_m=1.6), "clearance_margin_m"),
    (dict(max_length_m=7.0), "length_margin_m"),
])
def test_evaluation_one_negative_margin_is_infeasible(settings, negative_field):
    result = make_problem(PlanningSettings(**settings)).evaluate()
    assert getattr(result, negative_field) < 0.0
    assert result.feasible is False


def test_evaluation_two_negative_margins_are_infeasible():
    result = make_problem(PlanningSettings(1.6, 7.0)).evaluate()
    assert result.clearance_margin_m < 0 and result.length_margin_m < 0
    assert result.feasible is False


def test_evaluation_does_not_round_small_negative_margin():
    result = make_problem(PlanningSettings(1.5 + 1e-12, 8.0)).evaluate()
    assert result.clearance_margin_m < 0 and result.feasible is False


def test_evaluation_method_changes_observation_not_path():
    coordinates = [(0, 0), (4, 0)]
    endpoints = make_problem(PlanningSettings(method="waypoints"), coordinates).evaluate()
    interpolated = make_problem(PlanningSettings(method="interpolated"), coordinates).evaluate()
    assert endpoints.length_m == interpolated.length_m == 4.0
    assert endpoints.total_turn_rad == interpolated.total_turn_rad == 0.0
    assert endpoints.clearance_m == 1.5 and endpoints.sample_count == 2
    assert interpolated.clearance_m == -0.5 and interpolated.sample_count == 9
    assert endpoints.feasible is True and interpolated.feasible is False


def test_evaluation_resolution_changes_sample_count():
    coarse = make_problem(PlanningSettings(resolution_m=1.0)).evaluate()
    fine = make_problem(PlanningSettings(resolution_m=0.25)).evaluate()
    assert coarse.sample_count == 9 and fine.sample_count == 33
    assert coarse.length_m == fine.length_m == 8.0
    assert coarse.total_turn_rad == fine.total_turn_rad


def test_evaluation_no_print_and_no_mutation(capsys):
    problem = make_problem()
    before = problem.path.as_array().copy()
    first, second = problem.evaluate(), problem.evaluate()
    assert first == second
    np.testing.assert_array_equal(problem.path.as_array(), before)
    assert capsys.readouterr().out == ""
    with pytest.raises(FrozenInstanceError):
        first.feasible = False
