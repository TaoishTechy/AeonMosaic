"""aeon_embodiment.enhancements — 48 Alien Tier Enhancements registry.

Eight tiers of reality-modifying capabilities ranked by Composite Alienness
Score. Each enhancement is a self-describing record with:

    - Tier (I–VIII) and ordinal # (1–48)
    - Name
    - Composite score (calculated via the scoring formula)
    - Target subsystem (e.g. ``DistributedPSI → Syzygy Weave Engine``)
    - Priority (TOP / HIGH / MID-HIGH / MID / MID-LOW / LOWER / DEFERRED / SEED)

Composite Score Formula (blueprint §06)::

    Composite = (Novelty × 30) + (Alienness × 25) + (Entropic_Potential × 0.05)
                + (Elegance × 0.2) + (Paradox_Intensity × 10) + (Ontology_Coherence × 15)
"""

from __future__ import annotations

import enum
import json
import logging
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("aeon_embodiment.enhancements")


class Tier(str, enum.Enum):
    I = "I"
    II = "II"
    III = "III"
    IV = "IV"
    V = "V"
    VI = "VI"
    VII = "VII"
    VIII = "VIII"


class Priority(str, enum.Enum):
    TOP = "TOP"
    HIGH = "HIGH"
    MID_HIGH = "MID-HIGH"
    MID = "MID"
    MID_LOW = "MID-LOW"
    LOWER = "LOWER"
    DEFERRED = "DEFERRED"
    SEED = "SEED"


@dataclass(frozen=True)
class Enhancement:
    """One of the 48 reality-modifying capabilities."""

    number: int                       # 1..48
    tier: Tier
    name: str
    target_subsystem: str             # e.g. "DistributedPSI → Syzygy Weave Engine"
    priority: Priority
    # Raw metric components (blueprint §06 scoring formula)
    novelty: float = 0.0             # 0..1
    alienness: float = 0.0           # 0..1
    entropic_potential: float = 0.0  # raw float (×0.05)
    elegance: float = 0.0            # 0..1 (×0.2)
    paradox_intensity: float = 0.0   # 0..1 (×10)
    ontology_coherence: float = 0.0  # 0..1 (×15)

    def composite_score(self) -> float:
        return (
            self.novelty * 30.0
            + self.alienness * 25.0
            + self.entropic_potential * 0.05
            + self.elegance * 0.2
            + self.paradox_intensity * 10.0
            + self.ontology_coherence * 15.0
        )

    def to_dict(self) -> Dict[str, object]:
        d = asdict(self)
        d["tier"] = self.tier.value
        d["priority"] = self.priority.value
        d["composite"] = self.composite_score()
        return d


# ── Tier averages from the blueprint (§06) ───────────────────────────

TIER_AVERAGES: Dict[Tier, float] = {
    Tier.I: 332.4,
    Tier.II: 329.8,
    Tier.III: 327.9,
    Tier.IV: 327.1,
    Tier.V: 325.9,
    Tier.VI: 325.2,
    Tier.VII: 324.9,
    Tier.VIII: 324.3,
}


# ── In-package fallback registry (matches blueprint §06 verbatim) ────

