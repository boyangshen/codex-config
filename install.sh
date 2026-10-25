#!/bin/sh
set -eu
repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
runtime_file="${XDG_STATE_HOME:-$HOME/.local/state}/codex-config/python"
python_bin=${CODEX_CONFIG_PYTHON:-}
if [ -z "$python_bin" ] && [ -f "$runtime_file" ]; then
    IFS= read -r python_bin < "$runtime_file" || true
fi
if [ -n "$python_bin" ]; then
    "$python_bin" -c 'try: import tomllib
except ImportError: import tomli' >/dev/null
else
    for candidate in python3.14 python3.13 python3.12 python3.11 python3; do
        if command -v "$candidate" >/dev/null 2>&1 &&
           "$candidate" -c 'try: import tomllib
except ImportError: import tomli' >/dev/null 2>&1; then
            python_bin=$candidate
            break
        fi
    done
fi
if [ -z "$python_bin" ]; then
    echo '需要 Python 3.11+，或为 Python 3.10 安装 tomli；也可设置 CODEX_CONFIG_PYTHON。' >&2
    exit 1
fi
mode=install
if [ "${1:-}" = --capture ]; then
    mode=capture
    shift
fi
exec "$python_bin" "$repo_dir/scripts/manage.py" "$mode" "$@"
