# Project layout

This is the authoritative structure of the AeonMosaic repository.
Generated for v0.2.0.

```
AeonMosaic/
├── README.md                         # Master blueprint (mirrors the spec)
├── CHANGELOG.md                      # Semantic versioning log
├── LICENSE                           # MIT
├── .gitignore
├── Dockerfile                        # Reproducible build env
├── pyproject.toml                    # Setuptools + pytest + black + mypy config
├── requirements.txt                  # Pinned deps for reproducible builds
│
├── .github/
│   └── workflows/
│       └── ci.yml                    # Lint + test on Py 3.9/3.10/3.11/3.12
│
├── aeon_embodiment/                  # ← The Python package
│   ├── __init__.py
│   ├── config.py                     # 7-manifest loader
│   ├── core/
│   │   ├── __init__.py
│   │   ├── node.py                   # Node, NodeRole, NodeStatus
│   │   ├── modular_body.py           # Topology + NetworkX graph
│   │   ├── triple_mesh_comms.py      # WiFi/BT/LoRa failover
│   │   ├── distributed_psi.py        # PSI + leadership election
│   │   ├── hybrid_mobility.py        # Wheel ↔ leg state machine
│   │   └── magnetic_dock.py          # Pogo-pin docking
│   ├── sophia/                       # 12 foundation equations (SymPy)
│   ├── enhancements/                 # 48 Alien Tier Enhancements
│   ├── alignment/                    # 48 Alignment Formulas (SymPy)
│   ├── mobility/                     # Re-export shim
│   ├── dock/                         # Re-export shim
│   └── comms/                        # Re-export shim
│
├── configs/                          # ← JSON manifests (no hard-coded constants)
│   ├── manifest_base.json
│   ├── manifest_sophia.json
│   ├── critical_band.json
│   ├── erd_parameters.json
│   ├── efficiency_targets.json
│   ├── enhancements.json
│   └── alignment.json
│
├── firmware/
│   └── esp32/
│       ├── README.md
│       ├── mesh/                     # triple_mesh_comms.{h,c}
│       ├── dock/                     # magnetic_dock.h
│       └── mobility/                 # hybrid_mobility.{h,c}
│
├── scripts/                          # ← Phase build scripts
│   ├── simulate_syzygy.py
│   ├── phase1_mesh.py
│   ├── phase2_mobility.py
│   ├── phase3_intelligence.py
│   └── phase4_swarm.py
│
├── tests/                            # ← pytest suite (79 tests, ~3s)
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_modular_body.py
│   ├── test_triple_mesh.py
│   ├── test_distributed_psi.py
│   ├── test_hybrid_mobility.py
│   ├── test_magnetic_dock.py
│   ├── test_sophia.py
│   ├── test_enhancements.py
│   └── test_alignment.py
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── USAGE.md
│   ├── ENHANCEMENTS.md               # Full 48-row registry table
│   ├── EQUATIONS.md                  # 12 foundation equations
│   ├── ROADMAP.md
│   ├── RISKS.md
│   └── CONTRIBUTING.md
│
├── launch/                           # (placeholder for ROS 2 launch files)
├── sim/                              # (placeholder for PyBullet simulation assets)
├── hardware/                         # (placeholder for FreeCAD/Fusion 360 CAD)
└── tools/                            # (placeholder for dev utilities)
```

## Stats (v0.2.0)

- **Python source:** ~3,000 lines across 17 modules
- **Tests:** 79 (3.2 s wall time)
- **ESP32 firmware stubs:** ~400 lines C
- **Documentation:** 8 docs totalling ~2,000 lines
- **Config manifests:** 7 JSON files
- **Total repo size (excl. .git):** ~120 KB
