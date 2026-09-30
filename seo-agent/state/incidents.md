# HERMES Incidents Log

## Status

No incidents recorded yet.

## Incident Format

```
Date: YYYY-MM-DD
Type: SEO regression / deployment failure / data corruption / automation failure
Severity: P0 / P1 / P2 / P3
Affected URLs: ...
Evidence: ...
Action: DETECT → DIAGNOSE → FIX → TEST → RETEST → DEPLOY → VERIFY → REPORT
Status: open / resolved / rolled back
```

## Rollback Procedure

1. Identify the change (git diff)
2. Revert the change (git revert)
3. Test the revert
4. Verify production
5. Report the incident
6. Document the lesson
