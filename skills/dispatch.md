# Dispatch

<!-- changed_in: 0.3.0 -->

本模块是 `novel-pro` 的控制面权威源。它把长期文学阶段、当前临时任务、角色边界、文件接口和恢复动作放在同一张契约里。顶层先读取本模块，再按当前 `order.operation` 加载一个对应的创作模块；角色只获得完成自身任务所需的上下文。

## 版本与迁移边界

启动或恢复时先读取 `story.md` 的 `runtime_profile` 和 `.agent/status.yaml` 的 `migration` 节点。

满足任一条件即停止创作和运行时同步：存在 `story.yaml`、缺少 `runtime_profile`、profile 不是 `novel-pro-0.3`，或 `status.yaml` 缺少完整 `migration` 节点。提示作者使用 `python tools/migrate.py <旧项目> <新项目>` 完整重建迁移项目。

`cursor.step: migration.review` 表示迁移目标尚未 finalize。此时只允许阅读 `.migration/report.md`、处理迁移操作和等待作者确认，不得推进创作阶段或运行 `sync_runtime.py`。迁移循环见本文末尾。

## 长期阶段与临时操作

`.agent/status.yaml` 只记录长期创作位置；`.agent/order.yaml` 只记录正在执行或等待恢复的临时窗口。`order.operation` 可以比 `cursor.step` 更细，但不能创造第二套长期状态机。

### 长期 cursor

| `cursor.step` | 长期含义 | 形成的阶段产物 | 进入下一阶段的条件 |
|---|---|---|---|
| `outline.volume` | 卷纲与本卷必要设定 | `volumes/volume-N.md` 及已确认的项目设定 | 卷纲、设定和文风交作者确认 |
| `outline.acts` | 整卷幕地图与详细幕纲 | `acts/volume-N-acts.md`、`acts/vol-N-act-K.md` | 目标范围内幕纲共同成立 |
| `outline.chapters` | 按幕形成章纲 | `chapters/vol-N-ch-M.md`、幕级承接快照 | 目标范围内章纲全部形成 |
| `draft.write` | 顺序链路：Prompt 创建、审计、写作/编辑闭环与状态同步逐章交错推进 | `prompts/vol-N-ch-M.md`、`drafts/vol-N-ch-M.md`、（编辑模式）`texts/vol-N-ch-M.md` | 目标范围章节全部完成（写作模式到 `drafts.ready`，编辑模式到 `volume.complete`） |
| `drafts.ready` | 写作模式 目标范围草稿已形成 | 目标范围内的 `drafts/` | 作者继续编辑模式或另行处理草稿 |
| `volume.complete` | 当前卷目标范围已接受 | `texts/` 与卷末承接事实 | 作者确定下一卷或全书完成 |
| `book.complete` | 全书范围均已接受 | 完整 `texts/` | 仅作已完成事实，不再创建普通写作任务 |
| `migration.review` | 迁移报告等待复核 | `.migration/report.md`、迁移状态节点 | `finalize` 后恢复 `resume_step` |

**顺序链路说明**（`draft.write` 阶段的内部循环）：不再存在"全部 Prompt 就绪"的批量节点（`prompts.ready` 已废除）。写作模式每章小循环：`prompt.create`（读上一章真实正文 + 状态文件）→ `prompt.review`（默认审计）→ `write.draft`（writer ×1）→ 顶层阅读判定 → `state.update`（状态回流）→ 下一章。编辑模式为逐章闭环：`prompt.create` → `prompt.review` → `edit.write` → `edit.review` → `edit.anti-ai` → `edit.synthesize` → `edit.repair` → `edit.commit` → `state.update` → 下一章。order 的 `current_chapter` 记录当前章，逐章推进。

`outline.acts` 是长期阶段；`outline.act-map` 和 `outline.act` 只是该阶段内部 operation，不能写入 `status.cursor.step`。`completion.inspect`、`completion.revise`、`alignment` 是旁路任务，不改变长期 cursor。`prompt.review` 与 `state.update` 是顺序链路的默认步骤（在 `draft.write` 阶段内逐章执行），不是旁路。迁移是唯一允许临时占用 `cursor.step` 的运行时例外，因为正常创作必须暂停。

