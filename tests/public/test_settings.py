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

def test_settings_defaults_and_owned_float_values():
    settings = PlanningSettings(min_clearance_m=0, max_length_m=8, resolution_m=1)
    assert (settings.min_clearance_m, settings.max_length_m, settings.resolution_m) == (0.0, 8.0, 1.0)
    assert all(type(getattr(settings, name)) is float for name in ("min_clearance_m", "max_length_m", "resolution_m"))
    assert settings.method == "interpolated"
    with pytest.raises(FrozenInstanceError):
        settings.method = "waypoints"


@pytest.mark.parametrize("method", ["waypoints", "interpolated"])
@pytest.mark.parametrize("clearance,length,resolution", [(0.0, 0.01, 0.05), (2.0, 20.0, 1.0)])
def test_settings_accept_contract_boundaries(method, clearance, length, resolution):
    settings = PlanningSettings(clearance, length, resolution, method)
    assert settings.method == method


@pytest.mark.parametrize("field,value", [
    ("min_clearance_m", -0.1), ("min_clearance_m", 2.1),
    ("max_length_m", 0.0), ("max_length_m", -1.0), ("max_length_m", 20.1),
    ("resolution_m", 0.0), ("resolution_m", 0.049), ("resolution_m", 1.001),
])
def test_settings_reject_out_of_range(field, value):
    with pytest.raises(PlanningModelError):
        PlanningSettings(**{field: value})


@pytest.mark.parametrize("field", ["min_clearance_m", "max_length_m", "resolution_m"])
@pytest.mark.parametrize("value", [True, "0.5", 0.5 + 0j, float("nan"), float("inf"), None])
def test_settings_reject_nonordinary_or_nonfinite_numbers(field, value):
    with pytest.raises(PlanningModelError):
        PlanningSettings(**{field: value})


@pytest.mark.parametrize("value", ["INTERPOLATED", "", "rrt", None, ["waypoints"]])
def test_settings_reject_unknown_method(value):
    with pytest.raises(PlanningModelError):
        PlanningSettings(method=value)
