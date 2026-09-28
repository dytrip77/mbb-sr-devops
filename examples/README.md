**Selected cloud: Microsoft Azure**

# Reference examples

These files support the assessment. They are deliberately scoped examples, not a deployable landing zone or an existing `pipeline-tools` release.

| File | Status and use |
|---|---|
| `azure-pipelines.yml` | Proposed consumer interface. Requires the actual protected root template and catalog implementation; `v1.4.0` is illustrative. |
| `release.yaml` | Proposed app-owned requirements shown in the architecture; validated against the trusted platform catalog. |
| `release-contract.yaml` | Proposed manifest format. Replace placeholders using trusted collectors; never accept self-asserted results. |
| `storage-security.policy.json` | Azure Policy definition example; JSON checked locally. Test aliases and assignment behavior in a disposable Azure RG before rollout. Does not remediate existing resources or configure retention. |
| `release-health.kql` | Azure Monitor/Application Insights query example, not executed against a workspace. Assumes application instrumentation and unsampled customer request telemetry. |
| `health_gate.py` | Runnable, dependency-free subset of the shared HTTP policy: freshness, sample volume, smoke, HTTP errors/latency, dwell and recovery decisions. |
| `test_health_gate.py` | Offline tests including stale/malformed/wrong-release evidence, failed smoke, regression and insufficient samples. |

Run locally from the repository root with Python 3.10 or later (standard library only):

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s examples -p 'test_*.py' -v
```

The health gate's exit codes are 0 = GO, 20 = HOLD, 30 = ROLLBACK. It does not change Azure resources. A production coordinator must authenticate its inputs, check business-success and infrastructure metrics, handle API errors, bind resource/config/artifact IDs, retain an approved preswitch baseline, and persist decision/timer state under an exclusive lock. `required_dwell_seconds` is selected by the trusted profile, not the app. At 100% traffic the fifteen-minute critical bake uses a recent retained baseline; exhausted baseline freshness blocks progression.

The HTTP policy first catches severe failures (at least ten errors and ≥20% error rate, or twenty requests and p95 ≥2,000 ms), before the promotion sample floor and baseline checks. Qualified ordinary error regressions require at least five failures and 200 requests per cohort. Fewer failures above the absolute threshold hold until more evidence or the thirty-minute deadline. Ordinary latency recovery requires p95 >500 ms, or both p95 >1.2× baseline and a slowdown of at least 50 ms, with 200 requests per cohort. One qualified bad window triggers recovery; overlapping five-minute windows never increment a confirmation counter. This is an operational threshold policy, not a formal significance test.

| Protected profile | Canary-step dwell | Full-traffic bake |
|---|---|---|
| Critical HTTP | 600 seconds | 900 seconds |
| Standard HTTP blue-green | Not applicable | 600 seconds |
| Approved emergency HTTP | 420 seconds | 600 seconds |

The controller selects these values from the approved profile, binds them to the release record and supplies `required_dwell_seconds`; application configuration cannot lower the profile. The controller records `stage_started_at` when the new traffic state is confirmed and resets it for each step/bake. The gate derives elapsed time from this timestamp, and `GO` requires `window_end - window_seconds >= stage_started_at`. Earlier/overlapping windows cannot approve progression. The hard floor is 420 seconds: a full five-minute window wholly within the current stage plus two minutes ingestion allowance; polling/late data may extend it. Custom profiles need acceptance tests before catalog admission.

Duplicate observations and recovery requests are idempotent. Incomplete/malformed evidence starts or continues the missing-telemetry timer. A watchdog recovers after five minutes without valid observations, including input parsing failures. After an Azure mutation times out, reconcile actual state before retrying, especially for swaps.

The `prod-smoke` pool runs approved application-owned smoke bundles with private endpoint connectivity, no Azure service connection, no host managed identity and no deployment credentials. Its job token/repository scope and egress are restricted; any authenticated test account has only test-user privileges.

Recommended coordinator state contract:

```text
LOCKED → VERIFY → PREPARE_CANDIDATE → SMOKE → EXPOSURE_STEP → EVALUATE
EVALUATE → next EXPOSURE_STEP | BAKE | HOLD | RECOVER
HOLD → EVALUATE | RECOVER (deadline)
BAKE → VERIFIED_SUCCESS | RECOVER
RECOVER → VERIFY_OLD_VERSION → VERIFIED_RECOVERY | INCIDENT
```

All transitions append an idempotent record containing state version, release ID, target, observed runtime version, action and evidence URI. A lease/fencing token ensures the watchdog and pipeline cannot both mutate traffic. Recovery retains the lock until the application/database state is known.

For the database variant, use one Azure Pipelines stage per protected database domain/tier with `lockBehavior: sequential` and ordered **prepare → migrate → rollout → bake** jobs. Binding every writer to the same environment is required; setting the YAML property without the external exclusive-lock check does not create a lock.

Provider references: [Azure Policy](https://learn.microsoft.com/en-us/azure/governance/policy/concepts/definition-structure-basics), [Storage policy reference](https://learn.microsoft.com/en-us/azure/storage/common/policy-reference), [Blob anonymous access policy](https://learn.microsoft.com/en-us/azure/storage/blobs/anonymous-read-access-prevent), [AppRequests schema](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/apprequests).
