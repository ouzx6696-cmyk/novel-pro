import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import state_delta


def delta(chapter, source_path):
    return {
        "chapter": chapter,
        "source_path": source_path,
        "character_changes": {"沈砚": "从犹豫到行动"},
        "information_state": {"沈砚": {"knows": ["铜钱"], "unknown": ["来处"], "misjudges": []}},
        "timeline_changes": ["雨停"],
        "foreshadowing_changes": ["铜钱推进"],
        "setting_notifications": {"fulfilled": [], "pending": []},
        "chapter_end_state_deviations": [],
    }


class StateDeltaTests(unittest.TestCase):
    def test_same_chapter_upsert_replaces_previous_delta(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "drafts" / "vol-1-ch-1.md"
            source.parent.mkdir()
            source.write_text("首稿", encoding="utf-8")
            first, working = state_delta.upsert_delta(root, "task-1", delta("vol-1-ch-1", "drafts/vol-1-ch-1.md"))
            source.write_text("返修后的首稿", encoding="utf-8")
            state_delta.upsert_delta(root, "task-1", delta("vol-1-ch-1", "drafts/vol-1-ch-1.md"))

            ledger = state_delta.read_json(first)
            self.assertEqual(len(ledger["chapters"]), 1)
            self.assertEqual(ledger["chapters"]["vol-1-ch-1"]["source_hash"], state_delta.sha256_file(source))
            self.assertTrue(working.is_file())
            self.assertEqual(state_delta.check_ledger(root, first), [])

    def test_source_hash_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "draft.md"
            source.write_text("正文", encoding="utf-8")
            value = delta("vol-1-ch-1", "draft.md")
            value["source_hash"] = "0" * 64

            with self.assertRaises(ValueError):
                state_delta.normalize_delta(root, value)


if __name__ == "__main__":
    unittest.main()
