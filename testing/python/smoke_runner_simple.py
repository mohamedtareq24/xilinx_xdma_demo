#!/usr/bin/env python3
"""Simple XDMA FIR smoke test runner.

No CLI args. Just reads input_signal.bin, runs DMA loop, writes output.bin.

Usage:
    sudo python3 smoke_runner_simple.py
"""

import struct
import subprocess
import sys
import time
from pathlib import Path


# Hardcoded paths and config
XDMA_H2C_DEV = "/dev/xdma0_h2c_0"
XDMA_C2H_DEV = "/dev/xdma0_c2h_0"
XDMA_USER_DEV = "/dev/xdma0_user"

TESTS_BIN_DIR = Path(__file__).resolve().parent.parent / "XDMA_drivers" / "dma_ip_drivers" / "XDMA" / "linux-kernel" / "tools"
REG_RW = TESTS_BIN_DIR / "reg_rw"
DMA_TO = TESTS_BIN_DIR / "dma_to_device"
DMA_FROM = TESTS_BIN_DIR / "dma_from_device"

# Fixed FIR taps (5-tap pass-through)
TAPS = [1, 0, 0, 0, 0]
BASE_ADDR = 0xA0000000
BAR_RELATIVE = True

# Input/output files in current directory
INPUT_FILE = Path("input_signal.bin")
OUTPUT_FILE = Path("output_signal.bin")

# DMA parameters
TRANSFER_ADDR = 0x0
C2H_READY_DELAY = 1.0
DMA_TIMEOUT = 30.0


def get_register_address(word_index: int) -> int:
    if BAR_RELATIVE:
        return word_index * 4
    return BASE_ADDR + (word_index * 4)


def run_cmd(cmd: list) -> None:
    print("$", " ".join(str(x) for x in cmd))
    result = subprocess.run(cmd, check=True, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout)


def main() -> int:
    print("=== XDMA FIR Smoke Test ===\n")
    
    # Validate input file
    if not INPUT_FILE.exists():
        print(f"ERROR: Input file not found: {INPUT_FILE}")
        return 1
    
    transfer_size = INPUT_FILE.stat().st_size
    if transfer_size == 0:
        print(f"ERROR: Input file is empty: {INPUT_FILE}")
        return 1
    if transfer_size % 4 != 0:
        print(f"ERROR: Input file size not a multiple of 4 bytes: {transfer_size}")
        return 1
    
    # Validate tools exist
    for tool in [REG_RW, DMA_TO, DMA_FROM]:
        if not tool.exists():
            print(f"ERROR: Tool not found: {tool}")
            return 1
    
    print(f"Input file: {INPUT_FILE} ({transfer_size} bytes)")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Taps: {TAPS}")
    print()
    
    try:
        # Program 5 taps (register writes to 0x4, 0x8, 0xc, 0x10, 0x14)
        print("Programming FIR taps...")
        for idx, tap in enumerate(TAPS, start=1):
            write_addr = get_register_address(idx)
            write_data = tap & 0xFFFF
            run_cmd([str(REG_RW), XDMA_USER_DEV, hex(write_addr), "w", hex(write_data)])
        
        # Enable filter (control register at 0x0)
        print("\nEnabling filter...")
        ctrl_addr = get_register_address(0)
        run_cmd([str(REG_RW), XDMA_USER_DEV, hex(ctrl_addr), "w", "0x1"])
        
        # Spawn C2H capture thread
        print("\nStarting C2H capture (background)...")
        c2h_cmd = [
            str(DMA_FROM),
            "-d", XDMA_C2H_DEV,
            "-a", hex(TRANSFER_ADDR),
            "-s", str(transfer_size),
            "-c", "1",
            "-f", str(OUTPUT_FILE),
        ]
        print("$", " ".join(c2h_cmd), "&")
        c2h_proc = subprocess.Popen(
            c2h_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        
        # Wait for C2H to be ready
        time.sleep(max(C2H_READY_DELAY, 0.0))
        
        # Send H2C stream
        print("Sending H2C data...")
        h2c_cmd = [
            str(DMA_TO),
            "-d", XDMA_H2C_DEV,
            "-a", hex(TRANSFER_ADDR),
            "-s", str(transfer_size),
            "-c", "1",
            "-f", str(INPUT_FILE),
        ]
        run_cmd(h2c_cmd)
        
        # Wait for C2H completion
        print("Waiting for C2H completion...")
        c2h_stdout, c2h_stderr = c2h_proc.communicate(timeout=max(DMA_TIMEOUT, 1.0))
        if c2h_proc.returncode != 0:
            print(f"ERROR: C2H failed with code {c2h_proc.returncode}")
            if c2h_stderr:
                print("stderr:", c2h_stderr)
            return 1
        
        if c2h_stdout:
            print(c2h_stdout)
        
        # Verify output file was created
        if not OUTPUT_FILE.exists():
            print(f"ERROR: Output file not created: {OUTPUT_FILE}")
            return 1
        
        out_size = OUTPUT_FILE.stat().st_size
        print(f"\n=== Transfer Complete ===")
        print(f"Input:  {transfer_size} bytes")
        print(f"Output: {out_size} bytes")
        print(f"Output file: {OUTPUT_FILE.resolve()}")
        
        return 0
    
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: Command failed: {exc}")
        return 1
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
