"""aeon_embodiment.core.node — AeonMosaic node primitives.

A *node* is a body segment with its own compute, sensors, and a slice of the
system's Psychic State Index (PSI). Nodes correspond physically to one of
six agent slots on the robot:

    HEAD  ·  TORSO  ·  LEFT_ARM  ·  RIGHT_ARM  ·  LEFT_LEG  ·  RIGHT_LEG

Every node carries:
    - identity (id, role, status)
    - capability bag (compute class, sensor list, comm links)
    - PSI slice (localised Sophia-weighted psychic state)
    - dock state (which neighbours it is currently joined to)
"""

from __future__ import annotations

import enum
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


class NodeRole(str, enum.Enum):
    """The six canonical agent slots on the robot."""

    HEAD = "head"
    TORSO = "torso"
    LEFT_ARM = "left_arm"
    RIGHT_ARM = "right_arm"
    LEFT_LEG = "left_leg"
    RIGHT_LEG = "right_leg"

    @classmethod
    def all(cls) -> Tuple["NodeRole", ...]:
        return tuple(cls)


class NodeStatus(str, enum.Enum):
    """Lifecycle status of a node."""

    OFFLINE = "offline"
    BOOTING = "booting"
    ONLINE = "online"
    DOCKED = "docked"
    DETACHED = "detached"
    FAULT = "fault"


@dataclass
class Node:
    """A single AeonMosaic cognitive agent.

    Attributes
    ----------
    id:
        Unique short identifier (e.g. ``"head"``).
    role:
        Canonical slot from :class:`NodeRole`.
    compute:
        Compute class string (e.g. ``"rpi4"`` / ``"rpi_zero_2w"`` /
        ``"rpi_3a_plus"``).
    sensors:
        List of sensor IDs attached to this node.
    psi_slice:
        Local PSI contribution in ``[0, 1]``.
    status:
        Current lifecycle status.
    neighbours:
        IDs of nodes currently docked to this one.
    last_seen:
        Epoch-millis of last successful heartbeat.
    """

    id: str
    role: NodeRole
    compute: str = "rpi_zero_2w"
    sensors: List[str] = field(default_factory=list)
    psi_slice: float = 0.5
    status: NodeStatus = NodeStatus.OFFLINE
    neighbours: List[str] = field(default_factory=list)
    last_seen: float = field(default_factory=time.time)

    # ── Mutation helpers ─────────────────────────────────────────────────

    def mark_seen(self) -> None:
        self.last_seen = time.time()

    def is_alive(self, timeout_s: float = 5.0, now: Optional[float] = None) -> bool:
        """Heartbeat liveness check."""
        now = now if now is not None else time.time()
        return (now - self.last_seen) <= timeout_s

    def dock(self, neighbour_id: str) -> None:
        if neighbour_id not in self.neighbours:
            self.neighbours.append(neighbour_id)
        if self.status == NodeStatus.ONLINE:
            self.status = NodeStatus.DOCKED

    def undock(self, neighbour_id: str) -> None:
        if neighbour_id in self.neighbours:
            self.neighbours.remove(neighbour_id)
        if not self.neighbours and self.status == NodeStatus.DOCKED:
            self.status = NodeStatus.DETACHED

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "role": self.role.value,
            "compute": self.compute,
            "sensors": list(self.sensors),
            "psi_slice": float(self.psi_slice),
            "status": self.status.value,
            "neighbours": list(self.neighbours),
            "last_seen": float(self.last_seen),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, object]) -> "Node":
        return cls(
            id=str(d["id"]),
            role=NodeRole(str(d["role"])),
            compute=str(d.get("compute", "rpi_zero_2w")),
            sensors=list(d.get("sensors", [])),  # type: ignore[arg-type]
            psi_slice=float(d.get("psi_slice", 0.5)),
            status=NodeStatus(str(d.get("status", "offline"))),
            neighbours=list(d.get("neighbours", [])),  # type: ignore[arg-type]
            last_seen=float(d.get("last_seen", time.time())),
        )


__all__ = ["Node", "NodeRole", "NodeStatus"]
