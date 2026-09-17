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
