/* demo -- interactive monitor: the week 6 deliverable.
 * Type commands in a serial terminal (115200 8N1) and the CPU responds.
 *
 *   help          list commands
 *   led <hex>     set the 16 LEDs
 *   seg <hex>     show 4 hex digits on the 7-segment display
 *   sw            read the switches
 *   btn           read the buttons
 *   time          cycles since reset, from the timer
 *   bench         time 1000 multiplies (compare before and after D10)
 */
#include <stddef.h>
#include <stdint.h>
#include "mmio.h"
#include "uart.h"

int strncmp(const char *a, const char *b, size_t n);   /* sw/common/libc_min.c */

static uint32_t parse_hex(const char *s)
{
    uint32_t v = 0;
    while (*s == ' ')
        s++;
    for (; *s; s++) {
        char c = *s;
        if (c >= '0' && c <= '9')      v = (v << 4) | (uint32_t)(c - '0');
        else if (c >= 'a' && c <= 'f') v = (v << 4) | (uint32_t)(c - 'a' + 10);
        else if (c >= 'A' && c <= 'F') v = (v << 4) | (uint32_t)(c - 'A' + 10);
        else break;
    }
    return v;
}

static void help(void)
{
    puts("Commands: help, led <hex>, seg <hex>, sw, btn, time, bench");
}

int main(void)
{
    char line[64];
    puts("");
    puts("CENG 4100 RV32I monitor");
    help();
    for (;;) {
        printf("> ");
        readline(line, sizeof line);
        if (line[0] == '\0')
            continue;
        if (!strncmp(line, "help", 4)) {
            help();
        } else if (!strncmp(line, "led", 3)) {
            LED = parse_hex(line + 3) & 0xFFFF;
            printf("LED = 0x%04x\n", LED);
        } else if (!strncmp(line, "seg", 3)) {
            SEG = parse_hex(line + 3) & 0xFFFF;
            printf("SEG = 0x%04x\n", SEG);
        } else if (!strncmp(line, "sw", 2)) {
            printf("SW = 0x%04x\n", SW & 0xFFFF);
        } else if (!strncmp(line, "btn", 3)) {
            printf("BTN = 0x%02x\n", BTN & 0x1F);
        } else if (!strncmp(line, "time", 4)) {
            printf("%u cycles since reset\n", TIMER_COUNT);
        } else if (!strncmp(line, "bench", 5)) {
            volatile uint32_t x = 12345, y = 678, sum = 0;
            uint32_t start = TIMER_COUNT;
            for (int i = 0; i < 1000; i++)
                sum += x * y;
            uint32_t cycles = TIMER_COUNT - start;
            printf("1000 multiplies: %u cycles (sum %u)\n", cycles, sum);
        } else if (!strncmp(line, "exit", 4)) {
            return 0;                       /* ends a simulation run */
        } else {
            printf("Unknown command: %s\n", line);
        }
    }
}
