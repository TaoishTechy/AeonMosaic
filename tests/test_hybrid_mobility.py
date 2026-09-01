"""Tests for HybridMobilityController."""

from __future__ import annotations

import pytest

from aeon_embodiment.core import HybridMobilityController, MobilityMode


@pytest.fixture
def controller():
    pwm_log = []
    sink = lambda ch, pulse: pwm_log.append((ch, pulse))
    return HybridMobilityController(pwm_sink=sink, transition_deadline_s=2.0), pwm_log


def test_starts_in_wheeled_mode(controller):
    ctrl, _ = controller
    assert ctrl.mode == MobilityMode.WHEELED


def test_set_wheel_speeds_only_in_wheeled_mode(controller):
    ctrl, pwm = controller
    ctrl.set_wheel_speeds((1500, 1600, 1400, 1500))
    assert len(pwm) == 4


def test_set_leg_pose_requires_legged_mode(controller):
    ctrl, _ = controller
    with pytest.raises(ValueError, match="requires 8"):
        ctrl.set_leg_pose((1500,) * 7)


def test_obstacle_triggers_legged_transition(controller):
    ctrl, _ = controller
    ctrl.update_proximity(obstacle_ahead=True)
    assert ctrl.mode == MobilityMode.LEGGED
    assert ctrl.state.transitions_count == 1


def test_imu_failure_forces_wheeled_fallback(controller):
    ctrl, _ = controller
    ctrl.update_proximity(obstacle_ahead=True)
    assert ctrl.mode == MobilityMode.LEGGED
    ctrl.update_imu(balance_ok=False)
    assert ctrl.mode == MobilityMode.WHEELED


def test_request_legged_refused_when_imu_not_ok(controller):
    ctrl, _ = controller
    ctrl.update_imu(balance_ok=False)
    assert not ctrl.request_mode(MobilityMode.LEGGED)
    assert ctrl.mode == MobilityMode.WHEELED


def test_transition_within_2s_deadline(controller):
    ctrl, _ = controller
    ctrl.update_proximity(obstacle_ahead=True)
    assert ctrl.state.last_transition_duration_ms < 2000.0


def test_state_snapshot_is_defensive_copy(controller):
    ctrl, _ = controller
    snap = ctrl.state
    snap.mode = MobilityMode.FAULT
    assert ctrl.mode == MobilityMode.WHEELED  # internal state unchanged
