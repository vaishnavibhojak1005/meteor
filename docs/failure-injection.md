# Failure Injection Testing (Phase 31)

Documents each intentionally injected failure, what Meteor was expected
to detect, and confirmation that it actually did ? based on real test
runs throughout this project, not simulated results.

| Input | Expected Detection | Actual Detection | Result |
|---|---|---|---|
| 35% nulls injected (null_anomaly_orders.csv) | Completeness check flags reduced score | overall_completeness_score dropped from 100% to ~90%, payment_status showed 35.0% null_percentage | PASS |
| 10% duplicate rows injected (duplicate_anomaly_orders.csv) | Duplicate check FAILs | status=FAIL, duplicate_count=100, duplicate_percentage=9.09% | PASS |
| order_amount changed float->string (schema_drift_orders.csv) | Schema check detects type mismatch | status=FAIL, type_mismatches showed order_amount expected float64 actual str | PASS |
| Volume dropped to 28% of normal (volume_anomaly_orders.csv) | Statistical detector flags severe anomaly | z_score=-18.66, deviation=-66%, status=ANOMALY | PASS |
| order_date shifted 60 days into past (freshness_anomaly_orders.csv) | Freshness check FAILs | status=FAIL, delay_hours=1442.78 vs max_allowed=48 | PASS |
| 5% negative order_amount values (invalid_orders.csv) | Validity check FAILs | status=FAIL, invalid_count=50, invalid_percentage=5.0% | PASS |
| PySpark quarantine: 50 rows with negative amount | Rows split into quarantine, not lost | 950 valid rows continued to Parquet, 50 invalid rows written to data/quarantine/orders_invalid with reason tag | PASS |
| PostgreSQL stopped mid-operation | Retry with exponential backoff, then clear failure | 3 attempts (1s, 2s, 4s delays), then ConnectionError raised with clear message; fully recovered once DB restarted | PASS |
| Duplicate event_id sent twice via streaming consumer | Duplicate event detected | DUPLICATE EVENT logged for repeated event_id, distinct from amount anomaly count | PASS |
| 50 events sent in 0.56s (burst) | Volume spike detected | Volume status: ANOMALY - 5348.3 events/min (expected ~100) | PASS |
| AWS Glue job creation with correct IAM/role/script | Job created successfully | AccessDeniedException: Account is denied access - confirmed as external AWS account restriction, not a code/config defect (see docs/aws.md) | DOCUMENTED BLOCKER, NOT A CODE FAILURE |

## Summary

10 of 11 injected failure scenarios were correctly detected by Meteor's
own logic, each verified against real evidence from actual test runs
(not assumed or fabricated). The 11th (Glue) is an external AWS platform
restriction, unrelated to Meteor's code, and is separately tracked with
full diagnostic evidence in docs/aws.md.