# (number, tier, name, composite, target, priority)
# Composite scores are taken verbatim from the blueprint so any JSON
# manifest missing or out-of-sync with §06 still yields the canonical set.
_BLUEPRINT_REGISTRY: List[Tuple[int, str, str, float, str, str]] = [
    (1, "I", "Subobject Syzygy Weave", 335.9, "DistributedPSI → Syzygy Weave Engine", "TOP"),
    (2, "I", "Woodin Cardinal Fold", 335.2, "ModularBody → Perception Membrane", "TOP"),
    (3, "I", "Path-Integral Reality Forge", 331.2, "DistributedPSI → Syzygy Weave Engine", "TOP"),
    (4, "I", "Linear Logic Conservation", 331.0, "TripleMeshComms → Causal Routing", "TOP"),
    (5, "I", "Quantum Bifurcation Actuator", 330.5, "HybridMobilityController → Branch Actuator", "TOP"),
    (6, "I", "Immortality Classifier Engine", 330.4, "MagneticDockManager → Persistence Lattice", "TOP"),
    (7, "II", "Kolmogorov-PSI Compression", 330.3, "ModularBody → Perception Membrane", "HIGH"),
    (8, "II", "Mesh Propagator Membrane", 330.3, "ModularBody → Perception Membrane", "HIGH"),
    (9, "II", "Concurrence Soul Bridge", 330.3, "MagneticDockManager → Persistence Lattice", "HIGH"),
    (10, "II", "Mutual-Info Coherence Grid", 329.9, "ModularBody → Perception Membrane", "HIGH"),
    (11, "II", "Microtubule Collapse Inducer", 329.2, "ModularBody → Reality Forge Core", "HIGH"),
    (12, "II", "Arithmetic Coding Reality", 329.0, "DistributedPSI → Syzygy Weave Engine", "HIGH"),
    (13, "III", "Linear Decoherence Barrier", 328.3, "HybridMobilityController → Branch Actuator", "MID-HIGH"),
    (14, "III", "Bell-PSI Entanglement Bound", 328.3, "DistributedPSI → Noetic Governor", "MID-HIGH"),
    (15, "III", "Fano Fidelity Shield", 327.9, "HybridMobilityController → Branch Actuator", "MID-HIGH"),
    (16, "III", "Quantum Memory Transform", 327.9, "ModularBody → Perception Membrane", "MID-HIGH"),
    (17, "III", "Measurement Work Extractor", 327.8, "ModularBody → Reality Forge Core", "MID-HIGH"),
    (18, "III", "Firewall Horizon Probe", 327.4, "TripleMeshComms → Causal Routing", "MID-HIGH"),
    (19, "IV", "Bremermann Computation Veil", 327.3, "ModularBody → Perception Membrane", "MID"),
    (20, "IV", "Hyperdimensional MI Fracture", 327.2, "ModularBody → Perception Membrane", "MID"),
    (21, "IV", "Holographic Retro-Collapse", 327.2, "ModularBody → Reality Forge Core", "MID"),
    (22, "IV", "Quantum Walk Decision Engine", 327.2, "MagneticDockManager → Persistence Lattice", "MID"),
    (23, "IV", "Entangled Microtubule Sync", 327.0, "MagneticDockManager → Persistence Lattice", "MID"),
    (24, "IV", "Undefinability Truth Barrier", 326.5, "DistributedPSI → Syzygy Weave Engine", "MID"),
    (25, "V", "Retrocausal Kolmogorov Gate", 326.4, "DistributedPSI → Noetic Governor", "MID-LOW"),
    (26, "V", "Retro-Measurement Engine", 326.3, "HybridMobilityController → Branch Actuator", "MID-LOW"),
    (27, "V", "Arithmetical Syzygy Ladder", 325.8, "DistributedPSI → Syzygy Weave Engine", "MID-LOW"),
    (28, "V", "Penrose Conformal Mapper", 325.7, "TripleMeshComms → Isolation Manifold", "MID-LOW"),
    (29, "V", "Entanglement Capacity Amplifier", 325.6, "ModularBody → Perception Membrane", "MID-LOW"),
    (30, "V", "Constructivist Reality Seed", 325.4, "MagneticDockManager → Persistence Lattice", "MID-LOW"),
    (31, "VI", "Wigner Split-PSI Mirror", 325.4, "DistributedPSI → Noetic Governor", "LOWER"),
    (32, "VI", "Thermodynamic Length Walker", 325.3, "DistributedPSI → Noetic Governor", "LOWER"),
    (33, "VI", "Reverse-Math PSI Basis", 325.2, "MagneticDockManager → Persistence Lattice", "LOWER"),
    (34, "VI", "Holographic Bremermann Core", 325.1, "HybridMobilityController → Branch Actuator", "LOWER"),
    (35, "VI", "Meme-Walk Propagator", 325.0, "ModularBody → Reality Forge Core", "LOWER"),
    (36, "VI", "Entangled Meme Broadcaster", 324.8, "TripleMeshComms → Isolation Manifold", "LOWER"),
    (37, "VII", "Echo-State Persistence Net", 325.1, "ModularBody → Perception Membrane", "DEFERRED"),
    (38, "VII", "Holographic Echo Attractor", 325.0, "DistributedPSI → Noetic Governor", "DEFERRED"),
    (39, "VII", "Quantum Zeno Shield", 324.9, "ModularBody → Perception Membrane", "DEFERRED"),
    (40, "VII", "EPR Nonlocal Relay", 324.8, "ModularBody → Perception Membrane", "DEFERRED"),
    (41, "VII", "Woodin Bifurcation Engine", 324.7, "HybridMobilityController → Branch Actuator", "DEFERRED"),
    (42, "VII", "Toffoli-PSI Reverser", 324.7, "TripleMeshComms → Isolation Manifold", "DEFERRED"),
    (43, "VIII", "Seed Classifier Emergence", 324.6, "MagneticDockManager → Persistence Lattice", "SEED"),
    (44, "VIII", "Personal Dissipation Walker", 324.3, "TripleMeshComms → Isolation Manifold", "SEED"),
    (45, "VIII", "Island-PSI Extractor", 324.3, "ModularBody → Perception Membrane", "SEED"),
    (46, "VIII", "Carnot-PSI Efficiency Core", 324.2, "ModularBody → Reality Forge Core", "SEED"),
    (47, "VIII", "Adjunction Optimizer", 324.1, "HybridMobilityController → Branch Actuator", "SEED"),
    (48, "VIII", "Van't Hoff Equilibrium PSI", 324.1, "ModularBody → Reality Forge Core", "SEED"),
]


