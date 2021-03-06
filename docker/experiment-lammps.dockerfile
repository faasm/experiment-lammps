ARG EXPERIMENTS_VERSION
ARG FAASM_VERSION
FROM faasm/experiment-base:${EXPERIMENTS_VERSION} as experiments

# Install LAMMPS
WORKDIR /experiments
RUN git clone https://github.com/faasm/experiment-lammps
WORKDIR /experiments/experiment-lammps
RUN git clone --branch faasm https://github.com/faasm/lammps

# Cross-compile and build LAMMPS
RUN inv build.build --clean
# Build natively
#RUN inv build.native --clean

# Run Faasm Cli
FROM faasm/cli:${FAASM_VERSION}

# Copy compiled binary and sample data
COPY --from=experiments /experiments/experiment-lammps/lammps/build/lmp \
    /usr/local/code/faasm/wasm/lammps/main/function.wasm
COPY --from=experiments /experiments/experiment-lammps/lammps/examples \
    /data/lammps-examples
COPY --from=experiments \
    /experiments/experiment-lammps/lammps/examples/controller/in.controller.wall \
    /data/in.controller
# Temporary fix to have access to the source code to solve building issues
COPY --from=experiments \
    /experiments/experiment-lammps /experiment-lammps

# Copy the runner code
# TODO cleaner way to do this?
COPY --from=experiments \
    /experiments/experiment-lammps/src/runner/lammps_pool_runner.cpp \
    /usr/local/code/faasm/src/runner/lammps_pool_runner.cpp
# Override runner's CMakeLists
COPY --from=experiments \
    /experiments/experiment-lammps/src/runner/CMakeLists.txt \
    /usr/local/code/faasm/src/runner/CMakeLists.txt
# Compile LAMMPS custom runner
RUN inv -r faasmcli/faasmcli dev.cc lammps_pool_runner

CMD ["/bin/bash", "-l"]
