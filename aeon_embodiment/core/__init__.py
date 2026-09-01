"""aeon_embodiment.core — Core AeonEmbodiment classes.

This sub-package hosts the five primary classes described in the Master
Blueprint section 04:

    ModularBody  · TripleMeshComms  · DistributedPSI
    HybridMobilityController  · MagneticDockManager

Each class is hardware-agnostic. Hardware coupling (GPIO, I2C, SPI, CSI-2)
is injected via adapter objects so the entire stack can run on a developer
laptop without a single Raspberry Pi attached.
"""

from __future__ import annotations

from .node import Node, NodeRole, NodeStatus
from .modular_body import ModularBody
from .triple_mesh_comms import TripleMeshComms, MeshLayer, MeshState
from .distributed_psi import (
    DistributedPSI,
    PSISample,
    SOPHIA_PHI,
    COHERENCE_FLOOR,
    STABLE_PRIME_COUNTS,
)
from .hybrid_mobility import HybridMobilityController, MobilityMode
from .magnetic_dock import MagneticDockManager, DockEvent, DockState

__all__ = [
    "Node",
    "NodeRole",
    "NodeStatus",
    "ModularBody",
    "TripleMeshComms",
    "MeshLayer",
    "MeshState",
    "DistributedPSI",
    "PSISample",
    "SOPHIA_PHI",
    "COHERENCE_FLOOR",
    "STABLE_PRIME_COUNTS",
    "HybridMobilityController",
    "MobilityMode",
    "MagneticDockManager",
    "DockEvent",
    "DockState",
]
