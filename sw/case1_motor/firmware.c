/* firmware.c -- the customer's current motor-control firmware (Case 1).
 *
 * A PI speed controller: each pass reads the target speed and the measured
 * speed, and sets the motor's PWM duty cycle. It computes the right answer,
 * but its run time changes from pass to pass. Your team may rewrite this file
 * (and change the hardware) to meet the requirements in the case brief. The
 * outputs must stay exactly the same: the harness in main.c checks every one.
 */
#include <stdint.h>
#include "mmio.h"
#include "firmware.h"
#include "data.h"

/* Gains live in memory (not constants) so the customer can tune them later. */
struct pi_gains gains = { GAIN_KP, GAIN_KI, INTEG_LIM };

static int32_t integ;

void control_reset(void)
{
    integ = 0;
}

uint32_t control_step(int32_t sp, int32_t meas)
{
    int32_t err = sp - meas;
    int32_t p = gains.kp * err;

    integ += gains.ki * err;
    if (integ > gains.ilim)            /* anti-windup */
        integ = gains.ilim;
    else if (integ < -gains.ilim)
        integ = -gains.ilim;

    int32_t u = (p + integ) >> 8;      /* gains are Q8 fixed point */
    if (u < 0)
        u = 0;
    else if (u > PWM_RANGE)
        u = PWM_RANGE;

    PWM_DUTY = (uint32_t)u;
    return (uint32_t)u;
}
