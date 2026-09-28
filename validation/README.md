**Selected cloud: Microsoft Azure**

# Validation record

The repository was prepared for public review on 28 September 2026. The example code is unchanged from the successful test run on 25 September 2026; [checks.json](checks.json) records source hashes, results and their dates.

| Check | Result | Scope |
|---|---|---|
| HTTP health-policy tests | **34 passed**, 0 failed | Previous-step/straddling-window rejection, derived dwell, emergency timing, latency-margin boundaries, severe failures, sparse errors, stale/malformed evidence and recovery deadlines. |
| Example syntax | **Passed** | Three YAML documents and the Azure Policy JSON parsed successfully. |
| Architecture authoring | **9/9 showcase checks per diagram**, zero errors/warnings | Archify checked the source diagrams; their rendered images were visually reviewed on 25 September 2026. The retained source and image bytes are unchanged. |
| Public repository preparation | **Passed** | Relative document/image links resolve. All 28 local links resolve. Gitleaks found zero secrets; retained text, file names and image metadata were checked for personal paths, employer identifiers and email addresses. The diagrams contain scenario labels. |
| Azure acceptance | **Pending** | Deployment, effective permissions and recovery behavior require live acceptance. |

## Reproduce the offline tests

From the repository root, using Python 3.10 or later:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s examples -p 'test_*.py' -v
```

The tests use the standard library and require no Azure credentials. They exercise the policy evaluator, not Azure APIs or the complete production controller.

## Required live acceptance

The [assessment](../Senior-DevOps-Assessment-Azure.md) lists the acceptance cases: actual pinned-template compilation, WIF exchange and RBAC denial, Azure Policy assignment, artifact/signature verification, KQL execution, canary/swap recovery, agent-loss watchdog recovery, database restore and regional failover.

Local tests and diagram review establish only their stated scopes. The sample pipeline requires the proposed protected template/catalog implementation before it can run in Azure DevOps.
