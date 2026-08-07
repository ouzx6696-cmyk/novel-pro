import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import context_cache


class ContextCacheTests(unittest.TestCase):
    def test_act_cache_hash_match_then_stale_after_source_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "acts" / "vol-1-act-1.md"
            source.parent.mkdir()
            source.write_text("幕纲稳定资料", encoding="utf-8")

            cache = context_cache.write_cache(root, ".agent/cache/vol-1-act-1-act-pack.md", "act", "vol-1-act-1", ["acts/vol-1-act-1.md"])
            ok, problems = context_cache.check_cache(root, cache)
            self.assertTrue(ok, problems)

            source.write_text("幕纲稳定资料已变化", encoding="utf-8")
            ok, problems = context_cache.check_cache(root, cache)
            self.assertFalse(ok)
            self.assertTrue(any("hash mismatch" in problem for problem in problems))

    def test_profile_and_chapter_targets_follow_runtime_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "settings" / "writing-style.md"
            source.parent.mkdir()
            source.write_text("稳定文风", encoding="utf-8")

            profile = context_cache.write_cache(root, ".agent/cache/writer-profile.md", "writer", "writer-profile", ["settings/writing-style.md"])
            chapter = context_cache.write_cache(root, ".agent/tasks/task-1/chapter-context.yaml", "chapter", "task-1", ["settings/writing-style.md"])

            self.assertTrue(profile.is_file())
            self.assertTrue(chapter.is_file())
            self.assertTrue(chapter.as_posix().endswith(".agent/tasks/task-1/chapter-context.yaml"))
            self.assertTrue(context_cache.check_cache(root, profile)[0])
            self.assertTrue(context_cache.check_cache(root, chapter)[0])

    def test_missing_cache_is_compatible_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            ok, problems = context_cache.check_cache(Path(directory), Path(".agent/cache/absent.md"))

            self.assertFalse(ok)
            self.assertIn("cache does not exist", problems[0])


if __name__ == "__main__":
    unittest.main()
