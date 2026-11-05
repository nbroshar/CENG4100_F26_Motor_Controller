#!/usr/bin/env python3
"""build_tests.py -- build the official riscv-tests for this core.

Downloads riscv-tests (once) into tests/riscv-tests, then compiles every test
in a suite with the CSR-free environment in tests/env/ and the same linker
script as the C programs. Output: tests/build/<test>/ with .elf, .dis and
memory images. Run them with:  python scripts/sim.py --tests

Suites:
  rv32ui  (default) the base integer instructions; every team must pass these
  rv32um  multiply and divide (D10). A Zmmul core runs only the multiply
          tests:  python tests/build_tests.py --suite rv32um mul mulh mulhsu mulhu

Skipped rv32ui tests:
  fence_i  needs the Zifencei extension (self-modifying code); not in scope
  ma_data  tests misaligned accesses; enable it only if D8 supports them
"""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / "tests"
UPSTREAM = TESTS / "riscv-tests"
REPO = "https://github.com/riscv-software-src/riscv-tests"
SKIP = {"fence_i", "ma_data"}

sys.path.insert(0, str(ROOT / "sw"))
from build import find_prefix, run  # noqa: E402  (same toolchain lookup as sw/)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tests", nargs="*", help="test names (default: the whole suite)")
    ap.add_argument("--suite", choices=("rv32ui", "rv32um"), default="rv32ui")
    ap.add_argument("--include-misaligned", action="store_true", help="also build ma_data (D8)")
    ap.add_argument("--cross", help="toolchain prefix, e.g. riscv-none-elf-")
    args = ap.parse_args()

    if not UPSTREAM.exists():
        print(f"Cloning {REPO} ...")
        run(["git", "clone", "--depth", "1", REPO, UPSTREAM])
    src_dir = UPSTREAM / "isa" / args.suite
    march = "rv32im" if args.suite == "rv32um" else "rv32i"
    skip = SKIP - ({"ma_data"} if args.include_misaligned else set())
    names = args.tests or sorted(p.stem for p in src_dir.glob("*.S") if p.stem not in skip)
    prefix = find_prefix(args.cross)

    for name in names:
        out = TESTS / "build" / name
        out.mkdir(parents=True, exist_ok=True)
        elf = out / f"{name}.elf"
        run([prefix + "gcc", f"-march={march}", "-mabi=ilp32", "-nostdlib", "-nostartfiles",
             f"-I{TESTS / 'env'}", f"-I{UPSTREAM / 'isa' / 'macros' / 'scalar'}",
             f"-T{ROOT / 'sw' / 'common' / 'link.ld'}", src_dir / f"{name}.S", "-o", elf])
        (out / f"{name}.dis").write_text(run([prefix + "objdump", "-d", "-M", "no-aliases", elf]))
        run([sys.executable, ROOT / "sw" / "elf2mem.py", elf])
        print(f"built {name}")
    print(f"{len(names)} tests in {TESTS / 'build'}")


if __name__ == "__main__":
    main()
