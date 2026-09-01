"""Tests for the 48 Alien Tier Enhancements registry."""

from __future__ import annotations

import pytest

from aeon_embodiment.enhancements import (
    Enhancement,
    Priority,
    Tier,
    TIER_AVERAGES,
    all_enhancements,
    by_number,
    by_priority,
    by_subsystem,
    by_tier,
    count_by_subsystem,
    to_json,
)


def test_registry_has_48():
    assert len(all_enhancements()) == 48


def test_tier_distribution_six_each():
    for tier in Tier:
        assert len(by_tier(tier)) == 6


def test_numbers_1_to_48_in_order():
    nums = [e.number for e in all_enhancements()]
    assert nums == list(range(1, 49))


def test_by_number_lookup():
    e = by_number(1)
    assert e.name == "Subobject Syzygy Weave"
    assert e.tier == Tier.I
    assert e.priority == Priority.TOP


def test_by_number_out_of_range():
    with pytest.raises(IndexError):
        by_number(0)
    with pytest.raises(IndexError):
        by_number(49)


def test_composite_scores_match_blueprint_within_tolerance():
    """Spot-check that composite scores round-trip close to the blueprint values."""
    # Blueprint §06 verbatim
    expected = {
        1: 335.9, 2: 335.2, 3: 331.2, 4: 331.0, 5: 330.5, 6: 330.4,
        7: 330.3, 12: 329.0, 18: 327.4, 24: 326.5, 30: 325.4,
        36: 324.8, 42: 324.7, 48: 324.1,
    }
    for num, exp in expected.items():
        e = by_number(num)
        assert e.composite_score() == pytest.approx(exp, abs=0.5), f"#{num}: {e.composite_score()} vs {exp}"


def test_tier_averages_present():
    for tier in Tier:
        assert tier in TIER_AVERAGES


def test_by_subsystem_lookup():
    matches = by_subsystem("DistributedPSI")
    assert len(matches) >= 10
    matches = by_subsystem("ModularBody")
    assert len(matches) >= 18


def test_by_priority_lookup():
    top = by_priority(Priority.TOP)
    assert len(top) == 6
    seed = by_priority(Priority.SEED)
    assert len(seed) == 6


def test_count_by_subsystem():
    """Per-subsystem counts based on the verbatim blueprint §06 registry.

    Note: the blueprint's "Enhancement Distribution by Subsystem" summary
    table lists DistributedPSI=9 / HybridMobility=9 / TripleMeshComms=5,
    but counting from the explicit per-row registry yields 10/7/6
    respectively. We treat the registry rows as authoritative.
    """
    counts = count_by_subsystem()
    assert counts["ModularBody"] == 18
    assert counts["DistributedPSI"] == 10
    assert counts["HybridMobilityController"] == 7
    assert counts["MagneticDockManager"] == 7
    assert counts["TripleMeshComms"] == 6
    assert sum(counts.values()) == 48


def test_to_json_serialisable():
    import json
    data = json.loads(to_json())
    assert len(data) == 48
    assert all("composite" in e for e in data)
