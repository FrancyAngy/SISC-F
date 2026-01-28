from include import exceptions
from include.instruction import *
from amaranth import Module, Signal, Cat
from include.enums import *

def _SUBI_ABS(m:Module, core, register: Signal):
    with m.If(core.instr_state == 1):
        core.advance_ip_goto_state(m, 2)
    with m.Else():
        m.d.comb += [
            core.alu_1.eq(register),
            core.alu_2.eq(core.data_in),
            core.alu_op.eq(AluOps.SUB),
            core.alu_en.eq(1)
        ]
        m.d.sync += register.eq(core.alu_out)
        core.end_instr(m, core.ip + 1)

def SUBA_ABS_exec(m:Module, core):
    _SUBI_ABS(m, core, core.ra)

def SUBB_ABS_exec(m:Module, core):
    _SUBI_ABS(m, core, core.rb)

def SUBX_ABS_exec(m:Module, core):
    _SUBI_ABS(m, core, core.rx)

SUBA_ABS = Instruction(0x33, "SUBA_ABS", SUBA_ABS_exec, 0x02)
SUBB_ABS = Instruction(0x34, "SUBB_ABS", SUBB_ABS_exec, 0x02)
SUBX_ABS = Instruction(0x35, "SUBX_ABS", SUBX_ABS_exec, 0x02)