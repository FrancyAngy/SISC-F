from include import exceptions
from include.instruction import *
from amaranth import Module, Signal

_length = 0x3

def _LDI_ABS(m: Module, core, register: Signal):
    with m.If(core.instr_state == 1):
        core.advance_ip_goto_state(m, 2)
    with m.Else():
        m.d.sync += register.eq(core.data_in)
        core.end_instr(m, core.ip + 1)

def LDA_ABS_exec(m: Module, core):
    _LDI_ABS(m, core, core.ra)
def LDB_ABS_exec(m: Module, core):
    _LDI_ABS(m, core, core.rb)
def LDX_ABS_exec(m: Module, core):
    _LDI_ABS(m, core, core.rx)

LDA_ABS = Instruction(0x20, "LDA_ABS", LDA_ABS_exec, _length)
LDB_ABS = Instruction(0x21, "LDB_ABS", LDB_ABS_exec, _length)
LDX_ABS = Instruction(0x22, "LDX_ABS", LDX_ABS_exec, _length)