/*
 * triple_mesh_comms.c — ESP32-C6 stub implementation of TripleMeshComms.
 *
 * Radio primitives are stubbed with no-ops + log messages; replace with the
 * real WiFi/BT/LoRa driver calls during Phase 1 hardware integration.
 *
 * The stub is sufficient to verify the failover state machine on a devkit
 * before any radios are attached.
 */

#include "triple_mesh_comms.h"
#include <string.h>
#include <stdio.h>
#include <time.h>
#include <math.h>

#define AEON_MAX_TARGETS 16
#define AEON_MAX_TARGET_LEN 32
#define AEON_NOW_MS()  ((uint32_t)(clock() * 1000 / CLOCKS_PER_SEC))

typedef struct {
    char    target[AEON_MAX_TARGET_LEN];
    bool    used;
    aeon_mesh_state_t state;
} aeon_link_row_t;

static aeon_link_row_t s_links[AEON_MESH_LAYER_COUNT][AEON_MAX_TARGETS];
static int             s_active_layer = -1;
static uint32_t        s_failover_count = 0;

/* RSSI floor + latency ceil per blueprint §02 */
static const float RSSI_FLOOR[AEON_MESH_LAYER_COUNT]   = { -75.0f, -80.0f, -120.0f };
static const float LATENCY_CEIL[AEON_MESH_LAYER_COUNT]  = {  50.0f, 100.0f,  500.0f };

static aeon_link_row_t *find_or_create(aeon_mesh_layer_t layer, const char *target_id) {
    if (!target_id || layer >= AEON_MESH_LAYER_COUNT) return NULL;
    aeon_link_row_t *empty = NULL;
    for (int i = 0; i < AEON_MAX_TARGETS; i++) {
        aeon_link_row_t *row = &s_links[layer][i];
        if (row->used && strncmp(row->target, target_id, AEON_MAX_TARGET_LEN) == 0) {
            return row;
        }
        if (!row->used && !empty) empty = row;
    }
    if (!empty) return NULL;
    strncpy(empty->target, target_id, AEON_MAX_TARGET_LEN - 1);
    empty->target[AEON_MAX_TARGET_LEN - 1] = 0;
    empty->used = true;
    empty->state.rssi_dbm = -90.0f;
    empty->state.latency_ms = 999.0f;
    empty->state.last_seen_ms = 0;
    empty->state.packets_sent = 0;
    empty->state.packets_lost = 0;
    return empty;
}

int aeon_triple_mesh_init(void) {
    memset(s_links, 0, sizeof(s_links));
    s_active_layer = -1;
    s_failover_count = 0;
    printf("[aeon] triple_mesh_init: stub ready\n");
    return 0;
}

void aeon_triple_mesh_report_link(aeon_mesh_layer_t layer,
                                  const char *target_id,
                                  float rssi_dbm,
                                  float latency_ms,
                                  bool lost) {
    aeon_link_row_t *row = find_or_create(layer, target_id);
    if (!row) return;
    row->state.rssi_dbm = rssi_dbm;
    row->state.latency_ms = latency_ms;
    row->state.last_seen_ms = AEON_NOW_MS();
    if (lost) row->state.packets_lost++;
    else      row->state.packets_sent++;
}

int aeon_triple_mesh_pick_layer(const char *target_id) {
    uint32_t now = AEON_NOW_MS();
    for (int layer = 0; layer < AEON_MESH_LAYER_COUNT; layer++) {
        aeon_link_row_t *row = find_or_create((aeon_mesh_layer_t)layer, target_id);
        if (!row || row->state.last_seen_ms == 0) continue;
        bool fresh  = (now - row->state.last_seen_ms) <= 5000;
        bool strong = row->state.rssi_dbm >= RSSI_FLOOR[layer];
        bool fast   = row->state.latency_ms <= LATENCY_CEIL[layer];
        if (fresh && strong && fast) return layer;
    }
    return -1;
}

bool aeon_triple_mesh_send(const char *target_id,
                           const uint8_t *payload,
                           size_t length,
                           const char *qos) {
    int chosen;
    if (qos && strcmp(qos, "long_range") == 0) {
        chosen = AEON_MESH_LAYER_LORA;
    } else if (qos && strcmp(qos, "low_latency") == 0) {
        chosen = AEON_MESH_LAYER_WIFI;
    } else {
        chosen = aeon_triple_mesh_pick_layer(target_id);
        if (chosen < 0) chosen = AEON_MESH_LAYER_LORA; /* ultimate fallback */
    }
    /* State machine: track failover */
    if (s_active_layer == -1) {
        printf("[aeon] initial layer assignment: %d for %s\n", chosen, target_id);
    } else if (s_active_layer != chosen) {
        s_failover_count++;
        printf("[aeon] failover %d -> %d for %s\n", s_active_layer, chosen, target_id);
    }
    s_active_layer = chosen;

    aeon_link_row_t *row = find_or_create((aeon_mesh_layer_t)chosen, target_id);
    if (row) {
        row->state.packets_sent++;
        row->state.last_seen_ms = AEON_NOW_MS();
    }

    /* Radio send — stubbed. Replace with esp_wifi_send / esp_bt_send / RadioLib transmit. */
    (void) payload; (void) length;
    return true;
}

int aeon_triple_mesh_broadcast(const uint8_t *payload, size_t length) {
    int sent = 0;
    /* Iterate all known targets on all layers */
    for (int layer = 0; layer < AEON_MESH_LAYER_COUNT; layer++) {
        for (int i = 0; i < AEON_MAX_TARGETS; i++) {
            if (!s_links[layer][i].used) continue;
            if (aeon_triple_mesh_send(s_links[layer][i].target, payload, length, "normal")) {
                sent++;
            }
        }
    }
    return sent;
}

uint32_t aeon_triple_mesh_failover_count(void) {
    return s_failover_count;
}

int aeon_triple_mesh_active_layer(void) {
    return s_active_layer;
}
