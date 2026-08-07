import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import prompt_lint


CONTRACT_4 = """---
prompt_contract: 4
chapter: vol-1-ch-2
act: vol-1-act-1
preceding_source: drafts/vol-1-ch-1.md
preceding_hash: {source_hash}
---

## 前情上下文
门口的灯刚灭，桌上留下半枚铜钱。

## 本章故事
他必须在天亮前作出选择，阻力来自那封没有署名的信。

## 角色初始状态
沈砚在门内，知道信的存在但不知道来处。

## 人物动机与情绪
他想保住母亲，压力逼他承认自己误判了对手。

## 场景展开
试探从一件物证开始，行动、反制、选择和余波逐步落地。

## 必守事实与边界
- 信息差变化：沈砚知道铜钱来历，周执不知。
- 必须发生：他带着铜钱离开。
- 相关事实：信件内容保持不变。
- 保留边界：不得提前揭示幕后者。
"""

CONTRACT_5 = """---
prompt_contract: 5
chapter: vol-1-ch-3
act: vol-1-act-1
preceding_source: 幕纲 start_state
---

## 承接与初始状态
雨停在檐角，沈砚手里仍攥着铜钱。

## 本章变化
他从试探转为主动设局，代价是暴露行踪。

## 场景卡
入场、阻力、反制、选择和可见结果各有动作。

## 人物动机和信息差
沈砚知道信的来处，周执只知道有人在查。

## 硬边界与收束画面
不得改写铜钱来历；他在渡口收起染血的袖口。
"""


class PromptLintTests(unittest.TestCase):
    def test_contract_4_with_matching_source_hash_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "drafts" / "vol-1-ch-1.md"
            source.parent.mkdir()
            source.write_text("上一章真实正文。", encoding="utf-8")
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            prompt = root / "prompt.md"
            prompt.write_text(CONTRACT_4.format(source_hash=digest), encoding="utf-8")

            result = prompt_lint.lint_prompt(prompt, root)

            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["errors"], [])

    def test_contract_5_uses_experimental_five_block_shape(self):
        with tempfile.TemporaryDirectory() as directory:
            prompt = Path(directory) / "prompt.md"
            prompt.write_text(CONTRACT_5, encoding="utf-8")

            result = prompt_lint.lint_prompt(prompt, Path(directory))

            self.assertEqual(result["status"], "PASS")

    def test_missing_placeholder_forbidden_and_hash_mismatch_are_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "drafts" / "vol-1-ch-1.md"
            source.parent.mkdir()
            source.write_text("changed", encoding="utf-8")
            prompt = root / "prompt.md"
            body = CONTRACT_4.format(source_hash="0" * 64)
            body = body.replace("## 场景展开", "## 场景展开\n这一段不是测试，而是禁句式。\n{未填占位符}")
            duplicate = "这是一段足够长的重复片段用于确定性重复检查测试并验证警告输出。"
            body = body.replace("保留边界：不得提前揭示幕后者。", "保留边界：不得提前揭示幕后者。\n" + duplicate + "\n" + duplicate)
            prompt.write_text(body, encoding="utf-8")

            result = prompt_lint.lint_prompt(prompt, root)

            self.assertEqual(result["status"], "FAIL")
            joined = "\n".join(result["errors"])
            self.assertIn("hash mismatch", joined)
            self.assertIn("unresolved placeholders", joined)
            self.assertIn("forbidden contrast syntax", joined)
            self.assertTrue(result["warnings"])

    def test_numeric_and_date_formats_are_checked_deterministically(self):
        with tempfile.TemporaryDirectory() as directory:
            prompt = Path(directory) / "prompt.md"
            text = CONTRACT_5.replace("preceding_source: 幕纲 start_state", "preceding_source: 幕纲 start_state\ntarget_chars: many")
            text = text.replace("雨停在檐角", "雨停在 2026-02-31")
            prompt.write_text(text, encoding="utf-8")

            result = prompt_lint.lint_prompt(prompt, Path(directory))
            joined = "\n".join(result["errors"])

            self.assertIn("numeric frontmatter field is invalid", joined)
            self.assertIn("invalid date", joined)


if __name__ == "__main__":
    unittest.main()
