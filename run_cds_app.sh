#!/usr/bin/env bash
# Backward-compatible launcher (run from CKD Dataset folder).
cd "$(dirname "$0")"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$(pwd)/.mplconfig}"
export MPLBACKEND="${MPLBACKEND:-Agg}"
exec .venv312/bin/streamlit run app/demo_app.py "$@"
