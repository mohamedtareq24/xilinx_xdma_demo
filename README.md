# xilinx_xdma_demo

## What Has Been Built So Far

![alt text](docs/bd.png)
This repository contains an FPGA demo setup that integrates:

- A custom AES streaming hardware block in the Vivado design.
- Xilinx XDMA IP in the same system for PCIe-based host communication.
- Vivado project and block design recreation scripts under `vivado/`.
- Driver references and test support files under `testing/XDMA_drivers/`.

The current implementation is focused on wiring and integration so the host can exchange data with FPGA logic through XDMA.

## AES Hardware Validation Plan

Testing will confirm the AES hardware functionality by communicating with the FPGA from the host using the Xilinx XDMA driver path. The validation flow is to send test vectors from the host, process them in AES hardware, and read results back through XDMA for comparison.

## RTL Source

The AES RTL used here is based on the AXIS AES core from: https://github.com/2122aaor/AXIS-AES

The RTL files are mirrored into this demo source tree for integration and build reproducibility.

This repository provides a practical guide for communicating with FPGA hardware through the Xilinx XDMA IP while integrating a custom AES hardware module as a place holder.
