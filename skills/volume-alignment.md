# Volume Alignment

整卷对齐只在作者明确要求时运行。它按叙事顺序检查尚未执行的幕纲、章纲和 Prompt 是否共同服务卷目标，并把修改交给拥有对应产物的角色。

`alignment` 只使用当前 order/task 记录范围，不改变长期 cursor，也不修改已接受 `texts/`。act-planner 只写幕产物，chapter-planner 只写章纲，prompt-crafter 只写 Prompt；顶层读过返回后再持久化报告和状态。

## 幕纲

act-planner 按幕检查 `start_state`、`dramatic_task`、冲突发展、人物与信息变化、continuity contract、`chapter_roles` 和 `end_state`。相邻幕接口在同一条卷内因果线上衔接。

## 章纲

chapter-planner 一次处理一幕，顺序复读该幕全部章纲。第一章承接幕起点，最后一章交付幕终点；人物选择、信息取得、能力资源、伏笔和唯一事件在幕内连续。

## Prompt

顺序链路下 Prompt 由 prompt-crafter **逐章创建**（前情取自上一章真实正文、角色初始状态取自状态文件），不存在批量节点。对齐任务按本章范围形成或修复 Prompt；对齐产生的 Prompt 修复仍需经过默认 `prompt.review` 审计（顺序链路默认步骤），不因对齐而跳过。

## 状态文件连续性检查

对齐时检查 `settings/character-setting/*.md` 的 `state_history`、`settings/timeline.md`、`settings/foreshadowing.md` 与已接受正文是否连续：

- `state_history` 缺失已验收章节的状态块（应同步而未同步）→ 漂移，列入重建清单（补 `state.update`）。
- 状态块的信息持有（知道/不知道/误判）与已接受正文矛盾 → 漂移，回告顶层核对。
- 时间线/伏笔台账与正文事实不符 → 以正文为准修正或回告。

状态文件是"当前状态"的真相源：它决定下一章 Prompt 的角色初始状态与信息差起点，漂移会直接污染后续创作。

## 正文之后

已接受正文提供已经发生的事实。正文终点与下一幕入口一致时继续创作；真实偏差只影响尚未执行的幕纲、章纲和 Prompt。

对齐使用当前 order 与 task 保存范围和报告，不增加长期创作节点。

## 预制包漂移核对

对齐时检查本卷 `settings/context-pack.md` 与已确认 `settings/genre-setting.md`、`settings/writing-style.md` 是否漂移：题材期待、作者边界或声线规则变化会令 pack 失效。发现漂移时列入重建清单，由下一个 `prompt.create` 任务重建 pack，不改动已接受正文。
