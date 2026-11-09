/* case_util.h -- shared helpers for the case-study acceptance harnesses. */
#ifndef CASE_UTIL_H
#define CASE_UTIL_H

#include <stdint.h>

/* Harness exit codes, reported through tohost (FAIL code n). */
#define CASE_PASS            0
#define CASE_WRONG_OUTPUT    1
#define CASE_TIMING_VARIES   2
#define CASE_TOO_SLOW        3

uint32_t cycles_to_ns(uint32_t cycles);            /* uses CPU_HZ from mmio.h */
void     print_us(const char *label, uint32_t ns);  /* prints "label: 12.345 us" */
void     print_header(const char *case_name);       /* name, clock, ISA */

#endif