### 临时 order

`order.status` 使用 `idle`、`running`、`interrupted`、`completed`；`idle` 时 `operation` 和 `phase` 留空。`subtasks.status` 使用 `pending`、`running`、`completed`、`failed`：`completed` 只表示产物已返回且由顶层读过，不表示文学自动通过。

| `order.operation` | 对应长期 cursor | 任务窗口 |
|---|---|---|
| `outline.volume` | `outline.volume` | 一卷卷纲、必要设定和文风确认 |
| `outline.act-map` | `outline.acts` | 整卷幕地图 |
| `outline.act` | `outline.acts` | 一个详细幕纲 |
| `outline.chapters` | `outline.chapters` | 一幕章纲 |
| `prompt.create` | `draft.write`（顺序链路步骤） | 单章 Prompt |
| `prompt.review` | `draft.write`（顺序链路默认步骤） | 单章 Prompt 独立审计 |
| `write.draft` | `draft.write`（顺序链路步骤） | 写作模式单章草稿窗口 |
| `edit.write` | `draft.write`（顺序链路步骤） | 编辑模式 单章首稿窗口 |
| `edit.review` | `draft.write`（顺序链路步骤） | 单章冷读（上下文含本章之前全部已提交正文） |
| `edit.anti-ai` | `draft.write`（顺序链路步骤） | 单章 Anti-AI 全量扫描 |
| `edit.synthesize` | `draft.write`（顺序链路步骤） | 单章两份报告分级与返修意见 |
| `edit.repair` | `draft.write`（顺序链路步骤） | 单章按返修意见返修并复读 |
| `edit.commit` | `draft.write` → `volume.complete` | 单章接受正文提交 |
| `state.update` | `draft.write`（顺序链路默认步骤） | 单章状态回流（角色状态/时间线/伏笔/通知消费） |
| `completion.inspect` | 不变 | 显式全书冷读 |
| `completion.revise` | 不变 | 显式完本返修与复读 |
| `alignment` | 不变 | 作者要求的整卷产物对齐 |
| `migration.review` | `migration.review` | 报告、finalize 和 cleanup |

## 文件接口与所有权

`novel-agent` 是唯一的控制面写入者：它独占 `.agent/status.yaml`、`.agent/order.yaml`、`.agent/tasks/<task-id>/` 的任务元数据、`.agent/run-log.yaml`，并执行 `edit.commit` 向 `texts/` 的提交。角色返回报告或候选后，由顶层阅读并持久化；角色不能自行推进 cursor、order、run-log 或 `texts/`。

### 操作派发卡（按 order.operation 索引）

派发时先读本表，再按「加载模块」载入对应阶段模块，把角色只需要的上下文交给它。九字段：触发 → 加载模块 → 创建角色 → 角色输入 → 允许写入 → 返回顶层 → 完成判定 → 下一跳 → 恢复入口。

### outline.volume
- 触发：初始化或上一卷完成；本卷卷纲与本卷必要设定/文风尚未确认
- 加载模块：`skills/planning.md`
- 创建角色：volume-planner ×1（范围 = 一卷）
- 角色输入：`story.md`、作者方向、现有设定、必要知识；文风未形成时读 `knowledge/style/`
- 允许写入：`volumes/volume-N.md`（按 `templates/volumes/volume-N.md` 字段 schema，`volume_contract: 1`）；本卷任务明确分配的 `settings/` 与人物设定
- 返回顶层：卷纲（含主导驱动力/冲突阶梯/信息差弧线等驱动字段）、事实缺口、作者确认项
- 完成判定：卷纲 contract 字段完整、`settings/writing-style.md` 已含基准样章（缺样章不进下一阶段）、设定和文风交作者确认
- 下一跳：`outline.act-map`
- 恢复入口：重读现有卷纲与设定，只补缺失或冲突项

