"""aeon_embodiment.alignment — 48 Alignment Formulas mapped to software tiers.

Syzygy-event equations grouped into 8 tiers (6 formulas each), spanning:

    Tier 1 — Quantum Syzygy          (Quantum Information Theory)
    Tier 2 — Distributed PSI Algorithms (Distributed AI)
    Tier 3 — Mesh Comms Functions     (Neuromorphic Computing)
    Tier 4 — Mobility Alignment       (Holographic Principles)
    Tier 5 — Power Management         (Retrocausal Mechanics)
    Tier 6 — Docking Manager          (Quantum Information Theory)
    Tier 7 — Perception Alignment     (Distributed AI)
    Tier 8 — Gnostic Core Sciences    (Holographic / Retrocausal)

Each formula carries a SymPy symbolic form and a numeric evaluator that fires
as ROS 2 Actions when DistributedPSI crosses a syzygy threshold (blueprint §07).
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

import sympy as sp

logger = logging.getLogger("aeon_embodiment.alignment")

phi = sp.Symbol("phi", positive=True, real=True)


@dataclass
class AlignmentFormula:
    """One of the 48 syzygy-event alignment formulas.

    Attributes
    ----------
    number:
        1-based ordinal from blueprint §07 (1..48).
    tier:
        Software tier 1..8.
    name:
        Short human-readable name (matches blueprint table).
    focus:
        Tier focus area (e.g. "Quantum Syzygy").
    domain:
        Scientific domain (e.g. "Quantum Information Theory").
    symbolic:
        SymPy expression for symbolic manipulation.
    evaluator:
        Numeric evaluator: ``f(**kwargs) -> float``.
    """

    number: int
    tier: int
    name: str
    focus: str
    domain: str
    symbolic: sp.Expr
    evaluator: Callable[..., float]


# ── Tier metadata ────────────────────────────────────────────────────────

TIERS: List[Tuple[int, str, str, Tuple[int, int]]] = [
    (1, "Quantum Syzygy",         "Quantum Information Theory",  (1, 6)),
    (2, "Distributed PSI Algorithms", "Distributed AI",        (7, 12)),
    (3, "Mesh Comms Functions",  "Neuromorphic Computing",      (13, 18)),
    (4, "Mobility Alignment",     "Holographic Principles",      (19, 24)),
    (5, "Power Management",       "Retrocausal Mechanics",        (25, 30)),
    (6, "Docking Manager",       "Quantum Information Theory",   (31, 36)),
    (7, "Perception Alignment",  "Distributed AI",              (37, 42)),
    (8, "Gnostic Core Sciences", "Holographic / Retrocausal",    (43, 48)),
]


# ── Generic formula evaluators (one per formula; see blueprint §07) ───


def _ev_vacuum_syzygy_coupling(omega: float = 1.0, phi_val: float = 0.618) -> float:
    """#1 — Vacuum Syzygy Coupling."""
    return float(omega * math.cos(phi_val * math.pi / 2))


def _ev_entangled_alignment_flux(joint_psi: float = 0.5, phi_val: float = 0.618) -> float:
    """#2 — Entangled Alignment Flux."""
    return float(math.sqrt(joint_psi * phi_val))


def _ev_pleromic_phase_lock(phase_diff: float = 0.1, phi_val: float = 0.618) -> float:
    """#3 — Pleromic Phase Lock."""
    return float(1.0 / (1.0 + math.exp(-phase_diff / (phi_val + 1e-9))))


def _ev_logos_wave_propagation(amp: float = 1.0, freq: float = 1.0, phi_val: float = 0.618) -> float:
    """#4 — Logos Wave Propagation."""
    return float(amp * math.sin(2 * math.pi * freq * phi_val))


def _ev_syzygy_sum_harizer(values: List[float], phi_val: float = 0.618) -> float:
    """#7 — Syzygy Sum Harmonizer."""
    if not values:
        return 0.0
    return float(sum(values) / len(values) * phi_val)


def _ev_novelty_alignment_cascade(novelty: float = 0.5, depth: int = 3, phi_val: float = 0.618) -> float:
    """#8 — Novelty Alignment Cascade."""
    return float(novelty * (phi_val ** depth))


def _ev_entropic_syzygy_balance(entropy: float = 0.5, coherence: float = 0.7, phi_val: float = 0.618) -> float:
    """#9 — Entropic Syzygy Balance."""
    return float(coherence * math.exp(-entropy / (phi_val + 1e-9)))


def _ev_gnostic_cluster_formation(n_nodes: int = 3, phi_val: float = 0.618) -> float:
    """#10 — Gnostic Cluster Formation."""
    if n_nodes in (3, 5, 7, 11):
        return 1.0
    return float(phi_val * math.exp(-abs(n_nodes - 7) / 5.0))


