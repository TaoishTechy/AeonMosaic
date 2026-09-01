# ARCHITECTURE

> AeonMosaic architecture deep-dive. See `README.md` for the high-level
> blueprint.

## Design philosophy

The stack is **hardware-agnostic by default**. Every class that touches
hardware (GPIO, I2C, SPI, CSI-2, PWM, LoRa radios) accepts an injected
adapter rather than importing the hardware library directly. This means
the entire codebase runs on a developer laptop with zero hardware
attached — useful for CI, simulation, and rapid prototyping.

The simulation-only entry points are `scripts/simulate_syzygy.py` and
`scripts/phase{1..4}_*.py`. They use no-op adapters and the loopback
mesh transport.

## Package layout

```
aeon_embodiment/
├── __init__.py              # Public API re-exports
├── config.py                # Config loader (7 JSON manifests)
├── core/
│   ├── __init__.py
│   ├── node.py              # Node, NodeRole, NodeStatus primitives
│   ├── modular_body.py      # Topology registry + NetworkX graph
│   ├── triple_mesh_comms.py # WiFi / BT / LoRa failover
│   ├── distributed_psi.py   # PSI compute + leadership election
│   ├── hybrid_mobility.py   # Wheel ↔ leg state machine
│   └── magnetic_dock.py     # Pogo-pin docking + role reassignment
├── sophia/                  # 12 foundation equations (SymPy)
├── enhancements/            # 48 Alien Tier Enhancements registry
├── alignment/               # 48 Alignment Formulas (SymPy)
├── mobility/                # Re-export shim → core.hybrid_mobility
├── dock/                    # Re-export shim → core.magnetic_dock
└── comms/                   # Re-export shim → core.triple_mesh_comms
```

## Class responsibilities

### ModularBody

In-memory model of the robot topology. Maintains a NetworkX `Graph` where
nodes are body segments and edges are physical docking connections.
Topology mutations (`dock`, `undock`, `register`, `unregister`) emit
events to subscribed callbacks so downstream subsystems (PSI, mesh,
mobility) can react.

### TripleMeshComms

Per-message failover coordinator. Tracks per-link RSSI/latency on all
three layers (WiFi, BT, LoRa). For each outbound message it picks the
best healthy layer via a priority-ordered scan. When the active layer
changes it increments the `failover_count` so operators can monitor mesh
health.

### DistributedPSI

Aggregator for the Psychic State Index. Holds per-node `PSISample`
objects and computes:

- `system_psi()` — Sophia-weighted mean composite score
- `syzygy_score(graph)` — coherence amplified by NetworkX clustering
- `paradox_pressure()` — RMS paradox across nodes
- `elect_leader(graph)` — eigenvector centrality (NetworkX) weighted by PSI

The `on_syzygy_threshold()` callback mechanism is the trigger for the
48 alignment formulas — they fire as ROS 2 Actions when the system PSI
crosses a configurable threshold.

### HybridMobilityController

Centaur-Bot state machine. Holds two PWM channel maps (4× wheels, 8×
leg servos). Transitions take <2 s and are guarded by IMU balance +
obstacle proximity. An IMU failure mid-legged-mode triggers an
automatic fallback to wheeled.

### MagneticDockManager

Per-node pogo-pin docking face manager. Each face has a state machine
(`UNDOCKED → DETECTED → NEGOTIATING → DOCKED`) driven by GPIO
interrupts. When a dock completes, `set_partner()` fills in the partner
identity and downstream subsystems get notified.

## Config system

All tunable numerics live in `configs/*.json` — there are **no
hard-coded constants anywhere in the runtime path**. The `Config` class
loads seven manifests and exposes them via dotted-path getters:

```python
from aeon_embodiment import Config
cfg = Config()
phi = cfg.phi                        # 0.618
omega = cfg.get("manifest_sophia", "sophia_oscillator", "omega_0")
```

The system supports runtime overrides for testing:

```python
cfg = Config(overrides={
    "manifest_sophia": {"phi": 0.5, "sophia_oscillator": {"omega_0": 99.0}}
})
```

## Sophia framework

`aeon_embodiment.sophia` exposes 12 `SophiaEquation` records. Each
carries:

- A SymPy symbolic expression for symbolic manipulation
- A Python numeric evaluator for runtime use
- A human-readable description from the blueprint

Use `all_equations()` to iterate, `get_equation(n)` to look up by
1-based index, and `evaluate_all(**kwargs)` to bulk-evaluate.

## Enhancements registry

`aeon_embodiment.enhancements` exposes 48 `Enhancement` records. Each
carries the Composite Score components (novelty, alienness, entropy,
elegance, paradox, ontology_coherence) and computes its composite via
the formula from blueprint §06:

```
Composite = (Nov×30) + (Ali×25) + (Ent×0.05) + (Ele×0.2)
            + (Par×10) + (Coh×15)
```

Lookups: `by_tier(Tier)`, `by_number(n)`, `by_subsystem(name)`,
`by_priority(Priority)`.

## Alignment formulas

`aeon_embodiment.alignment` exposes 48 `AlignmentFormula` records
across 8 tiers of 6 each. Each has a SymPy expression + numeric
evaluator. Use `evaluate_tier(n, **kwargs)` to bulk-evaluate a tier.

## Thread safety

Every class with mutable state holds an `RLock` and acquires it on every
public method. Defensive copies are returned for snapshot-style
accessors (`snapshot()`, `state`, `history()`) so callers cannot mutate
internals.

## Hardware adaptation

To run on real hardware, inject adapters:

```python
from aeon_embodiment import HybridMobilityController

def real_pwm_sink(channel: int, pulse_us: int) -> None:
    import pigpio
    pi = pigpio.pi()
    pi.set_servo_pulsewidth(channel, pulse_us)

controller = HybridMobilityController(pwm_sink=real_pwm_sink)
```

The same pattern applies to `TripleMeshComms` (transport adapter),
`MagneticDockManager` (GPIO ISR adapter), and `ModularBody` (heartbeat
source).
