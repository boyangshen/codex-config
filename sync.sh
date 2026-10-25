#!/bin/sh
set -eu
repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ -n "$(git -C "$repo_dir" status --porcelain)" ]; then
    echo '配置仓库有未提交改动，未自动拉取；请先提交并推送或自行处理。' >&2
    exit 1
fi
if command -v timeout >/dev/null 2>&1; then
    timeout 20 git -C "$repo_dir" pull --ff-only
else
    git -C "$repo_dir" pull --ff-only
fi
exec "$repo_dir/install.sh" "$@"
