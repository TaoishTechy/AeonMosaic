"""aeon_embodiment.config — Unified configuration loader for AeonMosaic.

Loads the seven JSON manifests that parameterise every tunable numeric in the
stack (no hard-coded constants anywhere in the runtime path). Mirrors the
ProtoAGI manifest pattern but extended with AeonMosaic-specific subsystems.

Manifests
---------
- ``manifest_base.json``         — runtime / persistence / pin layout
- ``manifest_sophia.json``       — Sophia constant, oscillator, critical band
- ``critical_band.json``         — spectral projector + hysteresis
- ``erd_parameters.json``        — entropy-Richter-Drake continuity bounds
- ``efficiency_targets.json``    — power / sleep / latency targets
- ``enhancements.json``          — 48 Alien Tier enhancements registry
- ``alignment.json``             — 48 alignment formulas metadata
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Union

logger = logging.getLogger("aeon_embodiment.config")

# Canonical manifest filenames in load order.
MANIFEST_FILES = (
    "manifest_base.json",
    "manifest_sophia.json",
    "critical_band.json",
    "erd_parameters.json",
    "efficiency_targets.json",
    "enhancements.json",
    "alignment.json",
)


class Config:
    """Unified configuration object loaded from JSON manifests.

    Parameters
    ----------
    config_dir:
        Directory containing the manifest JSON files. Defaults to the
        package's bundled ``configs/`` directory.
    overrides:
        Optional dict-of-dicts used to patch sections at runtime. Top-level
        keys are manifest names (without the ``.json`` suffix) and inner
        dicts deep-merge with the loaded manifest.
    strict:
        If True, missing required manifests raise ``FileNotFoundError``. If
        False, missing manifests default to an empty dict (useful for tests).
    """

    DEFAULT_CONFIG_DIR: Path = Path(__file__).resolve().parent.parent / "configs"

    def __init__(
        self,
        config_dir: Optional[Union[str, Path]] = None,
        overrides: Optional[Dict[str, Dict[str, Any]]] = None,
        strict: bool = True,
    ) -> None:
        self.config_dir: Path = Path(config_dir) if config_dir else self.DEFAULT_CONFIG_DIR
        self._strict = strict
        self._overrides = overrides or {}
        self._raw: Dict[str, Dict[str, Any]] = {}

        for fname in MANIFEST_FILES:
            section = fname.removesuffix(".json")
            self._raw[section] = self._load(fname)

        # Apply overrides
        for section, patch in self._overrides.items():
            if section not in self._raw:
                self._raw[section] = {}
            self._raw[section] = _deep_merge(self._raw[section], patch)

        # Convenience aliases (kept flat for ergonomics)
        self.base: Dict[str, Any] = self._raw["manifest_base"]
        self.sophia: Dict[str, Any] = self._raw["manifest_sophia"]
        self.critical_band: Dict[str, Any] = self._raw["critical_band"]
        self.erd: Dict[str, Any] = self._raw["erd_parameters"]
        self.efficiency: Dict[str, Any] = self._raw["efficiency_targets"]
        self.enhancements: Dict[str, Any] = self._raw["enhancements"]
        self.alignment: Dict[str, Any] = self._raw["alignment"]

        # Frequently used scalars
        self.phi: float = float(self.sophia.get("phi", 0.618))
        self.phi_inv: float = float(self.sophia.get("phi_inv", 1.0 / 0.618))
        self.seed: int = int(self.base.get("runtime", {}).get("seed", 42))

    # ── Public API ────────────────────────────────────────────────────────

    def get(self, section: str, *path: str, default: Any = None) -> Any:
        """Dotted-path getter: ``cfg.get("sophia", "field_memory", "logical_units")``."""
        node: Any = self._raw.get(section)
        for key in path:
            if not isinstance(node, dict) or key not in node:
                return default
            node = node[key]
        return node

    def section(self, name: str) -> Dict[str, Any]:
        """Return a defensive copy of an entire manifest section."""
        return json.loads(json.dumps(self._raw.get(name, {})))

    def paths(self) -> Iterable[str]:
        """Iterate over loaded manifest filenames."""
        return MANIFEST_FILES

    def as_dict(self) -> Dict[str, Dict[str, Any]]:
        """Return a deep copy of all loaded manifests."""
        return json.loads(json.dumps(self._raw))

    # ── Internals ───────────────────────────────────────────────────────

    def _load(self, fname: str) -> Dict[str, Any]:
        path = self.config_dir / fname
        if not path.is_file():
            if self._strict:
                raise FileNotFoundError(f"Missing manifest: {path}")
            logger.warning("Manifest %s not found — using empty dict", path)
            return {}
        try:
            with path.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Malformed manifest {path}: {exc}") from exc


def _deep_merge(base: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
    """Recursive dict merge — ``patch`` wins on key conflicts."""
    out = dict(base)
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


__all__ = ["Config", "MANIFEST_FILES"]
