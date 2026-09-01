"""Tests for the 48 Alignment Formulas."""

from __future__ import annotations

import pytest

from aeon_embodiment.alignment import (
    all_formulas,
    by_tier,
    get_formula,
    evaluate_tier,
    tier_summary,
)


def test_registry_has_48():
    assert len(all_formulas()) == 48


def test_formulas_numbered_1_to_48():
    nums = [f.number for f in all_formulas()]
    assert nums == list(range(1, 49))


def test_six_formulas_per_tier():
    for tier in range(1, 9):
        assert len(by_tier(tier)) == 6


def test_get_formula_out_of_range():
    with pytest.raises(IndexError):
        get_formula(0)
    with pytest.raises(IndexError):
        get_formula(49)


def test_formula_has_symbolic_and_evaluator():
    f = get_formula(1)
    assert f.symbolic is not None
    assert callable(f.evaluator)


def test_tier_metadata():
    summary = tier_summary()
    assert len(summary) == 8
    for entry in summary:
        assert entry["formula_count"] == 6
        assert "Quantum" in entry["domain"] or "Distributed" in entry["domain"] \
            or "Neuromorphic" in entry["domain"] or "Holographic" in entry["domain"] \
            or "Retrocausal" in entry["domain"]


def test_evaluate_tier_returns_floats():
    out = evaluate_tier(1)
    assert len(out) == 6
    for k, v in out.items():
        assert isinstance(v, float)
        assert -1e6 < v < 1e6


def test_formula_tier_focus():
    f = get_formula(1)
    assert f.tier == 1
    assert f.focus == "Quantum Syzygy"
    assert f.domain == "Quantum Information Theory"


def test_specific_formula_evaluators():
    # Formula #1 = Vacuum Syzygy Coupling
    v1 = get_formula(1).evaluator(omega=1.0, phi_val=0.618)
    assert abs(v1 - 1.0 * __import__("math").cos(0.618 * 3.14159 / 2)) < 1e-6

    # Formula #16 = LoRa Harmony Pulse
    v16 = get_formula(16).evaluator(distance_m=100.0, phi_val=0.618)
    assert 0 <= v16 <= 1

    # Formula #31 = Magnetic Syzygy Lock
    v31 = get_formula(31).evaluator(field_strength=1.0, phi_val=0.618)
    assert v31 == pytest.approx(0.618, abs=1e-6)