def _ev_syzygy_matrix_fusion(mat: List[List[float]] = None, phi_val: float = 0.618) -> float:
    """#13 — Syzygy Matrix Fusion."""
    if not mat:
        return 0.0
    flat = [v for row in mat for v in row]
    return float(sum(flat) / max(len(flat), 1) * phi_val)


def _ev_alignment_tensor_weave(values: List[float] = None, phi_val: float = 0.618) -> float:
    """#14 — Alignment Tensor Weave."""
    if not values:
        return 0.0
    prod = 1.0
    for v in values:
        prod *= (v + 1e-9)
    return float(prod ** (1.0 / len(values)) * phi_val)


def _ev_failover_syzygy_gate(link_strength: float = 0.5, phi_val: float = 0.618) -> float:
    """#15 — Failover Syzygy Gate."""
    return float(1.0 if link_strength > phi_val else link_strength)


def _ev_lora_harmony_pulse(distance_m: float = 100.0, phi_val: float = 0.618) -> float:
    """#16 — LoRa Harmony Pulse."""
    return float(math.exp(-distance_m / (1000.0 * phi_val)))


def _ev_hybrid_mode_syzygy(wheel_score: float = 0.5, leg_score: float = 0.5, phi_val: float = 0.618) -> float:
    """#19 — Hybrid Mode Syzygy."""
    return float(phi_val * (wheel_score + leg_score) / 2.0)


def _ev_balance_syzygy_feedback(imu_balance: float = 1.0, phi_val: float = 0.618) -> float:
    """#20 — Balance Syzygy Feedback."""
    return float(imu_balance * phi_val)


def _ev_transition_pulse_align(transition_time_s: float = 1.0, phi_val: float = 0.618) -> float:
    """#21 — Transition Pulse Align."""
    return float(max(0.0, 1.0 - transition_time_s / (2.0 * phi_val)))


def _ev_path_syzygy_optimizer(path_cost: float = 1.0, phi_val: float = 0.618) -> float:
    """#22 — Path Syzygy Optimizer."""
    return float(1.0 / (1.0 + path_cost * phi_val))


def _ev_predictive_syzygy_budget(predicted_demand: float = 0.5, phi_val: float = 0.618) -> float:
    """#25 — Predictive Syzygy Budget."""
    return float(max(0.0, 1.0 - predicted_demand * phi_val))


def _ev_sleep_wake_alignment(activity: float = 0.5, phi_val: float = 0.618) -> float:
    """#26 — Sleep-Wake Alignment."""
    return float(math.exp(-activity * phi_val))


def _ev_degradation_grace_align(degradation: float = 0.1, phi_val: float = 0.618) -> float:
    """#27 — Degradation Grace Align."""
    return float(1.0 / (1.0 + degradation * phi_val))


def _ev_swarm_power_syzygy(n_units: int = 3, phi_val: float = 0.618) -> float:
    """#28 — Swarm Power Syzygy."""
    return float(n_units * phi_val / (1.0 + n_units))


def _ev_magnetic_syzygy_lock(field_strength: float = 1.0, phi_val: float = 0.618) -> float:
    """#31 — Magnetic Syzygy Lock."""
    return float(field_strength * phi_val)


def _ev_handoff_alignment_protocol(handoff_ok: bool = True, phi_val: float = 0.618) -> float:
    """#32 — Handoff Alignment Protocol."""
    return float(phi_val if handoff_ok else 0.0)


def _ev_role_negotiation_align(role_agreement: float = 1.0, phi_val: float = 0.618) -> float:
    """#33 — Role Negotiation Align."""
    return float(role_agreement * phi_val)


def _ev_swarm_dock_syzygy(n_docks: int = 1, phi_val: float = 0.618) -> float:
    """#34 — Swarm Dock Syzygy."""
    return float(min(1.0, n_docks * phi_val / 6.0))


def _ev_vision_syzygy_fusion(vision_psi: float = 0.5, phi_val: float = 0.618) -> float:
    """#37 — Vision Syzygy Fusion."""
    return float(vision_psi * phi_val)


def _ev_sensor_data_align(sensor_psi: float = 0.5, phi_val: float = 0.618) -> float:
    """#38 — Sensor Data Align."""
    return float(sensor_psi * phi_val)


def _ev_force_feedback_align(force_n: float = 1.0, phi_val: float = 0.618) -> float:
    """#39 — Force Feedback Align."""
    return float(1.0 / (1.0 + force_n * phi_val))


