#!/usr/bin/env python3
"""Create and validate optional derived context cache manifests.

The tool never edits story facts. It writes only derived manifests under
``.agent/cache`` or the current task's ``.agent/tasks/<task-id>`` directory and
records source hashes so a stale cache can be rejected before use. A semantic
summary may be filled by the top-level agent after the manifest is created
(act-pack), or by the prompt-crafter for task-local chapter context.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_records(project_root: Path, paths: list[str]) -> list[dict[str, str | int]]:
    records = []
    for value in paths:
        path = Path(value)
        if not path.is_absolute():
            path = project_root / path
        path = path.resolve()
        if not path.is_file():
            raise SystemExit(f"cache source does not exist: {value}")
        try:
            relative = path.relative_to(project_root.resolve()).as_posix()
        except ValueError as exc:
            raise SystemExit(f"cache source must be inside project root: {path}") from exc
        records.append(
            {
                "path": relative,
                "sha256": sha256_file(path),
                "chars": len(path.read_text(encoding="utf-8")),
            }
        )
    return records


def cache_header(cache_type: str, identity: str, records: list[dict]) -> str:
    generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    lines = [
        "---",
        "cache_contract: 1",
        f"cache_type: {cache_type}",
        f"identity: {identity}",
        "derived: true",
        "truth_source: project files listed below",
        f"generated_at: {generated}",
        "sources:",
    ]
    for record in records:
        lines.append(f"  - path: {record['path']}")
        lines.append(f"    sha256: {record['sha256']}")
        lines.append(f"    chars: {record['chars']}")
    lines.extend(["---", "", "## Semantic Summary", "", "<!-- top-level agent may fill this section (act-pack). Keep source paths and hashes intact. -->", ""])
    lines.extend(["## Cache Use", "", "This is a derived acceleration layer. If any source hash changes, reread the source files and rebuild this cache.", ""])
    lines.extend(["## Source Manifest", ""])
    for record in records:
        lines.append(f"- `{record['path']}` sha256=`{record['sha256']}` chars={record['chars']}")
    return "\n".join(lines) + "\n"


def chapter_cache_content(cache_type: str, identity: str, records: list[dict]) -> str:
    """Emit a small YAML manifest for the task-local chapter context."""
    lines = [
        "cache_contract: 1",
        f"cache_type: {cache_type}",
        f"identity: {identity}",
        "derived: true",
        "truth_source: project files listed below",
        "sources:",
    ]
    for record in records:
        lines.extend(
            [
                f"  - path: {record['path']}",
                f"    sha256: {record['sha256']}",
                f"    chars: {record['chars']}",
            ]
        )
    lines.extend(
        [
            "semantic_summary: ''",
            "cache_use: 'If any source hash changes, reread the source files.'",
        ]
    )
    return "\n".join(lines) + "\n"


def write_cache(project_root: Path, relative_path: str, cache_type: str, identity: str, sources: list[str]) -> Path:
    root = project_root.resolve()
    records = source_records(root, sources)
    target = root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    existing = target.read_text(encoding="utf-8") if target.is_file() else ""
    semantic = ""
    match = re.search(r"(?ms)^## Semantic Summary\s*\n(.*?)(?=^## Cache Use\s*$)", existing)
    if match:
        semantic = match.group(1).strip()
    content = chapter_cache_content(cache_type, identity, records) if target.suffix.lower() in {".yaml", ".yml"} else cache_header(cache_type, identity, records)
    if semantic and "<!-- top-level agent may fill" not in semantic:
        content = content.replace("<!-- top-level agent may fill this section (act-pack). Keep source paths and hashes intact. -->", semantic)
    target.write_text(content, encoding="utf-8")
    return target


def check_cache(project_root: Path, cache_path: Path) -> tuple[bool, list[str]]:
    root = project_root.resolve()
    if not cache_path.is_absolute():
        cache_path = root / cache_path
    if not cache_path.is_file():
        return False, [f"cache does not exist: {cache_path}"]
    text = cache_path.read_text(encoding="utf-8")
    problems = []
    manifests = re.findall(r"^- `([^`]+)` sha256=`([0-9a-f]+)`", text, re.MULTILINE)
    if not manifests:
        yaml_paths = re.findall(r"^\s*- path:\s*['\"]?([^'\"\r\n]+?)['\"]?\s*$", text, re.MULTILINE)
        yaml_hashes = re.findall(r"^\s*sha256:\s*['\"]?([0-9a-f]+)['\"]?\s*$", text, re.MULTILINE)
        if len(yaml_paths) != len(yaml_hashes):
            return False, [f"cache manifest is malformed: {len(yaml_paths)} paths vs {len(yaml_hashes)} hashes"]
        manifests = [(path_value.strip(), expected) for path_value, expected in zip(yaml_paths, yaml_hashes)]
    for path_value, expected in manifests:
        source = root / path_value
        if not source.is_file():
            problems.append(f"missing source: {path_value}")
        elif sha256_file(source) != expected:
            problems.append(f"hash mismatch: {path_value}")
    return not problems, problems


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build or verify optional novel-pro context caches")
    sub = parser.add_subparsers(dest="command", required=True)

    for name, cache_type, suffix in (
        ("build-act", "act", "act-pack.md"),
        ("build-profile", "writer", "writer-profile.md"),
        ("build-chapter", "chapter", "chapter-context.yaml"),
    ):
        command = sub.add_parser(name)
        command.set_defaults(cache_type=cache_type, suffix=suffix)
        command.add_argument("project_root", type=Path)
        command.add_argument("identity")
        command.add_argument("sources", nargs="+", help="project-relative source paths")

    verify = sub.add_parser("check")
    verify.add_argument("project_root", type=Path)
    verify.add_argument("cache", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "check":
        ok, problems = check_cache(args.project_root, args.cache)
        print("PASS" if ok else "STALE")
        for problem in problems:
            print(f"  - {problem}")
        return 0 if ok else 1

    project_root = args.project_root.resolve()
    if args.command == "build-chapter":
        target = project_root / ".agent" / "tasks" / args.identity / args.suffix
    elif args.command == "build-profile":
        target = project_root / ".agent" / "cache" / args.suffix
    else:
        target = project_root / ".agent" / "cache" / f"{args.identity}-{args.suffix}"
    output = write_cache(project_root, target.relative_to(project_root).as_posix(), args.cache_type, args.identity, args.sources)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
