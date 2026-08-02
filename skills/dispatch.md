# Dispatch

<!-- changed_in: 0.2.3 -->

本模块是 `novel-pro` 的控制面权威源。它把长期文学阶段、当前临时任务、角色边界、文件接口和恢复动作放在同一张契约里。顶层先读取本模块，再按当前 `order.operation` 加载一个对应的创作模块；角色只获得完成自身任务所需的上下文。

## 版本与迁移边界

启动或恢复时先读取 `story.md` 的 `runtime_profile` 和 `.agent/status.yaml` 的 `migration` 节点。

满足任一条件即停止创作和运行时同步：存在 `story.yaml`、缺少 `runtime_profile`、profile 不是 `novel-pro-0.2`，或 `status.yaml` 缺少完整 `migration` 节点。提示作者使用 `python tools/migrate.py <旧项目> <新项目>` 完整重建迁移项目。

`cursor.step: migration.review` 表示迁移目标尚未 finalize。此时只允许阅读 `.migration/report.md`、处理迁移操作和等待作者确认，不得推进创作阶段或运行 `sync_runtime.py`。迁移循环见本文末尾。

## 长期阶段与临时操作

`.agent/status.yaml` 只记录长期创作位置；`.agent/order.yaml` 只记录正在执行或等待恢复的临时窗口。`order.operation` 可以比 `cursor.step` 更细，但不能创造第二套长期状态机。

### 长期 cursor

| `cursor.step` | 长期含义 | 形成的阶段产物 | 进入下一阶段的条件 |
|---|---|---|---|
| `outline.volume` | 卷纲与本卷必要设定 | `volumes/volume-N.md` 及已确认的项目设定 | 卷纲、设定和文风交作者确认 |
| `outline.acts` | 整卷幕地图与详细幕纲 | `acts/volume-N-acts.md`、`acts/vol-N-act-K.md` | 目标范围内幕纲共同成立 |
| `outline.chapters` | 按幕形成章纲 | `chapters/vol-N-ch-M.md` | 目标范围内章纲全部形成 |
| `prompts.ready` | 目标范围的 Prompt 已完整形成 | `prompts/vol-N-ch-M.md` | 每章 Prompt 均已由顶层读过并确认存在 |
| `draft.write` | 写作模式或编辑模式 首稿正在形成 | `drafts/vol-N-ch-M.md` | 当前 writer 窗口完成或转入恢复 |
| `drafts.ready` | 写作模式 目标范围草稿已形成 | 目标范围内的 `drafts/` | 作者继续编辑模式或另行处理草稿 |
| `review` | 编辑模式正文正在冷读、返修或提交 | Reader 报告、task 候选、接受结论 | 目标范围全部复读接受并提交 |
| `volume.complete` | 当前卷目标范围已接受 | `texts/` 与卷末承接事实 | 作者确定下一卷或全书完成 |
| `book.complete` | 全书范围均已接受 | 完整 `texts/` | 仅作已完成事实，不再创建普通写作任务 |
| `migration.review` | 迁移报告等待复核 | `.migration/report.md`、迁移状态节点 | `finalize` 后恢复 `resume_step` |

`outline.acts` 是长期阶段；`outline.act-map` 和 `outline.act` 只是该阶段内部 operation，不能写入 `status.cursor.step`。`completion.inspect`、`completion.revise`、`alignment` 和 `prompt.review` 是旁路任务，不改变长期 cursor。迁移是唯一允许临时占用 `cursor.step` 的运行时例外，因为正常创作必须暂停。

### 临时 order

`order.status` 使用 `idle`、`running`、`interrupted`、`completed`；`idle` 时 `operation` 和 `phase` 留空。`subtasks.status` 使用 `pending`、`running`、`completed`、`failed`：`completed` 只表示产物已返回且由顶层读过，不表示文学自动通过。