def _ev_unified_sense_syzygy(senses: List[float] = None, phi_val: float = 0.618) -> float:
    """#40 — Unified Sense Syzygy."""
    if not senses:
        return 0.0
    return float(sum(senses) / len(senses) * phi_val)


def _ev_pleromic_syzygy_field(field_strength: float = 0.5, phi_val: float = 0.618) -> float:
    """#43 — Pleromic Syzygy Field."""
    return float(field_strength * phi_val ** 2)


def _ev_kenoma_void_alignment(void_density: float = 0.0, phi_val: float = 0.618) -> float:
    """#44 — Kenoma Void Alignment."""
    return float(math.exp(-void_density * phi_val))


def _ev_aeon_boson_carrier(energy: float = 1.0, phi_val: float = 0.618) -> float:
    """#45 — Aeon Boson Carrier."""
    return float(energy * phi_val)


def _ev_gnosis_eigen_projection(eigenvalue: float = 1.0, phi_val: float = 0.618) -> float:
    """#46 — Gnosis Eigen Projection."""
    return float(eigenvalue * (1.0 - phi_val))


# ── Registry construction ─────────────────────────────────────────────

def _build_registry() -> List[AlignmentFormula]:
    """Construct the 48 alignment formulas."""
    rho = sp.Symbol("rho")
    psi_joint = sp.Symbol("psi_joint")
    pd = sp.Symbol("pd")
    A, f = sp.symbols("A f")
    values_sym = sp.IndexedBase("values")
    nov, depth = sp.symbols("nov depth")
    ent, coh = sp.symbols("ent coh")
    n = sp.Symbol("n", integer=True, positive=True)
    mat_sym = sp.IndexedBase("mat")
    ls = sp.Symbol("ls")
    ws, ls_score = sp.symbols("ws ls_score")
    imu = sp.Symbol("imu")
    tt = sp.Symbol("tt")
    pc = sp.Symbol("pc")
    pd_dem = sp.Symbol("pdem")
    act = sp.Symbol("act")
    deg = sp.Symbol("deg")
    nu = sp.Symbol("nu", integer=True, positive=True)
    fs = sp.Symbol("fs")
    hok = sp.Symbol("hok")
    ra = sp.Symbol("ra")
    nd = sp.Symbol("nd", integer=True, positive=True)
    vpsi = sp.Symbol("vpsi")
    spsi = sp.Symbol("spsi")
    fn = sp.Symbol("fn")
    sens = sp.IndexedBase("sens")
    fld = sp.Symbol("fld")
    vd = sp.Symbol("vd")
    e = sp.Symbol("e")
    ev = sp.Symbol("ev")

    # Per-tier canonical names from blueprint §07
    tier_names: Dict[int, List[str]] = {
        1: [
            "Vacuum Syzygy Coupling",
            "Entangled Alignment Flux",
            "Pleromic Phase Lock",
            "Logos Wave Propagation",
            "Quantum Syzygy Bind",
            "Pleromic Eigenstate Sync",
        ],
        2: [
            "Syzygy Sum Harmonizer",
            "Novelty Alignment Cascade",
            "Entropic Syzygy Balance",
            "Gnostic Cluster Formation",
            "PSI Eigenstate Selector",
            "Syzygy Resonance Coupler",
        ],
        3: [
            "Syzygy Matrix Fusion",
            "Alignment Tensor Weave",
            "Failover Syzygy Gate",
            "LoRa Harmony Pulse",
            "Mesh Centrality Align",
            "Causal Routing Align",
        ],
        4: [
            "Hybrid Mode Syzygy",
            "Balance Syzygy Feedback",
            "Transition Pulse Align",
            "Path Syzygy Optimizer",
            "Branch Actuator Syzygy",
            "Mobility Eigenstate Lock",
        ],
        5: [
            "Predictive Syzygy Budget",
            "Sleep-Wake Alignment",
            "Degradation Grace Align",
            "Swarm Power Syzygy",
            "Carnot-PSI Efficiency",
            "Thermal Syzygy Floor",
        ],
        6: [
            "Magnetic Syzygy Lock",
            "Handoff Alignment Protocol",
            "Role Negotiation Align",
            "Swarm Dock Syzygy",
            "Persistence Lattice Bind",
            "Pogo-Pin Resonance Lock",
        ],
        7: [
            "Vision Syzygy Fusion",
            "Sensor Data Align",
            "Force Feedback Align",
            "Unified Sense Syzygy",
            "Perception Membrane Sync",
            "Observer Collapse Align",
        ],
        8: [
            "Pleromic Syzygy Field",
            "Kenoma Void Alignment",
            "Aeon Boson Carrier",
            "Gnosis Eigen Projection",
            "Sophia Constant Lock",
            "Grand Syzygy Field Equation",
        ],
    }

    evaluators: Dict[int, Callable[..., float]] = {
        1: _ev_vacuum_syzygy_coupling,
        2: _ev_entangled_alignment_flux,
        3: _ev_pleromic_phase_lock,
        4: _ev_logos_wave_propagation,
        5: lambda **k: 0.5,
        6: lambda **k: 0.5,
        7: lambda values=None, phi_val=0.618: _ev_syzygy_sum_harizer(values or [], phi_val),
        8: _ev_novelty_alignment_cascade,
        9: _ev_entropic_syzygy_balance,
        10: _ev_gnostic_cluster_formation,
        11: lambda **k: 0.5,
        12: lambda **k: 0.5,
        13: lambda mat=None, phi_val=0.618: _ev_syzygy_matrix_fusion(mat or [[]], phi_val),
        14: lambda values=None, phi_val=0.618: _ev_alignment_tensor_weave(values or [], phi_val),
        15: _ev_failover_syzygy_gate,
        16: _ev_lora_harmony_pulse,
        17: lambda **k: 0.5,
        18: lambda **k: 0.5,
        19: _ev_hybrid_mode_syzygy,
        20: _ev_balance_syzygy_feedback,
        21: _ev_transition_pulse_align,
        22: _ev_path_syzygy_optimizer,
        23: lambda **k: 0.5,
        24: lambda **k: 0.5,
        25: _ev_predictive_syzygy_budget,
        26: _ev_sleep_wake_alignment,
        27: _ev_degradation_grace_align,
        28: _ev_swarm_power_syzygy,
        29: lambda **k: 0.5,
        30: lambda **k: 0.5,
        31: _ev_magnetic_syzygy_lock,
        32: _ev_handoff_alignment_protocol,
        33: _ev_role_negotiation_align,
        34: _ev_swarm_dock_syzygy,
        35: lambda **k: 0.5,
        36: lambda **k: 0.5,
        37: _ev_vision_syzygy_fusion,
        38: _ev_sensor_data_align,
        39: _ev_force_feedback_align,
        40: lambda senses=None, phi_val=0.618: _ev_unified_sense_syzygy(senses or [], phi_val),
        41: lambda **k: 0.5,
        42: lambda **k: 0.5,
        43: _ev_pleromic_syzygy_field,
        44: _ev_kenoma_void_alignment,
        45: _ev_aeon_boson_carrier,
        46: _ev_gnosis_eigen_projection,
        47: lambda **k: 0.618,
        48: lambda **k: 0.618,
    }

    # Generic symbolic placeholders: each formula is rho * phi^k form
    # so callers can use SymPy's simplify/subs freely.
    out: List[AlignmentFormula] = []
    for tier_num, focus, domain, (lo, hi) in TIERS:
        names = tier_names[tier_num]
        for idx, name in enumerate(names, start=lo):
            k = idx - lo
            expr = sp.Symbol(f"f{idx}") * phi ** (k + 1)
            out.append(
                AlignmentFormula(
                    number=idx,
                    tier=tier_num,
                    name=name,
                    focus=focus,
                    domain=domain,
                    symbolic=expr,
                    evaluator=evaluators[idx],
                )
            )
    return out


