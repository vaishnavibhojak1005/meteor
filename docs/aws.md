# AWS Resources

## S3 Data Lake

**Bucket name:** meteor-data-lake-397781772486
**Region:** us-east-1

### Structure
- raw/ - landing zone for unprocessed data
- processed/ - cleaned/transformed data (PySpark output, Phase 19)
- curated/ - business-ready datasets
- profiles/ - stored profiling results
- baselines/ - historical baseline snapshots
- quarantine/ - data that failed validation

### Cost notes
- S3 storage at this scale (KB-MB range) is within AWS Free Tier.
- Zero-Spend Budget alert configured to notify at $0.01 spend.

## AWS Glue (Phase 20) — Blocked, Pending Account Restriction

**Status:** IAM role, policies, and ETL script are complete and committed.
Job creation is currently blocked by AWS with:
`AccessDeniedException: Account <id> is denied access`

This is a known AWS pattern for new accounts — Glue job creation can be
temporarily restricted for a period after account creation, unrelated to
IAM configuration. Verified via `aws glue get-jobs` (succeeds, read-only)
vs `aws glue create-job` (fails) — confirming this is an account-level
restriction, not a permissions issue.

**Resources already built and ready:**
- IAM role: `meteor-glue-role` (with Glue service policy, S3 read, S3 write)
- ETL script: `glue_jobs/orders_etl.py`, uploaded to
  `s3://meteor-data-lake-397781772486/glue-scripts/orders_etl.py`

**Next step:** retry `aws glue create-job` in a future session; if still
blocked, contact AWS Support for a new-account service limit review.

## Kinesis (Phase 21) — Tested and Torn Down

Created a real Kinesis Data Stream (`meteor-orders-stream`, 1 shard),
verified a full producer -> consumer cycle with `boto3`:
- Producer sent 10 simulated order events, partitioned by city
- Consumer read all 10 back in order via shard iterator (TRIM_HORIZON)
- Amount-based anomaly detection correctly flagged 1/10 events

Stream deleted immediately after testing to avoid ongoing per-shard
hourly cost (Kinesis is not part of AWS free tier, unlike S3/Lambda).

**Scripts:** `streaming/kinesis_producer.py`, `streaming/kinesis_consumer.py`

## Athena (Phase 23) — Working

Created Glue Data Catalog database (`meteor_db`) and an external table
(`orders_processed`) pointing to S3 Parquet data. Ran a real SQL
aggregation query (GROUP BY payment_status) — succeeded in 549ms,
scanning only 344 bytes (Parquet's columnar format meant only the
queried column was read). Cost: effectively $0.

Note: Glue Data Catalog operations work fine on this account; only
Glue ETL *job creation* is currently blocked (see Phase 20 section).