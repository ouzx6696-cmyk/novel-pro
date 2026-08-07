#!/usr/bin/env python3
"""Persist task-local chapter deltas without creating a long-term state store.

The input and output use JSON, which is valid YAML 1.2. Only the top-level
orchestrator should run this tool because it writes under ``.agent/tasks``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True


REQUIRED_FIELDS = (
    "chapter",
    "source_path",
    "character_changes",
    "information_state",
    "timeline_changes",
    "foreshadowing_changes",
    "setting_notifications",
    "chapter_end_state_deviations",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("delta input must be a JSON object")
    return value


def resolve_source(project_root: Path, value: str) -> Path:
    source = Path(value)
    if not source.is_absolute():
        source = project_root / source
    source = source.resolve()
    try:
        source.relative_to(project_root.resolve())
    except ValueError as exc:
        raise ValueError(f"source_path must stay inside project root: {source}") from exc
    if not source.is_file():
        raise ValueError(f"source_path does not exist: {source}")
    return source


def normalize_delta(project_root: Path, raw: dict) -> dict:
    missing = [field for field in REQUIRED_FIELDS if field not in raw]
    if missing:
        raise ValueError("missing delta fields: " + ", ".join(missing))
    source = resolve_source(project_root, str(raw["source_path"]))
    actual_hash = sha256_file(source)
    expected_hash = str(raw.get("source_hash") or "")
    if expected_hash and expected_hash != actual_hash:
        raise ValueError("source_hash does not match source_path")
    value = dict(raw)
    value["source_path"] = source.relative_to(project_root.resolve()).as_posix()
    value["source_hash"] = actual_hash
    return value


def load_ledger(path: Path, contract_key: str) -> dict:
    if not path.is_file():
        return {contract_key: 1, "chapters": {}}
    value = read_json(path)
    if not isinstance(value.get("chapters"), dict):
        raise ValueError(f"invalid chapter delta ledger: {path}")
    value.setdefault(contract_key, 1)
    return value


def write_json_atomic(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def upsert_delta(project_root: Path, task_id: str, raw: dict) -> tuple[Path, Path]:
    root = project_root.resolve()
    delta = normalize_delta(root, raw)
    task_root = root / ".agent" / "tasks" / task_id
    delta_path = task_root / "chapter-delta.yaml"
    working_path = task_root / "working-state.yaml"

    ledger = load_ledger(delta_path, "delta_contract")
    ledger["chapters"][str(delta["chapter"])] = delta
    write_json_atomic(delta_path, ledger)

    working = load_ledger(working_path, "working_state_contract")
    working["chapters"][str(delta["chapter"])] = delta
    working["latest_chapter"] = str(delta["chapter"])
    write_json_atomic(working_path, working)
    return delta_path, working_path


def check_ledger(project_root: Path, path: Path) -> list[str]:
    root = project_root.resolve()
    ledger = read_json(path)
    problems = []
    for chapter, delta in ledger.get("chapters", {}).items():
        try:
            source = resolve_source(root, str(delta.get("source_path", "")))
        except ValueError as exc:
            problems.append(f"{chapter}: {exc}")
            continue
        if sha256_file(source) != str(delta.get("source_hash", "")):
            problems.append(f"{chapter}: source hash mismatch")
    return problems


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Persist or verify task-local novel-pro chapter deltas")
    sub = parser.add_subparsers(dest="command", required=True)
    upsert = sub.add_parser("upsert")
    upsert.add_argument("project_root", type=Path)
    upsert.add_argument("task_id")
    upsert.add_argument("delta", type=Path, help="JSON object containing the chapter delta")
    check = sub.add_parser("check")
    check.add_argument("project_root", type=Path)
    check.add_argument("ledger", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "upsert":
            delta_path, working_path = upsert_delta(args.project_root, args.task_id, read_json(args.delta))
            print(delta_path)
            print(working_path)
            return 0
        ledger = args.ledger if args.ledger.is_absolute() else args.project_root / args.ledger
        problems = check_ledger(args.project_root, ledger)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print("PASS" if not problems else "STALE")
    for problem in problems:
        print(f"  - {problem}")
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
