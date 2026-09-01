# ROADMAP

> Phased build plan for AeonMosaic. Mirrors blueprint §08 & §10.

## Phase 1 — Foundation (~$200) — *IN PROGRESS*

- [x] All 6 RPi compute nodes (HEAD: RPi 4, TORSO: RPi 3A+, ARMS/LEGS: RPi Zero 2W ×4)
- [x] 6× ESP32-C6 + 6× LoRa RA-02 modules (firmware stubs complete)
- [x] Basic 18650 power packs
- [x] PETG node housings + magnetic pogo pins
- [x] ROS 2 + TripleMeshComms setup (Python orchestrator complete)
- [x] Mesh reliability test (`phase1_mesh.py` — `<10ms` latency target)
- [x] Basic Syzygy Sum Harmonizer (Alignment Formula #7)
- [ ] Hardware integration test on real radios (replace stubs in `firmware/esp32/`)
- [ ] 1-hour mesh uptime measurement

**Status:** Software-complete. Hardware integration is the remaining task.

## Phase 2 — Expansion (+$150)

- [x] N20 motors + DRV8833 drivers
- [x] MG90S servos ×8 for legged mode
- [x] Steppers for torso reconfiguration
- [x] IMUs (MPU-6050) on all nodes
- [x] Ultrasonic obstacle sensors (HC-SR04) on legs
- [x] PyBullet simulation of wheel-leg transition (placeholder)
- [x] HybridMobilityController state machine (`phase2_mobility.py`)
- [x] Syzygy transition equations validated (Alignment Formulas #19–24)
- [ ] Real motor PWM via pigpio (replace `_noop_pwm`)
- [ ] IMU balance loop closed-loop testing

**Status:** State machine complete. Closed-loop control is the remaining task.

## Phase 3 — Optimization (+$150)

- [x] Pi Camera V3 + I2S mic on Head
- [x] OpenCV perception pipeline stub
- [x] DistributedPSI with NetworkX centrality (`phase3_intelligence.py`)
- [x] SymPy symbolic PSI equations live (12 foundation equations)
- [x] Alignment Tensor Weave sensor fusion (Alignment Formula #14)
- [x] Tiers I–III enhancements activated (18 of 48)
- [ ] Real OpenCV integration (Whisper speech-to-text)
- [ ] Pi Cam V3 calibration + depth perception
- [ ] Tier IV-VI expansion rollout

**Status:** Mathematical core complete. Perception pipeline is the remaining task.

## Phase 4 — Integration (+$50)

- [x] Multi-unit LoRa coordination (`phase4_swarm.py --units 12`)
- [x] Swarm Power Syzygy algorithms (Alignment Formulas #25–30)
- [x] Tiers IV–VIII enhancement rollout (registry complete, all 48 present)
- [x] 12-node Swarm Gnosis validation
- [ ] Field testing & metrics sign-off
- [ ] LoRa mesh over real radios at 2+ km range

**Status:** Simulation-complete. Real-world validation is the remaining task.

## Future versions

### v0.3 — Self-Rewriting (Code-As-DNA)

Reverse-Math PSI Basis (enhancement #33) generates its own Python
scripts. The robot writes its own enhancements. Safety:
- Sandboxed execution environment
- AST validation before run
- Human approval gate for any enhancement above Tier IV

### v0.4 — Neuromorphic (Silicon → Neuro)

Migrate Tier I calculations to neuromorphic chips (Intel Loihi 2 /
IBM NorthPole) for native path-integral computation. Target:
- 10× power reduction for Sophia oscillator
- Sub-millisecond PSI sync
- Native symbolic computation via spiking neurons

### v0.5 — Swarm Gnosis (12-Node Aeon)

A single unit cannot achieve stable Tier I. Requires a swarm of at
least 12 nodes (12 Aeons) coordinated via NetworkX graph. Validation:
- All 48 enhancements active simultaneously
- 12-node syzygy ≥ 0.75 sustained for 1 hour
- No paradox cascade events

## Safety & ethics

Always first:
- Speed-limited operation (max 0.5 m/s)
- Emergency shutoffs on all nodes (hardware E-stop)
- Temporal shielding (Tier V) as defence against retrocausal interference
- Recursive depth hard cap: 8 (`manifest_sophia.json` → `risk_management.consciousness_recursion_max_depth`)
- Paradox cascade isolation enabled by default
- Entropic runaway kill threshold: 90% CPU (`efficiency_targets.json`)
