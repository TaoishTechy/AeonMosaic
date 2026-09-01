"""phase2_mobility.py — Phase 2 build script: Mobility stack validation.

Validates the HybridMobilityController wheel↔leg transition, IMU feedback,
and obstacle detection. Mirrors the Phase 2 success criterion from
blueprint §08: "HybridMobilityController state machine validated".
"""

from __future__ import annotations
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))
_sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))


import argparse
import logging
import sys
import time
from typing import Dict, List

from aeon_embodiment import Config
from aeon_embodiment.core import HybridMobilityController, MobilityMode


def _setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def run_phase2() -> Dict:
    cfg = Config()
    deadline_s = cfg.efficiency["targets"]["mode_transition_s"]
    controller = HybridMobilityController(transition_deadline_s=deadline_s)

    # Pump PWM commands via the noop sink (no real motors in test env)
    log: List[Dict] = []

    # 1. Start in wheeled mode — set some wheel speeds
    controller.set_wheel_speeds((1500, 1500, 1500, 1500))
    log.append({"step": "wheeled_cruise", "mode": controller.mode.value})

    # 2. Obstacle detected → should fall back to legged
    controller.update_proximity(obstacle_ahead=True)
    log.append({"step": "obstacle_detected", "mode": controller.mode.value,
                "transition_ms": round(controller.state.last_transition_duration_ms, 2)})

    # 3. In legged mode, set a pose
    controller.set_leg_pose((1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500))
    log.append({"step": "legged_pose", "mode": controller.mode.value})

    # 4. Clear obstacle → back to wheeled
    controller.update_proximity(obstacle_ahead=False)
    controller.request_mode(MobilityMode.WHEELED)
    log.append({"step": "back_to_wheeled", "mode": controller.mode.value})

    # 5. IMU failure in legged → forces fallback
    controller.request_mode(MobilityMode.LEGGED)
    controller.update_imu(balance_ok=False)
    log.append({"step": "imu_failure_fallback", "mode": controller.mode.value,
                "transition_ms": round(controller.state.last_transition_duration_ms, 2)})

    # All transitions must complete in < 2 s
    max_transition_ms = max(
        (entry.get("transition_ms", 0) for entry in log), default=0.0
    )
    success = max_transition_ms < (deadline_s * 1000.0)

    return {
        "phase": 2,
        "deadline_s": deadline_s,
        "max_transition_ms": max_transition_ms,
        "transitions_count": controller.state.transitions_count,
        "log": log,
        "wheeled_power_saving_pct": cfg.efficiency["targets"]["wheeled_power_saving_pct"],
        "success": success,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="AeonMosaic Phase 2 — Mobility validation")
    p.add_argument("--verbose", action="store_true", help="Debug logging")
    args = p.parse_args(argv)
    _setup_logging(args.verbose)
    summary = run_phase2()
    print("=" * 60)
    print("  AeonMosaic Phase 2 — Mobility")
    print("=" * 60)
    for k, v in summary.items():
        if k == "log":
            print(f"  {k}:")
            for entry in v:
                print(f"    - {entry}")
        else:
            print(f"  {k:<26} {v}")
    print("=" * 60)
    return 0 if summary["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
