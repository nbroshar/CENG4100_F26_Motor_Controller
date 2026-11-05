#!/usr/bin/env python3
"""sim.py -- run unit testbenches, riscv-tests and C programs in simulation.

Uses Vivado's simulator (xvlog/xelab/xsim) when it is on the PATH, otherwise
Verilator, otherwise Icarus Verilog. Force one with --sim xsim, --sim verilator
or --sim iverilog. Verilator compiles slowly but runs long programs about 100x
faster than Icarus; use it for the case-study programs (on Windows, via WSL).

Examples (from the repo root):
  python scripts/sim.py --tb tb_alu                   # tb/tb_alu.v, unit test
  python scripts/sim.py --tests                       # every test in tests/build
  python scripts/sim.py --tests add lw beq            # just these
  python scripts/sim.py --program sw/build/hello      # a C program
  python scripts/sim.py --program sw/build/demo --uart-in sw/demo/input.txt
  add --vcd to any run to write build/sim/wave.vcd for a waveform viewer

Results of --tests are also written to reports/tests.txt.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "build" / "sim"
MEM_FILES = ("imem.mem", "dmem.mem", "mem.mem")


def rtl_sources():
    """All .v and .sv files under rtl/, in a stable order."""
    files = sorted(p for p in (ROOT / "rtl").rglob("*") if p.suffix in (".v", ".sv"))
    if not files:
        sys.exit("No RTL found under rtl/.")
    return files


def run(cmd, cwd):
    """Run a command; return (exit code, combined output)."""
    proc = subprocess.run(
        [str(c) for c in cmd], cwd=cwd, capture_output=True, text=True,
        shell=(os.name == "nt"),   # Vivado tools are .bat files on Windows
    )
    return proc.returncode, proc.stdout + proc.stderr


def pick_simulator(choice):
    if choice == "auto":
        choice = next((sim for sim, tool in (("xsim", "xvlog"), ("verilator", "verilator"),
                                              ("iverilog", "iverilog")) if shutil.which(tool)),
                      "iverilog")
    needed = {"xsim": "xvlog", "verilator": "verilator", "iverilog": "iverilog"}[choice]
    if not shutil.which(needed):
        sys.exit(f"{needed} not found on PATH. Install it or pick --sim.")
    return choice


def compile_design(sim, top, sources, vcd):
    """Compile once into WORK. Returns the command that runs the simulation."""
    WORK.mkdir(parents=True, exist_ok=True)
    if sim == "iverilog":
        cmd = ["iverilog", "-g2012", "-s", top, "-o", "simv"]
        if vcd:
            cmd.append("-DDUMP")
        code, out = run(cmd + sources, WORK)
        if code:
            sys.exit(f"Compile failed:\n{out}")
        return ["vvp", "-n", "simv"]
    if sim == "verilator":
        cmd = ["verilator", "--binary", "--timing", "-O2", "-Wno-fatal", "-Wno-lint",
               "-Wno-style", "--top-module", top, "-Mdir", "obj_dir", "-o", "simv"]
        if vcd:
            cmd += ["-DDUMP", "--trace"]
        code, out = run(cmd + sources, WORK)
        if code:
            sys.exit(f"Verilator build failed:\n{out}")
        return [WORK / "obj_dir" / "simv"]
    # Vivado xsim
    v = [s for s in sources if s.suffix == ".v"]
    sv = [s for s in sources if s.suffix == ".sv"]
    define = ["-d", "DUMP"] if vcd else []
    for group, flags in ((v, []), (sv, ["-sv"])):
        if group:
            code, out = run(["xvlog"] + flags + define + group, WORK)
            if code:
                sys.exit(f"xvlog failed:\n{out}")
    code, out = run(["xelab", "-debug", "typical", top, "-s", f"{top}_snap"], WORK)
    if code:
        sys.exit(f"xelab failed:\n{out}")
    return ["xsim", f"{top}_snap", "-R"]


def plusarg(sim, name, value):
    """A +name=value plusarg in the form each simulator expects."""
    if sim in ("iverilog", "verilator"):
        return [f"+{name}={value}"]
    return ["-testplusarg", f"{name}={value}"]


def stage_program(prog_dir, uart_in=None):
    """Copy a program's memory images (and typed input) into WORK."""
    for name in MEM_FILES + ("uart_in.txt",):
        (WORK / name).unlink(missing_ok=True)
    found = False
    for name in MEM_FILES:
        src = Path(prog_dir) / name
        if src.exists():
            shutil.copy(src, WORK / name)
            found = True
    if not found:
        sys.exit(f"No memory images in {prog_dir}. Build the program first.")
    if uart_in:
        shutil.copy(uart_in, WORK / "uart_in.txt")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--tb", help="run unit testbench tb/<TB>.v (module name = file name)")
    mode.add_argument("--tests", nargs="*", help="run riscv-tests from tests/build (all if no names)")
    mode.add_argument("--program", help="run a program folder containing .mem images")
    ap.add_argument("--uart-in", help="file whose bytes are typed into RsRx (with --program)")
    ap.add_argument("--sim", choices=("auto", "xsim", "verilator", "iverilog"), default="auto")
    ap.add_argument("--max-cycles", type=int, default=None)
    ap.add_argument("--vcd", action="store_true", help="dump build/sim/wave.vcd")
    args = ap.parse_args()

    sim = pick_simulator(args.sim)

    if args.tb:
        tb = ROOT / "tb" / f"{args.tb}.v"
        if not tb.exists():
            sys.exit(f"{tb} not found")
        runner = compile_design(sim, args.tb, rtl_sources() + [tb], args.vcd)
        code, out = run(runner, WORK)
        print(out)
        ok = "ALL TESTS PASSED" in out
        print("RESULT:", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)

    tb = ROOT / "tb" / "tb_top.v"
    runner = compile_design(sim, "tb_top", rtl_sources() + [tb], args.vcd)

    if args.program:
        stage_program(args.program, args.uart_in)
        cycles = args.max_cycles or 20_000_000
        code, out = run(runner + plusarg(sim, "max_cycles", cycles), WORK)
        print(out)
        ok = "TOHOST: PASS" in out
        print("RESULT:", "PASS" if ok else "FAIL (see output above)")
        sys.exit(0 if ok else 1)

    # riscv-tests
    build = ROOT / "tests" / "build"
    if args.tests:
        names = args.tests
    elif build.exists():
        names = sorted(p.name for p in build.iterdir() if p.is_dir())
    else:
        names = []
    if not names:
        sys.exit("No tests found. Run: python tests/build_tests.py")
    cycles = args.max_cycles or 100_000
    results = []
    for name in names:
        stage_program(build / name)
        code, out = run(runner + plusarg(sim, "max_cycles", cycles), WORK)
        if "TOHOST: PASS" in out:
            status = "PASS"
        elif "TOHOST: FAIL" in out:
            line = next(l for l in out.splitlines() if "TOHOST: FAIL" in l)
            status = "FAIL" + line.split("FAIL", 1)[1]
        elif "TIMEOUT" in out:
            status = "TIMEOUT"
        else:
            status = "ERROR (no tohost write; check the simulator output)"
        results.append((name, status))
        print(f"{name:10s} {status}")
    passed = sum(1 for _, s in results if s == "PASS")
    summary = f"{passed}/{len(results)} riscv-tests passed ({sim})"
    print(summary)
    (ROOT / "reports").mkdir(exist_ok=True)
    with open(ROOT / "reports" / "tests.txt", "w") as fh:
        fh.write(summary + "\n")
        for name, status in results:
            fh.write(f"{name:10s} {status}\n")
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
