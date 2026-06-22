# Base sandbox image for open-afps: Lean + Mathlib + agent CLIs + lean-lsp-mcp.
#
# Phase-1 skeleton. Port the working specifics from milp_flare's
# assets/docker/Dockerfile. The one deliberate difference: this image is generic
# (no MILP-specific Common.lean) -- it carries a stock Mathlib project so any
# uploaded project pinned to the same toolchain builds against the warm cache.
#
# IMPORTANT: the toolchain pinned here is the contract. The verifier rejects any
# uploaded project whose lean-toolchain differs (see Verifier.check_compatible).
# Bump LEAN_TOOLCHAIN and rebuild to support a new pin; add a second image to
# support multiple pins side by side.

FROM ubuntu:24.04

ARG LEAN_TOOLCHAIN=leanprover/lean4:v4.31.0

# TODO(phase 1): port from milp_flare/assets/docker/Dockerfile
#   - system pkgs: ca-certificates curl git build-essential python3 ripgrep
#   - Node 20 + npm globals: @anthropic-ai/claude-code @openai/codex opencode-ai
#   - elan + pin ${LEAN_TOOLCHAIN}
#   - pipx: lean-lsp-mcp, uv
#   - pre-bake a stock Mathlib project at /workspace and `lake exe cache get`
#     so uploaded projects on the same pin hit a warm olean cache.

CMD ["bash"]
