import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import runtime_manifest


ROOT = Path(__file__).resolve().parents[2]


class RegressionTests(unittest.TestCase):
    def test_runtime_and_skill_versions_are_unchanged(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        manifest = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
        story = (ROOT / "templates" / "story.md").read_text(encoding="utf-8")

        self.assertRegex(skill, r'version:\s*"0\.3\.0-pro"')
        self.assertEqual(manifest["version"], "0.3.0-pro")
        self.assertRegex(story, r"skill_version\*\*:\s*5\.3")
        self.assertRegex(story, r"runtime_profile\*\*:\s*novel-pro-0\.3")

    def test_new_tools_are_on_runtime_manifest(self):
        entries = {path.name for path in ROOT.glob("tools/*.py")}
        manifest_names = set(runtime_manifest.PROJECT_TOOL_FILES)

        self.assertTrue({"context_cache.py", "prompt_lint.py", "usage_report.py"} <= manifest_names)
        self.assertTrue(manifest_names <= entries)

    def test_runtime_manifest_sources_exist(self):
        missing = [str(source) for source, _target, _kind in runtime_manifest.runtime_entries(ROOT) if not source.is_file()]
        self.assertEqual(missing, [])

    def test_writer_and_return_contracts_keep_artifact_first_recovery(self):
        writer = (ROOT / "agents" / "writer.md").read_text(encoding="utf-8")
        returns = (ROOT / "skills" / "agent-return-spec.md").read_text(encoding="utf-8")

        self.assertIn("产物优先恢复", writer)
        self.assertIn("自动重派一次", writer)
        self.assertIn("不在返回消息中回显正文", writer)
        self.assertIn("cumulative", returns)
        self.assertIn("input_hash", returns)


if __name__ == "__main__":
    unittest.main()
