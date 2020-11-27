from os.path import join
from subprocess import run
from copy import copy
import os

from faasmtools.build import CMAKE_TOOLCHAIN_FILE
from tasks.util.file import clean_dir
from invoke import task

from tasks.util.env import EXPERIMENT_ROOT

LAMMPS_DIR = join(EXPERIMENT_ROOT, "lammps")


# The LAMMPS CMake build instructions can be found in the following link
# https://lammps.sandia.gov/doc/Build_cmake.html


@task
def build(ctx, clean=False):
    """
    Build and install the LAMMPS Molecular Dynamics Simulator
    """
    work_dir = join(LAMMPS_DIR, "build")
    cmake_dir = join(LAMMPS_DIR, "cmake")
    install_dir = join(LAMMPS_DIR, "install")
    # wasm_path = join(PROJ_ROOT, "wasm", "lammps", "test", "function.wasm")

    clean_dir(work_dir, clean)
    clean_dir(install_dir, clean)

    env_vars = copy(os.environ)

    cmake_cmd = [
        "cmake",
        "-GNinja",
        "-DFAASM_BUILD_TYPE=wasm",
        "-DCMAKE_TOOLCHAIN_FILE={}".format(CMAKE_TOOLCHAIN_FILE),
        "-DCMAKE_BUILD_TYPE=Release",
        "-DCMAKE_INSTALL_PREFIX={}".format(install_dir),
        cmake_dir,
    ]

    cmake_str = " ".join(cmake_cmd)
    print(cmake_str)

    res = run(cmake_str, shell=True, cwd=work_dir, env=env_vars)
    if res.returncode != 0:
        raise RuntimeError("LAMMPS CMake config failed")

    res = run("ninja", shell=True, cwd=work_dir)
    if res.returncode != 0:
        raise RuntimeError("LAMMPS build failed")

    res = run("ninja install", shell=True, cwd=work_dir)
    if res.returncode != 0:
        raise RuntimeError("LAMMPS install failed")