| `order.operation` | 对应长期 cursor | 任务窗口 |
|---|---|---|
| `outline.volume` | `outline.volume` | 一卷卷纲、必要设定和文风确认 |
| `outline.act-map` | `outline.acts` | 整卷幕地图 |
| `outline.act` | `outline.acts` | 一个详细幕纲 |
| `outline.chapters` | `outline.chapters` | 一幕章纲 |
| `prompt.create` | `outline.chapters`，完成后才到 `prompts.ready` | 一幕或连续 Prompt 批次 |
| `prompt.review` | 不变 | 用户明确要求的 Prompt 审查 |
| `write.draft` | `prompts.ready` → `draft.write` | 写作模式单章草稿窗口 |
| `edit.write` | `prompts.ready` → `draft.write`，完成后到 `review` | 编辑模式 首稿窗口 |
| `edit.review` | `review` | 一幕顺序冷读，按幕(目)出冷读报告 |
| `edit.anti-ai` | `review` | Anti-AI 全量扫描同批章节，按幕(目)出报告 |
| `edit.synthesize` | `review` | 读两份报告，分级并给整体返修意见 |
| `edit.repair` | `review` | 按整体返修意见整体返修并复读 |
| `edit.commit` | `review` → `volume.complete` 或下一目标阶段 | 接受正文提交 |
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
- 角色输入：卷纲、当前幕纲、`genre-setting.md`、`world-setting.md`、`character-setting/`、`writing-preferences.md`、`foreshadowing.md`、`timeline.md`（本幕相关部分）、相邻幕接口、已接受正文入口
- 允许写入：`chapters/vol-N-ch-M.md`；完成本幕后额外写入幕级承接快照 `chapters/vol-N-act-K-handoff.md`（派生摘要，与章纲同目录）
- 返回顶层：章纲文件路径、整幕承接摘要、需由 Prompt 携带的关键事实、规划冲突
- 完成判定：目标范围内章纲全部形成
- 下一跳：`prompt.create`
- 恢复入口：从最早缺失章纲继续，并复读幕内接口

### prompt.create
- 触发：cursor 在 `outline.chapters` 且目标范围章纲全部形成；order 为 idle 或上一批次已完成
- 加载模块：`skills/prompt.md`；本卷首个任务（pack 尚未存在时）追加 `skills/context-pack.md`
- 创建角色：prompt-crafter ×1（范围 = 一幕或一个连续批次）
- 角色输入：context-pack（首任务为知识库原文）、幕级承接快照 `chapters/vol-N-act-K-handoff.md`（唯一落位路径；优先；缺失或与幕纲/章纲不一致时以幕纲+章纲为准）、当前幕纲、范围内章纲、`writing-style.md`、`genre-setting.md`、`world-setting.md`、相关人物设定、`writing-preferences.md`、`foreshadowing.md`、`timeline.md`（按章筛选所需）、承接入口；批次任务另含上一批次的批次出口摘要
- 允许写入：任务范围内的 `prompts/vol-N-ch-M.md`；首任务另写 `settings/context-pack.md`
- 返回顶层：Prompt 路径、每章承接摘要、自检结论表、事实缺口或上游冲突；本卷首任务另返建包摘要；批次任务另返批次出口摘要
- 完成判定：范围内每章 Prompt 落盘且顶层逐一读过（存在 ≠ 通过；顶层逐行核对自检表，对标记"成立"章节抽读原文 2-3 章复核），并已读 handoff 快照与幕纲/章纲核对一致，自检结论表无未解释缺口
- 下一跳：下一批次 `prompt.create`，或范围齐后 cursor 进 `prompts.ready`
- 恢复入口：只重做缺失或被正文证据点名的 Prompt；pack 未漂移不重建

### prompt.review
- 触发：用户明确提出审核提示词
- 加载模块：`skills/prompt.md` 末节
- 创建角色：prompt-reviewer ×1（范围 = 目标 Prompt 集合）
- 角色输入：目标 Prompt，再读对应幕纲和章纲
- 允许写入：不写 Prompt、规划或状态
- 返回顶层：`PASS` / `FIX` / `STOP` 报告
- 完成判定：报告给出明确结论
- 下一跳：返回作者/顶层，不改变主线
- 恢复入口：保留报告，按用户指定范围重新审查

