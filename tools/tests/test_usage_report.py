import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import usage_report


class UsageReportTests(unittest.TestCase):
    def test_resumed_cumulative_usage_becomes_incremental(self):
        records = [
            {
                "call_id": "call-1",
                "session_id": "session-1",
                "role": "writer",
                "operation": "write.draft",
                "chapter": "vol-1-ch-1",
                "usage_mode": "cumulative",
                "cumulative_usage": {"input_tokens": 100, "output_tokens": 20, "reasoning_tokens": 10},
            },
            {
                "call_id": "call-2",
                "session_id": "session-1",
                "role": "writer",
                "operation": "write.draft",
                "chapter": "vol-1-ch-1",
                "usage_mode": "cumulative",
                "cumulative_usage": {"input_tokens": 160, "output_tokens": 32, "reasoning_tokens": 14},
                "retried": True,
                "artifact_valid": True,
                "input_hashes": {"prompt": "abc"},
            },
        ]

        normalized, warnings = usage_report.normalize(records)
        report = usage_report.aggregate(normalized)

        self.assertEqual(warnings, [])
        self.assertEqual(report["total"], {"input_tokens": 160, "output_tokens": 32, "reasoning_tokens": 14})
        self.assertEqual(report["retried_records"], 1)
        self.assertEqual(report["valid_artifacts"], 1)
        self.assertEqual(normalized[1]["input_hashes"], {"prompt": "abc"})

    def test_exact_duplicate_record_is_skipped(self):
        record = {
            "event_id": "event-1",
            "call_id": "call-1",
            "role": "reader",
            "operation": "edit.review",
            "usage": {"input_tokens": 10, "output_tokens": 4, "reasoning_tokens": 2},
        }

        normalized, warnings = usage_report.normalize([record, dict(record)])

        self.assertEqual(len(normalized), 1)
        self.assertTrue(any("duplicate record skipped" in warning for warning in warnings))

    def test_json_input_and_markdown_output(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "usage.json"
            path.write_text(json.dumps({"records": [{"role": "writer", "usage": {"input_tokens": 1}}]}), encoding="utf-8")
            records = usage_report.read_records([path])
            normalized, warnings = usage_report.normalize(records)
            rendered = usage_report.markdown(usage_report.aggregate(normalized), warnings)

            self.assertIn("total tokens: 1", rendered)
            self.assertIn("writer", rendered)


if __name__ == "__main__":
    unittest.main()
