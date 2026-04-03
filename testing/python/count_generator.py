#!/usr/bin/env python3
"""Generate counting pattern binary vectors.

Usage:
    python3 count_generator.py <output_file> [sample_count] [start_value] [step]

Example:
    python3 count_generator.py input.bin 256 0 1
"""

import struct
import sys
from pathlib import Path


def generate_counting_binary(output_path: Path, sample_count: int, start: int, step: int) -> None:
    """Write counting sequence as little-endian 32-bit words."""
    words = []
    current = start
    for _ in range(sample_count):
        words.append(current & 0xFFFF)
        current += step
    
    data = b"".join(struct.pack("<I", w) for w in words)
    output_path.write_bytes(data)
    print(f"Generated {sample_count} samples: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    output_file = Path(sys.argv[1])
    sample_count = int(sys.argv[2]) if len(sys.argv) > 2 else 256
    start = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    step = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    
    generate_counting_binary(output_file, sample_count, start, step)
