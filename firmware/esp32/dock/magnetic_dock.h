/*
 * magnetic_dock.h — ESP32 GPIO interrupt handler for magnetic pogo-pin docking.
 *
 * Each docking face has one pogo-pin GPIO routed to an interrupt. The ISR
 * fires on physical contact, and the main task picks the event up via a
 * FreeRTOS queue and notifies the Python orchestrator via micro-ROS.
 *
 * Blueprint §04: "GPIO interrupts (gpiozero.Button on pogo pins); NetworkX
 * graph edge add/remove."
 */

#pragma once

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    AEON_DOCK_UNDOCKED    = 0,
    AEON_DOCK_DETECTED    = 1,
    AEON_DOCK_NEGOTIATING = 2,
    AEON_DOCK_DOCKED      = 3,
    AEON_DOCK_FAULT       = 4
} aeon_dock_state_t;

typedef struct {
    uint8_t            face_id;
    aeon_dock_state_t  state;
    char               partner_node[16];
    char               power_role[8];   /* "source" | "sink" | "peer" */
    uint32_t           timestamp_ms;
} aeon_dock_event_t;

typedef void (*aeon_dock_callback_t)(const aeon_dock_event_t *event);

/* Register a face (gpio_num) and start its ISR. */
int  aeon_dock_register_face(uint8_t face_id, int gpio_num);

/* Set the partner identity once negotiation completes. */
bool aeon_dock_set_partner(uint8_t face_id, const char *partner_node_id);

/* Subscribe to dock state changes. */
void aeon_dock_on_event(aeon_dock_callback_t cb);

/* Snapshot accessor. */
aeon_dock_state_t aeon_dock_get_state(uint8_t face_id);

#ifdef __cplusplus
}
#endif
