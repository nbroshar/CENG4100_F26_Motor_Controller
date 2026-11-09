# Module interfaces

This file is the contract between Core and Verification. Core builds each
module to match it. Verification writes each testbench from it, without
opening Core's Verilog. Change it only when the whole team agrees, and tell
both roles when you do.

Fill it in from the plan Copilot gives you (Lab 1, Step 5, Prompt 1), after
the team has reviewed and corrected that plan.

## Register file (`rtl/regfile.v`, module `regfile`)

Decision: D5 Register file.

| Port | Direction | Width | What it does |
| --- | --- | --- | --- |
| | | | |

Timing: when is a write stored, and when does a read see it? (Answer from D5.)

## ALU (`rtl/alu.v`, module `alu`)

Decision: D6 ALU, shifter and immediates.

| Port | Direction | Width | What it does |
| --- | --- | --- | --- |
| | | | |

### ALU operation codes

| Code (binary) | Operation | RV32I instructions that use it |
| --- | --- | --- |
| | add | add, addi (and address and link calculations, if our D6 says so) |
| | sub | sub |
| | sll | sll, slli |
| | slt | slt, slti |
| | sltu | sltu, sltiu |
| | xor | xor, xori |
| | srl | srl, srli |
| | sra | sra, srai |
| | or | or, ori |
| | and | and, andi |

## Datapath (`rtl/datapath.v`, module `datapath`)

Decision: D1 Microarchitecture (how the parts connect).

| Port | Direction | Width | What it does |
| --- | --- | --- | --- |
| | | | |

## Change log

| Date | What changed | Agreed by |
| --- | --- | --- |
| | | |
