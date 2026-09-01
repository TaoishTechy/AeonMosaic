# ESP32-C6 Firmware — AeonMosaic

This directory contains the ESP-IDF firmware stubs for the ESP32-C6 mesh
nodes. The firmware exposes the TripleMeshComms failover state machine,
the MagneticDockManager GPIO interrupt handler, and the HybridMobility
PWM driver — all callable from the Python orchestrator via micro-ROS.

## Directory layout

```
firmware/esp32/
├── mesh/
│   ├── triple_mesh_comms.h    # Public API for the failover coordinator
│   └── triple_mesh_comms.c    # Stub implementation (radios stubbed)
├── dock/
│   └── magnetic_dock.h        # Pogo-pin GPIO ISR + dock event queue
└── mobility/
    ├── hybrid_mobility.h      # Wheeled / legged state machine API
    └── hybrid_mobility.c      # PWM driver stub (4× N20 + 8× MG90S)
```

## Building

The firmware uses ESP-IDF v5.x with the ESP32-C6 as the target.

```bash
# Install ESP-IDF per the official docs:
# https://docs.espressif.com/projects/esp-idf/en/latest/esp32c6/get-started/

# From the firmware/esp32/ directory:
idf.py set-target esp32c6
idf.py build flash monitor
```

## Stub status

All radio primitives (`esp_wifi_send`, `esp_bt_send`, `RadioLib` transmit)
are stubbed with `printf` calls. The state machines themselves are fully
implemented — they can be unit-tested on a devkit before any radios are
attached.

Replace the stubs with the real driver calls during Phase 1 hardware
integration (see `docs/ROADMAP.md`).
