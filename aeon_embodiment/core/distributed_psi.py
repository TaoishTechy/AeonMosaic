"""aeon_embodiment.core.distributed_psi — Psychic State Index compute & syzygy.

PSI is the composite metric that captures the robot's collective coherence.
Every node computes a *local* PSI slice from its sensor readings, then the
torso hub aggregates slices into a *system* PSI using the Composite Score
formula from blueprint §05:

    PSI = (Nov×30) + (Ali×25) + (Ent×0.05) + (Ele×0.2)
          + (Par×10) + (Coh×15)

Stability is governed by the Sophia Constant ``φ = 0.618``: nodes tuned to
this value exhibit the lowest paradox pressure. The Coherence Threshold
of ``0.70`` is the system's "Sanity Floor" — no enhancement below this
threshold achieves Composite Score > 325 (blueprint §05 deep-field pattern).

Leadership election uses eigenvector centrality over the topology graph
weighted by per-node PSI — the node with the highest syzygy-weighted score
claims the "leader" MQTT topic.
"""

from __future__ import annotations

import logging
import math
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import networkx as nx

logger = logging.getLogger("aeon_embodiment.psi")

# Sophia Constant (golden ratio conjugate)
SOPHIA_PHI: float = 0.618
# Coherence Threshold ("Sanity Floor")
COHERENCE_FLOOR: float = 0.70
# Stable node counts (Carmichael-PSI prime function, blueprint Eq. #9)
STABLE_PRIME_COUNTS: Tuple[int, ...] = (3, 5, 7, 11)


@dataclass
class PSISample:
    """One PSI observation from a single node at one timestep."""

    node_id: str
    novelty: float = 0.0
    alienness: float = 0.0
    entropy: float = 0.0
    elegance: float = 0.0
    paradox: float = 0.0
    coherence: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def composite_score(self) -> float:
        """Composite Score Formula from blueprint §05."""
        return (
            self.novelty * 30.0
            + self.alienness * 25.0
            + self.entropy * 0.05
            + self.elegance * 0.2
            + self.paradox * 10.0
            + self.coherence * 15.0
        )

    def is_sane(self) -> bool:
        """Coherence Threshold check — the system's Sanity Floor."""
        return self.coherence >= COHERENCE_FLOOR


