/* mmio.h -- register addresses from docs/memory_map.md (locked). */
#ifndef MMIO_H
#define MMIO_H

#include <stdint.h>

#define MMIO32(addr) (*(volatile uint32_t *)(addr))

/* GPIO */
#define LED          MMIO32(0x10000000u)  /* R/W bits 15:0 */
#define SW           MMIO32(0x10000004u)  /* R   bits 15:0 */
#define BTN          MMIO32(0x10000008u)  /* R   bit 4 U, 3 L, 2 R, 1 D, 0 C */
#define SEG          MMIO32(0x1000000Cu)  /* R/W four hex digits */

/* UART, 115200 8N1 */
#define UART_TX      MMIO32(0x10001000u)  /* W   bits 7:0 */
#define UART_STATUS  MMIO32(0x10001004u)  /* R   bit 0 TX busy, bit 1 RX ready */
#define UART_RX      MMIO32(0x10001008u)  /* R   bits 7:0, read clears RX ready */
#define UART_TX_BUSY  (1u << 0)
#define UART_RX_READY (1u << 1)

/* Timer */
#define TIMER_COUNT  MMIO32(0x10002000u)  /* R   cycles since reset */
#define TIMER_CTRL   MMIO32(0x10002004u)  /* W   1 = reset count */

/* PWM (Case 1 peripheral; optional for other cases) */
#define PWM_PERIOD   MMIO32(0x10004000u)  /* R/W bits 15:0, counter period in CPU cycles */
#define PWM_DUTY     MMIO32(0x10004004u)  /* R/W bits 15:0, output high while count < duty */
#define PWM_CTRL     MMIO32(0x10004008u)  /* R/W bit 0 enable: LEDs show LED register gated by PWM */

/* Test result */
#define TOHOST       MMIO32(0x1000F000u)  /* W   1 = pass, (n << 1) | 1 = fail n */

/* CPU clock frequency in Hz. Change this after decision D12 if your core does
 * not run at 100 MHz. The case programs use it to convert timer cycles to
 * microseconds. */
#ifndef CPU_HZ
#define CPU_HZ 100000000u
#endif

#endif