### write.draft
- 触发：`prompts.ready` 且作者选择写作模式；目标范围草稿尚未全部形成
- 加载模块：`skills/writing.md` + `skills/writer-construction.md`
- 创建角色：writer ×N（每章独立，范围 = 单章）
- 角色输入：顶层生成的单章 writer base、一个目标 Prompt
- 允许写入：首稿写 `drafts/vol-N-ch-M.md`；返修写当前 task candidate
- 返回顶层：完整纯正文或失败原因
- 完成判定：当前 writer 窗口完成或转入恢复
- 下一跳：`drafts.ready`
- 恢复入口：只重派没有可用产物的章节，已有候选不覆盖

### edit.write
- 触发：`prompts.ready` 进入编辑模式；目标范围首稿尚未全部形成
- 加载模块：`skills/writing.md` + `skills/writer-construction.md`
- 创建角色：writer ×N（每章独立，范围 = 单章）
- 角色输入：顶层生成的单章 writer base、一个目标 Prompt
- 允许写入：首稿写 `drafts/vol-N-ch-M.md`；返修写当前 task candidate
- 返回顶层：完整纯正文或失败原因
- 完成判定：当前 writer 窗口完成或转入恢复
- 下一跳：`edit.review`
- 恢复入口：只重派没有可用产物的章节，已有候选不覆盖

### edit.review
- 触发：`edit.write` 完成（目标范围首稿形成）
- 加载模块：`skills/review-archive.md` + `skills/cold-read-discipline.md`
- 创建角色：reader ×1（范围 = 一幕顺序冷读）
- 角色输入：当前幕正文和候选；首读后才读契约、Prompt、知识
- 允许写入：不写项目产物
- 返回顶层：按幕(目)组织的冷读报告——幕级 verdict（PASS/FIX/STOP）、已成立处、正文证据、根因、最小处理范围、保留项、建议处理角色、接受候选和复读范围
- 完成判定：受影响范围全部顺序复读，无未解决问题或已分流
- 下一跳：`edit.anti-ai`
- 恢复入口：按受影响范围从头顺序复读

### edit.anti-ai
- 触发：`edit.review` 完成（冷读报告已返回）
- 加载模块：`skills/review-archive.md`（Anti-AI 全量扫描章节）+ `skills/edit-boundary.md`
- 创建角色：anti-ai ×1（范围 = 与 `edit.review` 同一批章节，全量扫描）
- 角色输入：Reader 读过的同批章节正文；`knowledge/anti-ai/index.md`（通用与题材规则）；不依赖 Reader 点名
- 允许写入：当前 task 的 Anti-AI 报告（按幕/目组织）；不直接改正文、不写 `texts/`
- 返回顶层：按幕(目)的 Anti-AI 报告——每章列出 AI 味/模板化表达/解释腔/机械重复/不自然对白等证据、原句定位、严重倾向（严重/中等/轻微），并标注是否越出局部编辑边界
- 完成判定：同批每章均经全量扫描并列于报告
- 下一跳：`edit.synthesize`
- 恢复入口：只重扫缺失或被证据点名的章节

### edit.synthesize
- 触发：`edit.anti-ai` 完成（两份报告齐备）
- 加载模块：`skills/review-archive.md`（整体返修裁决章节）
- 创建角色：edit-synthesizer ×1（范围 = 同一批章节的整体裁决）
- 角色输入：Reader 冷读报告 + Anti-AI 报告（同批章节）；必要承接与已确认事实
- 允许写入：当前 task 的整体返修意见（分级 + 章节 + 怎么修 + 问题归属 + 优先级）；不写正文、规划或 `texts/`
- 返回顶层：整体返修意见——对每章每个问题标注来源（冷读 / Anti-AI），评估严重等级（严重/中等/轻微），明确修哪一章、怎么修、跨章关联与处理优先级；给出分流建议（REGENERATE 类 → writer/prompt-crafter/planner；局部表达类 → anti-ai 编辑模式）
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
- 下一跳：Reader 重新顺序阅读受影响范围
- 恢复入口：保留原文与候选，按返修意见重新交对应角色

