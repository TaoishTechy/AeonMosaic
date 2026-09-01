# USAGE

## Installation

### From source (development)

```bash
git clone https://github.com/TaoishTechy/AeonMosaic.git
cd AeonMosaic
pip install -e .[test,dev]
```

### Production (with ROS 2 + mesh extras)

```bash
pip install -e .[ros,mesh]
```

## Quick start — simulation

```python
from aeon_embodiment import Config
from aeon_embodiment.core import (
    DistributedPSI, ModularBody, Node, NodeRole, PSISample, TripleMeshComms,
)

cfg = Config()
body = ModularBody(initial_nodes=[
    Node(id="head", role=NodeRole.HEAD, compute="rpi_4"),
    Node(id="torso", role=NodeRole.TORSO, compute="rpi_3a_plus"),
])
body.dock("head", "torso")

psi = DistributedPSI(phi=cfg.phi)
psi.update(PSISample(
    node_id="head",
    novelty=0.6, alienness=0.5, entropy=100.0,
    elegance=0.7, paradox=0.2, coherence=0.72,
))

graph = body.graph()
print("System PSI:", psi.system_psi())
print("Syzygy:", psi.syzygy_score(graph))
print("Leader:", psi.elect_leader(graph))
```

## Phase scripts

Each phase script validates one chunk of the build roadmap:

```bash
# Phase 1 — Core Mesh bootstrap (1 hr / <10ms latency target)
python scripts/phase1_mesh.py --duration 5

# Phase 2 — Mobility (wheel↔leg transition <2s)
python scripts/phase2_mobility.py

# Phase 3 — Intelligence (Tiers I–III + Sophia equations live)
python scripts/phase3_intelligence.py

# Phase 4 — Swarm Gnosis (12 units, LoRa broadcast)
python scripts/phase4_swarm.py --units 12
```

All four scripts return exit code 0 on success and 1 on failure, so they
can be chained in CI.

## Syzygy simulator

```bash
python scripts/simulate_syzygy.py --ticks 100
python scripts/simulate_syzygy.py --json  # machine-readable output
```

## Sophia equations

```python
from aeon_embodiment.sophia import all_equations, get_equation, evaluate_all

# Iterate all 12
for eq in all_equations():
    print(f"#{eq.index:>2}  {eq.name:<35}  symbolic={eq.symbolic}")

# Evaluate one
eq3 = get_equation(3)  # Syzygy Resonance Frequency
freq = eq3.evaluator(inter_node_distance_m=1.0, phi_val=0.618)

# Bulk-evaluate
results = evaluate_all(phi_val=0.618)
```

## Enhancements registry

```python
from aeon_embodiment.enhancements import (
    Tier, Priority, all_enhancements, by_tier, by_priority, by_subsystem,
)

# All 48
all_enhancements()

# By tier
by_tier(Tier.I)  # → 6 Tier I (Singularity) enhancements

# By priority
by_priority(Priority.TOP)  # → 6 TOP-priority enhancements

# By subsystem
by_subsystem("ModularBody")  # → 18 enhancements targeting ModularBody
```

## Alignment formulas

```python
from aeon_embodiment.alignment import all_formulas, by_tier, evaluate_tier

# All 48
all_formulas()

# Per tier
by_tier(3)  # → 6 Mesh Comms formulas

# Evaluate all formulas in a tier
evaluate_tier(1, omega=1.0, phi_val=0.618)
```

## Running the tests

```bash
# Full suite (79 tests, ~3s)
pytest tests/ -v

# With coverage
pytest tests/ --cov=aeon_embodiment --cov-report=term-missing

# One module
pytest tests/test_distributed_psi.py -v
```

## Configuring manifests

Edit any of the seven JSON files in `configs/`:

| File | Purpose |
|------|---------|
| `manifest_base.json` | Runtime / persistence / pin layout / budget |
| `manifest_sophia.json` | Sophia constant, oscillator, critical band, risk mgmt |
| `critical_band.json` | Spectral projector + hysteresis |
| `erd_parameters.json` | Entropy-Richter-Drake continuity bounds |
| `efficiency_targets.json` | Power / sleep / latency targets |
| `enhancements.json` | 48 enhancements registry metadata |
| `alignment.json` | 48 alignment formulas metadata |

## ESP32 firmware

See [`firmware/esp32/README.md`](../firmware/esp32/README.md) for build
instructions. The stubs compile against ESP-IDF v5.x with the ESP32-C6 as
the target. Replace the radio stubs with real driver calls during Phase 1
hardware integration.

## ROS 2 integration (Phase 3+)

The `aeon_embodiment.ros_bridge` sub-package (not yet implemented in
v0.2) will expose:

- Each `ModularBody` topology event as a `std_msgs/String` topic
- Each `DistributedPSI` threshold crossing as a ROS 2 Action
- Each `HybridMobilityController` mode transition as a service call
- Each `MagneticDockManager` dock event as a `std_msgs/UInt8` topic

In the meantime the pure-Python classes can be wrapped manually — they
are thread-safe and emit discrete events via callbacks.
