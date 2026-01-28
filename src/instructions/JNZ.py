from include import exceptions
from include.instruction import *
from amaranth import Module, Signal, Cat
from include.enums import *

def JNZ_exec(m: Module, core):
    with m.If(~core.flags[Flags.ZERO]):
        with m.Switch(core.instr_state):
            with m.Case(2):
                m.d.sync += core.tmp8.eq(core.data_in), 
                core.advance_ip_goto_state(m, 3)
            with m.Case(3):
                address = Cat(core.tmp8, core.data_in)
                m.d.sync += core.tmp8.eq(0)
                core.end_instr(m, address)
            with m.Default():
                core.advance_ip_goto_state(m, 2)
    with m.Else():
        core.end_instr(m, core.ip + 3)

JNZ = Instruction(0x12, "JNZ", JNZ_exec, 0x03)