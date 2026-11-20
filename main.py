#!/usr/bin/env python3
"""Entry point: copy the pre-rendered front page to the grader output.

The image (entry.png) is generated offline by render.py (Pillow +
DejaVu fonts, no network) and shipped in this repository. This program
uses only the Python standard library, writes exactly one file, and is
byte-deterministic: two runs produce identical output.
"""

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(HERE / "entry.png", OUT_DIR / "entry.png")


if __name__ == "__main__":
    main()
