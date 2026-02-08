# SISC-F 32-bit CPU
# Copyright (c) 2026 Francesco Angeloni
#
# This source describes Open Hardware and is licensed under the CERN-OHL-W v2.
# You may redistribute and modify this source and make products using it 
# under the terms of the CERN-OHL-W v2 (https://cern.ch/cern-ohl).
#
# SPDX-License-Identifier: CERN-OHL-W-2.0

from amaranth import *
from amaranth.lib import wiring
from amaranth_soc import wishbone

class SISCFWishboneWrapper(wiring.Component):
    def __init__(self, core):
        self.core = core
        
        bus_signature = wishbone.Signature(addr_width=32, data_width=32, granularity=32)
        
        super().__init__({"bus": wiring.Out(bus_signature)})

    def elaborate(self, platform):
        m = Module()
        m.submodules.core = core = self.core

        m.d.comb += [
            self.bus.adr.eq(core.addr),
            self.bus.dat_w.eq(core.data_out),
            core.data_in.eq(self.bus.dat_r),
            self.bus.we.eq(~core.RW),
            
            self.bus.sel.eq(1), 
            
            self.bus.cyc.eq(1),
            self.bus.stb.eq(~core.internal_op)
        ]

        m.d.comb += core.stall.eq(self.bus.stb & ~self.bus.ack)

        return m