from pathlib import Path
from jinja2 import Template

from chuushutsu.main import Chuushutsu


class TestGenerator(object):

    def __init__(self, instruction_memory_size, data_memory_size, stack_memory_size):
        self.system = Chuushutsu(instruction_memory_size, data_memory_size, stack_memory_size)

    def generate_test_cases(self, benchmark_path, temp_mem_path, temp_sim_path, template_path, instruction_memory_size,
            data_memory_size, stack_size):
        self.system.os_interface.construct_temporary_folders(
            [temp_mem_path, temp_sim_path]
        )
        mem_contents = self.system.shiji.run(benchmark_path, False)
        trace_data = self.system.simulation_engine.run_simulation(mem_contents[0][0], instruction_memory_size,
                                                           mem_contents[0][2],
                                                           mem_contents[1][0], data_memory_size + stack_size,
                                                           Path(template_path, "simulation_tcl_script.template"),
                                                           Path(template_path, "ryuki_defines.template"),
                                                           Path(template_path, "testbench.template"),
                                                           temp_sim_path
                                                           )
        with open(str(Path(template_path, "test_suite.template")), 'r') as template_fp:
            template = Template(template_fp.read(), lstrip_blocks=True, trim_blocks=True)
        with open(str(Path("tests", "{0}_integration_tests.py".format(benchmark_path.stem))), "w") as output_file:
            output_file.write(template.render(
                trace_items = trace_data,
                benchmark_name = benchmark_path.stem
            ))


if __name__ == "__main__":
    memory_size = 4096
    system = TestGenerator(memory_size, memory_size, memory_size)
    system.generate_test_cases(Path("input", "benchmarks", "ud.c"), Path("temp", "memory_contents"), Path("temp", "simulation"),
            Path("input", "templates"), memory_size, memory_size, memory_size)