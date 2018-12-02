import os

from jinja2 import Template
from pathlib import Path
from shutil import copyfile

from joushi.vcd_engine import VCDEngine


class SimulationEngine(object):

    def __init__(self, project_path, os_interface):
        self.project_path = project_path
        self.os_interface = os_interface
        self.vcd_engine = VCDEngine()

    def run_simulation(self, instruction_memory_file, num_instr_words, trap_address, data_memory_file, num_data_words,
                       tcl_template_file, defines_template_file, testbench_template_file, temp_directory, save_data_loc):
        # Generate the correct define file
        defines_path = Path(temp_directory, "ryuki_defines.sv")
        testbench_path = Path(temp_directory, "testbench.sv")
        self.generate_file_from_template(defines_template_file, {
            "num_data_words": num_data_words,
            "num_instruction_words": num_instr_words
        }, defines_path)
        testbench_module_name = "sim_tb"
        # Generate an appropriate Testbench to stimulate the Processor
        self.generate_file_from_template(
            testbench_template_file, {
                "module_name": testbench_module_name,
                "trap_address": trap_address
            }, testbench_path
        )
        # Generate the TCL Script
        tcl_path =  Path(temp_directory, "run_sim.tcl")
        self.generate_file_from_template(
            tcl_template_file, {
                "relative_project_directory": Path(os.path.relpath(str(self.project_path), str(temp_directory))),
                "defines_file": defines_path.name,
                "instruction_mem_file": instruction_memory_file.name,
                "data_mem_file": data_memory_file.name,
                "testbench_module_name": testbench_module_name,
                "testbench_file": testbench_path.name
            }, tcl_path
        )
        vcd_output_file = Path("temp", "vcd_data", "data.vcd")
        # Run the SH Script to invoke the TCL Script and run that through Vivado
        self.os_interface.run_simulation(tcl_path, "behavioral", vcd_output_file.absolute())
        # Structure the output data and then return it
        if save_data_loc:
            copyfile(str(vcd_output_file), str(save_data_loc))
        return self.vcd_engine.extract_tracing_information(vcd_output_file, testbench_module_name)

    @staticmethod
    def generate_file_from_template(template_file, keyvals, output_file):
        with open(str(template_file), "r") as template_fp:
            template = Template(template_fp.read(), lstrip_blocks=True, trim_blocks=True)
            with open(str(output_file), "w") as output_fp:
                output_fp.write(template.render(keyvals))