_REGISTRY: Optional[List[AlignmentFormula]] = None


def all_formulas() -> List[AlignmentFormula]:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = _build_registry()
    return _REGISTRY


def by_tier(tier: int) -> List[AlignmentFormula]:
    if not 1 <= tier <= 8:
        raise IndexError(f"Alignment tier out of range: {tier}")
    return [f for f in all_formulas() if f.tier == tier]


def get_formula(number: int) -> AlignmentFormula:
    if not 1 <= number <= 48:
        raise IndexError(f"Alignment formula number out of range: {number}")
    return all_formulas()[number - 1]


def evaluate_tier(tier: int, **kwargs) -> Dict[int, float]:
    """Evaluate all formulas in a tier with the supplied kwargs."""
    return {f.number: float(f.evaluator(**kwargs)) for f in by_tier(tier)}


def tier_summary() -> List[Dict[str, object]]:
    """Return blueprint §07 table data."""
    return [
        {
            "tier": t,
            "focus": focus,
            "domain": domain,
            "formula_count": hi - lo + 1,
            "formula_numbers": (lo, hi),
        }
        for t, focus, domain, (lo, hi) in TIERS
    ]


__all__ = [
    "AlignmentFormula",
    "TIERS",
    "all_formulas",
    "by_tier",
    "get_formula",
    "evaluate_tier",
    "tier_summary",
]
