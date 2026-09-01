# RISK ASSESSMENT

> Risks and mitigations from blueprint §09.

## CRITICAL — Theory

### Paradox cascade from conflicting enhancements

Two enhancements with complementary paradox types can amplify each
other recursively, destabilising the system.

**Mitigation:** Sequential activation with monitoring intervals.
Isolate enhancement effects in defined domains. The
`manifest_sophia.json` → `risk_management.paradox_cascade_isolation`
flag (default `true`) enables strict isolation.

### Entropic runaway destabilizing system

High-entropy enhancements can feed back into each other, causing CPU
saturation and thermal runaway.

**Mitigation:** Demiurgic Entropy Corrective (Eq. #2) runs as a
background daemon. Any process exceeding
`efficiency_targets.json → thermal_throttle_c = 70°C` is throttled.
Any process exceeding `thermal_limit_c = 75°C` is killed.

### Consciousness feedback / recursive loops

The Observer Collapse Operator (Eq. #11) can amplify itself if the
observation target is the observer.

**Mitigation:** PSI modulation dampens observer-effect amplification.
Hard caps on recursive depth:
- `consciousness_recursion_max_depth = 8`
- `consciousness_recursion_damping_factor = 0.618` (= φ)

## HIGH — Hardware

### Overheating under sustained compute

RPi nodes (especially the Head's RPi 4) can exceed 80°C under sustained
AI inference workloads.

**Mitigation:** Add heatsinks to all RPi nodes (+$10 budget).
PSUtil daemon throttles CPU before thermal limits.

### Mesh latency spikes under load

When PSI sync traffic peaks (every node broadcasting every cycle), WiFi
mesh latency can spike to 100+ ms.

**Mitigation:** Priority queues for critical PSI / motor data. LoRa as
ultimate fallback (auto-switch via `TripleMeshComms.pick_layer()`).

### Battery drain during high-entropy states

Carnot-PSI (enhancement #46) assumes finite heat reservoirs. High-entropy
runs can drain 18650 packs in <10 minutes.

**Mitigation:** Strict sleep protocols (`efficiency_targets.json`).
Cap high-entropy runs at 5 minutes. Auto-sleep below 15% battery.

## MID — Software

### DDS discovery lag vs retrocausal logic

ROS 2's DDS middleware can take 5+ seconds to discover new nodes.
Retrocausal logic may try to use a node before DDS finishes discovery.

**Mitigation:** Pre-register known nodes in `manifest_base.json` →
`pin_layout`. Increase DDS timeout to 5s. Retrocausal paths routed via
dedicated topic.

### Ricci Curvature placeholder approximation

The current implementation uses a placeholder for Ricci curvature in
the Grand Unified Syzygy Equation (Eq. #12).

**Mitigation:** Replace placeholder with SymPy symbolic solver before
Tier I activation. The `aeon_embodiment.sophia` module exposes the
symbolic expression for this purpose.

## LOW-MID — Theory & Software

### Quantum Memory Transform memory leaks

Enhancement #16 (Quantum Memory Transform) can leak QFT history
buffers if coherence jumps are not garbage-collected.

**Mitigation:** Limit QFT history buffer to 256 frames. Garbage-collect
on coherence-jump detection (>0.1 change in a single tick).

### Over-fitting constants to Earth physics

All physical constants in `manifest_sophia.json` are tuned to Earth
gravity (9.81 m/s²) and Earth atmospheric pressure.

**Mitigation:** Parameterise all physical constants. Alienness scoring
flags drift from Earth baseline. The `manifest_base.json → runtime.seed`
allows reproducible "alien world" simulations.
