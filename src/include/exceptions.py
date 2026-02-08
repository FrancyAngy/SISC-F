# SISC-F 32-bit CPU
# Copyright (c) 2026 Francesco Angeloni
#
# This source describes Open Hardware and is licensed under the CERN-OHL-W v2.
# You may redistribute and modify this source and make products using it
# under the terms of the CERN-OHL-W v2 (https://cern.ch/cern-ohl).
#
# SPDX-License-Identifier: CERN-OHL-W-2.0

class InstructionNameAlreadyExists(Exception):
    def __init__(self, instrName: str, addInfo = None):
        self.instrName = instrName
        self.addInfo = addInfo
    
    def __str__(self) -> str:
        e = f"Tried to register {self.instrName} instruction, but an instruction with the same name already exists."
        if self.addInfo != None:
            e += f" Additional info are supplied: {self.addInfo}"
        
        return e
    
class AssemblerInstructionAlreadyExists(Exception):
    def __init__(self, instrName: str, isPseudo: bool = False, addInfo = None):
        self.instrName = instrName
        self.addInfo = addInfo
        self.isPseudo = isPseudo
    
    def __str__(self) -> str:
        if self.isPseudo:
            e = f"Tried to register {self.instrName} pseudo-instruction, but a pseudo-instuction with the same name already exists."
        else:
            e = f"Tried to register {self.instrName} instruction, but a pseudo-instuction with the same name already exists."
        if self.addInfo != None:
            e += f" Additional info are supplied: {self.addInfo}"
        
        return e