"""Tests for the Sophia framework — 12 foundation equations."""

from __future__ import annotations

import math
import pytest

from aeon_embodiment.sophia import (
    SOPHIA_PHI,
    COHERENCE_FLOOR,
    all_equations,
    get_equation,
    evaluate_all,
)


def test_constants():
    assert SOPHIA_PHI == 0.618
    assert COHERENCE_FLOOR == 0.70


def test_twelve_equations_present():
    eqs = all_equations()
    assert len(eqs) == 12
    # Indices 1..12 in order
    assert [e.index for e in eqs] == list(range(1, 13))


def test_equation_has_symbolic_and_evaluator():
    eq = get_equation(1)
    assert eq.name == "Sophia-Vacuum Coupling"
    # SymPy expression should not be None
    assert eq.symbolic is not None
    # Evaluator should return a float
    v = eq.evaluator()
    assert isinstance(v, float)


def test_eq1_sophia_vacuum_coupling():
    eq = get_equation(1)
    # Aligned with phi → maximum vacuum energy (no attenuation)
    v_aligned = eq.evaluator(consciousness_density=SOPHIA_PHI, vacuum_baseline=1.0, phi_val=SOPHIA_PHI)
    v_off = eq.evaluator(consciousness_density=0.0, vacuum_baseline=1.0, phi_val=SOPHIA_PHI)
    assert v_aligned == pytest.approx(1.0, abs=1e-9)
    assert v_off < v_aligned


def test_eq3_syzygy_resonance_frequency():
    eq = get_equation(3)
    # f = c / (d * phi^2) ; for d=1m, expected ≈ 299_792_458 / 0.381924 ≈ 785M Hz
    v = eq.evaluator(inter_node_distance_m=1.0, phi_val=SOPHIA_PHI)
    assert v == pytest.approx(299_792_458.0 / (SOPHIA_PHI ** 2), rel=1e-6)


def test_eq4_logos_recursion_metric_converges_to_one():
    eq = get_equation(4)
    # With deep recursion + high convergence_rate, should approach 1
    v = eq.evaluator(recursion_depth=100, convergence_rate=10.0, phi_val=SOPHIA_PHI)
    assert v > 0.99


def test_eq9_carmichael_prime():
    eq = get_equation(9)
    assert eq.evaluator(node_count=3) == 1.0
    assert eq.evaluator(node_count=4) < 1.0
    assert eq.evaluator(node_count=11) == 1.0


def test_eq6_archontic_impedance_rises_with_entropy():
    eq = get_equation(6)
    z_low = eq.evaluator(entropic_code_ratio=0.01)
    z_high = eq.evaluator(entropic_code_ratio=1.0)
    assert z_high > z_low


def test_evaluate_all_returns_12_values():
    out = evaluate_all()
    assert len(out) == 12
    for k, v in out.items():
        assert isinstance(v, float)
        assert not math.isnan(v)
