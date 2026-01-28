from include import exceptions
from include.instruction import *
from amaranth import Module, Signal, Cat
from include.enums import *

def _ADDI_ABS(m: Module, core, register: Signal):
    with m.If(core.instr_state == 1):
        core.advance_ip_goto_state(m, 2)
    with m.Else():
        m.d.comb += [
            core.alu_1.eq(register),
            core.alu_2.eq(core.data_in),
            core.alu_op.eq(AluOps.ADD),
            core.alu_en.eq(1)
        ]
        m.d.sync += register.eq(core.alu_out)
        core.end_instr(m, core.ip + 1)

def ADDA_ABS_exec(m: Module, core):
    _ADDI_ABS(m, core, core.ra)

def ADDB_ABS_exec(m: Module, core):
    _ADDI_ABS(m, core, core.rb)

def ADDX_ABS_exec(m: Module, core):
    _ADDI_ABS(m, core, core.rx)

ADDA_ABS = Instruction(0x30, "ADDA_ABS", ADDA_ABS_exec, 0x2)
ADDB_ABS = Instruction(0x31, "ADDB_ABS", ADDB_ABS_exec, 0x2)
ADDX_ABS = Instruction(0x32, "ADDX_ABS", ADDX_ABS_exec, 0x2)