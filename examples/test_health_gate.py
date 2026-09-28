"""Negative-path checks for the supplied policy example, not Azure acceptance."""
import copy
from datetime import datetime, timezone
import unittest

from health_gate import decide


class HealthPolicyTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc)
        self.observation = {
            "schema_version": 1, "service": "orders-api", "release_id": "r42",
            "smoke_passed": True, "telemetry_gap_seconds": 0,
            "heartbeat_at": "2026-09-25T11:59:30Z",
            "window_end": "2026-09-25T11:58:00Z", "window_seconds": 300,
            "stage_started_at": "2026-09-25T11:45:00Z",
            "required_dwell_seconds": 600,
            "candidate_requests": 1000, "baseline_requests": 1000,
            "candidate_errors": 2, "baseline_errors": 1,
            "candidate_p95_ms": 220, "baseline_p95_ms": 200,
            "baseline_source": "live", "baseline_at": "2026-09-25T11:58:00Z",
        }

    def action(self, **changes):
        value = copy.deepcopy(self.observation)
        value.update(changes)
        return decide(value, expected_service="orders-api", expected_release="r42", now=self.now)["action"]

    def test_healthy_observation_proceeds(self):
        self.assertEqual(self.action(), "GO")

    def test_wrong_release_or_service_cannot_proceed(self):
        self.assertEqual(self.action(release_id="r41"), "HOLD")
        self.assertEqual(self.action(service="another-service"), "HOLD")

    def test_missing_samples_hold_then_abort(self):
        self.assertEqual(self.action(candidate_requests=0, candidate_errors=0), "HOLD")
        self.assertEqual(self.action(candidate_requests=0, candidate_errors=0,
                                     stage_started_at="2026-09-25T11:30:00Z"), "ROLLBACK")

    def test_bad_correctness_smoke_recovers_immediately(self):
        self.assertEqual(self.action(smoke_passed=False), "ROLLBACK")

    def test_absolute_latency_breach_recovers_in_one_qualified_window(self):
        self.assertEqual(self.action(candidate_p95_ms=600), "ROLLBACK")

    def test_error_regression_even_below_absolute_limit(self):
        self.assertEqual(self.action(candidate_errors=8), "ROLLBACK")

    def test_good_http_health_does_not_skip_bake(self):
        self.assertEqual(self.action(required_dwell_seconds=1800), "HOLD")

    def test_stale_or_future_heartbeat_holds(self):
        self.assertEqual(self.action(heartbeat_at="2026-09-25T11:57:00Z"), "HOLD")
        self.assertEqual(self.action(heartbeat_at="2026-09-25T12:01:00Z"), "HOLD")

    def test_observability_gap_recovers(self):
        self.assertEqual(self.action(telemetry_gap_seconds=300), "ROLLBACK")

    def test_malformed_numbers_fail_closed(self):
        for value in (float("nan"), float("inf"), True, -1, "1000"):
            with self.subTest(value=value):
                self.assertEqual(self.action(candidate_requests=value), "HOLD")

    def test_missing_evidence_fails_closed(self):
        del self.observation["window_end"]
        self.assertEqual(self.action(), "HOLD")

    def test_no_live_baseline_at_full_traffic_needs_retained_baseline(self):
        self.assertEqual(self.action(baseline_requests=0, baseline_errors=0), "HOLD")
        self.assertEqual(self.action(baseline_source="preswitch"), "GO")

    def test_stale_baseline_holds(self):
        self.assertEqual(self.action(baseline_at="2026-09-25T10:30:00Z"), "HOLD")

    def test_impossible_counts_hold(self):
        self.assertEqual(self.action(candidate_errors=1001), "HOLD")

    def test_disastrous_low_volume_canary_recovers_immediately(self):
        self.assertEqual(self.action(candidate_requests=150, candidate_errors=120,
                                     candidate_p95_ms=4000), "ROLLBACK")

    def test_two_errors_are_insufficient_to_confirm_regression(self):
        self.assertEqual(self.action(candidate_requests=200, baseline_requests=200,
                                     candidate_errors=2, baseline_errors=0), "GO")

    def test_emergency_dwell_can_complete(self):
        self.assertEqual(self.action(required_dwell_seconds=420,
                                     stage_started_at="2026-09-25T11:53:00Z"), "GO")

    def test_previous_step_window_cannot_promote_current_step(self):
        self.assertEqual(self.action(required_dwell_seconds=420,
                                     stage_started_at="2026-09-25T11:53:00Z",
                                     window_end="2026-09-25T11:53:00Z"), "HOLD")

    def test_window_straddling_stage_start_cannot_promote(self):
        self.assertEqual(self.action(required_dwell_seconds=420,
                                     stage_started_at="2026-09-25T11:53:00Z",
                                     window_end="2026-09-25T11:57:59Z"), "HOLD")

    def test_stage_boundary_window_proceeds_after_standard_dwell(self):
        self.assertEqual(self.action(stage_started_at="2026-09-25T11:50:00Z",
                                     window_end="2026-09-25T11:55:00Z"), "GO")

    def test_old_stage_window_does_not_suppress_severe_recovery(self):
        self.assertEqual(self.action(required_dwell_seconds=420,
                                     stage_started_at="2026-09-25T11:53:00Z",
                                     window_end="2026-09-25T11:53:00Z",
                                     candidate_requests=50, candidate_errors=10), "ROLLBACK")

    def test_small_relative_latency_change_does_not_recover(self):
        self.assertEqual(self.action(candidate_requests=200, baseline_requests=200,
                                     candidate_p95_ms=241, baseline_p95_ms=200), "GO")

    def test_relative_latency_requires_fifty_millisecond_margin(self):
        self.assertEqual(self.action(candidate_p95_ms=249, baseline_p95_ms=200), "GO")
        self.assertEqual(self.action(candidate_p95_ms=250, baseline_p95_ms=200), "ROLLBACK")

    def test_relative_latency_ratio_is_strict(self):
        self.assertEqual(self.action(candidate_p95_ms=300, baseline_p95_ms=250), "GO")
        self.assertEqual(self.action(candidate_p95_ms=300.1, baseline_p95_ms=250), "ROLLBACK")

    def test_absolute_latency_limit_is_independent_of_margin(self):
        self.assertEqual(self.action(candidate_p95_ms=501, baseline_p95_ms=490), "ROLLBACK")

    def test_missing_stage_start_cannot_promote(self):
        del self.observation["stage_started_at"]
        self.assertEqual(self.action(), "HOLD")

    def test_future_stage_start_cannot_promote(self):
        self.assertEqual(self.action(stage_started_at="2026-09-25T12:00:01Z"), "HOLD")

    def test_legacy_elapsed_field_cannot_skip_dwell(self):
        # The old caller-supplied timer is ignored; actual stage age is 420s.
        self.assertEqual(self.action(stage_started_at="2026-09-25T11:53:00Z",
                                     stage_elapsed_seconds=900), "HOLD")

    def test_fatal_candidate_needs_no_baseline(self):
        del self.observation["baseline_requests"]
        self.assertEqual(self.action(candidate_requests=50, candidate_errors=10), "ROLLBACK")

    def test_low_volume_extreme_latency_recovers(self):
        self.assertEqual(self.action(candidate_requests=20, candidate_errors=0,
                                     candidate_p95_ms=2000), "ROLLBACK")

    def test_single_error_is_not_a_severe_sample(self):
        self.assertEqual(self.action(candidate_requests=1, candidate_errors=1), "HOLD")

    def test_error_floor_boundary(self):
        self.assertEqual(self.action(candidate_requests=200, candidate_errors=4,
                                     baseline_requests=200, baseline_errors=0), "HOLD")
        self.assertEqual(self.action(candidate_requests=200, candidate_errors=5,
                                     baseline_requests=200, baseline_errors=0), "ROLLBACK")

    def test_dwell_cannot_skip_measurement_window_and_ingestion(self):
        self.assertEqual(self.action(required_dwell_seconds=300), "HOLD")

    def test_unresolved_sparse_absolute_breach_hits_deadline(self):
        self.assertEqual(self.action(candidate_requests=200, candidate_errors=4,
                                     baseline_requests=200, baseline_errors=0,
                                     stage_started_at="2026-09-25T11:30:00Z"), "ROLLBACK")


if __name__ == "__main__":
    unittest.main()