### outline.act-map
- 触发：`outline.volume` 完成（卷纲/设定/文风确认）
- 加载模块：`skills/act-planning.md`
- 创建角色：act-planner ×1（范围 = 整卷幕地图）
- 角色输入：已确认卷纲、`genre-setting.md`、`world-setting.md`、相关人物设定、`foreshadowing.md`、`timeline.md`、相邻已接受正文、必要知识
- 允许写入：`acts/volume-N-acts.md`
- 返回顶层：全卷阶段地图和幕边界
- 完成判定：幕地图覆盖整卷，与卷纲无冲突
- 下一跳：`outline.act` 或 `outline.chapters`
- 恢复入口：以已存在幕地图为准继续未完成范围

### outline.act
- 触发：幕地图完成，按幕分解；或长幕需独立详细纲
- 加载模块：`skills/act-planning.md`
- 创建角色：act-planner ×1（范围 = 一个详细幕）
- 角色输入：卷纲、幕地图、项目事实、相邻幕接口、正文入口
- 允许写入：一个 `acts/vol-N-act-K.md`
- 返回顶层：写入路径、幕内事实概要、相邻幕接口、无法成立的证据（详细幕纲的 `start_state`、`dramatic_task`、continuity contract、`end_state` 等结构化字段写入 `acts/vol-N-act-K.md`，由顶层从文件读取）
- 完成判定：目标范围内幕任务与接口共同成立
- 下一跳：`outline.chapters`
- 恢复入口：只重做缺失或被证据点名冲突的幕纲

### outline.chapters
- 触发：当前幕纲成立
- 加载模块：`skills/planning.md`
- 创建角色：chapter-planner ×1（范围 = 一幕章纲）
- 角色输入：卷纲、当前幕纲、`genre-setting.md`、`world-setting.md`、`character-setting/`（含 `state_history`）、`writing-preferences.md`、`foreshadowing.md`、`timeline.md`（本幕相关部分）、相邻幕接口、已接受正文入口
- 允许写入：`chapters/vol-N-ch-M.md`（9 必填字段：goal/reader_effect/conflict/characters/info_gap/scenes/must_hold/chapter_end_state/ends_with）；完成本幕后额外写入幕级承接快照 `chapters/vol-N-act-K-handoff.md`（派生摘要，与章纲同目录）
- 返回顶层：章纲文件路径、整幕承接摘要、需由 Prompt 携带的关键事实、规划冲突
- 完成判定：目标范围内章纲全部形成
- 下一跳：顺序链路（`draft.write` 阶段，从范围首章 `prompt.create` 开始）
- 恢复入口：从最早缺失章纲继续，并复读幕内接口

### prompt.create
- 触发：顺序链路中，本章章纲已形成、上一章已验收/提交且 `state.update` 已完成；order 的 `current_chapter` 指向本章
- 加载模块：`skills/prompt.md`；本卷首个任务（pack 尚未存在时）追加 `skills/context-pack.md`
- 创建角色：prompt-crafter ×1（范围 = 单章）
- 角色输入：context-pack（首任务为知识库原文）、幕级承接快照 `chapters/vol-N-act-K-handoff.md`（优先；缺失或与幕纲/章纲不一致时以幕纲+章纲为准）、当前幕纲、本章章纲（含 `info_gap`/`chapter_end_state`）、**上一章真实正文（验收稿 `drafts/` 或已提交正文 `texts/`，必读）**、出场角色档案（含 `state_history` 倒读）、`writing-style.md`、`genre-setting.md`、`world-setting.md`、`writing-preferences.md`、`foreshadowing.md`、`timeline.md`（按章筛选所需）
- 允许写入：`prompts/vol-N-ch-M.md`（`prompt_contract: 4`，frontmatter 记录 `preceding_source`）；首任务另写 `settings/context-pack.md`
- 返回顶层：Prompt 路径、本章承接摘要（前情三件套来源）、自检结论表、事实缺口或上游冲突；本卷首任务另返建包摘要
- 完成判定：`prompts/vol-N-ch-M.md` 落盘且顶层逐一读过（存在 ≠ 通过），自检结论表无未解释缺口；已读上一章真实正文与状态文件核对一致
- 下一跳：`prompt.review`
- 恢复入口：只重做缺失或被正文证据点名的 Prompt；pack 未漂移不重建

