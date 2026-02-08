# SISC-F 32-bit CPU
# Copyright (c) 2026 Francesco Angeloni
#
# This source describes Open Hardware and is licensed under the CERN-OHL-W v2.
# You may redistribute and modify this source and make products using it
# under the terms of the CERN-OHL-W v2 (https://cern.ch/cern-ohl).
#
# SPDX-License-Identifier: CERN-OHL-W-2.0

from migen import *
from litex.soc.cores.cpu import CPU
from litex.soc.interconnect import wishbone

class SISCF_core(CPU):
    variants             = {"standard"}
    name                 = "siscf"
    family               = "siscf"

    data_width           = 32
    endianness           = "little"

    gcc_triple           = "none" # Dummy for now
    linker_output_format = "none"
    nop                  = 0x00000001
    gcc_flags            = ""

    reset_address        = 0x00000000

    io_regions = {0xFFFF0000:0x40000}

    mem_map = {
        "sram": 0x0000,
        "csr":  0xFFFF0000,
    }

    def __init__(self, platform, variant="standard"):
        self.platform = platform
        self.reset    = Signal()

        self.bus = wishbone.Interface(data_width=32, adr_width=32)

        self.periph_buses = [self.bus]
        self.memory_buses = [self.bus]
        self.interrupt = Signal(32)

        self.idbus = self.bus

    def elaborate(self, platform):
        m = Module()
        # Instantiate the Verilog module. 
        # Match these names to the 'bus__adr', 'bus__ack' etc. in your .v file
        siscf_instance = Instance("siscf_core_top",
            i_clk        = ClockSignal(),
            i_rst        = ResetSignal() | self.reset,
            
            # Map the pins to the LiteX Wishbone bus
            o_bus__adr   = self.bus.adr,
            o_bus__dat_w = self.bus.dat_w,
            i_bus__dat_r = self.bus.dat_r,
            o_bus__we    = self.bus.we,
            o_bus__sel   = self.bus.sel,
            o_bus__cyc   = self.bus.cyc,
            o_bus__stb   = self.bus.stb,
            i_bus__ack   = self.bus.ack,
        )
        
        m.specials += siscf_instance

        return m