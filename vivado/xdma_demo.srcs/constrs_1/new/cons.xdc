# PCI Express reference clock 100MHz
set_property PACKAGE_PIN AE12    [get_ports reset_n]
set_property IOSTANDARD LVCMOS18 [get_ports reset_n]

# PCI Express reference clock 100MHz
create_clock -add  -name clk_100_clk_p[0] -period 10 [get_ports clk_100_clk_p[0]]
set_property PACKAGE_PIN Y6  [get_ports {clk_100_clk_p[0]}]
set_property PACKAGE_PIN Y5  [get_ports {clk_100_clk_n[0]}]

# MGT locations
set_property PACKAGE_PIN U3  [get_ports {pcie_io_txn[0]}]
set_property PACKAGE_PIN U4  [get_ports {pcie_io_txp[0]}]

set_property PACKAGE_PIN W3  [get_ports {pcie_io_txn[1]}]
set_property PACKAGE_PIN W4  [get_ports {pcie_io_txp[1]}]

set_property PACKAGE_PIN Y2  [get_ports {pcie_io_rxp[0]}]
set_property PACKAGE_PIN Y1  [get_ports {pcie_io_rxn[0]}]

set_property PACKAGE_PIN V2  [get_ports {pcie_io_rxp[1]}]
set_property PACKAGE_PIN V1  [get_ports {pcie_io_rxn[1]}]