from pathlib import Path
import re

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

        # Take the data and create the set of loads/stores associated with each address
        mem_addresses = \
            sorted(list(set(
                [x[1].address for x in trace_data if re.match("^0x[0-9A-Za-z]{6}[082Aa]3$", x[1].instruction)]
            )))
        load_store_set = { x : [] for x in mem_addresses}
        for trace_item in trace_data:
            if re.match("^0x[0-9A-Za-z]{6}[08]3$", trace_item[1].instruction):
                load_store_set[trace_item[1].address].append((trace_item[0], trace_item[1], "LOAD"))
            elif re.match("^0x[0-9A-Za-z]{6}[2Aa]3$", trace_item[1].instruction):
                load_store_set[trace_item[1].address].append((trace_item[0], trace_item[1], "STORE"))
        for address, instruction_set in load_store_set.items():
            load_store_set[address] = sorted(instruction_set, key=lambda x: x[0])
        print("Hello World")
        # Postprocess the graph to construct the requested, required, contention list elements
        # Scan over the graph to find potential re-orderings
        # Create a schedule of memory
        return 0


if __name__ == "__main__":
    memory_size = 4096
    system = Chuushutsu(memory_size, memory_size, memory_size)
    system.run(Path("input", "benchmarks", "fdct.c"), Path("temp", "memory_contents"), Path("temp", "simulation"),
            Path("input", "templates"), memory_size, memory_size, memory_size)
