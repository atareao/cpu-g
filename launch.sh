#!/usr/bin/env bash
set -euo pipefail

# Sync the environment from uv.lock and launch cpu-g.
uv sync
uv run ./bin/cpu-g
