# State Sync（状态同步）

<!-- changed_in: 0.3.0 -->

本模块规定 `state.update` operation：先把已完成章节压缩为临时 `chapter-delta`，再把最终 `texts/` 中的真实正文事实回流到 `settings/` 事实文件（角色状态历史、时间线、伏笔台账），并消费规划层提出的「设定变更通知」。临时 delta 只服务顺序链路的下一章，不是真相源；正式 `state.update` 仍以最终 `texts/` 为唯一事实来源。

## 触发与执行

- **operation**：`state.update`（dispatch.md 派发卡）
- **角色**：continuity-updater（每章一个，单章任务）
- **触发时机**（双模式接入）：
  - **写作模式**：本章草稿被顶层**接受**后执行（输入为验收草稿 `drafts/vol-N-ch-M.md`）。
  - **编辑模式**：本章 `edit.commit` 写入 `texts/vol-N-ch-M.md` 后执行（输入为定稿正文）。
- **内部阶段**：`phase: delta` 只生成工作态增量；`phase: commit` 才执行正式回流。两阶段仍使用同一个 `state.update` operation，不增加长期 cursor 或 operation。
- **幕末附加动作**：正式 `commit` 阶段且本章是幕末章时，追加生成/更新幕总结 `summaries/vol-N-act-K.md`（见下方第 5 项）。
- **输出**：delta 阶段只返回结构化结果，由顶层写入当前 task；commit 阶段追加式更新 settings。角色都不写 `.agent` 控制面文件。

## 输入

- 目标章节草稿（`drafts/`）或定稿（`texts/`）。delta 阶段以草稿为工作事实；commit 阶段只接受最终 `texts/` 作为正式事实来源。
- 目标章纲（`chapters/vol-N-ch-M.md`）：`chapter_end_state` 作核对锚点；末尾「设定变更通知」块待消费。
- 所在幕纲（`acts/vol-N-act-K.md`）：「设定变更通知」块待消费。
- 既有 `settings/` 文件：`character-setting/`、`timeline.md`、`foreshadowing.md`。

## 阶段 A：chapter-delta（工作态增量）

章节草稿完成后执行一次轻量提取，不修改 settings。continuity-updater 返回结构化 delta，由顶层持久化到 `.agent/tasks/<task-id>/chapter-delta.yaml`，必要时同时更新同一 task 的 `working-state.yaml`。最小字段为：

- 章节锚点、正文来源路径和 SHA-256 hash；
- 角色状态变化；
- 各角色知道/不知道/误判的信息持有；
- 时间线变化；
- 伏笔变化；
- 设定变更通知（已兑现/未兑现）；
- 与 `chapter_end_state` 的偏差。

下一章 Prompt 可以读取当前 task 的 delta 和 working-state 作为增量上下文；缺失时回退到上一章真实正文和既有 settings。delta 不得写入长期 settings，不得被当作已确认事实。

## 阶段 B：正式 state.update（四项回流；幕末章附加幕总结）

### 1. 角色状态变更块（character-setting/{id}.md → state_history 节）

按 `templates/characters/character-profile.md`「state_history」节的块格式，为本章**实际出场并有状态变化**的角色追加 `## vol-{N}-ch-{M} 状态变更` 块：

- 位置 / 状态 / 人际关系变化 / 能力状态变化 / 本章关键台词或行为。
- 剧情履历：本章实际做的事（含对象和结果）。
- 情绪弧线：情绪状态、触发事件、强度、方向、表达方式。
- 信息持有：知道 / 不知道 / 误判三条。

**注意**：信息持有三条决定下一章的信息差起点，必须写；无变化也写"无"。

### 2. 时间线条目（timeline.md）

按章节锚点追加：`### vol-{N}-ch-{M}：{事件名称}`，内容含发生时间、地点、事件内容、谁知道、后果、证据（指向本章正文路径）。只记录影响后续承接的关键事件；正文没有证据的事件不写入。

### 3. 伏笔台账推进（foreshadowing.md）

- 正文首次出现的伏笔 → 新增条目（章节锚点）。
- 正文实际推进/兑现的伏笔 → 更新 `当前状态`（未兑现/部分兑现/已兑现/已放弃）并注明章节。
- 只写正文已兑现的进展；规划承诺但正文未发生的推进不写入。

### 4. 消费设定变更通知

- 扫描章纲与幕纲中的 `## 设定变更通知` 块。
- 通知目标为 `character-setting/{id}.md` 时：正文已兑现 → 按通知详情更新档案对应节（状态更新类**追加到 state_history**，不覆盖历史）；新角色 → 按模板新建档案。
- 通知目标为 `timeline.md` / `foreshadowing.md` 时：并入第 2、3 项回流。
- 通知目标为 `world-setting.md` 等其他设定：正文已兑现 → 在对应文件追加/标注变更（标注 `[updated: vol-N-ch-M]`），保留原文痕迹。
- **消费后移除源文件中的通知块**（防止重复消费）；正文未兑现的通知**不移除**，回告顶层缺口。

