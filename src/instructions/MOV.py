# SISC-F 32-bit CPU
# Copyright (c) 2026 Francesco Angeloni
#
# This source describes Open Hardware and is licensed under the CERN-OHL-W v2.
# You may redistribute and modify this source and make products using it
# under the terms of the CERN-OHL-W v2 (https://cern.ch/cern-ohl).
#
# SPDX-License-Identifier: CERN-OHL-W-2.0

from include.instruction import *
from include.enums import *
from amaranth import Module, Signal, Const, signed

_length = 0x6

def _exec(m: Module, core):
    reg_address = {
        0xFFFFFF00: core.ra,
        0xFFFFFF01: core.rb,
        0xFFFFFF02: core.rx,
    }
    with m.Switch(core.instr_state):
        with m.Case(2):
            with m.Switch(core.data_in):
                for key, val in reg_address.items():
                    with m.Case(Const(key, signed(32))):
                        m.d.sync += [
                            core.tmp32.eq(val),
                            core.tmp32_2.eq(0),
                            core.instr_state.eq(3)
                        ]
                with m.Default():
                    m.d.sync += [
                        core.addr.eq(core.data_in),
                        core.tmp32_2.eq(1),
                        core.instr_state.eq(3)
                    ]

        with m.Case(3):
            with m.If(core.tmp32_2):
                m.d.sync += [
                    core.tmp32.eq(core.data_in),
                    core.tmp32_2.eq(0)
                ]
            core.advance_ip_goto_state(m, 4)

        with m.Case(4):
            with m.Switch(core.data_in):
                for key, val in reg_address.items():
                    with m.Case(Const(key, signed(32))):
                        m.d.sync += [
                            val.eq(core.tmp32),
                            core.tmp32_2.eq(0),
                            core.instr_state.eq(5)
                        ]
                with m.Default():
                    m.d.sync += [
                        core.addr.eq(core.data_in),
                        core.tmp32_2.eq(1),
                        core.instr_state.eq(5)
                    ]
        
        with m.Case(5):
            with m.If(core.tmp32_2):
                m.d.sync += [
                    core.data_out.eq(core.tmp32),
                    core.tmp32_2.eq(0),
                    core.RW.eq(0)
                ]
            m.d.sync += core.instr_state.eq(6)
        
        with m.Case(6):
            m.d.sync += [
                core.tmp32.eq(0),
                core.RW.eq(1),
                core.data_out.eq(0)
            ]
            core.end_instr(m, core.ip + 1)
            
        with m.Default():
            core.advance_ip_goto_state(m, 2)


Instruction(0x02, "MOV", _exec, 0x3)