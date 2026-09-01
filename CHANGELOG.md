# Changelog

All notable changes to AeonMosaic will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Pending
- ESP32-C6 firmware: replace radio stubs with real driver calls (`esp_wifi_send`, `esp_bt_send`, `RadioLib`)
- ROS 2 bridge (`aeon_embodiment.ros_bridge`): expose topology events as ROS 2 topics + actions
- OpenCV perception pipeline integration on Head RPi 4
- PyBullet simulation of wheel-leg transition (currently pure-Python)

## [0.2.0] — 2026-02-01

### Added
- Initial public release of the AeonMosaic Unified Master Blueprint.
- `aeon_embodiment` Python package with five core classes:
  - `ModularBody` — topology registry + NetworkX graph
  - `TripleMeshComms` — WiFi 6 / BT 5.3 / LoRa failover coordinator
  - `DistributedPSI` — PSI compute, leadership election, syzygy detection
  - `HybridMobilityController` — Centaur-Bot wheel ↔ leg state machine
  - `MagneticDockManager` — pogo-pin docking + role reassignment
- `aeon_embodiment.sophia` — 12 Gnostic foundation equations (SymPy + numeric)
- `aeon_embodiment.enhancements` — 48 Alien Tier Enhancements registry
- `aeon_embodiment.alignment` — 48 Alignment Formulas (SymPy + numeric)
- 7 JSON config manifests (`configs/`)
- 4 phase scripts: `phase1_mesh.py`, `phase2_mobility.py`, `phase3_intelligence.py`, `phase4_swarm.py`
- `simulate_syzygy.py` — pure-Python syzygy simulator
- 79-test pytest suite covering all classes, equations, and registries
- ESP32-C6 firmware stubs (`.h` + `.c`) for mesh, dock, and mobility subsystems
- Full documentation set: README, ARCHITECTURE, USAGE, ENHANCEMENTS, EQUATIONS, ROADMAP, RISKS, CONTRIBUTING
- GitHub Actions CI workflow (lint + test on Python 3.9/3.10/3.11/3.12)
- Dockerfile for reproducible builds
- pyproject.toml with setuptools build backend
- MIT License

### Known Limitations
- All hardware primitives are stubbed (no real GPIO, I2C, SPI, or CSI-2 attached).
- ESP32 firmware radio calls are stubbed with `printf` — replace with real driver calls during Phase 1 hardware integration.
- ROS 2 bridge is not yet implemented — the pure-Python classes are thread-safe and emit discrete events via callbacks, ready for wrapping.
- PyBullet simulation is a placeholder — the state machine is complete but the physics simulation is a no-op.

[Unreleased]: https://github.com/TaoishTechy/AeonMosaic/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/TaoishTechy/AeonMosaic/releases/tag/v0.2.0
