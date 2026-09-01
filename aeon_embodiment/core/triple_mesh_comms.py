"""aeon_embodiment.core.triple_mesh_comms — TripleMesh failover coordinator.

Implements the three-layer failover hierarchy described in blueprint §02:

    Primary   → ESP32-C6 WiFi 6 Mesh  (~5 ms, 100 m indoor)
    Backup    → Bluetooth 5.3          (~15 ms, 30 m, auto-failover)
    Long-Range → LoRa RA-02 via RadioLib (~200 ms, 2+ km, SOS beacons / swarm)

The class is the in-process orchestrator — it tracks per-link signal
strength, picks the best available layer for any given message, and falls
over automatically when the primary layer drops below a configurable RSSI
threshold. The actual RF work is delegated to a transport adapter so the
class is unit-testable on a dev machine with a loopback transport.
"""

from __future__ import annotations

import enum
import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Callable, Deque, Dict, List, Optional, Tuple

logger = logging.getLogger("aeon_embodiment.triple_mesh")


class MeshLayer(str, enum.Enum):
    """The three communication layers, in failover priority order."""

    WIFI = "wifi"
    BT = "bt"
    LORA = "lora"

    @classmethod
    def priority(cls) -> Tuple["MeshLayer", ...]:
        return (cls.WIFI, cls.BT, cls.LORA)


@dataclass
class MeshState:
    """Per-link liveness + quality snapshot."""

    rssi_dbm: float = -90.0
    latency_ms: float = 999.0
    last_seen: float = field(default_factory=time.time)
    packets_sent: int = 0
    packets_lost: int = 0

    @property
    def loss_ratio(self) -> float:
        total = self.packets_sent + self.packets_lost
        return self.packets_lost / total if total else 0.0


# Default thresholds (RSSI in dBm; closer to 0 = stronger)
DEFAULT_RSSI_FLOOR = {
    MeshLayer.WIFI: -75.0,
    MeshLayer.BT: -80.0,
    MeshLayer.LORA: -120.0,
}

DEFAULT_LATENCY_CEIL_MS = {
    MeshLayer.WIFI: 50.0,
    MeshLayer.BT: 100.0,
    MeshLayer.LORA: 500.0,
}


# A transport is a callable: (layer, target_id, payload: bytes) -> bool (sent)
Transport = Callable[[MeshLayer, str, bytes], bool]


