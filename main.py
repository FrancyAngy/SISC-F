from enum import IntEnum, auto
from typing import List, Dict, Tuple, Optional
from amaranth import Signal, Const, Module
from amaranth import Signal, Value, Elaboratable, Module, Cat, Const, Mux
from amaranth import ClockDomain, ClockSignal
from amaranth.hdl.ast import Statement
from amaranth.build import Platform
from amaranth.cli import main_parser, main_runner
from amaranth.sim import Simulator

class Reg8(IntEnum):
    NONE = 0
    IR = 1
    RA = 2
    RB = 3
    RX = 4
    TMP = 5
    TMP16L = 6
    TMP16H = 7
    DATAIN = 9
    DATAOUT = 10
    ADDRL = 11
    ADDRH = 12
    IPL = 13
    IPH = 14
    SPL = 15
    SPH = 16
    INT_ARGS_L = 17
    INT_ARGS_H = 18
    INT_RET_L = 19
    INT_RET_H = 20
    QPL = 21
    QPH = 22

class Reg16(IntEnum):
    IP = 0
    ADDR = 1
    SP = 2
    QP = 3
    TMP = 4
    INT_ARGS = 5
    INT_RET = 6


class Core(Elaboratable):
    def __init__(self):
        self.addr = Signal(16)
        self.data_in = Signal(8)
        self.data_out = Signal(8)
        self.RW = Signal(reset=1) # Read = 1, Write = 0

        #Registries
        self.ra = Signal(8, reset_less=True)
        self.rb = Signal(8, reset_less=True)
        self.rx = Signal(8, reset_less=True)
        self.ip = Signal(16, reset_less=True)
        self.ir = Signal(8, reset_less=True)
        self.sp = Signal(16, reset_less=True)
        self.qp = Signal(16, reset_less=True)
        self.tmp8 = Signal(8)
        self.tmp16 = Signal(16)

        #BUSes
        self.interrupt_args = Signal(16)
        self.interrupt_return = Signal(16)
        self.alu_1 = Signal(16)
        self.alu_2 = Signal(16)
        self.alu_out = Signal(16)

        #BUS selectors
        self.alu_1_sel = Signal(Reg16)
        self.alu_2_sel = Signal(Reg16)
        self.alu_write = Signal(len(Reg16.__members__))
        self.int_args_sel = Signal(Reg16)
        self.int_ret_sel = Signal(Reg16)
        self.int_write = Signal(len(Reg16.__members__))

        #States
        self.reset_state = Signal(2)
        self.instr_state = Signal(4)
        self.end_instr_flag = Signal()
        self.end_instr_addr = Signal(16)

        self.reg8_map = {
            Reg8.RA: (self.ra, True),
            Reg8.RB: (self.rb, True),
            Reg8.RX: (self.ra, True),
            Reg8.IPL: (self.ip[8:], True),
            Reg8.IPH: (self.ip[:8], True),
            Reg8.IR: (self.ir, True),
            Reg8.SPL: (self.sp[8:], True),
            Reg8.SPH: (self.sp[:8], True),
            Reg8.QPL: (self.qp[8:], True),
            Reg8.QPH: (self.qp[:8], True),
            Reg8.TMP: (self.tmp8, True),
            Reg8.TMP16L: (self.tmp16[8:], True),
            Reg8.TMP16H: (self.tmp16[:8], True),
            Reg8.INT_ARGS_L: (self.interrupt_args[8:], True),
            Reg8.INT_ARGS_H: (self.interrupt_args[:8], True),
            Reg8.INT_RET_H: (self.interrupt_return[8:], True),
            Reg8.INT_RET_L: (self.interrupt_return[:8], True),
            Reg8.ADDRL: (self.addr[8:], True),
            Reg8.ADDRH: (self.addr[:8], True),
            Reg8.DATAIN: (self.data_in, False),
            Reg8.DATAOUT: (self.data_out, True)
        }

        self.reg16_map = {
            Reg16.ADDR: (self.addr, True),
            Reg16.INT_ARGS: (self.interrupt_args, True),
            Reg16.INT_RET: (self.interrupt_return, True),
            Reg16.IP: (self.ip, True),
            Reg16.QP: (self.qp, True),
            Reg16.SP: (self.sp, True),
            Reg16.TMP: (self.tmp16, True)
        }

    def ports(self) -> List[Signal]:
        return [self.ip, self.ir, self.addr, self.data_in, self.tmp8, self.data_out, self.RW]
        
    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        m.d.comb += self.end_instr_flag.eq(0)

        self.src_bus_setup(m, self.reg16_map, self.alu_1, self.alu_1_sel)
        self.src_bus_setup(m, self.reg16_map, self.alu_2, self.alu_2_sel)
        self.dest_bus_setup(m, self.reg16_map, self.alu_out, self.alu_write)

        self.instruction_end_handler(m)
        self.reset_handler(m)

        with m.If(self.reset_state == 3):
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
            with m.Case(0x01):
                self.NOP(m)
            with m.Case(0x10):
                self.JMP(m)
            with m.Default():
                self.NOP(m)
    
    def NOP(self, m: Module):
        self.end_instr(m, self.ip + 1)

    def JMP(self, m: Module):
        with m.Switch(self.instr_state):
            with m.Case(2):
                m.d.sync += [
                    self.tmp8.eq(self.data_in),
                    self.addr.eq(self.ip + 1),
                    self.ip.eq(self.ip + 1),
                    self.RW.eq(1),
                    self.instr_state.eq(3)
                ]
            with m.Case(3):
                address = Cat(self.tmp8, self.data_in)
                m.d.sync += self.tmp8.eq(0)
                self.end_instr(m, address)
            with m.Default():
                m.d.sync += [
                    self.addr.eq(self.ip + 1),
                    self.ip.eq(self.ip + 1),
                    self.RW.eq(1),
                    self.instr_state.eq(2)
                ]

    def instruction_end_handler(self, m: Module):
        with m.If(self.end_instr_flag):
            m.d.sync += self.addr.eq(self.end_instr_addr)
            m.d.sync += self.ip.eq(self.end_instr_addr)
            m.d.sync += self.instr_state.eq(0)
    

    def end_instr(self, m: Module, addr: Statement):
        m.d.comb += self.end_instr_addr.eq(addr)
        m.d.comb += self.end_instr_flag.eq(1)

    def reset_handler(self, m: Module):
        with m.Switch(self.reset_state):
            with m.Case(0):
                m.d.sync += self.addr.eq(0x0009)
                m.d.sync += self.RW.eq(1)
                m.d.sync += self.reset_state.eq(1)
            with m.Case(1):
                m.d.sync += self.addr.eq(0x000A)
                m.d.sync += self.RW.eq(1)
                m.d.sync += self.reset_state.eq(2)
                m.d.sync += self.tmp8.eq(self.data_in)
            with m.Case(2):
                address = Cat(self.tmp8, self.data_in)
                m.d.sync += [
                    self.reset_state.eq(3),
                    self.tmp8.eq(0)
                ]
                self.end_instr(m, address)

    def src_bus_setup(self, m: Module, reg_map, bus: Signal, selector: Signal):
        with m.Switch(selector):
            for e, reg in reg_map.items():
                with m.Case(e):
                    m.d.comb += bus.eq(reg[0])
            with m.Default():
                m.d.comb += bus.eq(0)

    def dest_bus_setup(self, m: Module, reg_map, bus: Signal, bitmap: Signal):
        for e, reg in reg_map.items():
            if reg[1]:
                with m.If(bitmap[e.value]):
                    m.d.sync += reg[0].eq(bus)

if __name__ == "__main__":
    parser = main_parser()
    args = parser.parse_args()

    m = Module()
    
    m.submodules.core = core = Core()

    mem = {
        0x0009: 0x20,
        0x000A: 0x00,
        0x0020: 0x01,
        0x0023: 0x10,
        0x0024: 0x20,
        0x0025: 0x00,
        0x0026: 0xCD,
        0x0027: 0xEF
    }
    with m.Switch(core.addr):
        for addr, data in mem.items():
            with m.Case(addr):
                m.d.comb += core.data_in.eq(data)
        with m.Default():
            m.d.comb += core.data_in.eq(0xFF)
    
    sim = Simulator(m)
    sim.add_clock(1e-6)

    def process():
        yield
        yield
        yield
        yield
        yield
        yield
        yield
        yield
        yield
        yield
        yield
        yield
        yield
        yield
        yield
        yield
        yield
        yield
        yield
        yield
        yield
        yield
        yield
        yield

    sim.add_sync_process(process)
    with sim.write_vcd("core.vcd", "core.gtkw", traces=core.ports()):
        sim.run()