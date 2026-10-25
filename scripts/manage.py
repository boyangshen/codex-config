#!/usr/bin/env python3
"""Install portable preferences and skill links without exporting host state."""
import argparse
import copy
import datetime
import json
import math
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile

try:
    import tomllib
except ImportError:
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / 'codex' / 'shared-config.toml'
SAFE_PATHS = (
    ('model',), ('model_reasoning_effort',), ('plan_mode_reasoning_effort',),
    ('service_tier',), ('model_context_window',), ('model_auto_compact_token_limit',),
    ('approvals_reviewer',), ('tui', 'theme'), ('tui', 'fullscreen_transcript'),
    ('tui', 'presets'),
)


def get_path(data, path):
    for key in path:
        if not isinstance(data, dict) or key not in data:
            raise KeyError(path)
        data = data[key]
    return data


def set_path(data, path, value):
    for key in path[:-1]:
        data = data.setdefault(key, {})
        if not isinstance(data, dict):
            raise ValueError('配置表类型不兼容')
    data[path[-1]] = copy.deepcopy(value)


def select_portable(data):
    selected = {}
    for path in SAFE_PATHS:
        try:
            value = get_path(data, path)
        except KeyError:
            continue
        set_path(selected, path, value)
    return selected


def flatten(data, prefix=()):
    for key, value in data.items():
        path = prefix + (key,)
        if isinstance(value, dict):
            yield from flatten(value, path)
        else:
            yield path, value


def key_text(key):
    return key if re.fullmatch(r'[A-Za-z0-9_-]+', key) else json.dumps(key, ensure_ascii=False)


def value_text(value):
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float) and math.isfinite(value):
        return repr(value)
    if isinstance(value, list):
        return '[' + ', '.join(value_text(v) for v in value) + ']'
    if isinstance(value, dict):
        return '{' + ', '.join(key_text(k) + ' = ' + value_text(v) for k, v in value.items()) + '}'
    raise ValueError('不支持的可迁移配置类型：' + type(value).__name__)


def render(data):
    sections = {}
    for path, value in flatten(data):
        sections.setdefault(path[:-1], []).append(key_text(path[-1]) + ' = ' + value_text(value))
    chunks = []
    for section, values in sections.items():
        header = ['[' + '.'.join(map(key_text, section)) + ']'] if section else []
        chunks.append('\n'.join(header + values))
    return '\n\n'.join(chunks) + '\n'


def parsed_header(line):
    match = re.fullmatch(r'\s*(\[[^\n]+\])\s*(?:#.*)?', line.rstrip('\n'))
    if not match:
        return None
    header = match.group(1)
    if header.startswith('[['):
        return ('__array_table__',)
    tree = tomllib.loads(header + '\n__config_probe__ = true\n')
    path = []
    while '__config_probe__' not in tree:
        if len(tree) != 1:
            raise ValueError('无法识别配置表头')
        key, tree = next(iter(tree.items()))
        path.append(key)
    return tuple(path)


def merge_text(original, shared):
    """Preserve unrelated text; reject unsupported layouts before any writes."""
    before = tomllib.loads(original)
    desired = dict(flatten(shared))
    pending = dict(desired)
    section = ()
    headers = {}
    lines = original.splitlines(keepends=True)
    if lines and not lines[-1].endswith('\n'):
        lines[-1] += '\n'
    for index, line in enumerate(lines):
        header = parsed_header(line)
        if header is not None:
            section = header
            headers[section] = index
            continue
        match = re.match(r'^\s*([A-Za-z0-9_-]+|"(?:[^"\\]|\\.)*")\s*=', line)
        if not match:
            continue
        key = match.group(1)
        key = json.loads(key) if key.startswith('"') else key
        path = section + (key,)
        if path in pending:
            lines[index] = key_text(key) + ' = ' + value_text(pending.pop(path)) + '\n'
    inserts = {}
    append = []
    prefix = []
    grouped = {}
    for path, value in pending.items():
        grouped.setdefault(path[:-1], []).append(key_text(path[-1]) + ' = ' + value_text(value) + '\n')
    for path, values in grouped.items():
        if not path:
            prefix.extend(values)
        elif path in headers:
            inserts.setdefault(headers[path], []).extend(values)
        else:
            append.extend(['\n[' + '.'.join(map(key_text, path)) + ']\n', *values])
    result = prefix[:]
    for index, line in enumerate(lines):
        result.append(line)
        result.extend(inserts.get(index, []))
    result.extend(append)
    result = ''.join(result)
    expected = copy.deepcopy(before)
    for path, value in desired.items():
        set_path(expected, path, value)
    try:
        after = tomllib.loads(result)
    except Exception as exc:
        raise ValueError('本机 TOML 布局无法安全合并；原配置未修改') from exc
    if after != expected:
        raise ValueError('配置合并会影响未管理字段；原配置未修改')
    return result


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.' + path.name, delete=False) as f:
        f.write(text.encode())
        temporary = Path(f.name)
    os.chmod(temporary, 0o600)
    os.replace(temporary, path)


def install(home, dry_run=False):
    shared = tomllib.loads(SHARED.read_text())
    if select_portable(shared) != shared:
        raise ValueError('shared-config.toml 含不允许同步的字段')
    config = home / '.codex' / 'config.toml'
    original = config.read_text() if config.exists() else ''
    merged = merge_text(original, shared)
    links = []
    for skill in sorted((ROOT / 'skills').iterdir()):
        if skill.is_dir() and (skill / 'SKILL.md').is_file():
            for directory in (home / '.codex/skills', home / '.agents/skills'):
                links.append((directory / skill.name, skill))
    links.append((home / '.local/bin/codex-personal', ROOT / 'bin/codex-personal'))
    pending = [(p, t) for p, t in links if not (p.is_symlink() and p.resolve() == t.resolve())]
    changes = [str(p) for p, _ in pending]
    if original != merged:
        changes.append(str(config))
    if dry_run:
        print('计划更新：\n' + '\n'.join(changes) if changes else '已是最新，无需修改。')
        return
    backup = None
    def backup_path(path):
        nonlocal backup
        if backup is None:
            parent = home / '.codex' / 'backups' / 'codex-config'
            parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            backup = Path(tempfile.mkdtemp(prefix=datetime.datetime.now().strftime('%Y%m%d-%H%M%S-'), dir=parent))
        target = backup / path.relative_to(home)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(target))
    if original != merged:
        if config.exists() or config.is_symlink():
            backup_path(config)
        atomic_write(config, merged)
    for path, target in pending:
        if path.exists() or path.is_symlink():
            backup_path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(target, target_is_directory=target.is_dir())
    state_home = Path(os.environ.get('XDG_STATE_HOME', str(home / '.local/state'))) if home == Path.home() else home / '.local/state'
    atomic_write(state_home / 'codex-config/python', sys.executable + '\n')
    print('已安装：配置已合并，skills 与 codex-personal 已链接。')
    if backup:
        print('原有文件备份：' + str(backup))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['install', 'capture'])
    parser.add_argument('--home', type=Path, default=Path.home())
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if args.mode == 'capture':
        source = args.home / '.codex/config.toml'
        selected = select_portable(tomllib.loads(source.read_text()))
        atomic_write(SHARED, '# Portable preferences only; machine-local state is excluded.\n' + render(selected))
        print('已更新可迁移设置；请检查 git diff 后再提交。')
    else:
        install(args.home.expanduser().resolve(), args.dry_run)


if __name__ == '__main__':
    main()
