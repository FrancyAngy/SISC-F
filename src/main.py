# SISC-F 32-bit CPU
# Copyright (c) 2026 Francesco Angeloni
#
# This source describes Open Hardware and is licensed under the CERN-OHL-W v2.
# You may redistribute and modify this source and make products using it 
# under the terms of the CERN-OHL-W v2 (https://cern.ch/cern-ohl).
#
# SPDX-License-Identifier: CERN-OHL-W-2.0

from enum import IntEnum, auto
import os
from typing import List, Dict, Tuple, Optional
from amaranth import Signal, Const, Module, Memory, signed, Elaboratable
from amaranth.hdl.ast import Statement
from amaranth.build import Platform
from amaranth.cli import main_parser, main_runner
from amaranth.sim import Simulator, SimulatorContext, Settle, Tick
import instructions
from include.enums import *
from include.instruction import instruction_opcodes, instruction_names
from math import pow

class Core(Elaboratable):
    def __init__(self, *, useMemory: bool = False, mem_init: Optional[Dict] = None, useResetVector: bool = True, startAddr: int = 0x0009):
        if useMemory and mem_init == None:
            raise ValueError("Set useMemory flag without initializing memory")

        self.useMemory = useMemory
        self.useResetVector = useResetVector
        self.startAddr = startAddr

        self.addr = Signal(32)
        self.data_in = Signal(signed(32))
        self.data_out = Signal(32)
        self.RW = Signal(reset=1) # Read = 1, Write = 0

        if useMemory and not mem_init == None:
            init = [0xFFFFFFFF] * int(pow(2, 18))

            for addr, val in mem_init.items():
                init[addr] = val

            self.mem = Memory(width=32, depth=int(pow(2, 18)), init=init)

        #Registries
        self.ra = Signal(signed(32), reset_less=True)
        self.rb = Signal(signed(32), reset_less=True)
        self.rx = Signal(signed(32), reset_less=True)
        self.ip = Signal(32, reset_less=True)
        self.ir = Signal(32, reset_less=True)
        if useMemory:
            self.sp = Signal(32, reset=int(pow(2, 18) - 1))
        else:
            self.sp = Signal(32, reset_less=True)
        self.qp = Signal(32, reset_less=True)
        self.flags = Signal(8, reset_less=True)
        self.tmp32 = Signal(32)
        self.tmp32_2 = Signal(32)
        self.tmp32_3 = Signal(32)

        #BUSes
        self.interrupt_args = Signal(32)
        self.interrupt_return = Signal(32)
        self.alu_1 = Signal(signed(32))
        self.alu_2 = Signal(signed(32))
        self.alu_op = Signal(AluOps)
        self.alu_out = Signal(signed(32))
        self.alu_en = Signal()
        self.stack_op = Signal(StackOps)
        self.stack_data = Signal(32)
        self.stack_en = Signal()
        self.internal_op = Signal()
        self.stall = Signal()

        #States
        self.reset_state = Signal(2)
        self.instr_state = Signal(4)
        self.end_instr_flag = Signal()
        self.end_instr_addr = Signal(32)

    def ports(self) -> List[Signal]:
        return [self.ip, self.ir, self.addr, self.data_in, self.tmp32, self.tmp32_2, self.data_out, self.RW, self.ra, self.rb, self.rx, self.alu_op, self.flags, self.instr_state, self.stack_op]
        
    def alu_handler(self, m: Module):
        with m.If(self.alu_en):
            with m.Switch(self.alu_op):
                with m.Case(AluOps.ADD):
                    m.d.comb += [
                        self.alu_out.eq(self.alu_1 + self.alu_2)
                    ]
                    m.d.sync += [
                        self.flags[Flags.ZERO].eq(self.alu_out == 0),
                        self.flags[Flags.NEGATIVE].eq(self.alu_out < 0)
                    ]
                with m.Case(AluOps.SUB):
                    m.d.comb += [
                        self.alu_out.eq(self.alu_1 - self.alu_2),
                    ]
                    m.d.sync += [
                        self.flags[Flags.ZERO].eq(self.alu_out == 0),
                        self.flags[Flags.NEGATIVE].eq(self.alu_out < 0)
                   ]
                with m.Default():
                    m.d.comb += self.alu_out.eq(0)
                    m.d.sync += self.flags.eq(0)
                    m.d.sync += self.flags[Flags.ERROR].eq(1)

        m.d.comb += [
            self.alu_en.eq(0)
        ]
    
    def stack_handler(self, m: Module):
        with m.If(self.stack_en):
            with m.Switch(self.stack_op):
                with m.Case(StackOps.PUSH):
                    m.d.sync += [
                        self.addr.eq(self.sp),
                        self.sp.eq(self.sp - 1),
                        self.data_out.eq(self.stack_data),
                        self.RW.eq(0)
                    ]
                with m.Case(StackOps.POP):
                    m.d.sync += [
                        self.sp.eq(self.sp + 1),
                        self.addr.eq(self.sp + 1),
                        self.RW.eq(1)
                    ]
            m.d.comb += self.stack_en.eq(0)


    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        if self.useMemory:
            m.submodules.mem = self.mem
            self.read = self.mem.read_port(domain="comb")
            self.write = self.mem.write_port()
            m.d.comb += [
                self.read.addr.eq(self.addr),
                self.write.addr.eq(self.addr)
            ]
            with m.If(self.RW):
                m.d.comb += [
                    self.data_in.eq(self.read.data),
                    self.write.en.eq(0)
                ]
            with m.Else():
                m.d.comb += [
                    self.data_in.eq(0xFFFFFFFF),
                    self.write.data.eq(self.data_out),
                    self.write.en.eq(1)
                ]

        m.d.comb += [
            self.end_instr_flag.eq(0),
            self.alu_en.eq(0),
            self.stack_en.eq(0),
        ]

        self.instruction_end_handler(m)
        self.reset_handler(m)
        self.alu_handler(m)
        self.stack_handler(m)

        with m.If(self.reset_state == 2):
            self.cycle(m)

        return m

    def cycle(self, m):
        with m.If(self.instr_state == 0):
            self.fetch(m)
        with m.Else():
            self.execute(m)

    def fetch(self, m: Module):
        m.d.sync += [
            self.ir.eq(self.data_in),
            self.instr_state.eq(1)
        ]
    
    def execute(self, m: Module):
        with m.Switch(self.ir):
            for opcode, inst in instruction_opcodes.items():
                with m.Case(Const(opcode, signed(32))):
                    inst.execute(m, self)
            with m.Default():
                instruction_names["NOP"].execute(m, self)

    def instruction_end_handler(self, m: Module):
        with m.If(self.end_instr_flag):
            m.d.sync += self.addr.eq(self.end_instr_addr)
            m.d.sync += self.ip.eq(self.end_instr_addr)
            m.d.sync += self.instr_state.eq(0)

    def end_instr(self, m: Module, addr: Statement):
        m.d.comb += self.end_instr_addr.eq(addr)
        m.d.comb += self.end_instr_flag.eq(1)

    def advance_ip_goto_state(self, m: Module, state: int, RW: int = 1, overrideAddr: bool = True):
        m.d.sync += [
                    self.ip.eq(self.ip + 1),
                    self.RW.eq(RW),
                    self.instr_state.eq(state)
        ]
        if overrideAddr:
            m.d.sync += self.addr.eq(self.ip + 1)

    def reset_handler(self, m: Module):
        if self.useResetVector:
            with m.Switch(self.reset_state):
                with m.Case(0):
                    m.d.sync += self.addr.eq(self.startAddr)
                    m.d.sync += self.RW.eq(1)
                    m.d.sync += self.reset_state.eq(1)
                with m.Case(1):
                    m.d.sync += [
                        self.reset_state.eq(2),
                        self.tmp32.eq(0),
                        self.tmp32_2.eq(0),
                        self.tmp32_3.eq(0)
                    ]
                    self.end_instr(m, self.data_in)
        else:
            m.d.sync += [
                self.reset_state.eq(2),
                self.tmp32.eq(0),
                self.tmp32_2.eq(0),
                self.tmp32_3.eq(0)
            ]
            self.end_instr(m, self.startAddr)

