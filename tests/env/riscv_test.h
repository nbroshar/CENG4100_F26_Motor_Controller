// riscv_test.h -- CSR-free test environment for the official riscv-tests.
//
// The stock environment (riscv-tests/env/p) sets up machine-mode trap handling
// with CSR instructions and ends a test with ECALL. A pure RV32I core has no
// CSRs, so this replacement keeps the same macro names but:
//   - starts the test directly at _start (the reset PC, 0x0000_0000),
//   - reports the result with one store to tohost at 0x1000_F000:
//       PASS: writes 1
//       FAIL: writes (TESTNUM << 1) | 1, where TESTNUM is the failing case
//   - then spins forever.
// Only these macros differ; the test bodies are unmodified upstream code.

#ifndef CSR_FREE_RISCV_TEST_H
#define CSR_FREE_RISCV_TEST_H

#define TOHOST_ADDR 0x1000F000

// The failing test-case number lives in gp (x3), as in upstream riscv-tests.
#define TESTNUM gp

#define RVTEST_RV32U                                                    \
  .macro init;                                                          \
  .endm

#define RVTEST_RV64U RVTEST_RV32U

#define RVTEST_CODE_BEGIN                                               \
        .section .text.init;                                            \
        .align  2;                                                      \
        .globl _start;                                                  \
_start:                                                                 \
        li      TESTNUM, 0;                                             \
        init;

#define RVTEST_CODE_END                                                 \
        unimp

#define RVTEST_PASS                                                     \
        li      t6, TOHOST_ADDR;                                        \
        li      t5, 1;                                                  \
        sw      t5, 0(t6);                                              \
1:      j       1b;

#define RVTEST_FAIL                                                     \
        li      t6, TOHOST_ADDR;                                        \
        slli    t5, TESTNUM, 1;                                         \
        ori     t5, t5, 1;                                              \
        sw      t5, 0(t6);                                              \
1:      j       1b;

#define RVTEST_DATA_BEGIN                                               \
        .data;                                                          \
        .align 4;

#define RVTEST_DATA_END

#endif
