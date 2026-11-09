# Locked memory map

Both teams use this map unchanged, so every core runs the same riscv-tests and
C programs. Little-endian. Reset PC = 0x0000_0000.

| Address range | Size | Region | Notes |
| --- | --- | --- | --- |
| 0x0000_0000 – 0x0000_3FFF | 16 KB | Instruction memory | `.text`; image `imem.mem` |
| 0x0000_4000 – 0x0000_7FFF | 16 KB | Data memory | `.rodata`, `.data`, `.bss`; stack starts at 0x0000_8000 and grows down; image `dmem.mem` |
| 0x0000_8000 – 0x0FFF_FFFF | — | Reserved | Access undefined (D9 decides the response) |
| 0x1000_0000 – 0x1000_0FFF | 4 KB | GPIO | |
| 0x1000_1000 – 0x1000_1FFF | 4 KB | UART | 115200 baud, 8 data bits, no parity, 1 stop bit |
| 0x1000_2000 – 0x1000_2FFF | 4 KB | Timer | |
| 0x1000_3000 – 0x1000_3FFF | 4 KB | Sensor (stretch) | Team-defined if built |
| 0x1000_4000 – 0x1000_4FFF | 4 KB | PWM | Required for Case 1; optional otherwise |
| 0x1000_F000 – 0x1000_FFFF | 4 KB | tohost | Pass/fail for tests; `rtl/tohost.v` |

**Harvard designs (D2):** the instruction region is fetch-only. Loads and
stores to 0x0000_0000–0x0000_3FFF are undefined, which the RISC-V spec allows
because the execution environment defines which addresses each access type may
use. The linker script therefore puts string constants and initialized data in
data memory.

**Von Neumann designs (D2):** one 32 KB memory covers 0x0000_0000–0x0000_7FFF,
loaded from the combined image `mem.mem`.

## Peripheral registers

All 32-bit, word access only (byte or halfword access to peripherals is
undefined).

| Address | Name | Access | Function |
| --- | --- | --- | --- |
| 0x1000_0000 | LED | R/W | Bits 15:0 drive `led[15:0]` |
| 0x1000_0004 | SW | R | Bits 15:0 read `sw[15:0]` |
| 0x1000_0008 | BTN | R | Bit 4 btnU, 3 btnL, 2 btnR, 1 btnD, 0 btnC |
| 0x1000_000C | SEG | R/W | Bits 15:0 = four hex digits on the 7-segment display |
| 0x1000_1000 | UART_TX | W | Write bits 7:0 to send one byte |
| 0x1000_1004 | UART_STATUS | R | Bit 0 = TX busy, bit 1 = RX byte ready |
| 0x1000_1008 | UART_RX | R | Bits 7:0 = received byte; reading clears "RX byte ready" |
| 0x1000_2000 | TIMER_COUNT | R | CPU clock cycles since reset, wraps at 2^32 (set `CPU_HZ` when building C so programs convert cycles to time) |
| 0x1000_2004 | TIMER_CTRL | W | Write 1 to reset the count to 0 |
| 0x1000_4000 | PWM_PERIOD | R/W | Bits 15:0: PWM period in CPU clock cycles (counter runs 0 to period − 1) |
| 0x1000_4004 | PWM_DUTY | R/W | Bits 15:0: output is high while the counter is below this value |
| 0x1000_4008 | PWM_CTRL | R/W | Bit 0 = enable. When enabled, each LED shows its LED register bit AND the PWM output, so brightness follows the duty cycle |
| 0x1000_F000 | TOHOST | W | Write 1 = pass; any other odd value = fail, code = value >> 1 |

## Memory image format

`imem.mem`, `dmem.mem` and `mem.mem` hold one 32-bit word per line in hex, in
address order, starting at the region's base address. Load them with
`$readmemh("imem.mem", array)` using the plain file name; the scripts copy the
right images into the working directory for simulation and synthesis.

| File | Words (full size) | Covers (full size) |
| --- | --- | --- |
| `imem.mem` | 4096 | 0x0000_0000 – 0x0000_3FFF |
| `dmem.mem` | 4096 | 0x0000_4000 – 0x0000_7FFF |
| `mem.mem` | 8192 | 0x0000_0000 – 0x0000_7FFF |

These are the sizes with the full 16 KB memories. If your team chooses smaller
memories (D4 Memory sizes), change the `LENGTH` lines in `sw/common/link.ld`:
the build scripts read them, and each image then has exactly as many words as
your memory (for example 2,048 words for an 8 KB instruction memory). Keep
`link.ld`, your memory modules and these images the same size, and rebuild
the riscv-tests after changing it.
