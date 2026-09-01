"""Tests for MagneticDockManager."""

from __future__ import annotations

import pytest

from aeon_embodiment.core import DockState, MagneticDockManager


@pytest.fixture
def manager():
    return MagneticDockManager(faces=["face_top", "face_bottom"], is_source_default=True)


def test_starts_undocked(manager):
    assert manager.get_state("face_top") == DockState.UNDOCKED


def test_pogo_pin_high_transitions_to_detected(manager):
    manager.on_pogo_pin_high("face_top")
    assert manager.get_state("face_top") in (DockState.DETECTED, DockState.NEGOTIATING, DockState.DOCKED)


def test_full_dock_lifecycle(manager):
    events = []
    manager.on_event(lambda face_id, ev: events.append((face_id, ev.state)))
    manager.on_pogo_pin_high("face_top")
    # Should be negotiating at minimum
    assert manager.get_state("face_top") in (DockState.NEGOTIATING, DockState.DOCKED)
    manager.set_partner("face_top", "torso")
    assert manager.get_state("face_top") == DockState.DOCKED
    assert "torso" in manager.docked_partners().values()
    # Undock
    manager.on_pogo_pin_low("face_top")
    assert manager.get_state("face_top") == DockState.UNDOCKED
    # Events fired
    assert any(s == DockState.DOCKED for _, s in events)


def test_set_partner_rejected_when_not_negotiating(manager):
    assert not manager.set_partner("face_top", "torso")  # never detected


def test_unknown_face_ignored(manager):
    manager.on_pogo_pin_high("face_left_field")  # should not raise
    assert manager.get_state("face_left_field") is None


def test_snapshot_defensive_copy(manager):
    snap = manager.snapshot()
    assert len(snap) == 2
    snap[0].state = DockState.FAULT
    assert manager.get_state("face_top") == DockState.UNDOCKED


def test_power_role_source_when_default_is_source(manager):
    manager.on_pogo_pin_high("face_top")
    snap = manager.snapshot()
    top = [e for e in snap if e.face_id == "face_top"][0]
    assert top.power_role == "source"
