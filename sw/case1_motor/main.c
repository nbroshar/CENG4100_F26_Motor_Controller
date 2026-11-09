/* main.c -- Case 1 acceptance harness (motor controller). Do not modify.
 *
 * Runs control_step() for N_PASSES passes with recorded inputs and checks:
 *   1. every duty-cycle output matches the customer's golden data,
 *   2. every pass takes exactly the same number of CPU cycles,
 *   3. the slowest pass finishes within TARGET_NS (target.h).
 * Result through tohost: PASS, or FAIL code 1 (wrong output),
 * 2 (timing varies) or 3 (too slow).
 */
#include <stdint.h>
#include "mmio.h"
#include "uart.h"
#include "case_util.h"
#include "firmware.h"
#include "data.h"
#include "target.h"

int main(void)
{
    print_header("Case 1: motor controller");

    PWM_PERIOD = PWM_RANGE;
    PWM_CTRL = 1;
    LED = 0xFFFF;                     /* LED brightness follows the duty cycle */
    control_reset();

    uint32_t min_cycles = 0xFFFFFFFFu, max_cycles = 0, wrong = 0, first_got = 0;
    int first_wrong = -1;

    for (int i = 0; i < N_PASSES; i++) {
        int32_t sp = setpoint[i], meas = measured[i];
        uint32_t t0 = TIMER_COUNT;
        uint32_t duty = control_step(sp, meas);
        uint32_t t1 = TIMER_COUNT;

        uint32_t dt = t1 - t0;
        if (dt < min_cycles) min_cycles = dt;
        if (dt > max_cycles) max_cycles = dt;
        if (duty != expected_duty[i]) {
            if (first_wrong < 0) {
                first_wrong = i;
                first_got = duty;
            }
            wrong++;
        }
    }

    uint32_t worst_ns = cycles_to_ns(max_cycles);
    printf("Passes: %d, wrong outputs: %u", N_PASSES, wrong);
    if (first_wrong >= 0)
        printf(" (first at pass %d: got %u, expected %u)", first_wrong,
               first_got, expected_duty[first_wrong]);
    printf("\nCycles per pass: min %u, max %u, variation %u\n",
           min_cycles, max_cycles, max_cycles - min_cycles);
    print_us("Worst-case pass", worst_ns);
    print_us("Target", TARGET_NS);

    if (wrong) {
        puts("RESULT: FAIL, outputs differ from the golden data");
        return CASE_WRONG_OUTPUT;
    }
    if (max_cycles != min_cycles) {
        puts("RESULT: FAIL, pass time is not constant");
        return CASE_TIMING_VARIES;
    }
    if (worst_ns > TARGET_NS) {
        puts("RESULT: FAIL, slower than the target");
        return CASE_TOO_SLOW;
    }
    puts("RESULT: PASS");
    return CASE_PASS;
}
