"""
Meteor - Statistical Anomaly Detection Tests
Verifies z-score and percentage deviation calculations produce
correct, expected results for known inputs.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from anomaly_engine.statistical import calculate_percentage_deviation, calculate_z_score


def test_percentage_deviation_no_change():
    result = calculate_percentage_deviation(actual=1000, expected=1000)
    assert result == 0.0


def test_percentage_deviation_decrease():
    result = calculate_percentage_deviation(actual=340, expected=1200)
    assert result == pytest_approx(-71.67)


def test_percentage_deviation_increase():
    result = calculate_percentage_deviation(actual=1500, expected=1000)
    assert result == 50.0


def test_z_score_at_mean():
    result = calculate_z_score(current=1000, mean=1000, std=50)
    assert result == 0.0


def test_z_score_severe_outlier():
    result = calculate_z_score(current=340, mean=1001.67, std=35.45)
    assert abs(result) > 2.0


def test_z_score_zero_std_returns_zero():
    result = calculate_z_score(current=1000, mean=1000, std=0)
    assert result == 0.0


def pytest_approx(value, tolerance=0.5):
    """Small helper for approximate float comparison."""
    class Approx:
        def __eq__(self, other):
            return abs(other - value) <= tolerance
    return Approx()