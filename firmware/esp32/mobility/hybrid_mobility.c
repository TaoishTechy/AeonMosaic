/*
 * hybrid_mobility.c — ESP32-C6 PWM driver stub for the Centaur-Bot chassis.
 *
 * Manages 4× N20 motors (DRV8833) in wheeled mode and 8× MG90S servos in
 * legged mode. Mode transitions use a stepper-driven torso reconfiguration
 * with GPIO waveform sync (blueprint §02: <2 s deadline).
 *
 * Stubbed for unit testing — replace the PWM primitives with ESP-IDF's
 * ledc_set_duty / mcpwm_set_duty calls during Phase 2 integration.
 */

#include "hybrid_mobility.h"
#include <string.h>
#include <stdio.h>

typedef enum {
    AEON_MOBILITY_WHEELED = 0,
    AEON_MOBILITY_LEGGED  = 1,
    AEON_MOBILITY_TRANSITIONING = 2,
    AEON_MOBILITY_FAULT = 3
} aeon_mobility_mode_t;

static aeon_mobility_mode_t s_mode = AEON_MOBILITY_WHEELED;
static uint32_t s_transitions = 0;
static float    s_last_transition_ms = 0.0f;
static bool     s_imu_balance_ok = true;
static bool     s_obstacle_ahead = false;

int aeon_mobility_init(float transition_deadline_s) {
    (void) transition_deadline_s;
    s_mode = AEON_MOBILITY_WHEELED;
    s_transitions = 0;
    s_last_transition_ms = 0.0f;
    printf("[aeon] mobility_init: stub ready (wheeled mode)\n");
    return 0;
}

static bool do_transition(aeon_mobility_mode_t target) {
    if (s_mode == AEON_MOBILITY_TRANSITIONING) return false;
    if (target == AEON_MOBILITY_LEGGED && !s_imu_balance_ok) return false;
    aeon_mobility_mode_t prev = s_mode;
    s_mode = AEON_MOBILITY_TRANSITIONING;
    /* Stub waveform sync — real impl drives stepper reconfiguration via GPIO matrix */
    s_mode = target;
    s_last_transition_ms = 50.0f; /* simulated */
    s_transitions++;
    printf("[aeon] mobility transition %d -> %d in %.0f ms\n",
           (int)prev, (int)target, s_last_transition_ms);
    return true;
}

bool aeon_mobility_request_mode(int target_int) {
    if (target_int < 0 || target_int > 1) return false;
    return do_transition((aeon_mobility_mode_t)target_int);
}

void aeon_mobility_update_imu(bool balance_ok) {
    s_imu_balance_ok = balance_ok;
    if (!balance_ok && s_mode == AEON_MOBILITY_LEGGED) {
        printf("[aeon] IMU balance lost — falling back to wheeled\n");
        do_transition(AEON_MOBILITY_WHEELED);
    }
}

void aeon_mobility_update_proximity(bool obstacle_ahead) {
    s_obstacle_ahead = obstacle_ahead;
    if (obstacle_ahead && s_mode == AEON_MOBILITY_WHEELED) {
        printf("[aeon] obstacle detected — switching to legged\n");
        do_transition(AEON_MOBILITY_LEGGED);
    }
}

void aeon_mobility_set_wheel_speeds(const int speeds_us[4]) {
    if (s_mode != AEON_MOBILITY_WHEELED) return;
    for (int i = 0; i < 4; i++) {
        int p = speeds_us[i];
        if (p < 1000) p = 1000;
        if (p > 2000) p = 2000;
        /* Stub — real impl: ledc_set_duty(LEDC_LOW_SPEED_MODE, ch, p); */
    }
}

void aeon_mobility_set_leg_pose(const int pose_us[8]) {
    if (s_mode != AEON_MOBILITY_LEGGED) return;
    for (int i = 0; i < 8; i++) {
        int p = pose_us[i];
        if (p < 500) p = 500;
        if (p > 2500) p = 2500;
        /* Stub — real impl: mcpwm_set_duty(MCPWM_UNIT_0, MCPWM_TIMER_0, MCPWM_OPR_A, p); */
    }
}

int  aeon_mobility_mode(void)         { return (int)s_mode; }
int  aeon_mobility_transitions(void)  { return (int)s_transitions; }
float aeon_mobility_last_transition_ms(void) { return s_last_transition_ms; }