### edit.commit
- 触发：受影响范围重新顺序复读后无未解决问题
- 加载模块：`skills/review-archive.md`
- 创建角色：novel-agent 自身（无 subagent）
- 角色输入：已复读接受候选、task 报告、目标路径
- 允许写入：`texts/`、控制面文件、run-log 和 task 收尾
- 返回顶层：提交结果和下一长期阶段
- 完成判定：`edit.commit` 预检通过
- 下一跳：下一范围、`volume.complete` 或 `book.complete`
- 恢复入口：预检失败不写任何目标，保留现场

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
- 角色输入：已接受正文与尚未执行的幕纲、章纲、Prompt
- 允许写入：各自拥有的规划/Prompt（已接受正文不回写）
- 返回顶层：对齐后的产物差异
- 完成判定：尚未执行产物与已接受正文一致
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

规划角色只写自己负责的规划产物和被顶层明确分配的本卷设定；prompt-crafter 不写规划和正文；writer 不写 Prompt、设定或 `.agent`；Reader、completion-reviewer、prompt-reviewer 只返回报告。所有角色都不直接读取文风原型库，除 `volume-planner` 在项目文风尚未形成且作者需要选择方向时的形成阶段外。

## 项目事实的承接

以下文件不是第二套状态机，而是由规划阶段形成、由下游按需消费的事实来源：

| 文件 | 规划阶段用途 | Prompt/复读用途 |
|---|---|---|
| `settings/genre-setting.md` | 题材期待、作者边界和本作辨识度 | volume/act/chapter planner 与 prompt-crafter 只提取当前范围相关部分 |
| `settings/world-setting.md` | 会实际影响行动的地理、势力和规则 | planner 交叉核对；Prompt 携带本章需要的事实边界 |
| `settings/character-setting/*` | 人物可持续的欲望、关系、能力、资源和限制 | planner 与 prompt-crafter 选择当前人物事实；writer 只接收 Prompt |
| `settings/writing-preferences.md` | 作者明确确认、可跨章复用的偏好 | planner 将其转成规划选择；prompt-crafter 只提取当前章适用项 |
| `settings/foreshadowing.md` | 已进入规划或正文、会影响后续的伏笔及状态 | act/chapter planner 和 prompt-crafter 核对兑现、隐藏和余波；Reader 首读后按需追因 |
| `settings/timeline.md` | 已发生且影响承接的时间事实 | act/chapter planner 和 prompt-crafter 核对先后、间隔和人物可知范围；Reader 首读后按需追因 |
| `settings/writing-style.md` | volume-planner 与作者确认后的项目声线唯一来源 | prompt-crafter 按章提取；writer 通过 Prompt 和项目样章执行，Reader 只从正文判断 |
| `settings/context-pack.md` | 由本卷首个 `prompt.create` 任务从 `knowledge/` 裁剪压缩的预制包 | 后续 prompt-crafter 读包替代知识下钻；prompt-reviewer 可选核对 |

规划层只承接已经确认或正文已经发生的事实；不能用设定文件替代正文交付。Prompt 只携带当前章所需的事实、人物选择和边界，writer 不回读原型库或无关设定。正文一旦被接受，就成为后续规划的已发生事实；真实偏差只调整尚未执行的产物。

## 创作循环

- **规划链**（卷纲→幕→章纲→Prompt）：见 `skills/planning.md`「规划链执行入口」与 `skills/act-planning.md`「幕规划执行入口」
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
- 规划、Prompt、writer 和 Reader 分别从自己的最小恢复入口继续；不重建已经成立的范围。
- Prompt 创建恢复时，本卷 `settings/context-pack.md` 若未漂移则不重建；pack 重建只在换卷、文风或题材经作者重新确认、`alignment` 发现漂移时发生。
- Reader 或返修恢复必须从报告指定的受影响范围起点重新顺序阅读；未复读的候选不能提交。
- 顶层只在长期目标范围的产物成立后推进 `status.cursor.step`，并将恢复事实写入 task/run-log。
