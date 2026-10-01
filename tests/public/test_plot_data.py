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

def test_plot_data_schema_and_plain_lists():
    data = make_problem().to_plot_data()
    assert set(data) == {"path_xy", "samples_xy", "obstacle_center_xy", "obstacle_radius_m", "labels"}
    assert data["path_xy"] == [[0.0, 0.0], [0.0, 2.0], [4.0, 2.0], [4.0, 0.0]]
    assert len(data["samples_xy"]) == 17
    assert data["obstacle_center_xy"] == [2.0, 0.0] and data["obstacle_radius_m"] == 0.5
    assert data["labels"] == ["start", "waypoint_1", "waypoint_2", "goal"]
    assert type(data["path_xy"]) is list and type(data["path_xy"][0]) is list
    assert json.loads(json.dumps(data)) == data


def test_plot_data_is_fresh_and_does_not_modify_objects():
    problem = make_problem()
    first, second = problem.to_plot_data(), problem.to_plot_data()
    first["path_xy"][0][0] = 99.0
    first["samples_xy"][0][0] = 88.0
    first["obstacle_center_xy"][0] = 77.0
    first["labels"][0] = "changed"
    assert second == problem.to_plot_data()
    assert second["path_xy"][0] == [0.0, 0.0]
    assert problem.path.start.values == (0.0, 0.0)


def test_plot_data_respects_waypoints_method():
    data = make_problem(PlanningSettings(method="waypoints")).to_plot_data()
    assert data["samples_xy"] == data["path_xy"]
    assert data["samples_xy"] is not data["path_xy"]


def test_plot_data_does_not_evaluate_or_render(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("plot-data preparation must not evaluate or render")
    import ap_week05.visualization as visualization
    monkeypatch.setattr(ParametricPlanningProblem, "evaluate", forbidden)
    monkeypatch.setattr(visualization, "write_svg", forbidden)
    assert len(make_problem().to_plot_data()["samples_xy"]) == 17
