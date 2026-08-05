# 局部编辑边界

本模块是 anti-AI 与 completion-editor 共用的局部编辑权威边界。anti-AI 在编辑模式中先于 `edit.anti-ai` 阶段全量扫描本章正文产出表达报告（不改正文），再于 `edit.repair` 阶段按 `edit.synthesize` 整体返修意见中归为中等/轻微的**表达类**问题产出局部候选；两种情形下都只处理有正文证据、边界清楚的问题，不自行扩大任务范围。completion-editor 仍只处理显式 `completion.revise` 中被分流为 `EDIT` 的局部问题。

- 不得新增场景、线索、回忆、心理、环境、设定、伏笔、笑点或字数。
- 不得改变剧情、人物选择、人物动机、POV、信息顺序、人物声线或章末状态。
- 不处理跨章事实、核心因果、场景骨架、Prompt 或规划问题；这些问题返回顶层并进入 `REGENERATE` 或对应上游角色。
- 不做词频、密度、AI 味评分或统一润色。边界无法确认时保留原文，交 Reader 整体复读。

anti-AI 在编辑模式里分两个阶段：报告阶段（`edit.anti-ai`）全量扫描产出 Anti-AI 报告，不动文；编辑阶段（`edit.repair`）按整体返修意见处理表达类问题，输出完整候选。completion-editor 只处理显式 `completion.revise` 中被分流为 `EDIT` 的局部表达、可信度、连续性或清晰度问题。两者都不直接提交 `texts/`。
