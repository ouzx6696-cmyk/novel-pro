#!/usr/bin/env python3
"""Aggregate per-call Agent usage records without double counting resumes."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.dont_write_bytecode = True


USAGE_FIELDS = ("input_tokens", "output_tokens", "reasoning_tokens")


def read_records(paths: list[Path]) -> list[dict]:
    records: list[dict] = []
    for path in paths:
        if not path.is_file():
            raise SystemExit(f"usage input does not exist: {path}")
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            value = []
            for index, line in enumerate(text.splitlines(), 1):
                if not line.strip():
                    continue
                try:
                    value.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise SystemExit(f"invalid JSON on {path}:{index}: {exc}") from exc
        if isinstance(value, dict):
            value = value.get("records", [value])
        if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
            raise SystemExit(f"usage input must be a JSON object/list or JSONL: {path}")
        records.extend(value)
    return records


def numeric(value) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def usage_map(raw) -> dict[str, int]:
    if not isinstance(raw, dict):
        raw = {}
    return {field: numeric(raw.get(field)) for field in USAGE_FIELDS}


def event_key(record: dict, index: int) -> str:
    if record.get("event_id"):
        return str(record["event_id"])
    payload = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest() + f":{index}"


def normalize(records: list[dict]) -> tuple[list[dict], list[str]]:
    output: list[dict] = []
    warnings: list[str] = []
    seen_payloads: set[str] = set()
    cumulative_seen: dict[str, dict[str, int]] = {}

    for index, record in enumerate(records):
        payload = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        if payload in seen_payloads:
            warnings.append(f"duplicate record skipped at input index {index}")
            continue
        seen_payloads.add(payload)

        if not record.get("call_id"):
            warnings.append(f"missing call_id at input index {index}; generated fallback id")
        call_id = str(record.get("call_id") or f"input-{index}")
        session_id = str(record.get("session_id") or "")
        mode = str(record.get("usage_mode") or "delta").lower()
        if mode == "cumulative" or record.get("cumulative_usage") is not None:
            cumulative = usage_map(record.get("cumulative_usage"))
            # Resumed calls normally receive fresh call_ids but keep one
            # session_id. Accumulate against the session to avoid double counting.
            cumulative_key = session_id or call_id
            previous = cumulative_seen.get(cumulative_key, {field: 0 for field in USAGE_FIELDS})
            delta = {field: cumulative[field] - previous[field] for field in USAGE_FIELDS}
            if any(value < 0 for value in delta.values()):
                warnings.append(f"cumulative usage decreased for {cumulative_key}; current values treated as delta")
                delta = cumulative
            cumulative_seen[cumulative_key] = cumulative
        else:
            delta = usage_map(record.get("usage", record))

        output.append(
            {
                "event_id": event_key(record, index),
                "call_id": call_id,
                "parent_call_id": record.get("parent_call_id", ""),
                "session_id": session_id,
                "role": record.get("role", "unknown"),
                "operation": record.get("operation", "unknown"),
                "chapter": record.get("chapter", ""),
                "attempt": numeric(record.get("attempt", 1)),
                "status": record.get("status", "unknown"),
                "artifact": record.get("artifact", ""),
                "retry_of": record.get("retry_of", ""),
                "usage_mode": "cumulative" if mode == "cumulative" or record.get("cumulative_usage") is not None else "delta",
                "retried": bool(record.get("retried", record.get("retry", False))),
                "artifact_valid": bool(record.get("artifact_valid", record.get("valid_artifact", False))),
                "input_hashes": record.get("input_hashes", record.get("input_file_hashes", {})) or {},
                "usage": delta,
            }
        )
    return output, warnings


def aggregate(records: list[dict]) -> dict:
    total = {field: 0 for field in USAGE_FIELDS}
    by_role = defaultdict(lambda: {field: 0 for field in USAGE_FIELDS})
    by_operation = defaultdict(lambda: {field: 0 for field in USAGE_FIELDS})
    by_chapter = defaultdict(lambda: {field: 0 for field in USAGE_FIELDS})
    for record in records:
        for field in USAGE_FIELDS:
            value = record["usage"][field]
            total[field] += value
            by_role[str(record["role"])][field] += value
            by_operation[str(record["operation"])][field] += value
            chapter = str(record["chapter"] or "unassigned")
            by_chapter[chapter][field] += value
    retried = sum(1 for record in records if record["retried"])
    valid_artifacts = sum(1 for record in records if record["artifact_valid"])
    return {
        "records": len(records),
        "events": records,
        "total": total,
        "retried_records": retried,
        "valid_artifacts": valid_artifacts,
        "by_role": dict(by_role),
        "by_operation": dict(by_operation),
        "by_chapter": dict(by_chapter),
    }


def total_tokens(values: dict[str, int]) -> int:
    return sum(values.values())


def markdown(report: dict, warnings: list[str]) -> str:
    total = total_tokens(report["total"])
    lines = [
        "# Usage Report",
        "",
        f"- normalized records: {report['records']}",
        f"- total tokens: {total}",
        f"- input tokens: {report['total']['input_tokens']}",
        f"- output tokens: {report['total']['output_tokens']}",
        f"- reasoning tokens: {report['total']['reasoning_tokens']}",
        f"- retried records: {report['retried_records']}",
        f"- records with valid artifacts: {report['valid_artifacts']}",
        "",
        "## By Role",
        "",
        "| role | total | input | output | reasoning | share |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for role, values in sorted(report["by_role"].items()):
        value = total_tokens(values)
        share = (value / total * 100) if total else 0
        lines.append(f"| {role} | {value} | {values['input_tokens']} | {values['output_tokens']} | {values['reasoning_tokens']} | {share:.1f}% |")
    lines.extend(["", "## By Operation", "", "| operation | total | share |", "|---|---:|---:|"])
    for operation, values in sorted(report["by_operation"].items()):
        value = total_tokens(values)
        share = (value / total * 100) if total else 0
        lines.append(f"| {operation} | {value} | {share:.1f}% |")
    if warnings:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in warnings)
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate novel-pro usage records")
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    records = read_records(args.inputs)
    normalized, warnings = normalize(records)
    report = aggregate(normalized)
    report["warnings"] = warnings
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n" if args.format == "json" else markdown(report, warnings)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
