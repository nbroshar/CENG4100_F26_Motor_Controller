/* hello -- first C program for a new core. Runs in simulation and on the board.
 * Prints over the UART, checks a few results that use the software multiply
 * and divide, and returns 0 (PASS via tohost) if everything matched.
 */
#include <stdint.h>
#include "mmio.h"
#include "uart.h"

static int failures;

static void expect(const char *what, int32_t got, int32_t want)
{
    if (got != want) {
        printf("  FAIL %s: got %d, expected %d\n", what, got, want);
        failures++;
    }
}

int main(void)
{
    printf("Hello from RV32I on the Basys 3!\n");

    volatile int32_t a = 1234, b = -56;       /* volatile: computed at run time */
    expect("multiply", a * b, -69104);
    expect("divide",   a / b, -22);
    expect("modulo",   a % b, 2);
    expect("divide by zero", a / (b - b), -1);

    LED = 0xA5A5;
    printf("printf check: %d %u 0x%08x %s %c\n", -42, 42u, 0xBEEFu, "ok", '!');
    printf("%s\n", failures ? "Self-check FAILED" : "Self-check passed");
    return failures;
}
