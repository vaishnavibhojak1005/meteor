"""
Meteor - Statistical Anomaly Detection
Compares current dataset metrics against historical baselines
using percentage deviation and z-score analysis.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quality_engine.baseline import load_history, compute_baseline_stats

Z_SCORE_THRESHOLD = 2.0


def calculate_percentage_deviation(actual: float, expected: float) -> float:
    """Calculate percentage deviation of actual from expected."""
    if expected == 0:
        return 0.0
    return round(((actual - expected) / expected) * 100, 2)


def calculate_z_score(current: float, mean: float, std: float) -> float:
    """Calculate how many standard deviations current is from the mean."""
    if std == 0:
        return 0.0
    return round((current - mean) / std, 2)


def detect_volume_anomaly(dataset_name: str, current_record_count: int) -> dict:
    """Detect whether current_record_count is anomalous vs historical baseline."""
    history = load_history(dataset_name)
    baseline = compute_baseline_stats(history, "record_count")

    if baseline.get("status") == "NO_HISTORY":
        return {"status": "NO_HISTORY", "message": "Not enough historical data to compare."}

    mean = baseline["mean"]
    std = baseline["std"]

    deviation_pct = calculate_percentage_deviation(current_record_count, mean)
    z_score = calculate_z_score(current_record_count, mean, std)

    is_anomaly = abs(z_score) > Z_SCORE_THRESHOLD

    return {
        "dataset": dataset_name,
        "current_record_count": int(current_record_count),
        "expected_mean": float(mean),
        "expected_std": float(std),
        "deviation_percentage": float(deviation_pct),
        "z_score": float(z_score),
        "threshold": Z_SCORE_THRESHOLD,
        "is_anomaly": bool(is_anomaly),
        "status": "ANOMALY" if is_anomaly else "NORMAL",
    }


if __name__ == "__main__":
    print("=== TESTING: NORMAL VOLUME (1000 records) ===")
    result_normal = detect_volume_anomaly("orders", 1000)
    print(result_normal)

    print("\n=== TESTING: SEVERE VOLUME DROP (340 records) ===")
    result_anomaly = detect_volume_anomaly("orders", 340)
    print(result_anomaly)

    print("\n=== TESTING: MILD FLUCTUATION (1020 records) ===")
    result_mild = detect_volume_anomaly("orders", 1020)
    print(result_mild)