/*
 * hybrid_mobility.h — ESP32-C6 hybrid mobility driver (Centaur-Bot chassis).
 */

#pragma once

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

int   aeon_mobility_init(float transition_deadline_s);
bool  aeon_mobility_request_mode(int target_mode);  /* 0=wheeled, 1=legged */
void  aeon_mobility_update_imu(bool balance_ok);
void  aeon_mobility_update_proximity(bool obstacle_ahead);
void  aeon_mobility_set_wheel_speeds(const int speeds_us[4]);
void  aeon_mobility_set_leg_pose(const int pose_us[8]);
int   aeon_mobility_mode(void);
int   aeon_mobility_transitions(void);
float aeon_mobility_last_transition_ms(void);

#ifdef __cplusplus
}
#endif
