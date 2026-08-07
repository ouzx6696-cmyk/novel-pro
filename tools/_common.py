#!/usr/bin/env python3
"""Small stdlib helpers shared by source-side tools."""

import sys
from pathlib import Path

sys.dont_write_bytecode = True


def read_text(path):
    path = Path(path)
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise SystemExit(f"文件不是有效的 UTF-8，请先修复编码：{path} ({exc})")


def is_relative_to(path, parent):
    try:
        Path(path).resolve().relative_to(Path(parent).resolve())
        return True
    except (ValueError, TypeError, OSError):
        return False


# These source-side helpers intentionally use a looser root threshold and take
# a story file path. The deployed sync tool keeps stricter local copies because
# project runtimes do not receive _common.py.
SKILL_MARKERS = ("SKILL.md", "skill.json", "agents", "skills", "knowledge", "tools")


def looks_like_skill_root(path, min_markers=4):
    path = Path(path)
    return path.is_dir() and sum((path / marker).exists() for marker in SKILL_MARKERS) >= min_markers
