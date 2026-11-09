# CENG 4100 RV32I Capstone: Case 1, Motor Controller

Our team builds an RV32I RISC-V processor on a Digilent Basys 3 and runs our
client's motor controller program on it. This repo holds what the course gives
us: the locked top level, the scripts that build and test everything, the
memory map, and the client's firmware. Everything we design goes in `rtl/`,
`tb/` and `docs/interfaces.md`.

Our decisions go in our Team Decision Record, submitted in Canvas.

## What's here

| Path | What it is | Ours to change? |
| --- | --- | --- |
| `rtl/top.v` | The board wrapper. Its module name and ports match the board pins and `tb/tb_top.v` | Inside only, from Lab 2. Never the ports |
| `rtl/tohost.v` | Reports PASS or FAIL when a program stores to 0x1000_F000 | No |
| `rtl/` (everything else) | Our CPU, one module per file | Yes |
| `tb/tb_template.v` | The pattern every unit testbench follows | No (copy it) |
| `tb/tb_top.v` | Runs a whole program on `top`: clock, reset, UART, timeout | No |
| `tb/test_plan_lab1.md` | The Lab 1 test plan form | Yes (Verification fills it in) |
| `docs/interfaces.md` | Our modules' ports and codes: the contract between Core and Verification | Yes, when the whole team agrees |
| `docs/memory_map.md` | Where memory and every peripheral register live | No |
| `docs/briefs/` | Our client's brief | No |
| `constraints/basys3.xdc` | Basys 3 pin assignments for `top`'s ports | No |
| `scripts/sim.py` | Runs testbenches, riscv-tests and C programs in simulation | No |
| `scripts/schematic.tcl` | Draws one module's schematic in Vivado and saves a PDF | No |
| `scripts/build.tcl`, `scripts/program.tcl` | Vivado bitstream build with reports; programs the board | No |
| `sw/build.py`, `sw/elf2mem.py` | Compile a C program into `imem.mem` and `dmem.mem` | No |
| `sw/common/` | Startup code, `link.ld` (memory sizes), UART and printf | `link.ld` only, for D4 Memory sizes |
| `sw/hello/`, `sw/demo/` | Test programs: a greeting, and an interactive demo | No |
| `sw/case1_motor/` | Our client's program: acceptance harness (`main.c`), firmware to improve (`firmware.c`), golden data, time target | `firmware.c` only (Software & integration improves it) |
| `tests/` | Builds the official riscv-tests for our core | No |
| `RESOURCES.md` | Our resource and performance ledger | Yes, after every build |
| `reports/` | Test and build results (`tests.txt` is our gate evidence) | Written by the scripts |

## Commands

Run every command from the repo folder, in PowerShell or Command Prompt.

```
python scripts/sim.py --tb tb_template          # the simulator works
python sw/build.py hello                         # the RISC-V compiler works
python scripts/sim.py --tb tb_alu                # one unit testbench
python tests/build_tests.py                      # build the riscv-tests (from Lab 2)
python scripts/sim.py --tests                    # run all 40 riscv-tests
python sw/build.py case1_motor                   # build our client's program
python scripts/sim.py --program sw/build/hello   # run a C program in simulation
```

Add `--vcd` to any `sim.py` run to save a waveform in `build/sim/wave.vcd`.

## Tools

- Vivado (the version used in class).
- Python 3.9 or newer (no extra packages).
- The RISC-V compiler: the xPack build of `riscv-none-elf-gcc`
  (github.com/xpack-dev-tools/riscv-none-elf-gcc-xpack/releases, the
  `win32-x64.zip`). Unzip it and add its `bin` folder to the PATH.
- A simulator for `sim.py`: Vivado's (xsim) if its `bin` folder is on the
  PATH, otherwise Icarus Verilog or Verilator.
- GitHub Desktop, and the Copilot chat app.

## Rules

- Never keep backup copies in `rtl/` or `tb/`. `sim.py` compiles every `.v`
  file in `rtl/`, so a copy breaks the build. GitHub Desktop is our undo.
- Commit after every file and every fix.
- Generated files (`build/`, `sw/build/`, `tests/build/`) are not committed;
  `.gitignore` keeps them out.
