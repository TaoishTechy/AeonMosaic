"""Tests for the Config loader."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from aeon_embodiment import Config


def test_config_loads_default_bundled_manifests():
    cfg = Config()
    assert cfg.phi == pytest.approx(0.618, abs=1e-6)
    assert cfg.phi_inv == pytest.approx(1.618033988749895, abs=1e-6)
    assert cfg.seed == 42
    assert cfg.base["project"]["name"] == "AeonMosaic"
    assert "manifest_base" in cfg.as_dict()


def test_config_get_dotted_path():
    cfg = Config()
    val = cfg.get("manifest_sophia", "sophia_oscillator", "omega_0")
    assert val == pytest.approx(1.618033988749895, abs=1e-6)
    # default fallback
    assert cfg.get("manifest_sophia", "nonexistent", default="X") == "X"


def test_config_overrides_deep_merge(tmp_path):
    # Copy bundled configs to tmp
    src = Path(__file__).resolve().parent.parent / "configs"
    dst = tmp_path / "configs"
    dst.mkdir()
    for f in src.iterdir():
        (dst / f.name).write_text(f.read_text())

    cfg = Config(config_dir=dst, overrides={
        "manifest_sophia": {"phi": 0.5, "sophia_oscillator": {"omega_0": 99.0}},
    })
    assert cfg.phi == 0.5
    # Deep merge: omega_0 patched but rest of sophia_oscillator preserved
    assert cfg.sophia["sophia_oscillator"]["omega_0"] == 99.0
    assert "damping_inv_phi" in cfg.sophia["sophia_oscillator"]


def test_config_strict_missing_manifest(tmp_path):
    with pytest.raises(FileNotFoundError):
        Config(config_dir=tmp_path, strict=True)


def test_config_non_strict_missing_manifest(tmp_path):
    cfg = Config(config_dir=tmp_path, strict=False)
    assert cfg.phi == pytest.approx(0.618, abs=1e-6)  # uses builtin default
    assert cfg.base == {}
