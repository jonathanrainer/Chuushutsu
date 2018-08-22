from pathlib import Path

from shiji.shiji import Shiji


class Chuushutsu(object):

    def __init__(self):
        self.shiji = Shiji(Path("input", "templates"), Path("logs"), Path("output", "memory_contents"), Path("temp"),
                           "/opt/riscv/bin/", 256, 65536)

    def run(self, benchmark_path):
        # Take in some raw C code, and construct the appropriate testbench
        test = self.shiji.run(Path("input", "benchmarks", "fdct.c"))
        # Compile it and run the simulation using that benchmark
        # Take the data and create the new queriable graph structure
        # Postprocess the graph to construct the requested, required, contention list elements
        # Scan over the graph to find potential re-orderings
        # Create a schedule of memory
        return 0


if __name__ == "__main__":
    system = Chuushutsu()
    system.run(Path("input", "benchmarks", "test.c"))