### prompt.review
- 触发：本章 Prompt 落盘后（顺序链路默认步骤）；作者明确放行时可跳过并由顶层在 order 记录
- 加载模块：`skills/prompt.md`「默认 Prompt 审计」
- 创建角色：prompt-reviewer ×1（范围 = 单章 Prompt）
- 角色输入：目标 Prompt；`preceding_source` 对应的上一章真实正文、所在幕纲、对应章纲（含 `info_gap`/`chapter_end_state`）、出场角色档案 `state_history`
- 允许写入：不写 Prompt、规划、正文或状态（报告写入当前 task）
- 返回顶层：`PASS` / `FIX` / `STOP` 报告（9 维度逐项结论）
- 完成判定：报告给出明确结论
- 下一跳：`PASS` → `write.draft`（写作模式）或 `edit.write`（编辑模式）；`FIX` → 返回 `prompt.create` 修复后重审；`STOP` → 返回顶层交规划层
- 恢复入口：保留报告，对未通过的 Prompt 重新审计

### write.draft
- 触发：本章 Prompt 审计通过且作者选择写作模式
- 加载模块：`skills/writing.md` + `skills/writer-construction.md`
- 创建角色：writer ×1（范围 = 单章）
- 角色输入：顶层生成的单章 writer base、一个目标 Prompt
- 允许写入：首稿写 `drafts/vol-N-ch-M.md`；重派写当前 task candidate
- 返回顶层：完整纯正文或失败原因
- 完成判定：当前 writer 窗口完成或转入恢复
- 下一跳：顶层阅读实际草稿后三向判定——接受 → `state.update`；同一 Prompt 重派 → 本卡重派；回退 → `prompt.create`（必要时回规划层）
- 恢复入口：只重派没有可用产物的章节，已有候选不覆盖

### edit.write
- 触发：本章 Prompt 审计通过且作者选择编辑模式
- 加载模块：`skills/writing.md` + `skills/writer-construction.md`
- 创建角色：writer ×1（范围 = 单章）
- 角色输入：顶层生成的单章 writer base、一个目标 Prompt
- 允许写入：首稿写 `drafts/vol-N-ch-M.md`；返修写当前 task candidate
- 返回顶层：完整纯正文或失败原因
- 完成判定：当前 writer 窗口完成或转入恢复
- 下一跳：`edit.review`
- 恢复入口：只重派没有可用产物的章节，已有候选不覆盖

### edit.review
- 触发：本章首稿形成（`edit.write` 完成）
- 加载模块：`skills/review-archive.md` + `skills/cold-read-discipline.md`
- 创建角色：reader ×1（范围 = 单章冷读；阅读上下文含本章之前全部已提交正文与幕纲）
- 角色输入：本章正文和候选；首读后才读契约、Prompt、知识
- 允许写入：不写项目产物
- 返回顶层：单章冷读报告——verdict（PASS/FIX/STOP）、已成立处、正文证据、根因、最小处理范围、保留项、建议处理角色、接受候选和复读范围
- 完成判定：本章冷读完成且无未解决问题或已分流
- 下一跳：`edit.anti-ai`
- 恢复入口：按受影响范围从头顺序复读

### edit.anti-ai
- 触发：本章冷读报告已返回（`edit.review` 完成）
- 加载模块：`skills/review-archive.md`（Anti-AI 全量扫描章节）+ `skills/edit-boundary.md`
- 创建角色：anti-ai ×1（范围 = 本章，全量扫描）
- 角色输入：Reader 读过的本章正文；`knowledge/anti-ai/index.md`（通用与题材规则）；不依赖 Reader 点名
- 允许写入：当前 task 的 Anti-AI 报告；不直接改正文、不写 `texts/`
- 返回顶层：本章 Anti-AI 报告——AI 味/模板化表达/解释腔/机械重复/不自然对白等证据、原句定位、严重倾向（严重/中等/轻微），并标注是否越出局部编辑边界
- 完成判定：本章经全量扫描并列于报告
- 下一跳：`edit.synthesize`
- 恢复入口：只重扫缺失或被证据点名的章节

