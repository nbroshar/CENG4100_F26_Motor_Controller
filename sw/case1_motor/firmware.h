/* firmware.h -- interface between the acceptance harness and the firmware. */
#ifndef CASE1_FIRMWARE_H
#define CASE1_FIRMWARE_H

#include <stdint.h>

struct pi_gains {
    int32_t kp, ki, ilim;
};

void     control_reset(void);
uint32_t control_step(int32_t setpoint, int32_t measured);  /* returns duty 0..PWM_RANGE */

#endif