if __name__ == "__main__":
    parser = main_parser()
    args = parser.parse_args()

    m = Module()

    mem = {
        0x00000009: 0x00000020, #Reset vector
        0x00000020: 0x00000001, #NOP
        0x00000023: 0x00000020, #LDA_ABS
        0x00000024: 0x00000015,
        0x00000025: 0x00000021, #LDB_ABS
        0x00000026: 0x00000006,
        0x00000027: 0x00000022, #LDX_ABS
        0x00000028: 0x000000AB,
        0x00000029: 0x00000030, #ADDA_ABS
        0x0000002A: 0x00000015,
        0x0000002B: 0x00000034, #SUBB_ABS
        0x0000002C: 0x00000002,
        0x0000002D: 0x00000011, #JIZ
        0x0000002E: 0x00000040,
        0x00000030: 0x00000010, #JMP
        0x00000031: 0x00000029,
        0x00000040: 0x00000001, #NOP
        0x00000041: 0x00000033, #SUBA_ABS
        0x00000042: 0x00000010,
        0x00000045: 0x00000040, #STA
        0x00000046: 0x0000004A,
        0x00000048: 0x00000001, #NOP
        0x00000049: 0x00000031, #ADDB_ABS
        0x0000004A: 0x000000FA,
        0x0000004B: 0x000000E2, #ADDX
        0x0000004C: 0x00002000,
        0x0000004D: 0x00000041, #STB
        0x0000004E: 0x00002001,
        0x0000004F: 0x000000D0, #LDA
        0x00000050: 0x00002002,
        0x00000051: 0x000000C0, #SUBA
        0x00000052: 0x00002001,
        0x00000053: 0x00000000, #HALT

        0x00000070: 0x00000000, #HALT
        0x00002000: 0x10000000,
        0x00002002: 0x80000000,
    }

    subroutine_test_mem = {
        0x00004000: 0x00000030,
        0x00004001: 0x00000010,
        0x00004002: 0x00000034,
        0x00004003: 0x00000001,
        0x00004004: 0x000000B5,

        0x00000009: 0x00000020,
        0x00000020: 0x00000020,
        0x00000021: 0x00000005,
        0x00000022: 0x000000A1,
        0x00000023: 0x00000021,
        0x00000024: 0x00000011,
        0x00000025: 0x000000A2,
        0x00000026: 0x000000A5,
        0x00000027: 0x00004000,
        0x00000028: 0x000000B2,
        0x00000029: 0x000000B1,
        0x0000002A: 0x00000000
    }

    m.submodules.core = core = Core(useMemory=True, mem_init=mem)

    # with m.Switch(core.addr):
    #     for addr, data in mem.items():
    #         with m.Case(addr):
    #             m.d.comb += core.data_in.eq(data)
    #     with m.Default():
    #         m.d.comb += core.data_in.eq(0xFF)

    sim = Simulator(m)
    sim.add_clock(1e-6)

    def process():
        for i in range(300):
            if (yield core.ir == 0x00) and not 0 <= i <= 4:
                return
            yield Tick()

    if not os.path.isdir("../sim"):
        if os.path.exists("../sim"):
            raise FileExistsError("../sim must be a directory")
        else:
            os.mkdir("../sim")

    sim.add_process(process)
    with sim.write_vcd("../sim/core.vcd", "../sim/core.gtkw", traces=core.ports()):
        sim.run()