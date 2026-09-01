"""Tests for TripleMeshComms."""

from __future__ import annotations

import pytest

from aeon_embodiment.core import MeshLayer, TripleMeshComms


@pytest.fixture
def mesh():
    return TripleMeshComms()


def test_pick_layer_returns_wifi_when_strong(mesh):
    mesh.report_link(MeshLayer.WIFI, "torso", rssi_dbm=-50.0, latency_ms=8.0)
    layer = mesh.pick_layer("torso")
    assert layer == MeshLayer.WIFI


def test_pick_layer_falls_back_to_bt(mesh):
    # Strong BT but weak WiFi
    mesh.report_link(MeshLayer.WIFI, "torso", rssi_dbm=-95.0, latency_ms=80.0)
    mesh.report_link(MeshLayer.BT, "torso", rssi_dbm=-60.0, latency_ms=20.0)
    layer = mesh.pick_layer("torso")
    assert layer == MeshLayer.BT


def test_pick_layer_returns_none_when_all_dead(mesh):
    mesh.report_link(MeshLayer.WIFI, "torso", rssi_dbm=-95.0, latency_ms=80.0)
    mesh.report_link(MeshLayer.BT, "torso", rssi_dbm=-95.0, latency_ms=80.0)
    mesh.report_link(MeshLayer.LORA, "torso", rssi_dbm=-150.0, latency_ms=1000.0)
    assert mesh.pick_layer("torso") is None


def test_send_uses_best_layer(mesh):
    mesh.report_link(MeshLayer.WIFI, "head", rssi_dbm=-50.0, latency_ms=10.0)
    assert mesh.send("head", b"hello")
    hist = mesh.history(1)[0]
    assert hist["layer"] == "wifi"
    assert hist["bytes"] == 5


def test_send_forces_long_range_qos(mesh):
    mesh.report_link(MeshLayer.WIFI, "head", rssi_dbm=-50.0, latency_ms=10.0)
    mesh.report_link(MeshLayer.LORA, "head", rssi_dbm=-110.0, latency_ms=180.0)
    mesh.send("head", b"sos", qos="long_range")
    assert mesh.active_layer() == MeshLayer.LORA


def test_failover_increments_counter(mesh):
    mesh.report_link(MeshLayer.WIFI, "torso", rssi_dbm=-50.0, latency_ms=10.0)
    # First send — initial layer assignment (not counted as failover)
    mesh.send("torso", b"a")
    assert mesh.failover_count() == 0
    # Force a different layer via QoS — should count as a failover
    mesh.send("torso", b"sos", qos="long_range")
    assert mesh.failover_count() >= 1


def test_broadcast_reaches_all(mesh):
    for n in ("a", "b", "c"):
        mesh.report_link(MeshLayer.WIFI, n, rssi_dbm=-50.0, latency_ms=10.0)
    results = mesh.broadcast(b"hi")
    assert set(results.keys()) == {"a", "b", "c"}
    assert all(results.values())


def test_link_quality_report(mesh):
    mesh.report_link(MeshLayer.WIFI, "torso", rssi_dbm=-50.0, latency_ms=10.0)
    q = mesh.link_quality()
    assert "torso" in q
    assert "wifi_rssi" in q["torso"]
