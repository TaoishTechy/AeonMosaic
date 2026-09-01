"""Tests for ModularBody topology management."""

from __future__ import annotations

import pytest

from aeon_embodiment.core import Node, NodeRole, NodeStatus, ModularBody


@pytest.fixture
def six_node_body():
    nodes = [
        Node(id="head", role=NodeRole.HEAD, compute="rpi_4"),
        Node(id="torso", role=NodeRole.TORSO, compute="rpi_3a_plus"),
        Node(id="left_arm", role=NodeRole.LEFT_ARM),
        Node(id="right_arm", role=NodeRole.RIGHT_ARM),
        Node(id="left_leg", role=NodeRole.LEFT_LEG),
        Node(id="right_leg", role=NodeRole.RIGHT_LEG),
    ]
    body = ModularBody(initial_nodes=nodes)
    for limb in ("head", "left_arm", "right_arm", "left_leg", "right_leg"):
        body.dock("torso", limb)
    return body


def test_register_six_nodes(six_node_body):
    assert len(six_node_body.all_nodes()) == 6
    assert six_node_body.get("head").role == NodeRole.HEAD


def test_dock_creates_edge(six_node_body):
    g = six_node_body.graph()
    assert g.number_of_edges() == 5
    assert g.has_edge("torso", "head")
    # Both sides record the neighbour
    head = six_node_body.get("head")
    assert "torso" in head.neighbours
    assert head.status == NodeStatus.DOCKED


def test_undock_removes_edge(six_node_body):
    ok = six_node_body.undock("torso", "head")
    assert ok
    g = six_node_body.graph()
    assert not g.has_edge("torso", "head")
    head = six_node_body.get("head")
    assert "torso" not in head.neighbours
    # After undocking all neighbours, status flips to DETACHED
    assert head.status == NodeStatus.DETACHED


def test_register_idempotent():
    body = ModularBody()
    n = Node(id="head", role=NodeRole.HEAD)
    body.register(n)
    body.register(n)  # should not duplicate
    assert len(body.all_nodes()) == 1


def test_unregister_cascades_undock():
    body = ModularBody(initial_nodes=[
        Node(id="head", role=NodeRole.HEAD),
        Node(id="torso", role=NodeRole.TORSO),
    ])
    body.dock("head", "torso")
    body.unregister("torso")
    head = body.get("head")
    assert head is not None
    assert "torso" not in head.neighbours
    assert body.get("torso") is None


def test_reassign_role():
    body = ModularBody(initial_nodes=[Node(id="arm", role=NodeRole.LEFT_ARM)])
    assert body.reassign_role("arm", NodeRole.RIGHT_ARM)
    assert body.get("arm").role == NodeRole.RIGHT_ARM


def test_heartbeat():
    body = ModularBody(initial_nodes=[Node(id="head", role=NodeRole.HEAD)])
    body.get("head").status = NodeStatus.OFFLINE
    assert body.heartbeat("head")
    assert body.get("head").status == NodeStatus.ONLINE


def test_cull_dead_marks_stale_offline():
    body = ModularBody(initial_nodes=[Node(id="head", role=NodeRole.HEAD)])
    # Backdate the heartbeat
    body.get("head").last_seen = time.time() - 100
    culled = body.cull_dead(timeout_s=5.0)
    assert culled == ["head"]
    assert body.get("head").status == NodeStatus.OFFLINE


def test_topology_callback_fires(six_node_body):
    events = []
    six_node_body.on_topology_change(lambda kind, payload: events.append((kind, payload)))
    six_node_body.dock("head", "left_arm")
    assert any(kind == "dock" for kind, _ in events)


def test_ota_sync_logs(six_node_body):
    # Should succeed without raising — just records
    assert six_node_body.ota_sync_weights("torso", b"\x00" * 16)


def test_snapshot_round_trip(six_node_body):
    snap = six_node_body.snapshot()
    assert "nodes" in snap and "edges" in snap
    assert len(snap["nodes"]) == 6


import time  # used by test_cull_dead
