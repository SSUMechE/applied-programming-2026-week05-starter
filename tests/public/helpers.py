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


def make_problem(settings=None, coordinates=None):
    case = supplied_case()
    if coordinates is not None:
        case["path"] = Path([Configuration(point) for point in coordinates])
        case["start"], case["goal"] = case["path"].start, case["path"].goal
    return ParametricPlanningProblem(**case, settings=settings or PlanningSettings())
