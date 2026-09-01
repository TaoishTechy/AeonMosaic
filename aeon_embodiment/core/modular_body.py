"""aeon_embodiment.core.modular_body — Node registry, discovery, role negotiation.

``ModularBody`` is the registry that maintains the live topology of the robot.
Internally it stores the body as a NetworkX graph — nodes are body segments
and edges are physical docking connections. When a limb detaches or re-docks,
the graph is mutated and all downstream subsystems are notified via callbacks.

This class is the central truth source for:
    - Node presence & liveness
    - Current docking topology (NetworkX ``Graph``)
    - Role reassignment when a node joins/leaves
    - OTA neural-weight sync (stub interface; pluggable transport)

It is deliberately decoupled from any ROS primitives so it can be unit-tested
in pure Python. The ROS 2 wrapper lives in ``aeon_embodiment.ros_bridge``.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Callable, Dict, Iterable, List, Optional

import networkx as nx

from .node import Node, NodeRole, NodeStatus

logger = logging.getLogger("aeon_embodiment.modular_body")


# Callback signature: (event_kind: str, payload: dict) -> None
TopologyCallback = Callable[[str, dict], None]


class ModularBody:
    """In-memory model of the modular robot topology."""

    def __init__(self, initial_nodes: Optional[Iterable[Node]] = None) -> None:
        self._lock = threading.RLock()
        self._nodes: Dict[str, Node] = {}
        self._graph: nx.Graph = nx.Graph()
        self._callbacks: List[TopologyCallback] = []

        if initial_nodes:
            for n in initial_nodes:
                self.register(n)

    # ── Node lifecycle ──────────────────────────────────────────────────

    def register(self, node: Node) -> None:
        """Add a node to the registry. Idempotent."""
        with self._lock:
            if node.id in self._nodes:
                logger.debug("Re-registering existing node %s", node.id)
            node.mark_seen()
            if node.status == NodeStatus.OFFLINE:
                node.status = NodeStatus.ONLINE
            self._nodes[node.id] = node
            self._graph.add_node(node.id, role=node.role.value, status=node.status.value)
        self._emit("node_registered", {"node_id": node.id, "role": node.role.value})

    def unregister(self, node_id: str) -> None:
        with self._lock:
            node = self._nodes.pop(node_id, None)
            if node is None:
                return
            # Cascade-undock neighbours
            for nbr in list(node.neighbours):
                nbr_node = self._nodes.get(nbr)
                if nbr_node:
                    nbr_node.undock(node_id)
            self._graph.remove_node(node_id)
        self._emit("node_unregistered", {"node_id": node_id})

    def get(self, node_id: str) -> Optional[Node]:
        with self._lock:
            return self._nodes.get(node_id)

    def all_nodes(self) -> List[Node]:
        with self._lock:
            return list(self._nodes.values())

    def online_nodes(self) -> List[Node]:
        with self._lock:
            return [n for n in self._nodes.values() if n.status != NodeStatus.OFFLINE]

    def heartbeat(self, node_id: str) -> bool:
        """Mark a node as recently seen. Returns True if node was found."""
        with self._lock:
            node = self._nodes.get(node_id)
            if node is None:
                return False
            node.mark_seen()
            if node.status == NodeStatus.OFFLINE:
                node.status = NodeStatus.ONLINE
            return True

    def cull_dead(self, timeout_s: float = 5.0) -> List[str]:
        """Mark nodes with stale heartbeats as OFFLINE. Returns culled IDs."""
        now = time.time()
        culled: List[str] = []
        with self._lock:
            for n in self._nodes.values():
                if n.status in (NodeStatus.ONLINE, NodeStatus.DOCKED) and not n.is_alive(
                    timeout_s=timeout_s, now=now
                ):
                    n.status = NodeStatus.OFFLINE
                    culled.append(n.id)
                    self._emit("node_timeout", {"node_id": n.id})
        return culled

    # ── Topology mutation ───────────────────────────────────────────────

    def dock(self, a: str, b: str) -> bool:
        """Record a physical dock between two nodes. Returns True on success."""
        with self._lock:
            na, nb = self._nodes.get(a), self._nodes.get(b)
            if na is None or nb is None:
                logger.warning("Dock refused — missing node(s): %s<->%s", a, b)
                return False
            na.dock(b)
            nb.dock(a)
            self._graph.add_edge(a, b, since=time.time())
        self._emit("dock", {"a": a, "b": b})
        return True

    def undock(self, a: str, b: str) -> bool:
        with self._lock:
            na, nb = self._nodes.get(a), self._nodes.get(b)
            if na is None or nb is None:
                return False
            na.undock(b)
            nb.undock(a)
            if self._graph.has_edge(a, b):
                self._graph.remove_edge(a, b)
        self._emit("undock", {"a": a, "b": b})
        return True

    def graph(self) -> nx.Graph:
        """Return a defensive copy of the current topology graph."""
        with self._lock:
            return self._graph.copy()

    # ── Role negotiation ────────────────────────────────────────────────

    def reassign_role(self, node_id: str, new_role: NodeRole) -> bool:
        """Reassign a node's role (e.g. left_arm becomes left_leg after re-dock)."""
        with self._lock:
            node = self._nodes.get(node_id)
            if node is None:
                return False
            old_role = node.role
            node.role = new_role
            if node_id in self._graph:
                self._graph.nodes[node_id]["role"] = new_role.value
        self._emit(
            "role_reassigned",
            {"node_id": node_id, "old": old_role.value, "new": new_role.value},
        )
        return True

    # ── OTA neural-weight sync (stub interface) ─────────────────────────

    def ota_sync_weights(self, source_id: str, weights_blob: bytes) -> bool:
        """Stub: push a neural weight blob from ``source_id`` to docked neighbours.

        In production this calls into the ROS 2 OTA service. Here it just
        records that a sync was requested.
        """
        with self._lock:
            src = self._nodes.get(source_id)
            if src is None:
                return False
            for nbr_id in src.neighbours:
                logger.info("OTA sync %s -> %s (%d bytes)", source_id, nbr_id, len(weights_blob))
        self._emit("ota_sync", {"source": source_id, "size": len(weights_blob)})
        return True

    # ── Callbacks ───────────────────────────────────────────────────────

    def on_topology_change(self, cb: TopologyCallback) -> None:
        self._callbacks.append(cb)

    def _emit(self, kind: str, payload: dict) -> None:
        # Snapshot to avoid mutation-during-iteration
        for cb in list(self._callbacks):
            try:
                cb(kind, payload)
            except Exception as exc:  # pragma: no cover - defensive
                logger.exception("Topology callback raised: %s", exc)

    # ── Introspection ──────────────────────────────────────────────────

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        with self._lock:
            return (
                f"ModularBody(nodes={len(self._nodes)}, "
                f"edges={self._graph.number_of_edges()})"
            )

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "nodes": [n.to_dict() for n in self._nodes.values()],
                "edges": [list(e) for e in self._graph.edges()],
            }


__all__ = ["ModularBody", "TopologyCallback"]
