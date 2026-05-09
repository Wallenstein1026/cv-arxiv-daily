#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

PY_BIN="${PY:-python3}"
exec "$PY_BIN" run_agent.py --config agent_config.yaml "$@"
