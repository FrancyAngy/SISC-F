from include import exceptions
from include.instruction import *
from amaranth import Module

def HALT_exec(m: Module, core):
    core.end_instr(m, core.ip)

HALT = Instruction(0x00, "HALT", HALT_exec)