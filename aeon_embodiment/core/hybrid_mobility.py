"""aeon_embodiment.core.hybrid_mobility — Centaur-Bot wheel ↔ leg state machine.

The robot has two locomotion modes:

    Wheeled  → 4× N20 motors + DRV8833 drivers   (flat ground, 70% power saving)
    Legged   → 8× MG90S servos + IMU balance loop (stairs, obstacles)

Mode transition takes < 2 s and is driven by a stepper-actuated torso
reconfiguration with GPIO waveform sync (blueprint §02). This class is the
state machine + transition guard; actual motor PWM is delegated to a
hardware adapter injected at construction time.
"""

from __future__ import annotations

import enum
import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional

logger = logging.getLogger("aeon_embodiment.mobility")


class MobilityMode(str, enum.Enum):
    WHEELED = "wheeled"
    LEGGED = "legged"
    TRANSITIONING = "transitioning"
    FAULT = "fault"


@dataclass
class MobilityState:
    mode: MobilityMode = MobilityMode.WHEELED
    target_mode: MobilityMode = MobilityMode.WHEELED
    transition_started_at: float = 0.0
    transition_deadline_s: float = 2.0  # blueprint §02: < 2 s
    imu_balance_ok: bool = True
    obstacle_ahead: bool = False
    last_transition_duration_ms: float = 0.0
    transitions_count: int = 0


# Hardware adapter protocol: set_pwm(channel, pulse_us) -> None
PWMSink = Callable[[int, int], None]


class HybridMobilityController:
    """Centaur-Bot wheel/leg transition state machine."""

    def __init__(
        self,
        pwm_sink: Optional[PWMSink] = None,
        transition_deadline_s: float = 2.0,
    ) -> None:
        self._pwm = pwm_sink or _noop_pwm
        self._lock = threading.RLock()
        self._state = MobilityState(transition_deadline_s=transition_deadline_s)
        # Per-mode PWM channels (4 wheels, 8 leg servos)
        self._channels: Dict[MobilityMode, Dict[int, int]] = {
            MobilityMode.WHEELED: {0: 1500, 1: 1500, 2: 1500, 3: 1500},
            MobilityMode.LEGGED: {4: 1500, 5: 1500, 6: 1500, 7: 1500,
                                   8: 1500, 9: 1500, 10: 1500, 11: 1500},
        }

    # ── Mode introspection ──────────────────────────────────────────────

    @property
    def mode(self) -> MobilityMode:
        with self._lock:
            return self._state.mode

    @property
    def state(self) -> MobilityState:
        with self._lock:
            # Return a shallow copy so callers can't mutate internals
            return MobilityState(
                mode=self._state.mode,
                target_mode=self._state.target_mode,
                transition_started_at=self._state.transition_started_at,
                transition_deadline_s=self._state.transition_deadline_s,
                imu_balance_ok=self._state.imu_balance_ok,
                obstacle_ahead=self._state.obstacle_ahead,
                last_transition_duration_ms=self._state.last_transition_duration_ms,
                transitions_count=self._state.transitions_count,
            )

    # ── Sensor updates ──────────────────────────────────────────────────

    def update_imu(self, balance_ok: bool) -> None:
        with self._lock:
            self._state.imu_balance_ok = balance_ok
            if not balance_ok and self._state.mode == MobilityMode.LEGGED:
                logger.warning("IMU balance lost in legged mode — falling back to wheeled")
                # Trigger graceful fallback
                self._transition_to(MobilityMode.WHEELED, force=True)

    def update_proximity(self, obstacle_ahead: bool) -> None:
        with self._lock:
            self._state.obstacle_ahead = obstacle_ahead
            if obstacle_ahead and self._state.mode == MobilityMode.WHEELED:
                logger.info("Obstacle detected — switching to legged mode")
                self._transition_to(MobilityMode.LEGGED)

    # ── Mode transitions ────────────────────────────────────────────────

    def request_mode(self, target: MobilityMode) -> bool:
        with self._lock:
            if self._state.mode == target:
                return True
            if self._state.mode == MobilityMode.TRANSITIONING:
                logger.warning("Already transitioning — request ignored")
                return False
            if target == MobilityMode.LEGGED and not self._state.imu_balance_ok:
                logger.warning("Refusing legged mode — IMU balance not OK")
                return False
            return self._transition_to(target)

    def _transition_to(self, target: MobilityMode, force: bool = False) -> bool:
        # MUST be called under self._lock
        prev = self._state.mode
        self._state.target_mode = target
        self._state.mode = MobilityMode.TRANSITIONING
        self._state.transition_started_at = time.time()
        # Apply the stepper-driven torso reconfiguration waveform
        self._apply_reconfiguration_waveform(target)
        # Transition time check
        elapsed_ms = (time.time() - self._state.transition_started_at) * 1000.0
        if elapsed_ms > self._state.transition_deadline_s * 1000 and not force:
            logger.error("Transition exceeded deadline (%.0f ms)", elapsed_ms)
            self._state.mode = MobilityMode.FAULT
            return False
        self._state.mode = target
        self._state.last_transition_duration_ms = max(elapsed_ms, 50.0)  # sim floor
        self._state.transitions_count += 1
        logger.info(
            "Mobility transition %s -> %s in %.0f ms",
            prev.value,
            target.value,
            self._state.last_transition_duration_ms,
        )
        return True

    def _apply_reconfiguration_waveform(self, target: MobilityMode) -> None:
        """Drive the steppers with a synchronised GPIO waveform (blueprint §02).

        In simulation this is a no-op; in production the pwm_sink receives the
        actual pulse sequence via the hardware adapter.
        """
        for ch, pulse in self._channels.get(target, {}).items():
            self._pwm(ch, pulse)

    # ── Manual drive commands ───────────────────────────────────────────

    def set_wheel_speeds(self, speeds: tuple[int, int, int, int]) -> None:
        """Set per-wheel PWM (4 channels, pulse µs in [1000, 2000])."""
        if self.mode != MobilityMode.WHEELED:
            logger.warning("set_wheel_speeds ignored — not in wheeled mode")
            return
        for ch, pulse in zip(range(4), speeds):
            pulse = max(1000, min(2000, int(pulse)))
            self._channels[MobilityMode.WHEELED][ch] = pulse
            self._pwm(ch, pulse)

    def set_leg_pose(self, pose: tuple[int, ...]) -> None:
        """Set 8 servo pulses (µs in [500, 2500]) for legged mode."""
        if len(pose) != 8:
            raise ValueError(f"Legged mode requires 8 servo pulses, got {len(pose)}")
        if self.mode != MobilityMode.LEGGED:
            logger.warning("set_leg_pose ignored — not in legged mode")
            return
        for ch, pulse in zip(range(4, 12), pose):
            pulse = max(500, min(2500, int(pulse)))
            self._channels[MobilityMode.LEGGED][ch] = pulse
            self._pwm(ch, pulse)


def _noop_pwm(channel: int, pulse_us: int) -> None:
    """Default PWM sink — used when no hardware is attached."""
    logger.debug("[noop pwm] ch=%d pulse=%d µs", channel, pulse_us)


__all__ = [
    "HybridMobilityController",
    "MobilityMode",
    "MobilityState",
    "PWMSink",
]