### edit.synthesize
- 触发：本章两份报告齐备（`edit.anti-ai` 完成）
- 加载模块：`skills/review-archive.md`（整体返修裁决章节）
- 创建角色：edit-synthesizer ×1（范围 = 本章的整体裁决）
- 角色输入：Reader 冷读报告 + Anti-AI 报告（本章）；必要承接与已确认事实
- 允许写入：当前 task 的整体返修意见（分级 + 章节 + 怎么修 + 问题归属 + 优先级）；不写正文、规划或 `texts/`
- 返回顶层：整体返修意见——对每个问题标注来源（冷读 / Anti-AI），评估严重等级（严重/中等/轻微），明确修哪、怎么修、跨章关联与处理优先级；给出分流建议（REGENERATE 类 → writer/prompt-crafter/planner；局部表达类 → anti-ai 编辑模式）
- 完成判定：所有问题均被分级、归属并给出可执行返修意图
- 下一跳：`edit.repair` 或 `edit.commit`（无返修项时直接提交）
- 恢复入口：保留两份报告与返修意见，只重做缺失章节的裁决

### edit.repair
- 触发：`edit.synthesize` 完成（整体返修意见已返回，且存在需返修项）
- 加载模块：`skills/review-archive.md`（按整体返修意见执行）；表达编辑分流到 `skills/edit-boundary.md`
- 创建角色：按返修意见的分流建议创建 → 严重(REGENERATE)：新 writer / prompt-crafter / planner；中等/轻微表达：anti-ai（编辑模式）
- 角色输入：整体返修意见 + 受影响正文 + 必要承接与 Prompt；整体返修须考虑跨章关联与按严重等级的处理优先级
- 允许写入：按分流写 draft candidate / 修复 Prompt / 重建规划 / 表达候选
- 返回顶层：各候选完成状态与最小返修范围
- 完成判定：每个候选完成并进入复读
- 下一跳：Reader 重新顺序阅读受影响范围（复读通过后 `edit.commit`）
- 恢复入口：保留原文与候选，按返修意见重新交对应角色

### edit.commit
- 触发：本章复读后无未解决问题
- 加载模块：`skills/review-archive.md`
- 创建角色：novel-agent 自身（无 subagent）
- 角色输入：已复读接受候选、task 报告、目标路径
- 允许写入：`texts/`、控制面文件、run-log 和 task 收尾
- 返回顶层：提交结果和下一长期阶段
- 完成判定：`edit.commit` 预检通过
- 下一跳：`state.update`；目标范围全部提交后 → `volume.complete` 或 `book.complete`
- 恢复入口：预检失败不写任何目标，保留现场

### state.update
- 触发：本章正文被接受（写作模式草稿验收）或提交（编辑模式 `edit.commit` 完成）
- 加载模块：`skills/state-sync.md`
- 创建角色：continuity-updater ×1（范围 = 单章）
- 角色输入：本章验收稿或已提交正文；本章章纲（`chapter_end_state` 与「设定变更通知」块）；所在幕纲（「设定变更通知」块）；既有 `settings/` 文件
- 允许写入：向 `settings/character-setting/{id}.md` 的 `state_history` 节追加状态变更块、`settings/timeline.md` 追加章节锚点条目、`settings/foreshadowing.md` 推进台账；移除章纲/幕纲中已消费的「设定变更通知」块
- 返回顶层：状态同步摘要（追加清单、消费/保留的通知、与 `chapter_end_state` 的偏差清单）
- 完成判定：四项回流按章完成、幂等锚点已检查、通知块处理完毕
- 下一跳：目标范围未完成 → 下一章 `prompt.create`（order `current_chapter` 推进）；已完成 → `drafts.ready`（写作模式）或 `volume.complete`（编辑模式）
- 恢复入口：按章节锚点检查，已同步章节跳过，未同步章节重做

### completion.inspect
- 触发：作者要求显式全书冷读
- 加载模块：`skills/completion-quality.md` + `skills/cold-read-discipline.md`
- 创建角色：completion-reviewer ×1（范围 = 全书）
- 角色输入：当前 task 指定的 `texts/`；首读后才读根因资料
- 允许写入：不写正文、规划或状态
- 返回顶层：完本报告、分流和最小返修范围
- 完成判定：按幕冷读全书并追查根因
- 下一跳：`completion.revise` 或完成
- 恢复入口：从最早受影响幕重新顺序阅读