class TripleMeshComms:
    """Coordinator that picks the best mesh layer per message and fails over."""

    def __init__(
        self,
        transport: Optional[Transport] = None,
        rssi_floor: Optional[Dict[MeshLayer, float]] = None,
        latency_ceil: Optional[Dict[MeshLayer, float]] = None,
        max_history: int = 256,
    ) -> None:
        self._transport = transport or _loopback_transport
        self._rssi_floor = {**DEFAULT_RSSI_FLOOR, **(rssi_floor or {})}
        self._latency_ceil = {**DEFAULT_LATENCY_CEIL_MS, **(latency_ceil or {})}
        self._lock = threading.RLock()
        # state[layer][target_id] = MeshState
        self._state: Dict[MeshLayer, Dict[str, MeshState]] = {
            l: defaultdict(MeshState) for l in MeshLayer
        }
        self._history: Deque[dict] = deque(maxlen=max_history)
        # Failover bookkeeping
        self._failovers: int = 0
        # Active layer — starts as None so the first successful send counts
        # as a (trivial) initial assignment rather than a "failover".
        self._active_layer: Optional[MeshLayer] = None

    # ── State updates from transports ───────────────────────────────────

    def report_link(
        self,
        layer: MeshLayer,
        target_id: str,
        rssi_dbm: float,
        latency_ms: float,
        lost: bool = False,
    ) -> None:
        with self._lock:
            st = self._state[layer][target_id]
            st.rssi_dbm = rssi_dbm
            st.latency_ms = latency_ms
            st.last_seen = time.time()
            if lost:
                st.packets_lost += 1
            else:
                st.packets_sent += 1

    # ── Layer selection ──────────────────────────────────────────────────

    def pick_layer(self, target_id: str) -> Optional[MeshLayer]:
        """Return the best healthy layer for ``target_id`` or None."""
        now = time.time()
        with self._lock:
            for layer in MeshLayer.priority():
                st = self._state[layer].get(target_id)
                if st is None:
                    continue
                fresh = (now - st.last_seen) <= 5.0
                strong = st.rssi_dbm >= self._rssi_floor[layer]
                fast = st.latency_ms <= self._latency_ceil[layer]
                if fresh and strong and fast:
                    return layer
            return None

    def active_layer(self) -> Optional[MeshLayer]:
        """Return the layer used for the most recent send (or None yet)."""
        with self._lock:
            return self._active_layer

    # ── Send / receive ──────────────────────────────────────────────────

    def send(self, target_id: str, payload: bytes, qos: str = "normal") -> bool:
        """Send ``payload`` to ``target_id`` on the best layer.

        ``qos`` may be ``"normal"`` (use best layer), ``"low_latency"`` (force
        WiFi if available), or ``"long_range"`` (force LoRa).
        """
        if qos == "long_range":
            chosen = MeshLayer.LORA
        elif qos == "low_latency":
            chosen = MeshLayer.WIFI
        else:
            chosen = self.pick_layer(target_id) or MeshLayer.LORA  # ultimate fallback

        with self._lock:
            prev = self._active_layer
            self._active_layer = chosen
            if prev is None:
                logger.debug("Initial layer assignment: %s for %s", chosen.value, target_id)
            elif prev != chosen:
                self._failovers += 1
                logger.info(
                    "Failover %s -> %s for %s", prev.value, chosen.value, target_id
                )
            st = self._state[chosen][target_id]
            st.packets_sent += 1
            st.last_seen = time.time()
            self._history.append(
                {
                    "ts": time.time(),
                    "target": target_id,
                    "layer": chosen.value,
                    "qos": qos,
                    "bytes": len(payload),
                }
            )

        ok = self._transport(chosen, target_id, payload)
        if not ok:
            with self._lock:
                self._state[chosen][target_id].packets_lost += 1
        return ok

    def broadcast(self, payload: bytes, qos: str = "normal") -> Dict[str, bool]:
        """Send to all known targets across all layers."""
        targets: set[str] = set()
        with self._lock:
            for layer_states in self._state.values():
                targets.update(layer_states.keys())
        if not targets:
            # Loopback self-send so broadcast always has at least one delivery
            targets.add("self")
        return {t: self.send(t, payload, qos=qos) for t in sorted(targets)}

    # ── Stats / introspection ───────────────────────────────────────────

    def failover_count(self) -> int:
        with self._lock:
            return self._failovers

    def history(self, n: int = 32) -> List[dict]:
        with self._lock:
            return list(self._history)[-n:]

    def link_quality(self) -> Dict[str, Dict[str, float]]:
        """Return per-target per-layer {rssi, latency, loss}."""
        out: Dict[str, Dict[str, float]] = {}
        with self._lock:
            for layer, targets in self._state.items():
                for tid, st in targets.items():
                    out.setdefault(tid, {})[f"{layer.value}_rssi"] = st.rssi_dbm
                    out.setdefault(tid, {})[f"{layer.value}_latency_ms"] = st.latency_ms
                    out.setdefault(tid, {})[f"{layer.value}_loss"] = st.loss_ratio
        return out


# ── Default loopback transport (used in tests / dev) ───────────────────


def _loopback_transport(layer: MeshLayer, target_id: str, payload: bytes) -> bool:
    """Echo transport that always succeeds. Used when no real radio attached."""
    logger.debug("[loopback][%s] -> %s : %d bytes", layer.value, target_id, len(payload))
    return True


__all__ = [
    "MeshLayer",
    "MeshState",
    "TripleMeshComms",
    "Transport",
    "DEFAULT_RSSI_FLOOR",
    "DEFAULT_LATENCY_CEIL_MS",
]
