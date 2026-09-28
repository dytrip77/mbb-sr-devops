"""Pure HTTP health-policy example; no Azure calls or deployment permissions.

Input must be assembled by the trusted controller, not by application code.
stage_started_at is the recorded start of the current traffic step; elapsed time
is derived from it and the controller's evaluation time, now.
The production controller must authenticate queries, bind artifact/target IDs,
persist decision/timer state under the release lock, execute recovery and verify its result.
GO means this health evaluation passed, not approval to deploy on its own.
"""
import argparse
from datetime import datetime, timedelta, timezone
import json
import math
import sys


def number(data, name, *, integer=False, minimum=0):
    value = data[name]
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f"{name}: finite numeric value required")
    if integer and type(value) is not int:
        raise ValueError(f"{name}: integer required")
    if value < minimum:
        raise ValueError(f"{name}: below minimum")
    return value


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp requires timezone")
    return parsed


def decide(observation, *, expected_service, expected_release, now):
    def result(action, reason):
        return {"action": action, "reason": reason}

    try:
        if observation["service"] != expected_service or observation["release_id"] != expected_release:
            return result("HOLD", "Wrong service/release evidence")
        if observation["schema_version"] != 1:
            raise ValueError("unsupported observation schema")
        if type(observation["smoke_passed"]) is not bool:
            raise ValueError("smoke_passed requires boolean")
        if not observation["smoke_passed"]:
            return result("ROLLBACK", "Correctness/security smoke failed")

        gap = number(observation, "telemetry_gap_seconds")
        if gap >= 300:
            return result("ROLLBACK", "Telemetry unavailable for five minutes")
        heartbeat_age = (now - timestamp(observation["heartbeat_at"])).total_seconds()
        window_end = timestamp(observation["window_end"])
        end_age = (now - window_end).total_seconds()
        if not 0 <= heartbeat_age < 120 or not 120 <= end_age <= 420:
            return result("HOLD", "Stale, future or incomplete telemetry window")
        window_seconds = number(observation, "window_seconds")
        if window_seconds != 300:
            return result("HOLD", "Expected five-minute window")

        # The approved controller profile selects dwell. Seven minutes is the
        # hard floor: one five-minute window plus two minutes ingestion allowance.
        dwell = number(observation, "required_dwell_seconds", minimum=420)
        samples = number(observation, "candidate_requests", integer=True)
        errors = number(observation, "candidate_errors", integer=True)
        p95 = number(observation, "candidate_p95_ms")
        if errors > samples:
            raise ValueError("errors exceed request count")
        # A promotion sample floor must not suppress a clear safety failure.
        if errors >= 10 and errors / samples >= 0.20:
            return result("ROLLBACK", "Severe server-error rate")
        if samples >= 20 and p95 >= 2000:
            return result("ROLLBACK", "Severe latency")
        stage_started_at = timestamp(observation["stage_started_at"])
        elapsed = (now - stage_started_at).total_seconds()
        # Derive the timer from the recorded step boundary instead of trusting
        # a second, potentially inconsistent elapsed-time field.
        if elapsed < 0:
            return result("HOLD", "Future stage start")
        baseline_samples = number(observation, "baseline_requests", integer=True)
        if min(samples, baseline_samples) < 200:
            return result("ROLLBACK" if elapsed >= 1800 else "HOLD", "Insufficient cohort samples")

        baseline_errors = number(observation, "baseline_errors", integer=True)
        if errors > samples or baseline_errors > baseline_samples:
            raise ValueError("errors exceed request count")
        baseline_p95 = number(observation, "baseline_p95_ms", minimum=0.001)
        if observation["baseline_source"] not in ("live", "preswitch"):
            raise ValueError("invalid baseline source")
        baseline_age = (now - timestamp(observation["baseline_at"])).total_seconds()
        if not 0 <= baseline_age <= 3600:
            return result("HOLD", "Baseline is stale or future-dated")
        # This is an operational threshold with an error-count floor, not a
        # statistical confidence claim. Re-reading a window adds no evidence.
        error_regression = errors >= 5 and (
            errors / samples > 0.01
            or errors / samples - baseline_errors / baseline_samples > 0.005)
        relative_latency_regression = (
            p95 > 1.2 * baseline_p95 and p95 - baseline_p95 >= 50)
        unhealthy = error_regression or p95 > 500 or relative_latency_regression
        if unhealthy:
            return result("ROLLBACK", "Qualified HTTP error/latency window breached")
        if errors / samples > 0.01:
            return result("ROLLBACK" if elapsed >= 1800 else "HOLD",
                          "Absolute error threshold exceeded with sparse failures")
        # Previous-step evidence can reveal a safety failure, but cannot promote
        # this step. Every request in the promotion window must follow its start.
        if window_end - timedelta(seconds=window_seconds) < stage_started_at:
            return result("HOLD", "Telemetry window begins before current stage")
        if elapsed < dwell:
            return result("HOLD", "Minimum dwell not complete")
        return result("GO", "HTTP health, samples, freshness and dwell passed")
    except (KeyError, ValueError, TypeError, AttributeError, OverflowError) as exc:
        return result("HOLD", f"Invalid evidence: {exc}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("observation")
    parser.add_argument("--service", required=True)
    parser.add_argument("--release", required=True)
    parser.add_argument("--now", help="ISO timestamp for reproducible offline checks")
    args = parser.parse_args()
    try:
        with open(args.observation, encoding="utf-8") as stream:
            observation = json.load(stream)
        now = timestamp(args.now) if args.now else datetime.now(timezone.utc)
        decision = decide(observation, expected_service=args.service, expected_release=args.release, now=now)
    except (OSError, ValueError) as exc:
        decision = {"action": "HOLD", "reason": f"Cannot load evidence: {exc}"}
    print(json.dumps(decision))
    return {"GO": 0, "HOLD": 20, "ROLLBACK": 30}[decision["action"]]


if __name__ == "__main__":
    sys.exit(main())
