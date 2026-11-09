/* case_util.c -- shared helpers for the case-study acceptance harnesses. */
#include <stdint.h>
#include "mmio.h"
#include "uart.h"
#include "case_util.h"

uint32_t cycles_to_ns(uint32_t cycles)
{
    return (uint32_t)(((uint64_t)cycles * 1000000000ull) / CPU_HZ);
}

void print_us(const char *label, uint32_t ns)
{
    printf("%s: %u.%03u us\n", label, ns / 1000u, ns % 1000u);
}

void print_header(const char *case_name)
{
    printf("\n=== %s acceptance test ===\n", case_name);
    printf("CPU clock (CPU_HZ): %u Hz", (uint32_t)CPU_HZ);
#if defined(__riscv_mul) || defined(__riscv_zmmul)
    printf(", hardware multiply\n");
#else
    printf(", software multiply\n");
#endif
}
