"""AeonEmbodiment — the modular robotic cognition framework for AeonMosaic.

A pleromic modular robot where every body segment operates as an independent
cognitive agent. When physically docked via magnetic pogo-pin connectors the
agents achieve *syzygy*: a harmonious whole whose collective PSI exceeds the
sum of its parts.

Public API
----------
``aeon_embodiment.Config``
    Unified configuration loader (5 JSON manifests).

``aeon_embodiment.ModularBody``
    Node registry, role negotiation, OTA neural weight sync.

``aeon_embodiment.TripleMeshComms``
    WiFi 6 / BT 5.3 / LoRa failover coordinator.

``aeon_embodiment.DistributedPSI``
    Psychic State Index compute, leadership election, syzygy detection.

``aeon_embodiment.HybridMobilityController``
    Wheeled / legged state machine (Centaur-Bot).

``aeon_embodiment.MagneticDockManager``
    Pogo-pin connection detection, power/data handoff, role reassignment.

Author
------
Micheal Landry (@MyKey00110000)

License
-------
MIT
"""

from __future__ import annotations

__version__ = "0.2.0"
__author__ = "Micheal Landry (@MyKey00110000)"
__license__ = "MIT"

# Re-export the public API. Imports are kept lazy via try/except so a
# partial install (e.g. missing ROS 2 on a dev machine) does not break
# `import aeon_embodiment`.
try:  # pragma: no cover - exercised on real install
    from .config import Config
except Exception:  # pragma: no cover
    Config = None  # type: ignore[assignment]

try:  # pragma: no cover
    from .core.modular_body import ModularBody
    from .core.distributed_psi import DistributedPSI
    from .core.hybrid_mobility import HybridMobilityController
    from .core.magnetic_dock import MagneticDockManager
    from .core.triple_mesh_comms import TripleMeshComms
except Exception:  # pragma: no cover
    ModularBody = None  # type: ignore[assignment]
    DistributedPSI = None  # type: ignore[assignment]
    HybridMobilityController = None  # type: ignore[assignment]
    MagneticDockManager = None  # type: ignore[assignment]
    TripleMeshComms = None  # type: ignore[assignment]

__all__ = [
    "Config",
    "ModularBody",
    "TripleMeshComms",
    "DistributedPSI",
    "HybridMobilityController",
    "MagneticDockManager",
    "__version__",
    "__author__",
    "__license__",
]
