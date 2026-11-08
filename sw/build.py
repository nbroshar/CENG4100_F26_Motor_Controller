#!/usr/bin/env python3
"""build.py -- compile a C program in sw/<name>/ for the RV32I core.

Usage (from the repo root):
  python sw/build.py hello                 # builds sw/hello/*.c
  python sw/build.py demo
  python sw/build.py demo --march rv32im        # after D10, if you built full M
  python sw/build.py demo --march rv32i_zmmul   # after D10, multiply-only (Zmmul)

Output in sw/build/<name>/:
  <name>.elf   linked program        <name>.dis   disassembly (read this!)
  imem.mem / dmem.mem / mem.mem      memory images for $readmemh

The cross compiler is found automatically (riscv-none-elf-gcc from xPack, or
riscv64-unknown-elf-gcc); override with --cross <prefix>.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

SW = Path(__file__).resolve().parent
COMMON = SW / "common"
PREFIXES = ("riscv-none-elf-", "riscv64-unknown-elf-", "riscv32-unknown-elf-")


def find_prefix(requested):
    for prefix in ([requested] if requested else PREFIXES):
        if shutil.which(prefix + "gcc"):
            return prefix
    sys.exit("No RISC-V gcc found on PATH (tried: %s)." % ", ".join(PREFIXES))


def run(cmd, **kw):
    result = subprocess.run([str(c) for c in cmd], text=True, capture_output=True, **kw)
    if result.returncode:
        sys.exit(result.stdout + result.stderr)
    return result.stdout


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("prog", help="folder under sw/ holding the program's .c files")
    ap.add_argument("--march", default="rv32i", help="rv32i (default) or rv32im")
    ap.add_argument("--cross", help="toolchain prefix, e.g. riscv-none-elf-")
    ap.add_argument("-O", dest="opt", default="s", help="optimization level (default s)")
    ap.add_argument("-D", dest="define", action="append", default=[],
                    help="extra C define, e.g. -D CPU_HZ=50000000 (repeatable)")
    args = ap.parse_args()

    src_dir = SW / args.prog
    sources = sorted(src_dir.glob("*.c")) + sorted(src_dir.glob("*.S"))
    if not sources:
        sys.exit(f"No .c or .S files in {src_dir}")
    out = SW / "build" / args.prog
    out.mkdir(parents=True, exist_ok=True)
    elf = out / f"{args.prog}.elf"
    prefix = find_prefix(args.cross)

    cflags = [
        f"-march={args.march}", "-mabi=ilp32", f"-O{args.opt}", "-g", "-Wall",
        "-ffreestanding", "-fno-builtin", "-fno-tree-loop-distribute-patterns",
        "-ffunction-sections", "-fdata-sections",
        "-nostdlib", "-nostartfiles", f"-I{COMMON}",
        f"-T{COMMON / 'link.ld'}", "-Wl,--gc-sections", f"-Wl,-Map={out / (args.prog + '.map')}",
    ]
    common = [COMMON / "crt0.S"] + sorted(COMMON.glob("*.c"))
    # -lgcc supplies gcc's arithmetic helpers: without multiply hardware, every
    # * / % becomes a call to __mulsi3, __divsi3 and friends (read them in the
    # .dis file). Do not replace them with your own versions: libgcc's 64-bit
    # routines call the 32-bit ones assuming exactly which registers they use.
    extra = [f"-D{d}" for d in args.define]
    run([prefix + "gcc"] + cflags + extra + common + sources + ["-lgcc", "-o", elf])

    (out / f"{args.prog}.dis").write_text(run([prefix + "objdump", "-d", "-M", "no-aliases", elf]))
    run([sys.executable, SW / "elf2mem.py", elf])

    # Size check against the memory sizes in link.ld (D4).
    sys.path.insert(0, str(SW))
    from elf2mem import memory_sizes
    imem_size, dmem_size = memory_sizes(COMMON / "link.ld")
    sizes = run([prefix + "size", "-A", elf])
    text = data = 0
    for line in sizes.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[2].isdigit():
            addr = int(parts[2])
            if parts[0].startswith((".text",)):
                text += int(parts[1])
            elif addr >= 0x4000 and parts[0].startswith((".rodata", ".data", ".bss", ".sdata", ".sbss")):
                data += int(parts[1])
    print(f"{args.prog}: code {text} bytes of {imem_size}, data {data} bytes of {dmem_size} "
          f"(the stack uses the rest of data memory)")
    print(f"Images: {out}/imem.mem ({imem_size // 4} words), dmem.mem ({dmem_size // 4} words), mem.mem")
    if text > imem_size or data > dmem_size:
        sys.exit("Program does not fit the memory sizes in sw/common/link.ld.")


if __name__ == "__main__":
    main()
