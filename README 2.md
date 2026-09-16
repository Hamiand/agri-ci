# AGRI-CI v0.31 — Executable CI Release Gate

v0.31 turns the previously documented runtime proof into an actual GitHub Actions job.

Added:
- dedicated PostgreSQL 16 + Redis 7 RC1 proof job
- stale-evidence cleanup
- evidence metadata
- uploaded CI proof artifact
- RC1 certificate generated only after all four green files exist
- CI workflow contract tests
- `.rc1-evidence` excluded from source control

This is the point where external CI execution, rather than more speculative backend editing,
should determine the next fix.
