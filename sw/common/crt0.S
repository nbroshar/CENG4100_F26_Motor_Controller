# crt0.S -- startup code. Runs at the reset PC (0x0000_0000).
#   1. set the global pointer and stack pointer
#   2. clear .bss (uninitialized globals must start at zero)
#   3. call main()
#   4. report main's return value to tohost: 0 -> PASS, n -> FAIL code n
# Uses only RV32I instructions and no CSRs.

    .equ TOHOST, 0x1000F000

    .section .text.init
    .globl _start
_start:
    .option push
    .option norelax
    la      gp, __global_pointer$
    .option pop
    la      sp, __stack_top

    la      t0, __bss_start
    la      t1, __bss_end
1:  bgeu    t0, t1, 2f
    sw      zero, 0(t0)
    addi    t0, t0, 4
    j       1b

2:  call    main

    # main returned: a0 == 0 -> write 1 (PASS), else (a0 << 1) | 1 (FAIL code)
    li      t0, TOHOST
    li      t1, 1
    beqz    a0, 3f
    slli    t1, a0, 1
    ori     t1, t1, 1
3:  sw      t1, 0(t0)
4:  j       4b
