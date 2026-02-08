# SISC-F 32-bit CPU
# Copyright (c) 2026 Francesco Angeloni
#
# This source describes Open Hardware and is licensed under the CERN-OHL-W v2.
# You may redistribute and modify this source and make products using it
# under the terms of the CERN-OHL-W v2 (https://cern.ch/cern-ohl).
#
# SPDX-License-Identifier: CERN-OHL-W-2.0

import os, sys, argparse, importlib
from amaranth.back import verilog
from migen import *
from migen.fhdl import conv_output
from litex.soc.cores import cpu
from litex.soc.integration.soc_core import SoCCore
from litex.soc.integration.builder import Builder
from src.include.wishbone import SISCFWishboneWrapper
from litex_include import driver

sys.path.append(os.path.join(os.curdir, "src"))
from src.main import Core

def utf8_write(self, main_filename):
    with open(main_filename, "w", encoding="utf-8") as f:
        f.write(self.main_source)

    for filename, content in self.data_files.items():
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

build_dir = "litex_build"

def export_verilog(export, path: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(verilog.convert(export, "siscf_core_top"))


def main():
    wrapper = SISCFWishboneWrapper(Core(useResetVector=False, startAddr=0))
    verilog_path = os.path.join(build_dir, "verilog", "siscf_core_top.v")
    parser = argparse.ArgumentParser(description="SISC-F LiteX builder")
    
    parser.add_argument("--board", help="Set the board to build LiteX for")

    args = parser.parse_args()
    board_lib = None
    module = None
    try:
        module = f"litex_boards.targets.{args.board}"
        board_lib = importlib.import_module(module)
    except ImportError:
        print(f"Could not find board {args.board} in litex_boards. Is your board litex compatible?")
        print(module)
        sys.exit(1)

    export_verilog(wrapper, verilog_path)

    conv_output.ConvOutput.write = utf8_write

    cpu.CPUS["siscf"] = driver.SISCF_core

    if args.board == "sipeed_tang_nano_20k":
        soc = board_lib.BaseSoC(
            with_rgb_led         = True,
            cpu_type             = "siscf",
            csr_data_width       = 32,
            csr_origin           = 0xFFFF0000,
            csr_address_width    = 18,
            csr_ordering         = "little",
            integrated_sram_size = 0x10000,
            with_sdram           = False
        )
    else:
        soc = board_lib.BaseSoC(
            cpu_type             = "siscf",
            csr_data_width       = 32,
            csr_origin           = 0xFFFF0000,
            csr_address_width    = 18,
            csr_ordering         = "little",
            integrated_sram_size = 0x10000,
            with_sdram           = False
        )

    from litex.soc.integration.soc import SoCRegion

    soc.bus.regions["sram"] = SoCRegion(
        origin = 0x0000,
        size   = 0x10000,
        cached = True,
        linker = True
    )

    soc.platform.add_source(verilog_path)
    soc.bus.address_width = 32
    soc.bus.data_width = 32

    if "main_ram" in soc.bus.slaves:
        del soc.bus.slaves["main_ram"]
    if "main_ram" in soc.bus.regions:
        del soc.bus.regions["main_ram"]

    build = Builder(soc, output_dir=build_dir, compile_gateware=True, compile_software=False)
    build.build()

if __name__ == "__main__":
    if not os.path.exists(build_dir):
        os.mkdir(build_dir)
        os.mkdir(os.path.join(build_dir, "verilog"))
    elif os.path.isfile(build_dir):
        raise FileExistsError(f"{build_dir} is a file instead of a folder")
    
    main()