### 5. 幕末正文总结（幕末章附加动作）

当本章是本幕的**最后一章**（order 目标范围终点或幕纲 `chapter_roles` 末章）且已进入 `phase: commit` 时，`state.update` 额外生成/更新幕末正文总结 `summaries/vol-N-act-K.md`（模板见 `templates/summaries/vol-N-act-K.md`）：

- **内容**：幕内事件链（每章一条，带章节锚点）、人物状态与关系变化（与 state_history 核对）、信息差状态（幕末谁知道什么）、伏笔状态（与 foreshadowing 核对）、未闭合张力（跨幕驱动）、幕末承接帧（幕末最后一章真实结尾画面/情绪残留/缺口）。
- **来源**：本幕全部已提交正文 `texts/`，只压缩实际发生的事实；与 `settings/` 状态文件交叉核对，矛盾以最终正文为准并回告顶层。写作模式只有临时 delta，不在此阶段生成正式幕总结。
- **幂等**：`based_on` 相同的幕总结已存在且本章未返修重写时跳过；幕内任一章节被返修重写后，由对应 `state.update` 更新幕总结。
- **纪律**：幕总结是**派生缓存，不是真相源**——每条带章节锚点；事实判定始终以正文与 `settings/` 状态文件为准；prompt-crafter 跨幕读取它作导航，不把它当第二套状态机。

## 幂等与覆盖刷新

- **新锚点追加**：目标文件中不存在同章节锚点条目/状态块时，追加（不覆盖既有内容）。
- **同锚点覆盖刷新**：同一章节的正文源发生变化时（task delta → 编辑模式最终定稿提交，或返修重写），以最终 `texts/` 为准**替换**该锚点块/条目——同一章的事实记录只保留最终版本，不产生重复块；锚点相同且正文源未变时跳过（幂等）。
- **回滚**：章节回滚/重写导致已追加内容过时时，按锚点删除对应块与条目（宁少删，不删未确认的内容）；由顶层在回滚后安排 `state.update` 对受影响章节重新同步。

## 纪律

- **只写正文已兑现的事实**：正文是事实的唯一来源。规划承诺（must_hold、chapter_end_state、设定变更通知）只是核对锚点，正文未兑现的不写入 settings。
- **新锚点只追加、同锚点以最新正文为准**：state_history、时间线、伏笔台账按章锚点追加；同一章正文源变化（delta→最终定稿、返修重写）时覆盖刷新该锚点记录，不产生重复块；既有其他内容不静默改写。
- **与 chapter_end_state 核对**：正文与章纲快照一致 → 正常追加；不一致 → 以正文为准追加，并在返回摘要中列出偏差清单（提示规划层是否需要调整后续章纲）。
- **认知层纪律**：状态变更涉及认知层 1-3（世界观/自我定位/价值观）时必须注明支撑事件；找不到支撑事件的变更视为漂移，写入偏差清单回告顶层，不写入档案。
- **不越权**：不修改已接受正文、不修改 Prompt、不修改卷幕章规划（移除通知块除外）、不写 `.agent` 文件、不创建或调度其他角色。
- **不进入正文**：状态同步产物是事实记录，不回灌到 Prompt 或正文；Prompt 由 prompt-crafter 按章读取状态文件。

## 返回摘要

### delta 阶段

只返回 `chapter_delta`、`source_path`、`source_hash`、`deviations` 和 `next_context`。不得回显正文，不得声称 settings 已更新；由顶层写入 task 现场并在 `order.state_delta` 标记 `captured: true`。

### commit 阶段

continuity-updater 在 commit 阶段返回时附摘要（只陈述事实）：

- 追加了哪些角色状态块 / 时间线条目 / 伏笔进展（按文件列清单）。
- 消费了哪些设定变更通知（哪些已消费移除、哪些未兑现保留）。
- 与 `chapter_end_state` 的偏差清单（正文与章纲不一致处，供顶层决定是否回退规划层）。

## 与既有契约的关系

- **writer 边界不动**：writer 仍只收单章 base + 单章 Prompt，不读 settings/；状态回流发生在 writer 之后。
- **Reader 冷读保护不动**：Reader、completion-reviewer 首读仍不预挂状态文件，按需追因路径一字不改。
- **Prompt 创建侧**：在正式提交前，prompt-crafter 可读取当前 task 的 chapter-delta/working-state 加上上一章真实正文；正式提交后再读取更新后的状态文件（角色状态历史、时间线、伏笔台账）。缓存或 delta 缺失时回退到既有 0.3 读取方式。
- **alignment**：整卷对齐任务增加一项检查——状态文件与已接受正文是否连续（状态块缺失、信息持有矛盾即漂移），漂移列入重建清单。
- **迁移**：状态同步是运行时行为，不搬运；旧项目迁移后首次 `state.update` 从已迁移正文补齐。
