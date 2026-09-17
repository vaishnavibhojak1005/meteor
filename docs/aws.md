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