### completion.revise
- 触发：`completion.inspect` 报告点名最小范围
- 加载模块：`skills/completion-quality.md` + `skills/edit-boundary.md`
- 创建角色：completion-editor ×1（范围 = 点名章节）
- 角色输入：被点名章节、问题卡（由顶层从 completion-reviewer 报告中提取的单章问题摘要：`{章节路径, IGNORE/EDIT/REGENERATE, 根因类别, 具体问题描述, 编辑约束}`）、必要相邻正文和已确认事实
- 允许写入：当前 task 的局部完整候选
- 返回顶层：`EDIT` 候选或 `REGENERATE` 建议
- 完成判定：候选经受影响范围复读与全书承接复读
- 下一跳：completion-reviewer 复读
- 恢复入口：不符合边界时放弃候选，返回上游

### alignment
- 触发：作者明确要求整卷产物对齐
- 加载模块：`skills/volume-alignment.md`
- 创建角色：各产物拥有者（planner / prompt-crafter / 对应角色）按范围分配
- 角色输入：已接受正文与尚未执行的幕纲、章纲、Prompt；状态文件与正文连续性检查（`state_history` 缺失、信息持有矛盾即漂移）
- 允许写入：各自拥有的规划/Prompt（已接受正文不回写）
- 返回顶层：对齐后的产物差异
- 完成判定：尚未执行产物与已接受正文一致，状态文件与正文连续
- 下一跳：返回顶层，不改变主线
- 恢复入口：保留已确认正文，不创建空返修链

### migration.review
- 触发：`cursor.step: migration.review`（迁移目标尚未 finalize）
- 加载模块：`skills/migration.md`
- 创建角色：novel-agent 自身（无 subagent）
- 角色输入：`.migration/report.md`、迁移状态节点
- 允许写入：不写创作产物；`finalize` 后更新迁移节点
- 返回顶层：迁移确认结论
- 完成判定：作者完成 `finalize`
- 下一跳：恢复 `migration.resume_step`
- 恢复入口：保留报告与现场，不推进创作

### 所有权总则

规划角色只写自己负责的规划产物和被顶层明确分配的本卷设定；prompt-crafter 只写 Prompt；writer 不写 Prompt、设定或 `.agent`；Reader、completion-reviewer、prompt-reviewer 只返回报告；continuity-updater 只追加 `settings/` 的状态历史区（`state_history`、`timeline.md`、`foreshadowing.md`）并消费设定变更通知，不写规划、Prompt 或正文。所有角色都不直接读取文风原型库，除 `volume-planner` 在项目文风尚未形成且作者需要选择方向时的形成阶段外。

## 项目事实的承接

以下文件不是第二套状态机，而是由规划阶段形成、由下游按需消费的事实来源：

| 文件 | 规划阶段用途 | Prompt/复读用途 |
|---|---|---|
| `settings/genre-setting.md` | 题材期待、作者边界和本作辨识度 | volume/act/chapter planner 与 prompt-crafter 只提取当前范围相关部分 |
| `settings/world-setting.md` | 会实际影响行动的地理、势力和规则 | planner 交叉核对；Prompt 携带本章需要的事实边界 |
| `settings/character-setting/*` | 人物可持续的欲望、关系、能力、资源和限制；`state_history` 记录已兑现的状态变更（由 state.update 追加） | planner 与 prompt-crafter 从 `state_history` 倒读重建当前状态；writer 只接收 Prompt |
| `settings/writing-preferences.md` | 作者明确确认、可跨章复用的偏好 | planner 将其转成规划选择；prompt-crafter 只提取当前章适用项 |
| `settings/foreshadowing.md` | 已进入规划或正文、会影响后续的伏笔及状态（台账由 state.update 推进） | act/chapter planner 和 prompt-crafter 核对兑现、隐藏和余波；Reader 首读后按需追因 |
| `settings/timeline.md` | 已发生且影响承接的时间事实（由 state.update 按章追加） | act/chapter planner 和 prompt-crafter 核对先后、间隔和人物可知范围；Reader 首读后按需追因 |
| `settings/writing-style.md` | volume-planner 与作者确认后的项目声线唯一来源 | prompt-crafter 按章提取；writer 通过 Prompt 和项目样章执行，Reader 只从正文判断 |
| `settings/context-pack.md` | 由本卷首个 `prompt.create` 任务从 `knowledge/` 裁剪压缩的预制包 | 后续 prompt-crafter 读包替代知识下钻；prompt-reviewer 审计时核对 |

