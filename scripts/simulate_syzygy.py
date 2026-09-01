"""simulate_syzygy.py — Pure-Python syzygy simulator for AeonMosaic.

Boots a 6-node modular body (HEAD, TORSO, 4× limbs), docks them, runs a
few PSI cycles, and prints a dashboard. Used for development & CI without
any real hardware attached.

Usage::

    python simulate_syzygy.py
    python simulate_syzygy.py --ticks 100
    python simulate_syzygy.py --json
"""

from __future__ import annotations
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))
_sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))


import argparse
import json
import logging
import random
import sys
import time
from typing import Dict

import networkx as nx

from aeon_embodiment import Config
from aeon_embodiment.core import (
    DistributedPSI,
    HybridMobilityController,
    MagneticDockManager,
    ModularBody,
    Node,
    NodeRole,
    NodeStatus,
    PSISample,
    TripleMeshComms,
    MobilityMode,
    MeshLayer,
)
from aeon_embodiment.sophia import SOPHIA_PHI, all_equations, evaluate_all


def _setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _build_body(cfg: Config) -> ModularBody:
    """Build the canonical 6-node AeonMosaic body."""
    nodes = [
        Node(id="head",       role=NodeRole.HEAD,       compute="rpi_4",       sensors=["pi_cam_v3", "i2s_mic", "mpu6050"]),
        Node(id="torso",      role=NodeRole.TORSO,      compute="rpi_3a_plus", sensors=["mpu6050"]),
        Node(id="left_arm",   role=NodeRole.LEFT_ARM,   compute="rpi_zero_2w", sensors=["mpu6050", "fsr_402"]),
        Node(id="right_arm",  role=NodeRole.RIGHT_ARM,  compute="rpi_zero_2w", sensors=["mpu6050", "fsr_402"]),
        Node(id="left_leg",   role=NodeRole.LEFT_LEG,   compute="rpi_zero_2w", sensors=["mpu6050", "hc_sr04"]),
        Node(id="right_leg",  role=NodeRole.RIGHT_LEG,  compute="rpi_zero_2w", sensors=["mpu6050", "hc_sr04"]),
    ]
    body = ModularBody(initial_nodes=nodes)
    # Dock the limbs to the torso
    for limb in ("head", "left_arm", "right_arm", "left_leg", "right_leg"):
        body.dock("torso", limb)
    return body


def _run_simulation(ticks: int, seed: int, json_out: bool) -> Dict:
    random.seed(seed)
    cfg = Config()  # uses bundled configs/ directory
    body = _build_body(cfg)
    psi = DistributedPSI(phi=cfg.phi)
    mesh = TripleMeshComms()
    # Report healthy link state for all known targets
    for nid in body.all_nodes():
        for layer in MeshLayer.priority():
            mesh.report_link(layer, nid.id, rssi_dbm=-50.0, latency_ms=10.0)

    # Mobility starts in wheeled mode
    mobility = HybridMobilityController(transition_deadline_s=cfg.efficiency["targets"]["mode_transition_s"])

    history = []
    for tick in range(ticks):
        # Simulated per-node sensor readings — small noise around phi
        for node in body.all_nodes():
            sample = PSISample(
                node_id=node.id,
                novelty=random.uniform(0.4, 0.7),
                alienness=random.uniform(0.3, 0.6),
                entropy=random.uniform(50.0, 200.0),
                elegance=random.uniform(0.4, 0.8),
                paradox=random.uniform(0.1, 0.4),
                coherence=random.uniform(0.65, 0.78),  # near phi
            )
            psi.update(sample)

        # Mobility: simulate obstacles every ~10 ticks
        if tick and tick % 10 == 0:
            mobility.update_proximity(obstacle_ahead=True)
        elif tick and tick % 11 == 0:
            mobility.update_proximity(obstacle_ahead=False)
            mobility.update_imu(balance_ok=True)

        graph = body.graph()
        sys_psi = psi.system_psi()
        syzygy = psi.syzygy_score(graph)
        paradox = psi.paradox_pressure()
        leader = psi.elect_leader(graph)
        history.append(
            {
                "tick": tick,
                "system_psi": round(sys_psi, 3),
                "syzygy": round(syzygy, 3),
                "paradox": round(paradox, 3),
                "leader": leader,
                "mobility_mode": mobility.mode.value,
                "active_mesh_layer": (mesh.active_layer().value
                                       if mesh.active_layer() else "none"),
            }
        )

    # Sophia equations evaluated once for the final state
    sophia_eval = evaluate_all(phi_val=cfg.phi)

    summary = {
        "ticks": ticks,
        "nodes": [n.to_dict() for n in body.all_nodes()],
        "topology_edges": [list(e) for e in body.graph().edges()],
        "final_state": history[-1] if history else None,
        "mean_system_psi": sum(h["system_psi"] for h in history) / max(len(history), 1),
        "is_sane": psi.is_sane(),
        "golden_ratio_locked": psi.is_golden_ratio_locked(),
        "leader": psi.elect_leader(body.graph()),
        "sophia_equations": {str(k): round(v, 4) for k, v in sophia_eval.items()},
        "history": history,
    }
    if json_out:
        print(json.dumps(summary, indent=2))
    else:
        _print_dashboard(summary)
    return summary


def _print_dashboard(summary: Dict) -> None:
    print("=" * 60)
    print("  AeonMosaic — Syzygy Simulation")
    print("=" * 60)
    print(f"  Ticks:              {summary['ticks']}")
    print(f"  Nodes:              {len(summary['nodes'])}")
    print(f"  Topology edges:     {len(summary['topology_edges'])}")
    print(f"  Mean system PSI:    {summary['mean_system_psi']:.3f}")
    print(f"  Sane (>=0.70):      {summary['is_sane']}")
    print(f"  Golden-ratio lock:  {summary['golden_ratio_locked']}")
    print(f"  Elected leader:     {summary['leader']}")
    print()
    print("  Sophia equation values:")
    for k, v in summary["sophia_equations"].items():
        print(f"    Eq. #{k:>2}: {v}")
    print()
    print("  Final state:")
    for k, v in (summary["final_state"] or {}).items():
        print(f"    {k:<22} {v}")
    print("=" * 60)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="AeonMosaic syzygy simulator")
    p.add_argument("--ticks", type=int, default=20, help="Number of simulation ticks")
    p.add_argument("--seed", type=int, default=42, help="RNG seed")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of pretty dashboard")
    p.add_argument("--verbose", action="store_true", help="Debug logging")
    args = p.parse_args(argv)
    _setup_logging(args.verbose)
    _run_simulation(args.ticks, args.seed, args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
