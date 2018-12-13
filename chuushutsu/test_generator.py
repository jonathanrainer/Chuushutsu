import os
import re

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

    def generate_trace_indexes(self, test_case_path):
        # Read the file contents into memory
        with open(str(test_case_path), 'r') as test_cases_file:
            file_contents = test_cases_file.readlines()
        # Iterate over the file contents to find the occurences of the keyword class
        final_file_contents = []
        instruction_index = 0
        test_index = 0
        for class_counter,line in enumerate(file_contents):
            class_match = re.match("^class (.*)_(0X[0-9A-F]+.*)_([0-9]+)_.*", file_contents[class_counter])
            if class_match:
                test_index = 1
                instruction_index += 1
                # When a class has been found we can begin work, first we need to find the first line of the if_data
                # because this gives us a unique data point by which to find the information needed.
                final_file_contents.append("class {0}_{1}_{2}_Tests(unittest.TestCase):".format(
                    class_match.group(1), instruction_index, class_match.group(2)
                ))
                for if_marker_counter, _ in enumerate(file_contents[class_counter+1:], start=class_counter+1):
                    matches = re.match(
                        "^.*self.assertEqual\(trace_item\.if_data\[\"time_start\"\], \"(0x[A-F0-9a-f]+)\".*",
                        file_contents[if_marker_counter])
                    if matches:
                        break
                    # With this new information add in a setUp method to the class
                final_file_contents.extend([
                    "\n", "\n", "    def setUp(self):\n", "        self.trace_item = [trace_item for\n",
                    "                          trace_item in trace_data.values() if trace_item.if_data[\"time_start\"] "
                    "== \"{}\"][0]\n".format(matches.group(1))])
            elif re.match(".*trace_item = trace_data\[[0-9]+\]", line):
                continue
            elif re.match("\s+self\.assertEqual\(trace_item\..*\)", line):
                data_points = re.match("\s+self\.assertEqual\(trace_item\.(.*), \"(.*)\"\)", line)
                final_file_contents.append("        self.assertEqual(self.trace_item.{0}, \"{1}\")\n".format(
                    data_points.group(1), data_points.group(2)
                ))
            elif re.match("\s+ def test.*", line):
                method_elements = re.match("\s+def test_(.*)_(0X[0-9A-F]+)_[0-9]+_(.*)\(.*", line)
                final_file_contents.append("    def test_{0}_{1}_{2}_{3}_{4}(self):\n".format(
                    method_elements.group(1), instruction_index, method_elements.group(2), test_index,
                    method_elements.group(3)
                ))
                test_index += 1
            else:
                final_file_contents.append(line)
        print("Hello World")
        with open(str(Path("tests", "ud_integration_tests_updated.py")), 'w') as new_file:
            for line in final_file_contents:
                new_file.write(line)





if __name__ == "__main__":
    memory_size = 4096
    system = TestGenerator(memory_size, memory_size, memory_size)
    system.generate_trace_indexes(Path("tests", "ud_integration_tests.py"))
    #system.generate_test_cases(Path("input", "benchmarks", "ud.c"), Path("temp", "memory_contents"), Path("temp", "simulation"),
            #Path("input", "templates"), memory_size, memory_size, memory_size)