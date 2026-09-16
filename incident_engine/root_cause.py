"""
Meteor - Root Cause Engine
Deterministic, rule-based root cause analysis. Explainable by design -
no LLM involved. Confidence reflects how well the observed symptoms
match a known failure pattern.
"""

def analyze_root_cause(
    volume_anomaly: bool = False,
    freshness_failure: bool = False,
    schema_drift: bool = False,
    null_spike: bool = False,
    duplicate_spike: bool = False,
) -> dict:
    """Determine the most likely root cause from a combination of symptoms."""

    # Rule 1: Volume drop + stale data => classic upstream ingestion failure
    if volume_anomaly and freshness_failure:
        return {
            "root_cause": "Upstream ingestion failure",
            "confidence": 92,
            "reasoning": "Significant volume drop combined with stale data strongly suggests the upstream source stopped sending data.",
        }

    # Rule 2: Volume drop alone => partial ingestion failure, less certain
    if volume_anomaly and not freshness_failure:
        return {
            "root_cause": "Partial ingestion failure or upstream filtering change",
            "confidence": 65,
            "reasoning": "Volume dropped but data is still fresh, suggesting a filtering or partial delivery issue rather than a full outage.",
        }

    # Rule 3: Schema drift alone => upstream schema change
    if schema_drift and not volume_anomaly:
        return {
            "root_cause": "Upstream schema change",
            "confidence": 85,
            "reasoning": "Column types changed while volume remained normal, indicating the source system altered its data format.",
        }

    # Rule 4: Null spike + duplicate spike => pipeline processing bug
    if null_spike and duplicate_spike:
        return {
            "root_cause": "Pipeline processing bug (retry or merge logic)",
            "confidence": 70,
            "reasoning": "Simultaneous null and duplicate spikes suggest a bug in retry or merge logic within the pipeline itself, not the source.",
        }

    # Rule 5: Freshness failure alone => stalled pipeline job
    if freshness_failure and not volume_anomaly:
        return {
            "root_cause": "Stalled or delayed pipeline job",
            "confidence": 60,
            "reasoning": "Data is stale but volume is normal, suggesting the pipeline job itself is delayed rather than the source failing.",
        }

    # Default: no strong pattern matched
    return {
        "root_cause": "Unknown - insufficient pattern match",
        "confidence": 20,
        "reasoning": "Observed symptoms do not match a known failure pattern strongly enough for a confident conclusion.",
    }


if __name__ == "__main__":
    print("=== SCENARIO: Volume anomaly + Freshness failure (plan's main example) ===")
    result = analyze_root_cause(volume_anomaly=True, freshness_failure=True)
    print(result)

    print("\n=== SCENARIO: Volume drop only ===")
    result = analyze_root_cause(volume_anomaly=True)
    print(result)

    print("\n=== SCENARIO: Schema drift only ===")
    result = analyze_root_cause(schema_drift=True)
    print(result)

    print("\n=== SCENARIO: No clear symptoms ===")
    result = analyze_root_cause()
    print(result)