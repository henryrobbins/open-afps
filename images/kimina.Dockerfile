# GPU image for the KiminaProver: vLLM (to serve Kimina-Prover) + Lean + Mathlib.
#
# Separate from images/Dockerfile (the CPU verify/agent image) because serving the
# model needs a CUDA + torch + vLLM stack. We base on the official vLLM image so that
# stack is known-good and version-matched, then layer our *standard* Lean toolchain
# on top -- Kimina has no LeanDojo / fixed-commit pin, so this reuses the exact
# elan + Mathlib-cache recipe from images/Dockerfile (a big simplification over BFS).
#
# One image serves two roles, like the CPU image: it runs the one-shot
# kimina_generate.py (GPU) *and* can run `lake env lean` (verify) on the same pin.
# Model weights are NOT baked (multi-GB); vLLM downloads them to HF_HOME at runtime,
# which a Modal Volume mounted at /root/.cache/huggingface persists across runs.
#
# Build context is images/ :
#   open-afps build-kimina-image            (publishes a Modal image named "kimina")
#   docker build -f images/kimina.Dockerfile -t kimina:latest images/   (local/GPU)

FROM vllm/vllm-openai:v0.6.6

ENV DEBIAN_FRONTEND=noninteractive

# Lean's build needs git/curl/build-essential; the vLLM image is minimal.
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# elan + Lean toolchain in a global ELAN_HOME (Modal runs as root). The pinned
# toolchain in lean/lean-toolchain installs lazily on the first `lake` call.
ENV ELAN_HOME=/opt/elan
ENV PATH="/opt/elan/bin:${PATH}"
RUN curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf \
        | sh -s -- -y --default-toolchain none --no-modify-path

WORKDIR /workspace

# Bake the lake project skeleton + warm Mathlib olean cache (same as the CPU image),
# so any uploaded project on the matching pin compiles against a warm cache.
COPY lean/ /workspace/
RUN lake update && lake exe cache get

# The one-shot generation entrypoint KiminaProver invokes.
COPY kimina/ /opt/kimina/

# The base image's ENTRYPOINT launches the vLLM OpenAI server; we drive the image
# with explicit commands (kimina_generate.py / lake) via the compute backend instead.
ENTRYPOINT []
CMD ["bash"]
