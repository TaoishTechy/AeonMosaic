"""Tests for DistributedPSI."""

from __future__ import annotations

import math
import networkx as nx
import pytest

from aeon_embodiment.core import (
    DistributedPSI,
    PSISample,
    SOPHIA_PHI,
    COHERENCE_FLOOR,
)


def _sample(node_id: str, coherence: float = 0.7) -> PSISample:
    return PSISample(
        node_id=node_id,
        novelty=0.5, alienness=0.5, entropy=100.0,
        elegance=0.5, paradox=0.2, coherence=coherence,
    )


def test_composite_score_formula():
    s = PSISample(
        node_id="x",
        novelty=1.0, alienness=1.0, entropy=100.0,
        elegance=1.0, paradox=1.0, coherence=1.0,
    )
    # 1*30 + 1*25 + 100*0.05 + 1*0.2 + 1*10 + 1*15 = 30+25+5+0.2+10+15 = 85.2
    assert s.composite_score() == pytest.approx(85.2, abs=1e-6)


def test_is_sane_uses_coherence_floor():
    s = _sample("x", coherence=0.6)
    assert not s.is_sane()
    s.coherence = 0.70
    assert s.is_sane()
    assert COHERENCE_FLOOR == 0.70


def test_system_psi_zero_when_empty():
    psi = DistributedPSI()
    assert psi.system_psi() == 0.0
    assert not psi.is_sane()


def test_system_psi_aggregates():
    psi = DistributedPSI()
    psi.update(_sample("a", coherence=0.7))
    psi.update(_sample("b", coherence=0.75))
    val = psi.system_psi()
    assert val > 0


def test_syzygy_score_amplifies_with_topology():
    psi = DistributedPSI()
    psi.update(_sample("a", coherence=0.75))
    psi.update(_sample("b", coherence=0.75))
    psi.update(_sample("c", coherence=0.75))

    # Sparse: 2 nodes, no triangles → clustering = 0
    g_sparse = nx.Graph()
    g_sparse.add_edges_from([("a", "b"), ("b", "c")])  # path, no triangle
    # Dense: 3 nodes in a triangle → clustering = 1
    g_dense = nx.Graph()
    g_dense.add_edges_from([("a", "b"), ("b", "c"), ("a", "c")])
    s_sparse = psi.syzygy_score(g_sparse)
    s_dense = psi.syzygy_score(g_dense)
    assert s_dense > s_sparse


def test_paradox_pressure_rms():
    psi = DistributedPSI()
    psi.update(PSISample(node_id="a", paradox=0.3, coherence=0.7))
    psi.update(PSISample(node_id="b", paradox=0.4, coherence=0.7))
    expected = math.sqrt((0.3 ** 2 + 0.4 ** 2) / 2)
    assert psi.paradox_pressure() == pytest.approx(expected, abs=1e-9)


def test_elect_leader_picks_highest_centrality():
    psi = DistributedPSI()
    psi.update(PSISample(node_id="torso", novelty=1.0, alienness=1.0,
                        entropy=200.0, elegance=1.0, paradox=0.1, coherence=0.75))
    psi.update(_sample("head", coherence=0.7))
    psi.update(_sample("arm", coherence=0.7))
    g = nx.Graph()
    g.add_edges_from([("torso", "head"), ("torso", "arm")])
    leader = psi.elect_leader(g)
    assert leader == "torso"


def test_is_golden_ratio_locked():
    psi = DistributedPSI()
    # All nodes with coherence exactly phi
    for nid in ("a", "b", "c"):
        psi.update(PSISample(node_id=nid, coherence=SOPHIA_PHI, novelty=0.5, alienness=0.5,
                             entropy=100.0, elegance=0.5, paradox=0.2))
    # variance is 0, |0 - 0.618| < 0.0309
    assert psi.is_golden_ratio_locked()


def test_carmichael_stable_counts():
    assert DistributedPSI.is_stable_node_count(3)
    assert DistributedPSI.is_stable_node_count(5)
    assert DistributedPSI.is_stable_node_count(7)
    assert DistributedPSI.is_stable_node_count(11)
    assert not DistributedPSI.is_stable_node_count(4)
    assert not DistributedPSI.is_stable_node_count(6)


def test_syzygy_threshold_callback():
    psi = DistributedPSI()
    fired = []
    psi.on_syzygy_threshold(threshold=0.0, cb=lambda p, g: fired.append(p))
    psi.update(_sample("a"))
    g = nx.Graph()
    g.add_node("a")
    psi.check_syzygy_thresholds(g)
    assert len(fired) == 1
    assert fired[0] > 0


def test_drop_removes_node():
    psi = DistributedPSI()
    psi.update(_sample("a"))
    psi.drop("a")
    assert psi.system_psi() == 0.0
