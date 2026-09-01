"""phase3_intelligence.py — Phase 3 build script: Intelligence & perception.

Validates DistributedPSI with NetworkX centrality, the Sophia framework
(12 equations), and Tier I–III enhancements. Mirrors blueprint §08 Phase 3:
"Tiers I–III enhancements activated".
"""

from __future__ import annotations
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))
_sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))


import argparse
import logging
import sys
from typing import Dict

from aeon_embodiment import Config
from aeon_embodiment.core import (
    DistributedPSI,
    ModularBody,
    Node,
    NodeRole,
    PSISample,
)
from aeon_embodiment.enhancements import Tier, by_tier, by_priority, Priority
from aeon_embodiment.sophia import all_equations, evaluate_all


def _setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def run_phase3() -> Dict:
    cfg = Config()
    body = ModularBody(
        initial_nodes=[
            Node(id="head", role=NodeRole.HEAD, compute="rpi_4"),
            Node(id="torso", role=NodeRole.TORSO, compute="rpi_3a_plus"),
            Node(id="left_arm", role=NodeRole.LEFT_ARM),
            Node(id="right_arm", role=NodeRole.RIGHT_ARM),
            Node(id="left_leg", role=NodeRole.LEFT_LEG),
            Node(id="right_leg", role=NodeRole.RIGHT_LEG),
        ]
    )
    for limb in ("head", "left_arm", "right_arm", "left_leg", "right_leg"):
        body.dock("torso", limb)

    psi = DistributedPSI(phi=cfg.phi)
    for node in body.all_nodes():
        psi.update(
            PSISample(
                node_id=node.id,
                novelty=0.6, alienness=0.5, entropy=120.0,
                elegance=0.7, paradox=0.2, coherence=0.72,
            )
        )

    # Sophia 12 equations
    sophia = evaluate_all(phi_val=cfg.phi)

    # Tier I-III enhancements
    tier1 = by_tier(Tier.I)
    tier2 = by_tier(Tier.II)
    tier3 = by_tier(Tier.III)

    top_priority = by_priority(Priority.TOP)

    graph = body.graph()
    leader = psi.elect_leader(graph)
    sys_psi = psi.system_psi()
    syzygy = psi.syzygy_score(graph)

    return {
        "phase": 3,
        "sophia_equations_count": len(all_equations()),
        "sophia_eval": {str(k): round(v, 4) for k, v in sophia.items()},
        "system_psi": round(sys_psi, 3),
        "syzygy_score": round(syzygy, 3),
        "is_sane": psi.is_sane(),
        "golden_ratio_locked": psi.is_golden_ratio_locked(),
        "leader": leader,
        "tier_1_enhancements": len(tier1),
        "tier_2_enhancements": len(tier2),
        "tier_3_enhancements": len(tier3),
        "top_priority_count": len(top_priority),
        "carmichael_stable": DistributedPSI.is_stable_node_count(len(body.all_nodes())),
        "success": sys_psi > 0 and psi.is_sane() and leader is not None,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="AeonMosaic Phase 3 — Intelligence")
    p.add_argument("--verbose", action="store_true", help="Debug logging")
    args = p.parse_args(argv)
    _setup_logging(args.verbose)
    summary = run_phase3()
    print("=" * 60)
    print("  AeonMosaic Phase 3 — Intelligence")
    print("=" * 60)
    for k, v in summary.items():
        if k == "sophia_eval":
            print(f"  {k}:")
            for eq_id, val in v.items():
                print(f"    Eq #{eq_id}: {val}")
        else:
            print(f"  {k:<26} {v}")
    print("=" * 60)
    return 0 if summary["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
