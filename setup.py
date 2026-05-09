from setuptools import setup
from setuptools.command.build_py import build_py
import subprocess
from pathlib import Path


class CBuild(build_py):
    def run(self):
        self.announce("Compiling C library...")
        source = "csrc/zcopy_pulses.c"
        output_dir = Path("src/rppulses")
        lib_name = "zcopy_pulses.so"
        subprocess.check_call(
            [
                "gcc",
                "-O3",
                "-march=native",
                "-mfpu=neon",
                "-mfloat-abi=hard",
                "-shared",
                "-fPIC",
                "-o",
                output_dir / lib_name,
                source,
            ]
        )
        build_py.run(self)

setup(
    cmdclass={"build_py": CBuild},
)
