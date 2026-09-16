"""
Meteor - Incident Severity Calculator
Determines incident severity based on the magnitude of an anomaly's
deviation from baseline.
"""

SEVERITY_THRESHOLDS = [
    (50, "CRITICAL"),
    (25, "HIGH"),
    (10, "MEDIUM"),
    (0, "LOW"),
]


def calculate_severity(deviation_percentage: float) -> str:
    """Map an absolute deviation percentage to a severity level."""
    abs_deviation = abs(deviation_percentage)

    for threshold, severity in SEVERITY_THRESHOLDS:
        if abs_deviation >= threshold:
            return severity

    return "LOW"


if __name__ == "__main__":
    test_cases = [-71.67, -12.5, -5.0, 3.2, 60.0]

    for deviation in test_cases:
        severity = calculate_severity(deviation)
        print(f"Deviation: {deviation}% -> Severity: {severity}")