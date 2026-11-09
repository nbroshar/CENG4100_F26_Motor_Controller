/* link.ld -- linker script for the locked memory map (docs/memory_map.md).
 * Code goes in instruction memory; everything a program reads or writes as
 * data (constants, strings, globals, stack) goes in data memory, so the same
 * image works for Harvard and von Neumann designs.
 * Used by sw/ programs and by tests/ (riscv-tests).
 */
OUTPUT_ARCH("riscv")
ENTRY(_start)

MEMORY
{
    IMEM (rx)  : ORIGIN = 0x00000000, LENGTH = 16K
    DMEM (rw)  : ORIGIN = 0x00004000, LENGTH = 16K
}

SECTIONS
{
    .text : {
        *(.text.init)            /* _start first: the reset PC is 0x0 */
        *(.text .text.*)
    } > IMEM

    .rodata : {
        *(.rodata .rodata.* .srodata .srodata.*)
    } > DMEM

    .data : {
        *(.data .data.*)
        . = ALIGN(4);
        __global_pointer$ = . + 0x800;
        *(.sdata .sdata.*)
    } > DMEM

    .bss (NOLOAD) : {
        . = ALIGN(4);
        __bss_start = .;
        *(.sbss .sbss.* .bss .bss.* COMMON)
        . = ALIGN(4);
        __bss_end = .;
    } > DMEM

    __stack_top = ORIGIN(DMEM) + LENGTH(DMEM);

    /DISCARD/ : { *(.eh_frame .eh_frame_hdr .comment .note.*) }
}
