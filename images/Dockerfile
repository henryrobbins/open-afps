# Base sandbox image for open-afps: Lean + Mathlib, with the olean cache pre-baked.
#
# Mirrors milp_flare's assets/docker/Dockerfile, minus the MILP-specific Lean
# skeleton and (for phase 1) the agent CLIs -- this image only needs to *verify*.
# Agent CLIs (claude-code/codex/opencode) + lean-lsp-mcp get layered on in phase 3.
#
# The toolchain pinned in images/lean/lean-toolchain is the contract: the verifier
# rejects any uploaded project whose lean-toolchain differs. Bump it (and the mathlib
# rev in images/lean/lakefile.toml) and rebuild to support a new pin.
#
# Build context is images/ :  docker build -t open-afps:latest images/

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# ripgrep is recommended for lean-lsp-mcp's local search (used in later phases).
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        build-essential \
        python3 \
        ripgrep \
        procps \
    && rm -rf /var/lib/apt/lists/*

# Non-root user (matches milp_flare; Lean's elan lives under this user's HOME).
RUN useradd -m -s /bin/bash agent
USER agent
WORKDIR /home/agent

# elan + Lean toolchain. `--default-toolchain none` lets the lean-toolchain file
# we copy below pin the version on the first `lake` invocation.
RUN curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf \
        | sh -s -- -y --default-toolchain none --no-modify-path
ENV PATH="/home/agent/.elan/bin:/home/agent/.local/bin:${PATH}"

WORKDIR /workspace

# Bake the lake project skeleton: a bare "require mathlib" project. lake update
# resolves the manifest and clones mathlib; cache get downloads its oleans so any
# uploaded project on the same pin compiles against a warm cache.
COPY --chown=agent:agent lean/ /workspace/
RUN lake update && lake exe cache get

# Verification workdirs are bind-mounted to /workspace/wd; the DockerBackend
# symlinks /workspace/wd/.lake -> /workspace/.lake so they reuse this warm cache.

CMD ["bash"]
