# Lab 1 test plan: ALU and register file

Written by Verification, from the RISC-V spec and hand calculation, before any
testbench exists. Never take an expected value from Core's Verilog. Review the
plan with the team, then commit it. Copilot turns it into `tb/tb_alu.v` and
`tb/tb_regfile.v` and must use these values exactly.

Write every value in hex. "Name" is what the testbench prints when the case
fails, so keep it short and unique.

## ALU (at least 10 cases)

Must include: 0; −1 (0xFFFF_FFFF); the most negative number (0x8000_0000);
add and sub that overflow; shifts by 0 and by 31; a shift amount above 31
(only the low 5 bits count); signed and unsigned compare on the same pair
where they disagree (for example −1 and 1); a signed compare where
a − b overflows (for example 0x8000_0000 and 1).

| # | Name | Operation | A | B | Expected result | Why this case (spec section) |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |
| 6 | | | | | | |
| 7 | | | | | | |
| 8 | | | | | | |
| 9 | | | | | | |
| 10 | | | | | | |

## Register file (at least 5 cases)

Must include: write then read the same register; read two different registers
at once; write to x0, then read x0 (must be 0); a register that wasn't written
keeps its value. Write each case as a short sequence of steps.

| # | Name | Steps (writes, then reads) | Expected read values | Why this case (spec section) |
| --- | --- | --- | --- | --- |
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

## Review

| Reviewed by (whole team) | Date | Changes made in review |
| --- | --- | --- |
| | | |
