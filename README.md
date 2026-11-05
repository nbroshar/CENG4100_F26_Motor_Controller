# CENG 4100 RV32I Capstone: team starter repo

Each team builds an RV32I RISC-V processor on a Digilent Basys 3, runs C
programs on it, and designs a carrier board. The lab workbook explains the
weekly cycle; this repo holds the locked interfaces, scripts and software kit.

## What's here

| Path | What it is |
| --- | --- |
| `.github/copilot-instructions.md` | Rules GitHub Copilot follows in this repo (decision-first, roles, two-attempt stop) |
| `DECISIONS.md` | The 14 decisions: week, implementing role, RISC-V spec sections, textbook readings (your decisions themselves go in your Team Decision Record, in Canvas) |
| `RESOURCES.md` | Resource and performance ledger |
| `docs/memory_map.md` | Locked memory map, peripheral registers, memory image format |
| `docs/interfaces.md` | Your team's agreed module ports and ALU codes: the contract between Core and Verification |
| `rtl/top.v` | Locked top-level ports (empty design to start) |
| `rtl/tohost.v` | Pass/fail reporter at 0x1000_F000 (do not modify) |
| `constraints/basys3.xdc` | Basys 3 pins for the locked ports |
| `tb/tb_top.v` | System testbench: clock, reset, UART monitor, typed input |
| `tb/tb_template.v` | Pattern for self-checking unit testbenches |
| `tb/test_plan_lab1.md` | Lab 1 test plan for the ALU and register file (Verification fills it in) |
| `scripts/sim.py` | Simulation runner (Vivado xsim, Verilator or Icarus Verilog) |
| `scripts/build.tcl`, `scripts/program.tcl` | Vivado bitstream build with reports; board programming |
| `scripts/schematic.tcl` | Draws the schematic of one module in Vivado and saves it as a PDF |
| `sw/` | `build.py`, startup code, linker script, UART/printf, `hello` and `demo` |
| `docs/briefs/` | The four client briefs |
| `sw/case1_motor`, `sw/case2_sensor`, `sw/case3_audio`, `sw/case4_sonar` | Client case studies (each team works only in its own case's folder): acceptance harness (`main.c`), client firmware to improve (`firmware.c`), golden data (`data.h`, `gen_data.py`), time target (`target.h`) |
| `tests/` | CSR-free environment and builder for the official riscv-tests (rv32ui, plus rv32um for multiply) |

## Quick start (students)

```
python scripts/sim.py --tb tb_template           # simulator works
python sw/build.py hello                          # RISC-V gcc works
vivado -mode batch -source scripts/build.tcl     # Vivado works (empty design)
```

Once the core exists:

```
python tests/build_tests.py                       # once: download and build riscv-tests
python scripts/sim.py --tests                     # all 40 rv32ui tests -> reports/tests.txt
python scripts/sim.py --program sw/build/hello    # run C in simulation, UART on the console
python scripts/sim.py --program sw/build/demo --uart-in sw/demo/input.txt
vivado -mode batch -source scripts/build.tcl -tclargs sw/build/demo
vivado -mode batch -source scripts/program.tcl
```

Your client's acceptance program (example: Case 3, core running at 50 MHz with
multiply-only hardware):

```
python sw/build.py case3_audio --march rv32i_zmmul -D CPU_HZ=50000000
python scripts/sim.py --program sw/build/case3_audio --sim verilator
```

Serial terminal (PuTTY, Tera Term): the Basys 3's COM port, 115200 baud, 8N1,
no flow control. Long programs (`demo` with typed input, the case programs)
run millions of cycles: seconds in Verilator, minutes in xsim or Icarus.

## Tools to install on lab machines

- Vivado (the version used in class), with `vivado`, `xvlog`, `xelab` and `xsim`
  on the PATH. On Windows, run `settings64.bat` from the Vivado folder, or add
  its `bin` folder to the PATH.
- RISC-V GCC: the xPack build `riscv-none-elf-gcc`
  (github.com/xpack-dev-tools/riscv-none-elf-gcc-xpack/releases); unzip and add
  its `bin` folder to the PATH. `riscv64-unknown-elf-gcc` also works.
- Python 3.9 or newer (no extra packages needed).
- Git, VS Code, and the GitHub Copilot extension, signed in with an account
  that can select Claude Opus 5.5.
- Recommended: Verilator 5 for fast simulation of long programs (Linux, macOS,
  or WSL on Windows). Optional: Icarus Verilog.

## Instructor setup (no GitHub Classroom needed)

1. Push this folder to a new GitHub repository, then in its **Settings** tick
   **Template repository**.
2. For each team, on the template's page choose **Use this template → Create a
   new repository**: private, named for example `ceng4100-team-a`.
3. In each team repo, **Settings → Collaborators**: add the team's four
   students with the Write role. Add yourself if the repo is not under your
   account.
4. Optional but recommended: **Settings → Branches**, protect `main` so every
   merge needs a pull request approved by one teammate.
5. Before week 1, run the quick start on one lab machine with each team's repo.

## What the kit has been checked against

- On an instructor-only reference core, in Icarus Verilog and Verilator: all
  40 rv32ui riscv-tests (and the 4 rv32um multiply tests on its multiply
  variant) pass; `hello` and `demo` (with typed input) run correctly; the PWM
  peripheral produces the programmed duty cycle.
- Every case acceptance program was run with the client firmware and with
  several solution designs: the client firmware fails each case, and at least
  two different designs pass each one.
- The Vivado scripts (`build.tcl`, `program.tcl`) and the xsim path of
  `sim.py` follow standard Vivado batch commands but should be run once on a
  lab machine before week 1.
