#!/usr/bin/env python3
"""elf2mem.py -- turn a linked RV32 ELF into $readmemh memory images.

Writes three files next to the ELF (one 32-bit little-endian word per line).
The sizes come from the IMEM and DMEM LENGTH lines in sw/common/link.ld (D4),
so the images always match your memories. With the full 16 KB + 16 KB:
  imem.mem  4096 words, 0x0000_0000 - 0x0000_3FFF  (Harvard: instruction memory)
  dmem.mem  4096 words, 0x0000_4000 - 0x0000_7FFF  (Harvard: data memory)
  mem.mem   8192 words, 0x0000_0000 - 0x0000_7FFF  (von Neumann: one memory)
Data memory always starts at 0x0000_4000 (locked memory map).

Pure Python, no packages needed. Usage: python elf2mem.py prog.elf
"""

import struct
import sys
from pathlib import Path

import re

LINK_LD = Path(__file__).resolve().parent / "common" / "link.ld"


def memory_sizes(link_ld=LINK_LD):
    """Return (imem_bytes, dmem_bytes) from the LENGTH lines in link.ld."""
    text = link_ld.read_text()
    sizes = {}
    for name in ("IMEM", "DMEM"):
        m = re.search(name + r"\b[^\n]*LENGTH\s*=\s*(0x[0-9a-fA-F]+|\d+)\s*([KkMm]?)", text)
        if not m:
            sys.exit(f"Can't find the {name} LENGTH line in {link_ld}.")
        value = int(m.group(1), 0) * {"": 1, "K": 1024, "M": 1024 * 1024}[m.group(2).upper()]
        if value > 0x4000:
            sys.exit(f"{name} LENGTH in {link_ld} is more than the 16 KB the memory map allows.")
        sizes[name] = value
    return sizes["IMEM"], sizes["DMEM"]


IMEM_BASE, DMEM_BASE = 0x0000, 0x4000
IMEM_SIZE, DMEM_SIZE = memory_sizes()
SHF_ALLOC, SHT_PROGBITS = 0x2, 1


def load_sections(elf):
    """Yield (address, bytes, name) for every allocated section with contents."""
    if elf[:4] != b"\x7fELF" or elf[4] != 1 or elf[5] != 1:
        sys.exit("Not a 32-bit little-endian ELF file.")
    e_shoff, = struct.unpack_from("<I", elf, 0x20)
    e_shentsize, e_shnum, e_shstrndx = struct.unpack_from("<HHH", elf, 0x2E)
    sections = [struct.unpack_from("<IIIIIIIIII", elf, e_shoff + i * e_shentsize)
                for i in range(e_shnum)]
    strtab_off = sections[e_shstrndx][4]
    for name_off, sh_type, flags, addr, offset, size, *_ in sections:
        if sh_type == SHT_PROGBITS and flags & SHF_ALLOC and size:
            end = elf.index(b"\0", strtab_off + name_off)
            name = elf[strtab_off + name_off:end].decode()
            yield addr, elf[offset:offset + size], name


def write_words(path, image):
    with open(path, "w") as fh:
        for i in range(0, len(image), 4):
            fh.write("%08x\n" % struct.unpack_from("<I", image, i))


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    elf_path = Path(sys.argv[1])
    image = bytearray(DMEM_BASE + DMEM_SIZE)
    for addr, data, name in load_sections(elf_path.read_bytes()):
        end = addr + len(data)
        if addr < DMEM_BASE < end:
            sys.exit(f"Section {name} crosses from instruction into data memory.")
        if addr < DMEM_BASE and end > IMEM_BASE + IMEM_SIZE:
            sys.exit(f"Section {name} doesn't fit the {IMEM_SIZE // 1024} KB instruction memory.")
        if addr >= DMEM_BASE and end > DMEM_BASE + DMEM_SIZE:
            sys.exit(f"Section {name} doesn't fit the {DMEM_SIZE // 1024} KB data memory.")
        image[addr:end] = data
    out = elf_path.parent
    write_words(out / "imem.mem", image[:IMEM_SIZE])
    write_words(out / "dmem.mem", image[DMEM_BASE:])
    write_words(out / "mem.mem", image)


if __name__ == "__main__":
    main()
