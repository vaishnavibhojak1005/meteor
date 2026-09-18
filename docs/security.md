# Security (Phase 27)

## Credentials Management

Database credentials moved from hardcoded values in source code to
environment variables, loaded via `.env` (gitignored) and `python-dotenv`.

**Important:** an earlier version of this project had the PostgreSQL
password hardcoded in `api/main.py` and committed to Git history. Once
discovered, the actual database password was changed (not just the
code) since the old value remains visible in past commits. This is the
correct remediation: rotating a leaked credential, not just removing
it from current files.

**Files updated:** `api/main.py`, `incident_engine/incident_manager.py`,
`lineage/lineage_manager.py`

**Setup for new environments:** copy `.env.example` to `.env` and fill
in real values. `.env` is gitignored and never committed.

## IAM (AWS)

Currently using `AdministratorAccess` on the `meteorAdmins` IAM group,
a deliberate simplification for the learning/development stage (see
Phase 15 setup notes). This should be narrowed to least-privilege
policies before any production use - not yet done, tracked here as a
known gap rather than silently ignored.