规划层只承接已经确认或正文已经发生的事实；不能用设定文件替代正文交付。Prompt 只携带当前章所需的事实、人物选择和边界，writer 不回读原型库或无关设定。正文一旦被接受，就成为后续规划的已发生事实；真实偏差只调整尚未执行的产物。

## 创作循环

- **规划链**（卷纲→幕→章纲）：见 `skills/planning.md`「规划链执行入口」与 `skills/act-planning.md`「幕规划执行入口」
- **顺序链路**（逐章：Prompt → 审计 → 写作/编辑闭环 → 状态同步）：见 `skills/writing.md`「顺序链路执行入口」
- **写作模式**：见 `skills/writing.md`「写作模式流程」
- **编辑模式**：见 `skills/review-archive.md`「编辑模式创作流程」
- **Completion**：见 `skills/completion-quality.md`
- **Migration**：见下方「迁移」节
- **TASKS.md**：见下方「TASKS.md」节
- **Alignment**：见 `skills/volume-alignment.md`

### 迁移

```text
旧项目
→ `tools/migrate.py create`
→ 新项目 `cursor.step: migration.review`
→ 阅读 `.migration/report.md` 并由作者确认
→ `tools/migrate.py finalize <新项目>`
→ 恢复 `migration.resume_step`
→ 可选 `cleanup <新项目> --confirm`
```

迁移期间不创建规划、Prompt、writer 或 Reader，不运行同步；`cleanup` 只处理报告列出的旧运行时文件。

### TASKS.md

`TASKS.md` 是 Novel Desk 到顶层的作者请求适配器。字段定义、状态流转（`pending` -> `in_progress` -> `completed` / `blocked` / `cancelled`）与所有权边界以 `templates/TASKS.md` 为权威源。顶层按该 schema 汇总全部 `pending` 的 `source`、`scope` 和将采用的 `operation`，等待作者确认后才标记 `in_progress`；完成后回写 `status` 与 `result`。它不写长期 cursor，不替代 order/task/run-log，也不改变任何角色所有权。

## 恢复

恢复先读取 `status`、`order`、当前 task 和相关 run-log，再按 operation 处理：

- `completed` subtask 由顶层确认产物仍存在且与任务相符；成立则保留。
- `running`、`failed` 或没有对应产物的 subtask 回到 `pending`。
- **顺序链路逐章断点**：按 order 的 `current_chapter` 定位当前章，按该章产物状态决定恢复步骤——Prompt 缺失或 `preceding_source` 已变（上一章正文被返修重写）→ 从 `prompt.create` 重做；Prompt 在但未审计 → 从 `prompt.review` 继续；草稿缺失 → 从 `write.draft`/`edit.write` 重派；草稿在但未验收/未提交 → 顶层阅读后继续；正文已验收但 `state_updated: false` → 从 `state.update` 继续。已同步章节（`state_updated: true`）不重复同步。
- 规划、Prompt、writer 和 Reader 分别从自己的最小恢复入口继续；不重建已经成立的范围。
- Prompt 创建恢复时，本卷 `settings/context-pack.md` 若未漂移则不重建；pack 重建只在换卷、文风或题材经作者重新确认、`alignment` 发现漂移时发生。
- Reader 或返修恢复必须从报告指定的受影响范围起点重新顺序阅读；未复读的候选不能提交。
- 顶层只在长期目标范围的产物成立后推进 `status.cursor.step`，并将恢复事实写入 task/run-log。
