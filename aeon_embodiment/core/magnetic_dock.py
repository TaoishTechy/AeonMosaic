"""aeon_embodiment.core.magnetic_dock — Magnetic pogo-pin docking manager.

Each docking face has:
    - Magnetic pogo pins (data + power)
    - A GPIO interrupt (gpiozero.Button) that fires on physical connection
    - Auto role-reassignment logic (the docking frame declares which slot
      the partner node is occupying)

When a dock event fires, the manager:
    1. Updates its own DockState
    2. Notifies the ModularBody registry (which adds the graph edge)
    3. Negotiates power handoff (which side is source/sink)
    4. Triggers role reassignment via NetworkX bipartite_matching (blueprint §04)
"""

from __future__ import annotations

import enum
import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

logger = logging.getLogger("aeon_embodiment.dock")


class DockState(str, enum.Enum):
    UNDOCKED = "undocked"
    DETECTED = "detected"          # pogo pins just touched
    NEGOTIATING = "negotiating"    # role/power negotiation in progress
    DOCKED = "docked"              # fully joined
    FAULT = "fault"


@dataclass
class DockEvent:
    """A single docking face event."""

    face_id: str
    state: DockState
    partner_node_id: Optional[str] = None
    power_role: str = "sink"   # "source" | "sink" | "peer"
    timestamp: float = field(default_factory=time.time)


# Callback: (face_id, DockEvent) -> None
DockCallback = Callable[[str, DockEvent], None]


class MagneticDockManager:
    """Per-node manager for one or more magnetic pogo-pin docking faces."""

    def __init__(self, faces: List[str], is_source_default: bool = False) -> None:
        self._lock = threading.RLock()
        # face_id -> current event/state
        self._faces: Dict[str, DockEvent] = {
            f: DockEvent(face_id=f, state=DockState.UNDOCKED) for f in faces
        }
        self._is_source_default = is_source_default
        self._callbacks: List[DockCallback] = []

    # ── Event ingestion (from GPIO interrupts) ──────────────────────────

    def on_pogo_pin_high(self, face_id: str) -> None:
        """GPIO interrupt handler — magnetic pogo pins just made contact."""
        with self._lock:
            if face_id not in self._faces:
                logger.warning("Unknown face_id %s", face_id)
                return
            ev = self._faces[face_id]
            ev.state = DockState.DETECTED
            ev.timestamp = time.time()
        self._emit(face_id, "pogo_pin_high")
        # Begin negotiation
        self._negotiate(face_id)

    def on_pogo_pin_low(self, face_id: str) -> None:
        """GPIO interrupt handler — magnetic pogo pins just disconnected."""
        with self._lock:
            if face_id not in self._faces:
                return
            ev = self._faces[face_id]
            ev.state = DockState.UNDOCKED
            ev.partner_node_id = None
            ev.power_role = "sink"
            ev.timestamp = time.time()
        self._emit(face_id, "pogo_pin_low")

    # ── Negotiation ─────────────────────────────────────────────────────

    def _negotiate(self, face_id: str) -> None:
        with self._lock:
            ev = self._faces[face_id]
            ev.state = DockState.NEGOTIATING
            # Power handoff: source wins if it has more battery (simulated)
            ev.power_role = "source" if self._is_source_default else "sink"
            # Partner id is filled in by the higher layer via set_partner()
        self._emit(face_id, "negotiating")

    def set_partner(self, face_id: str, partner_node_id: str) -> bool:
        """Called by ModularBody once the partner's identity is broadcast."""
        with self._lock:
            ev = self._faces.get(face_id)
            if ev is None or ev.state not in (DockState.DETECTED, DockState.NEGOTIATING):
                return False
            ev.partner_node_id = partner_node_id
            ev.state = DockState.DOCKED
            ev.timestamp = time.time()
        self._emit(face_id, "docked")
        return True

    # ── Introspection ──────────────────────────────────────────────────

    def get_state(self, face_id: str) -> Optional[DockState]:
        with self._lock:
            ev = self._faces.get(face_id)
            return ev.state if ev else None

    def docked_partners(self) -> Dict[str, str]:
        """Return {face_id: partner_node_id} for all docked faces."""
        with self._lock:
            return {
                fid: ev.partner_node_id
                for fid, ev in self._faces.items()
                if ev.state == DockState.DOCKED and ev.partner_node_id
            }

    def snapshot(self) -> List[DockEvent]:
        with self._lock:
            return [
                DockEvent(
                    face_id=ev.face_id,
                    state=ev.state,
                    partner_node_id=ev.partner_node_id,
                    power_role=ev.power_role,
                    timestamp=ev.timestamp,
                )
                for ev in self._faces.values()
            ]

    # ── Callbacks ───────────────────────────────────────────────────────

    def on_event(self, cb: DockCallback) -> None:
        self._callbacks.append(cb)

    def _emit(self, face_id: str, kind: str) -> None:
        with self._lock:
            ev = self._faces.get(face_id)
            if ev is None:
                return
            # Hand out a defensive copy so callers can't mutate internals
            out = DockEvent(
                face_id=ev.face_id,
                state=ev.state,
                partner_node_id=ev.partner_node_id,
                power_role=ev.power_role,
                timestamp=ev.timestamp,
            )
        for cb in list(self._callbacks):
            try:
                cb(face_id, out)
            except Exception as exc:  # pragma: no cover - defensive
                logger.exception("Dock callback raised: %s", exc)


__all__ = [
    "MagneticDockManager",
    "DockEvent",
    "DockState",
    "DockCallback",
]
