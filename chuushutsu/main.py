from pathlib import Path

from shiji.shiji import Shiji

from chuushutsu.simulation_engine import SimulationEngine
from chuushutsu.os_interface import OperatingSystemInterface


class Chuushutsu(object):

    def __init__(self, instruction_memory_size, data_memory_size, stack_memory_size):
        self.shiji = Shiji(Path("input", "templates"), Path("logs"), Path("temp", "memory_contents"),
                           Path("temp", "shiji"), "/opt/riscv/bin/", 256, 65536, instruction_memory_size,
                           data_memory_size, stack_memory_size)
        self.os_interface = OperatingSystemInterface(Path("scripts", "sh"))
        self.simulation_engine = SimulationEngine(
            Path.home().joinpath("Documents", "Experiments", "4_pulpino", "Ryuki"), self.os_interface)

    def run(self, benchmark_path, temp_mem_path, temp_sim_path, template_path, instruction_memory_size,
            data_memory_size, stack_size):
        self.os_interface.construct_temporary_folders(
            [temp_mem_path, temp_sim_path]
        )
        # Take in some raw C code, and construct the appropriate testbench
        mem_contents = self.shiji.run(benchmark_path, False)
        # Compile it and run the simulation using that benchmark
        trace_data = self.simulation_engine.run_simulation(mem_contents[0][0], instruction_memory_size, mem_contents[0][2],
                                                           mem_contents[1][0], data_memory_size + stack_size,
                                                           Path(template_path, "simulation_tcl_script.template"),
                                                           Path(template_path, "ryuki_defines.template"),
                                                           Path(template_path, "testbench.template"),
                                                           temp_sim_path
                                                           )
        print("Hello World")
        # Take the data and create the new queriable graph structure
        # Postprocess the graph to construct the requested, required, contention list elements
        # Scan over the graph to find potential re-orderings
        # Create a schedule of memory
        return 0


if __name__ == "__main__":
    memory_size = 4096
    system = Chuushutsu(memory_size, memory_size, memory_size)
    system.run(Path("input", "benchmarks", "fdct.c"), Path("temp", "memory_contents"), Path("temp", "simulation"),
            Path("input", "templates"), memory_size, memory_size, memory_size)
