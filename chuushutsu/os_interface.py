import os
import subprocess

from pathlib import Path


class OperatingSystemInterface(object):

    def __init__(self, sh_script_dir):
        self.sh_script_dir = sh_script_dir

    @staticmethod
    def construct_temporary_folders(temporary_paths):
        for path in temporary_paths:
            os.makedirs(str(path), exist_ok=True)

    def run_simulation(self, tcl_script_path, mode, vcd_output_path):
        os.makedirs(str(vcd_output_path.parent), exist_ok=True)
        subprocess.run(
            "{0} {1} {2} {3}".format(
                Path(self.sh_script_dir, "run_vivado.sh").absolute(), tcl_script_path, mode, vcd_output_path), shell=True
        )


