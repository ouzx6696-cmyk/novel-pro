#!/usr/bin/env python3
"""Deterministic checks for chapter Prompt files.

This tool validates structure and traceability only. It does not judge
literary quality, AI style, character quality, or whether a scene is moving.
Those remain reading responsibilities.
"""

from __future__ import annotations

import argparse
import datetime as _datetime
import hashlib
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True


REQUIRED_FIELDS = ("prompt_contract", "chapter", "act", "preceding_source")
CONTRACT_SECTIONS = {
    "4": (
        "前情上下文",
        "本章故事",
        "角色初始状态",
        "人物动机与情绪",
        "场景展开",
        "必守事实与边界",
    ),
    "5": (
        "承接与初始状态",
        "本章变化",
        "场景卡",
        "人物动机和信息差",
        "硬边界与收束画面",
    ),
}
CHAPTER_RE = re.compile(r"^vol-\d+-ch-\d+$")
ACT_RE = re.compile(r"^vol-\d+-act-\d+$")
PLACEHOLDER_RE = re.compile(r"(?<!\\)\{[^{}\r\n]{1,200}\}")
FORBIDDEN_CONTRAST_RE = re.compile(r"不是[^。！？\n]{0,60}[，,]\s*(?:而)?是")
DATE_RE = re.compile(r"\b(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})日?\b")
NUMERIC_FIELDS = ("target_chars", "min_chars", "target_words", "min_words")
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n", text, re.DOTALL)
    if not match:
        return {}, text
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip("'\"")
    return values, text[match.end() :]


def section_names(body: str) -> list[str]:
    return [match.group(1).strip() for match in SECTION_RE.finditer(body)]


def normalized_lines(body: str) -> list[str]:
    lines = []
    for raw in body.splitlines():
        value = re.sub(r"\s+", "", raw.strip())
        value = value.replace("。", "").replace("，", "").replace(",", "")
        if len(value) >= 24 and not value.startswith("#"):
            lines.append(value)
    return lines


def lint_prompt(path: Path, source_root: Path | None = None) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    text = path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(text)

    if not frontmatter:
        errors.append("missing or malformed YAML frontmatter")
    for field in REQUIRED_FIELDS:
        if not frontmatter.get(field):
            errors.append(f"missing frontmatter field: {field}")

    contract = frontmatter.get("prompt_contract", "")
    if contract and contract not in {"4", "5"}:
        errors.append(f"unsupported prompt_contract: {contract}")

    chapter = frontmatter.get("chapter", "")
    if chapter and not CHAPTER_RE.fullmatch(chapter):
        errors.append(f"invalid chapter identifier: {chapter}")

    act = frontmatter.get("act", "")
    if act and not ACT_RE.fullmatch(act):
        errors.append(f"invalid act identifier: {act}")

    for field in NUMERIC_FIELDS:
        value = frontmatter.get(field, "")
        if value and not value.isdigit():
            errors.append(f"numeric frontmatter field is invalid: {field}")

    invalid_dates = []
    for year, month, day in DATE_RE.findall(body):
        try:
            _datetime.date(int(year), int(month), int(day))
        except ValueError:
            invalid_dates.append(f"{year}-{month}-{day}")
    if invalid_dates:
        errors.append("invalid date(s): " + ", ".join(invalid_dates[:8]))

    sections = section_names(body)
    required_sections = CONTRACT_SECTIONS.get(contract, CONTRACT_SECTIONS["4"])
    missing = [name for name in required_sections if name not in sections]
    if missing:
        errors.append("missing sections: " + ", ".join(missing))
    present_order = [name for name in sections if name in required_sections]
    expected_order = [name for name in required_sections if name in present_order]
    if present_order != expected_order:
        errors.append("required sections are out of order")

    placeholders = sorted(set(PLACEHOLDER_RE.findall(body)))
    if placeholders:
        errors.append("unresolved placeholders: " + ", ".join(placeholders[:8]))
        if len(placeholders) > 8:
            errors.append(f"and {len(placeholders) - 8} more placeholders")

    forbidden = [line.strip() for line in body.splitlines() if FORBIDDEN_CONTRAST_RE.search(line)]
    if forbidden:
        errors.append(f"forbidden contrast syntax found in {len(forbidden)} line(s)")

    source = frontmatter.get("preceding_source", "")
    if source and source != "幕纲 start_state" and source_root:
        source_path = Path(source)
        if not source_path.is_absolute():
            source_path = source_root / source_path
        if not source_path.is_file():
            errors.append(f"preceding_source does not exist: {source}")
        else:
            expected_hash = frontmatter.get("preceding_hash", "") or frontmatter.get("source_hash", "")
            if expected_hash:
                actual_hash = sha256_file(source_path)
                if actual_hash != expected_hash:
                    errors.append(f"preceding_source hash mismatch: {source}")
            else:
                warnings.append("preceding_source hash is not recorded")

    duplicate_lines = []
    seen: dict[str, int] = {}
    for line in normalized_lines(body):
        seen[line] = seen.get(line, 0) + 1
    for line, count in seen.items():
        if count > 1:
            duplicate_lines.append(line[:80])
    if duplicate_lines:
        warnings.append(f"duplicate normalized content: {len(duplicate_lines)} fragment(s)")

    return {
        "path": str(path),
        "status": "FAIL" if errors else "WARN" if warnings else "PASS",
        "errors": errors,
        "warnings": warnings,
        "sections": sections,
        "frontmatter": frontmatter,
        "checks": {
            "structure": not missing and present_order == expected_order,
            "placeholder_free": not placeholders,
            "forbidden_syntax_free": not forbidden,
            "source_traceable": not any("preceding_source" in item for item in errors),
            "duplicate_fragments": len(duplicate_lines),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lint a novel-pro chapter Prompt")
    parser.add_argument("prompt", type=Path)
    parser.add_argument("--source-root", type=Path, help="project root used to resolve preceding_source")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    parser.add_argument("--strict-warnings", action="store_true", help="return non-zero when warnings exist")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = args.prompt.resolve()
    if not path.is_file():
        print(f"prompt file does not exist: {path}", file=sys.stderr)
        return 2
    try:
        result = lint_prompt(path, args.source_root.resolve() if args.source_root else None)
    except UnicodeDecodeError as exc:
        print(f"prompt is not valid UTF-8: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"{result['status']}: {result['path']}")
        for item in result["errors"]:
            print(f"  error: {item}")
        for item in result["warnings"]:
            print(f"  warning: {item}")
    if result["errors"] or (args.strict_warnings and result["warnings"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
