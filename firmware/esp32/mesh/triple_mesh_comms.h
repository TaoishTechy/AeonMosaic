/*
 * triple_mesh_comms.h — ESP32-C6 firmware stub for the TripleMeshComms layer.
 *
 * Implements the WiFi 6 / BT 5.3 / LoRa failover priority from blueprint §02.
 * This is a *stub*: the radio primitives are stubbed and the public API mirrors
 * what the Python orchestrator expects to call via micro-ROS.
 *
 * Build:
 *   idf.py set-target esp32c6
 *   idf.py build flash
 */

#pragma once

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    AEON_MESH_LAYER_WIFI = 0,
    AEON_MESH_LAYER_BT   = 1,
    AEON_MESH_LAYER_LORA = 2,
    AEON_MESH_LAYER_COUNT
} aeon_mesh_layer_t;

typedef struct {
    float    rssi_dbm;
    float    latency_ms;
    uint32_t last_seen_ms;
    uint32_t packets_sent;
    uint32_t packets_lost;
} aeon_mesh_state_t;

/* Initialize all three radio layers + register micro-ROS topics. */
int  aeon_triple_mesh_init(void);

/* Send payload to target_id; layer chosen by failover priority. */
bool aeon_triple_mesh_send(const char *target_id,
                           const uint8_t *payload,
                           size_t length,
                           const char *qos);

/* Broadcast to all known peers. */
int  aeon_triple_mesh_broadcast(const uint8_t *payload, size_t length);

/* Report link state from a radio driver (called from ISR context OK). */
void aeon_triple_mesh_report_link(aeon_mesh_layer_t layer,
                                  const char *target_id,
                                  float rssi_dbm,
                                  float latency_ms,
                                  bool lost);

/* Pick the best layer for the given target. Returns -1 if none. */
int  aeon_triple_mesh_pick_layer(const char *target_id);

/* Statistics accessors. */
uint32_t aeon_triple_mesh_failover_count(void);
int      aeon_triple_mesh_active_layer(void); /* returns -1 before first send */

#ifdef __cplusplus
}
#endif
