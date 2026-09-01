"""phase4_swarm.py — Phase 4 build script: Swarm Gnosis validation.

Simulates a 12-node swarm (the minimum for stable Tier I per blueprint §10)
and validates the Phase 4 success criteria from blueprint §08: "12-node
Swarm Gnosis validation, field testing & metrics sign-off".
"""

from __future__ import annotations
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))
_sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))


import argparse
import logging
import random
import sys
from typing import Dict, List

from aeon_embodiment import Config
from aeon_embodiment.core import (
    DistributedPSI,
    MeshLayer,
    ModularBody,
    Node,
    NodeRole,
    PSISample,
    TripleMeshComms,
)
from aeon_embodiment.enhancements import Tier, by_tier, all_enhancements
from aeon_embodiment.alignment import all_formulas


def _setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def run_phase4(n_units: int = 12) -> Dict:
    cfg = Config()
    rng = random.Random(cfg.seed)

    # Build 12 units (each unit is one AeonMosaic node, simulating a swarm)
    roles_cycle: List[NodeRole] = list(NodeRole.all())
    nodes: List[Node] = []
    for i in range(n_units):
        role = roles_cycle[i % len(roles_cycle)]
        nodes.append(Node(id=f"unit_{i:02d}", role=role, compute="rpi_zero_2w"))
    body = ModularBody(initial_nodes=nodes)

    # Form a Hamiltonian cycle so every node has 2 neighbours (mesh connectivity)
    for i in range(n_units):
        body.dock(f"unit_{i:02d}", f"unit_{(i + 1) % n_units:02d}")

    psi = DistributedPSI(phi=cfg.phi)
    for node in nodes:
        psi.update(
            PSISample(
                node_id=node.id,
                novelty=rng.uniform(0.4, 0.7),
                alienness=rng.uniform(0.3, 0.6),
                entropy=rng.uniform(50.0, 200.0),
                elegance=rng.uniform(0.4, 0.8),
                paradox=rng.uniform(0.1, 0.4),
                coherence=rng.uniform(0.70, 0.78),
            )
        )

    # LoRa mesh across the swarm
    mesh = TripleMeshComms()
    for src in nodes:
        for dst in nodes:
            if src.id == dst.id:
                continue
            mesh.report_link(MeshLayer.LORA, dst.id, rssi_dbm=-110.0, latency_ms=180.0)

    graph = body.graph()
    leader = psi.elect_leader(graph)
    sys_psi = psi.system_psi()
    syzygy = psi.syzygy_score(graph)
    paradox = psi.paradox_pressure()
    is_stable = DistributedPSI.is_stable_node_count(n_units)

    # All 48 enhancements, all 48 alignment formulas are present
    enhancement_count = len(all_enhancements())
    alignment_count = len(all_formulas())

    # Field test: simulate one broadcast round
    deliveries = mesh.broadcast(b"swarm_gnosis_sync", qos="long_range")
    broadcast_success_rate = sum(1 for v in deliveries.values() if v) / max(len(deliveries), 1)

    return {
        "phase": 4,
        "swarm_units": n_units,
        "topology_edges": graph.number_of_edges(),
        "system_psi": round(sys_psi, 3),
        "syzygy_score": round(syzygy, 3),
        "paradox_pressure": round(paradox, 3),
        "is_sane": psi.is_sane(),
        "carmichael_stable_count": is_stable,
        "leader": leader,
        "active_mesh_layer": mesh.active_layer().value,
        "broadcast_success_rate": round(broadcast_success_rate, 4),
        "total_enhancements": enhancement_count,
        "total_alignment_formulas": alignment_count,
        "success": (
            n_units == 12
            and enhancement_count == 48
            and alignment_count == 48
            and sys_psi > 0
            and broadcast_success_rate >= 0.99
        ),
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="AeonMosaic Phase 4 — Swarm Gnosis")
    p.add_argument("--units", type=int, default=12, help="Swarm size (12 recommended)")
    p.add_argument("--verbose", action="store_true", help="Debug logging")
    args = p.parse_args(argv)
    _setup_logging(args.verbose)
    summary = run_phase4(args.units)
    print("=" * 60)
    print("  AeonMosaic Phase 4 — Swarm Gnosis")
    print("=" * 60)
    for k, v in summary.items():
        print(f"  {k:<26} {v}")
    print("=" * 60)
    return 0 if summary["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