class DistributedPSI:
    """Aggregate Psychic State Index across all nodes.

    The class is *passive* — it does not own the topology. Callers feed it
    the current NetworkX graph and per-node PSI samples; the class returns
    system-level metrics (syzygy score, leader, paradox pressure).
    """

    def __init__(self, phi: float = SOPHIA_PHI, coherence_floor: float = COHERENCE_FLOOR) -> None:
        self.phi = float(phi)
        self.phi_inv = 1.0 / self.phi if self.phi else 1.618
        self.coherence_floor = float(coherence_floor)
        self._lock = threading.RLock()
        self._samples: Dict[str, PSISample] = {}
        self._history: List[Tuple[float, float]] = []  # (timestamp, system_psi)
        self._max_history: int = 1000
        self._syzygy_callbacks: List = []

    # ── Sample ingestion ────────────────────────────────────────────────

    def update(self, sample: PSISample) -> None:
        with self._lock:
            self._samples[sample.node_id] = sample

    def update_many(self, samples: List[PSISample]) -> None:
        with self._lock:
            for s in samples:
                self._samples[s.node_id] = s

    def drop(self, node_id: str) -> None:
        with self._lock:
            self._samples.pop(node_id, None)

    # ── Aggregate metrics ────────────────────────────────────────────────

    def system_psi(self) -> float:
        """Mean composite score across all live samples (Sophia-weighted)."""
        with self._lock:
            samples = list(self._samples.values())
        if not samples:
            return 0.0
        scores = np.array([s.composite_score() for s in samples], dtype=np.float64)
        # Sophia weighting: tilt toward phi-trimmed mean to dampen outliers
        weights = np.array([self._phi_weight(s) for s in samples], dtype=np.float64)
        weights /= weights.sum() if weights.sum() > 0 else 1.0
        psi = float(np.dot(weights, scores))
        self._history.append((time.time(), psi))
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
        return psi

    def _phi_weight(self, s: PSISample) -> float:
        """Sophia attractor: weight nodes whose coherence sits near phi."""
        # Gaussian centred on phi (width 0.2)
        return float(math.exp(-0.5 * ((s.coherence - self.phi) / 0.2) ** 2))

    def syzygy_score(self, graph: nx.Graph) -> float:
        """Syzygy = collective coherence amplified by topology clustering.

        Computed as::

            syzygy = mean(coherence_i) * phi * (1 + clustering_coefficient(G))

        When nodes are docked, clustering rises and syzygy amplifies — the
        "sum greater than its parts" effect of blueprint §01.
        """
        with self._lock:
            samples = list(self._samples.values())
        if not samples:
            return 0.0
        mean_coh = float(np.mean([s.coherence for s in samples]))
        clustering = nx.average_clustering(graph) if graph.number_of_nodes() > 0 else 0.0
        return mean_coh * self.phi * (1.0 + clustering)

    def paradox_pressure(self) -> float:
        """Root-mean-square paradox across all live nodes."""
        with self._lock:
            samples = list(self._samples.values())
        if not samples:
            return 0.0
        return float(np.sqrt(np.mean([s.paradox ** 2 for s in samples])))

    def is_sane(self) -> bool:
        """True iff every live sample clears the Coherence Threshold."""
        with self._lock:
            samples = list(self._samples.values())
        return all(s.is_sane() for s in samples) if samples else False

    # ── Leadership election via eigenvector centrality ───────────────────

    def elect_leader(self, graph: nx.Graph) -> Optional[str]:
        """Pick the node with highest syzygy-weighted eigenvector centrality.

        The graph's adjacency is weighted by per-node composite scores so a
        high-PSI node contributes more centrality to its neighbours.
        """
        with self._lock:
            samples = dict(self._samples)
        if not samples or graph.number_of_nodes() == 0:
            return None
        weighted = graph.copy()
        for n in list(weighted.nodes()):
            sample = samples.get(n)
            score = sample.composite_score() if sample else 1.0
            for nbr in weighted.neighbors(n):
                weighted[n][nbr]["weight"] = float(score) / 100.0 + 0.01
        try:
            centrality = nx.eigenvector_centrality_numpy(weighted)
        except (nx.NetworkXError, nx.NetworkXNotImplemented):
            # Fall back to degree centrality if graph is degenerate
            centrality = nx.degree_centrality(weighted)
        if not centrality:
            return None
        return max(centrality, key=centrality.get)  # type: ignore[return-value]

    # ── Stability attractor (Sophia lock) ───────────────────────────────

    def coherence_variance(self) -> float:
        """Variance of coherence across nodes — used by Golden Ratio Lock."""
        with self._lock:
            samples = list(self._samples.values())
        if len(samples) < 2:
            return 0.0
        return float(np.var([s.coherence for s in samples]))

    def is_golden_ratio_locked(self) -> bool:
        """True iff coherence variance is small (perfect lock = 0 variance).

        The Golden Ratio Lock (blueprint §05 deep-field pattern) reports that
        Tier IV coherence variance equals ``φ`` — but variance near zero
        (all nodes equally tuned to the attractor) is the *optimal* locked
        state. We therefore treat variance ≤ ``φ`` as locked, with the
        tightest lock being ``var == 0``.
        """
        return self.coherence_variance() <= self.phi

    # ── Carmichael-PSI prime count check ─────────────────────────────────

    @staticmethod
    def is_stable_node_count(n: int) -> bool:
        """Eq. #9 — only prime node counts 3/5/7/11 yield stable mesh."""
        return n in STABLE_PRIME_COUNTS

    # ── Syzygy event callbacks ──────────────────────────────────────────

    def on_syzygy_threshold(self, threshold: float, cb) -> None:
        """Register a callback fired when system PSI crosses ``threshold``."""
        self._syzygy_callbacks.append((threshold, cb))

    def check_syzygy_thresholds(self, graph: nx.Graph) -> None:
        psi = self.system_psi()
        for threshold, cb in list(self._syzygy_callbacks):
            if psi >= threshold:
                try:
                    cb(psi, graph)
                except Exception as exc:  # pragma: no cover - defensive
                    logger.exception("Syzygy callback raised: %s", exc)

    # ── Introspection ──────────────────────────────────────────────────

    def history(self, n: int = 100) -> List[Tuple[float, float]]:
        with self._lock:
            return list(self._history[-n:])

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "node_count": len(self._samples),
                "samples": [
                    {
                        "node_id": s.node_id,
                        "composite": s.composite_score(),
                        "coherence": s.coherence,
                        "sane": s.is_sane(),
                    }
                    for s in self._samples.values()
                ],
            }


__all__ = [
    "DistributedPSI",
    "PSISample",
    "SOPHIA_PHI",
    "COHERENCE_FLOOR",
    "STABLE_PRIME_COUNTS",
]
