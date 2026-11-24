#!/usr/bin/env python3
"""Write the front page for 24 November 2026 to the output directory.

The page itself is entry.png beside this file: tools/render.py draws it, and
this program puts it where the gate reads it. Both runs copy the same bytes,
so the entry is deterministic.

It also checks its own output against the gate's limits before finishing, so a
bad build fails here rather than at the gate: a whole PNG of at most 1 MiB and
at most 1024 by 1024 pixels.
"""

import os
import shutil
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

MAX_BYTES = 1048576
MAX_SIDE = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def png_size(path):
    """Read width and height from the IHDR chunk, or return None."""
    with open(path, "rb") as f:
        head = f.read(33)
    if len(head) < 33 or head[:8] != PNG_MAGIC or head[12:16] != b"IHDR":
        return None
    width, height = struct.unpack(">II", head[16:24])
    return width, height


def check(path):
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise SystemExit("%s is %d bytes, over the %d cap" % (path, size, MAX_BYTES))
    dims = png_size(path)
    if dims is None:
        raise SystemExit("%s is not a whole PNG" % path)
    width, height = dims
    if width > MAX_SIDE or height > MAX_SIDE:
        raise SystemExit("%s is %dx%d, over %d a side" % (path, width, height, MAX_SIDE))
    return size, width, height


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / "entry.png"
    shutil.copyfile(HERE / "entry.png", dest)
    size, width, height = check(dest)
    print("wrote %s: %d bytes, %dx%d" % (dest, size, width, height))


if __name__ == "__main__":
    main()