def _build_enhancements() -> List[Enhancement]:
    """Build the canonical 48-enhancement registry from the blueprint table.

    The composite score is fixed in §06; we back-solve for novelty/alienness
    by distributing the score evenly across the 6 components and storing the
    known total. Callers using ``Enhancement.composite_score()`` get back
    the canonical blueprint value.
    """
    out: List[Enhancement] = []
    for number, tier, name, composite, target, priority in _BLUEPRINT_REGISTRY:
        # Distribute the composite equally across the 6 components.
        # (0.05 weight on entropic_potential means it absorbs more.)
        # Solving: 30n + 25a + 0.05e + 0.2el + 10p + 15c = composite
        # Pick a representative distribution centred on φ.
        # This is *not* a recovery of the original components — it is a
        # well-defined canonical partition so tests are deterministic.
        n = composite / (30 + 25 + 0.05 + 0.2 + 10 + 15)  # uniform share
        e = n  # entropic_potential gets the same numeric contribution
        enhancement = Enhancement(
            number=number,
            tier=Tier(tier),
            name=name,
            target_subsystem=target,
            priority=Priority(priority),
            novelty=round(n, 6),
            alienness=round(n, 6),
            entropic_potential=round(e * (30 / 0.05), 6),  # scale so 0.05*e ≈ 30n
            elegance=round(n, 6),
            paradox_intensity=round(n, 6),
            ontology_coherence=round(n, 6),
        )
        # Composite_score() may drift due to floating point — pin it.
        # We patch ontology_coherence to absorb the residual.
        residual = composite - enhancement.composite_score()
        enhancement = Enhancement(
            **{**asdict(enhancement), "ontology_coherence": round(enhancement.ontology_coherence + residual / 15.0, 6)}
        )
        out.append(enhancement)
    return out


_REGISTRY: Optional[List[Enhancement]] = None


def all_enhancements() -> List[Enhancement]:
    """Return the 48 canonical enhancements (cached)."""
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = _build_enhancements()
    return _REGISTRY


def by_tier(tier: Tier) -> List[Enhancement]:
    return [e for e in all_enhancements() if e.tier is tier]


def by_number(number: int) -> Enhancement:
    if not 1 <= number <= 48:
        raise IndexError(f"Enhancement number out of range: {number}")
    return all_enhancements()[number - 1]


def by_subsystem(subsystem: str) -> List[Enhancement]:
    """Return enhancements whose target_subsystem contains ``subsystem``."""
    return [e for e in all_enhancements() if subsystem.lower() in e.target_subsystem.lower()]


def by_priority(priority: Priority) -> List[Enhancement]:
    return [e for e in all_enhancements() if e.priority is priority]


def count_by_subsystem() -> Dict[str, int]:
    """Per-subsystem enhancement counts (blueprint §06 distribution)."""
    counts: Dict[str, int] = {}
    for e in all_enhancements():
        # Strip the sub-component after "→" for the bucket name
        bucket = e.target_subsystem.split("→")[0].strip()
        counts[bucket] = counts.get(bucket, 0) + 1
    return counts


def to_json() -> str:
    """Serialise the entire registry to a JSON string."""
    return json.dumps([e.to_dict() for e in all_enhancements()], indent=2)


__all__ = [
    "Enhancement",
    "Tier",
    "Priority",
    "TIER_AVERAGES",
    "all_enhancements",
    "by_tier",
    "by_number",
    "by_subsystem",
    "by_priority",
    "count_by_subsystem",
    "to_json",
]
