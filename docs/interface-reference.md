# novel-pro 接口功能参考

本文档描述每个操作（operation）、技能模块（skill module）、角色（agent）和知识入口的实际功能与接口约定。供开发时查阅。

---

## 一、操作派发卡索引（18 张）

dispatch.md 中的每张派发卡定义了 operation 的完整契约。九字段格式：触发 → 加载模块 → 创建角色 → 角色输入 → 允许写入 → 返回顶层 → 完成判定 → 下一跳 → 恢复入口。

### outline.volume
- **触发**：初始化或上一卷完成；卷纲与设定/文风尚未确认
- **加载模块**：`skills/planning.md`
- **角色**：volume-planner ×1
- **输入**：story.md、作者方向、现有设定、必要知识；文风未形成时读 `knowledge/style/`
- **允许写入**：`volumes/volume-N.md`（按 `templates/volumes/volume-N.md` 字段 schema，`volume_contract: 1`）；分配的 `settings/` 与人物设定
- **返回**：卷纲（含主导驱动力/冲突阶梯/信息差弧线等驱动字段）、事实缺口、作者确认项
- **完成**：卷纲 contract 字段完整、`writing-style.md` 已含基准样章（缺样章不进下一阶段）、设定和文风交作者确认
- **下一跳**：`outline.act-map`
- **恢复入口**：重读现有卷纲与设定，只补缺失或冲突项

### outline.act-map
- **触发**：卷纲/设定/文风确认
- **加载模块**：`skills/act-planning.md`
- **角色**：act-planner ×1
- **输入**：卷纲、`genre-setting.md`、`world-setting.md`、人物设定、`foreshadowing.md`、`timeline.md`、相邻正文、必要知识
- **允许写入**：`acts/volume-N-acts.md`
- **返回**：全卷阶段地图和幕边界
- **完成**：幕地图覆盖整卷，与卷纲无冲突
- **下一跳**：`outline.act` 或 `outline.chapters`
- **恢复入口**：以已存在幕地图为准继续未完成范围

### outline.act
- **触发**：幕地图完成，按幕分解；或长幕需独立详细纲
- **加载模块**：`skills/act-planning.md`
- **角色**：act-planner ×1
- **输入**：卷纲、幕地图、项目事实、相邻幕接口、正文入口
- **允许写入**：`acts/vol-N-act-K.md`
- **返回**：写入路径、幕内事实概要、相邻幕接口、无法成立的证据；详细幕纲的 start_state/dramatic_task/continuity contract/end_state 等结构化字段写入文件，由顶层从文件读取
- **完成**：目标范围内幕任务与接口共同成立
- **下一跳**：`outline.chapters`
- **恢复入口**：只重做缺失或被证据点名冲突的幕纲

### outline.chapters
- **触发**：当前幕纲成立
- **加载模块**：`skills/planning.md`
- **角色**：chapter-planner ×1
- **输入**：卷纲、当前幕纲、`genre-setting.md`、`world-setting.md`、`character-setting/`（含 state_history）、`writing-preferences.md`、`foreshadowing.md`、`timeline.md`、相邻接口、正文入口
- **允许写入**：`chapters/vol-N-ch-M.md`（9 必填字段：goal/reader_effect/conflict/characters/info_gap/scenes/must_hold/chapter_end_state/ends_with + 可选 key_points/must_hold 三清单/设定变更通知）；完成本幕后额外写入幕级承接快照 `chapters/vol-N-act-K-handoff.md`
- **返回**：章纲路径、承接摘要、需由 Prompt 携带的关键事实、规划冲突
- **完成**：目标范围内章纲全部形成
- **下一跳**：顺序链路（`draft.write` 阶段，从范围首章 `prompt.create` 开始）
- **恢复入口**：从最早缺失章纲继续，并复读幕内接口

### prompt.create
- **触发**：顺序链路中，本章章纲已形成、上一章真实正文可用且必要的 delta 已捕获或正式状态已完成；order `current_chapter` 指向本章；本幕 act-pack 已由顶层建立
- **加载模块**：`skills/prompt.md`；首任务追加 `skills/context-pack.md`
- **角色**：prompt-crafter ×1（单章）
- **输入**：**幕级复用资料包 `.agent/cache/vol-N-act-K-act-pack.md`（先核 source hash；本幕稳定资料压缩：context-pack 摘要、writing-style 提取卡、题材/作者边界、幕纲与 handoff 稳定事实、出场角色稳定事实、台账结构）**、本章章纲（含 info_gap/chapter_end_state）、**上一章真实正文（验收稿 drafts/ 或已提交正文 texts/，必读）**、可选上一章 chapter-delta、出场角色档案 state_history 最新块；包缺失或 hash 失效时回退完整读取（context-pack、幕纲、handoff、`settings/` 六件套按章筛读）
- **允许写入**：`prompts/vol-N-ch-M.md`（`prompt_contract: 4`，六块，frontmatter 记录 preceding_source）；首任务另写 `settings/context-pack.md`
- **返回**：Prompt 路径、lint 状态、本章承接摘要（前情三件套来源）、语义自检结论、事实缺口或上游冲突；本卷首任务另返建包摘要；不回显 Prompt 正文
- **完成**：`prompts/vol-N-ch-M.md` 落盘且顶层逐一读过（存在 ≠ 通过），lint 无错误、已读上一章真实正文与状态/delta 核对一致，语义自检无未解释缺口
- **下一跳**：顶层轻量审查（lint + Prompt 阅读 + 自检表）——无明确问题 → `write.draft` / `edit.write`；发现明确问题或作者要求 → `prompt.review`
- **恢复入口**：只重做缺失或被正文证据点名的 Prompt；act-pack 未漂移不重建，pack 未漂移不重建

### prompt.review（按需细节审查）
- **触发**：顶层轻量审查发现明确问题（lint 错误超 micro-fix 边界、语义自检缺口、前情/信息差/可执行性存疑）、作者明确要求强制细节审查，或幕内首章/返修重写章被顶层点名；通过轻量审查的章不派发
- **加载模块**：`skills/prompt.md`「两级审查 · 细节审查」
- **角色**：prompt-reviewer ×1（单章）
- **输入**：`prompt_lint.py` 结果 + 目标 Prompt + 顶层指出的疑点 + `preceding_source` 对应上一章真实正文 + 幕纲 + 章纲 + 角色档案 state_history
- **允许写入**：不写任何产物（报告写入当前 task）
- **返回**：PASS / FIX / STOP 结构化短报告（真实前情、层间一致、信息差、核心场景可执行性；F/H/I 默认警告）
- **完成**：报告给出明确结论
- **下一跳**：PASS → `write.draft` 或 `edit.write`；机械问题且不超过 3 处 → micro-fix、保存 diff、重跑 lint；FIX → 返回 `prompt.create`；STOP → 交规划层
- **恢复入口**：保留报告，对未通过的 Prompt 重新审计

### write.draft
- **触发**：本章 Prompt 审计通过且作者选择写作模式
- **加载模块**：`skills/writing.md` + `skills/writer-construction.md`
- **角色**：writer ×1（单章）
- **输入**：单章 writer base + 目标 Prompt
- **允许写入**：`drafts/vol-N-ch-M.md`；重派写 task candidate
- **返回**：固定短状态或失败原因；正文只写目标文件，不在消息中回显
- **完成**：目标文件完整，或按产物优先恢复完成至多一次自动重试
- **下一跳**：顶层阅读三向判定——接受 → `state.update phase: delta`；重派 → 本卡；回退 → `prompt.create`
- **恢复入口**：空返回/取消/异常先检查目标文件；完整则直接进入顶层阅读，缺失或截断才用相同 Prompt/profile 自动重试一次；第二次失败保留现场并停止盲目重派

### edit.write
- **触发**：本章 Prompt 审计通过且作者选择编辑模式
- **加载模块**：`skills/writing.md` + `skills/writer-construction.md`
- **角色**：writer ×1
- **输入/输出**：同 write.draft
- **完成**：目标文件完整，或按产物优先恢复转入一次自动重试
- **下一跳**：幕内每章草稿完成后 `state.update`（`phase: delta` 轻量工作态增量，不写 settings）；幕内全部草稿形成后 `edit.review`
- **恢复入口**：空返回/取消/异常先检查目标文件；完整则继续，缺失或截断才用相同 Prompt/profile 自动重试一次；第二次失败保留现场

### edit.review
- **触发**：本幕草稿全部形成（幕末批量审读）
- **加载模块**：`skills/review-archive.md` + `skills/cold-read-discipline.md`
- **角色**：reader ×1（一幕）
- **输入**：本幕正文和候选（上下文含前幕已提交正文）；首读后才读契约、Prompt、知识
- **允许写入**：不写项目产物
- **返回**：按幕(目)组织的冷读报告——幕级 verdict、已成立处、正文证据、根因、最小处理范围、保留项、建议处理角色、接受候选、复读范围
- **完成**：受影响范围全部顺序复读，无未解决问题或已分流
- **下一跳**：`edit.anti-ai`
- **恢复入口**：按受影响范围从头顺序复读

### edit.anti-ai
- **触发**：`edit.review` 完成（冷读报告已返回）
- **加载模块**：`skills/review-archive.md`（Anti-AI 全量扫描章节）+ `skills/edit-boundary.md`
- **角色**：anti-ai ×1（范围 = 与 `edit.review` 同幕章节，全量扫描）
- **输入**：Reader 读过的同幕章节正文；`knowledge/anti-ai/index.md`；不依赖 Reader 点名
- **允许写入**：当前 task 的 Anti-AI 报告（按幕/目组织）；不直接改正文、不写 `texts/`
- **返回**：按幕(目)的 Anti-AI 报告——每章列出 AI 味/模板化/解释腔/机械重复/不自然对白等证据、原句定位、严重倾向（严重/中等/轻微）、是否越界
- **完成**：同幕每章均经全量扫描并列于报告
- **下一跳**：`edit.synthesize`
- **恢复入口**：只重扫缺失或被证据点名的章节

### edit.synthesize
- **触发**：`edit.anti-ai` 完成（两份报告齐备）
- **加载模块**：`skills/review-archive.md`（整体返修裁决章节）
- **角色**：edit-synthesizer ×1
- **输入**：Reader 冷读报告 + Anti-AI 报告（同幕章节）；必要承接与已确认事实
- **允许写入**：当前 task 的整体返修意见（分级 + 章节 + 怎么修 + 问题归属 + 优先级）；不写正文/规划/`texts/`
- **返回**：整体返修意见——标注来源（冷读/Anti-AI）、严重等级（严重/中等/轻微）、修哪章怎么修、跨章关联与优先级（含 REGENERATE 是否触发后继章前情刷新）、分流建议
- **完成**：所有问题均被分级、归属并给出可执行返修意图
- **下一跳**：`edit.repair` 或 `edit.commit`（无返修项时直接提交）
- **恢复入口**：保留两份报告与返修意见，只重做缺失章节的裁决

### edit.repair
- **触发**：`edit.synthesize` 完成（整体返修意见已返回，且存在需返修项）
- **加载模块**：`skills/review-archive.md`（按整体返修意见执行）；表达编辑分流到 `skills/edit-boundary.md`
- **角色**：按返修意见分流建议创建 → 严重(REGENERATE)：新 writer / prompt-crafter / planner；中等/轻微表达：anti-ai（编辑模式）
- **输入**：整体返修意见 + 受影响正文 + 必要承接与 Prompt；REGENERATE 改变既定事实时，从被重写章的后一章开始重做 prompt.create（前情刷新）与 edit.write
- **允许写入**：按分流写 draft candidate / 修复 Prompt / 重建规划 / 表达候选
- **返回**：各候选完成状态与最小返修范围
- **完成**：每个候选完成并进入复读
- **下一跳**：Reader 重新顺序阅读受影响范围（复读通过后 `edit.commit`）
- **恢复入口**：保留原文与候选，按返修意见重新交对应角色

### edit.commit
- **触发**：本幕复读后无未解决问题
- **加载模块**：`skills/review-archive.md`
- **角色**：novel-agent 自身（无 subagent）
- **输入**：已复读接受候选、task 报告、目标路径
- **允许写入**：`texts/`（逐章）、控制面文件、run-log、task 收尾
- **返回**：提交结果和下一长期阶段
- **完成**：预检通过
- **下一跳**：`state.update phase: commit`（逐章，同锚点覆盖刷新；幕末章含幕总结）；目标范围全部提交后 → `volume.complete` 或 `book.complete`
- **恢复入口**：预检失败不写任何目标，保留现场

### state.update（顺序链路默认步骤）
- **触发**：本章草稿完成时执行 `phase: delta`；编辑模式 `edit.commit` 完成后执行 `phase: commit`
- **加载模块**：`skills/state-sync.md`
- **角色**：continuity-updater ×1（单章）
- **输入**：phase、草稿或最终 `texts/`；章纲（chapter_end_state + 设定变更通知块）；幕纲（设定变更通知块）；既有 settings/
- **允许写入**：delta 阶段只返回 `chapter-delta`，由顶层写当前 task；commit 阶段才写 `settings/character-setting/*.md`、`timeline.md`、`foreshadowing.md`，移除已消费通知并在幕末生成/更新幕总结
- **返回**：delta 阶段返回 source hash、角色/信息/时间线/伏笔/通知/偏差；commit 阶段返回追加清单、消费/保留通知和偏差清单
- **完成**：delta 已捕获，或 commit 已按最终 `texts/` 幂等回流并标记 committed
- **下一跳**：delta 完成后 → 下一章 `prompt.create`；commit 完成后 → 下一章/下一幕或 `drafts.ready` / `volume.complete`
- **恢复入口**：按 source hash 检查；delta 缺失/失效则重提取，commit 同 hash 已完成则跳过

### completion.inspect（旁路）
- **触发**：作者要求显式全书冷读
- **加载模块**：`skills/completion-quality.md` + `skills/cold-read-discipline.md`
- **角色**：completion-reviewer ×1
- **输入**：当前 task 指定的 `texts/`；首读后才读根因资料
- **允许写入**：不写正文、规划或状态
- **返回**：完本报告、分流和最小返修范围
- **完成**：按幕冷读全书并追查根因
- **下一跳**：`completion.revise` 或完成
- **恢复入口**：从最早受影响幕重新顺序阅读

### completion.revise（旁路）
- **触发**：`completion.inspect` 报告点名最小范围
- **加载模块**：`skills/completion-quality.md` + `skills/edit-boundary.md`
- **角色**：completion-editor ×1
- **输入**：被点名章节、问题卡（`{章节路径, IGNORE/EDIT/REGENERATE, 根因类别, 具体问题描述, 编辑约束}`）、相邻正文和已确认事实
- **允许写入**：当前 task 的局部完整候选
- **返回**：EDIT 候选或 REGENERATE 建议
- **完成**：候选经受影响范围和全书承接复读
- **下一跳**：completion-reviewer 复读
- **恢复入口**：不符合边界时放弃候选，返回上游

### alignment（旁路）
- **触发**：作者明确要求整卷产物对齐
- **加载模块**：`skills/volume-alignment.md`
- **角色**：各产物拥有者按范围分配
- **输入**：已接受正文与尚未执行的幕纲、章纲、Prompt
- **允许写入**：各自拥有的规划/Prompt（已接受正文不回写）
- **返回**：对齐后的产物差异
- **完成**：尚未执行产物与已接受正文一致
- **下一跳**：返回顶层，不改变主线
- **恢复入口**：保留已确认正文，不创建空返修链

### migration.review（临时占用 cursor）
- **触发**：`cursor.step: migration.review`
- **加载模块**：`skills/migration.md`
- **角色**：novel-agent 自身
- **输入**：`.migration/report.md`、迁移状态节点
- **允许写入**：不写创作产物；finalize 后更新迁移节点
- **返回**：迁移确认结论
- **完成**：作者完成 finalize
- **下一跳**：恢复 `migration.resume_step`
- **恢复入口**：保留报告与现场，不推进创作

---

## 二、技能模块功能说明（15 个）

### dispatch.md
**定位**：控制面权威源。定义状态机、操作派发卡、所有权总则、恢复规则。
**消费者**：novel-agent（启动时全量加载）。
**关键内容**：
- 版本门禁（novel-pro-0.3）
- 长期 cursor 表（8 阶段，含顺序链路说明）
- 临时 order 表（18 种操作，含 current_chapter 逐章推进）
- 所有权总则（含 continuity-updater 只追加 settings 状态历史区）
- 18 张操作派发卡（含 state.update）
- 项目事实承接表
- 创作循环路由指针
- 恢复规则（逐章断点）

### planning.md
**定位**：卷纲与章纲规划规则。
**操作**：`outline.volume`、`outline.chapters`。
**内容**：
- **规划链执行入口**：4 步链路表（outline.volume → act-map → act → chapters 的读/写/判定）+ 知识库方法映射表；Prompt 创建已移出规划链（顺序链路承担）
- 卷纲形成：按 `templates/volumes/volume-N.md` 字段 schema（`volume_contract: 1`）——本卷目标与失败代价、主导驱动力（五型）、卷级冲突阶梯、卷级信息差弧线、人物弧线、承诺清单、卷末状态、设定需求；字段链：信息差弧线 → 幕纲 → 章纲 `info_gap` → Prompt 前情/角色初始状态
- 设定形成：`genre-setting.md`、`world-setting.md`、`character-setting/`（含 state_history）、`writing-preferences.md`
- 文风形成与风格蒸馏（同前）
- 章纲形成：9 必填字段（goal/reader_effect/conflict/characters/**info_gap**/scenes/must_hold/**chapter_end_state**/ends_with）；可选引导——key_points、must_hold 三清单、设定变更通知块；场景知识指引
- author_confirmed 机制
- 顺序链路交接：章纲完成后进入 `draft.write`，Prompt 逐章创建

### act-planning.md
**定位**：幕规划规则。
**操作**：`outline.act-map`、`outline.act`。
**内容**：
- **幕规划执行入口**：2 步链路表 + 知识调用
- 整卷幕地图、详细幕纲（11 字段）
- 幕间承接
- 「设定变更通知」块规范（消费后移除，正文兑现才写入 settings）
- 引用 `knowledge/plot/act-decomposition.md` 作为拆幕方法论

### prompt.md
**定位**：单章 Prompt 创建与两级审查规则。
**操作**：`prompt.create`、`prompt.review`。
**内容**：
- 作者确认前置条件（`author_confirmed` 检查）
- 任务范围：**单章**，跟随正文顺序逐章创建（顺序链路）
- 创作上下文：**幕级复用资料包 act-pack**（本幕稳定资料，先核 hash）+ 本章动态资料（上一章真实正文入口，必读，提取前情三件套：上章结尾画面/情绪残留/缺口；角色档案 state_history 最新块）；包失效时回退完整读取
- 建包返回摘要：本卷首任务返回题材执行要点/边界/来源/一致性声明
- 单章 Prompt 模板默认是 **Contract 4 六块**：前情上下文、本章故事（含承接收束）、角色初始状态、人物动机与情绪、场景展开（场景叙述/行动脉络/本场怎么写/本场声线）、必守事实与边界（含信息差变化）；frontmatter 记录 preceding_source。Contract 5 五块仅作开发版同幕 A/B 实验，必须经质量指标对照后才可切换默认
- 四步转化法：锚定角色 → **角色认知重建（锚定信息差）** → 锚定情绪递进 → 溶解输出；结构项由 `prompt_lint.py` 检查，语义项由顶层轻量审查或 reviewer 核对
- 场景权重标注：每章 1 核心场景 + 至多 1 低权重转场（≤100 字）
- 案例骨架：六块结构示范
- 自检结论：返回时按章附 lint 状态和语义自检短表（承接、状态/动机、场景行动链、信息差、声线）
- 顺序链路与承接：冲突回顶层；完成语义为单章完成（无 prompts.ready 批量节点）
- **两级审查**：prompt_lint.py 预检后顶层轻量审查（无明确问题直接进写作）；发现明确问题或作者要求时派发 prompt.review 细节审查（PASS/FIX/STOP）；F/H/I 默认警告
- 引用 `knowledge/scene/self-contained-prompt.md` 作为自包含方法论

### context-pack.md
**定位**：预制包规则（卷级知识包 context-pack + 幕级复用资料包 act-pack）。
**消费者**：本卷首个 `prompt.create` 任务的 prompt-crafter（context-pack）；顶层（act-pack 建立）+ 幕内每章 prompt-crafter（act-pack 使用）。
**内容**：
- 形成者：本卷第一个 prompt.create 任务的 prompt-crafter（context-pack）；顶层在幕首章前（act-pack）
- 消费者：本卷后续所有 prompt.create 任务
- 建包：通用写作底座 + 类型风格知识，压缩为 8 节
- 建包子文件选择清单：按卷叙事重心映射；**角色类跨重心默认叠加 arc-continuity（状态变更记录方法）**
- 用包：后续任务读 1 个文件替代 8-18 个文件；承接入口特指上一章真实正文
- **幕级复用资料包（act-pack）**：顶层幕首章前建 `.agent/cache/vol-N-act-K-act-pack.md`（manifest + 语义摘要）；幕内每章只读 act-pack + 本章动态资料（章纲/上一章真实正文/chapter-delta/角色 state_history 最新块）；换幕重建，hash 失效重建，缺包回退完整读取
- 补包、重建（同前）

### state-sync.md
**定位**：状态回流规则（"当前状态"系统）。
**操作**：`state.update`。
**内容**：
- 触发：草稿完成时 phase: delta / `edit.commit` 后 phase: commit
- 输入：草稿或最终定稿 + 章纲（chapter_end_state/设定变更通知）+ 幕纲（设定变更通知）+ 既有 settings/
- 增量字段：角色状态、信息持有、时间线、伏笔、设定通知、正文 source hash 与 chapter_end_state 偏差；由顶层保存到 task 的 chapter-delta/working-state
- 五项正式回流：角色 state_history 状态块、timeline 章节锚点条目、foreshadowing 台账推进、设定变更通知消费（移除源块）、**幕末章生成幕总结 `summaries/vol-N-act-K.md`**
- 幂等与回滚：按章节锚点追加，宁少删；幕总结 based_on 相同且未返修时跳过
- 纪律：只写正文已兑现事实、只追加不覆盖、认知层 1-3 变更须有支撑事件；幕总结是派生缓存非真相源

### writer-construction.md
**定位**：writer base 构造规范。
**操作**：`write.draft`、`edit.write`。
**内容**：
- novel-agent 如何从 `templates/runtime/novel-base.md` 构造单章动态 writer 任务
- 实例化使用章节标识、任务模式、Prompt 路径、输出路径、返修焦点；可选复用 hash 有效的 writer-profile
- 声线核对（不写入 base）；contract-4 下「前情上下文」「角色初始状态」是 Prompt 专属事实块，writer 不自行回读上一章正文
- base/profile 建立身份和创作边界（通用框架），Prompt 提供本章内容与声线；空返回按产物优先规则最多自动重试一次

### writing.md
**定位**：顺序链路调度与写作原则。
**操作**：`write.draft`、`edit.write`。
**内容**：
- **顺序链路执行入口**：链路表（幕首章前顶层建 act-pack → prompt.create（读 act-pack + 本章动态资料）→ prompt_lint + 顶层轻量审查 →（按需 prompt.review）→ write.draft/edit.write → 顶层阅读 → state.update delta/commit）
- 写作模式流程：逐章循环（一章验收后才创建下一章 Prompt）
- 写作模式阅读信号清单：接受信号 / 重派信号 / 回退信号
- 编辑模式调度：逐章写作、幕末批量审读
- 真实展开原则：5 条写作原则
- 恢复：current_chapter 逐章断点

### review-archive.md
**定位**：编辑模式阅读闭环。
**操作**：`edit.review`、`edit.anti-ai`、`edit.synthesize`、`edit.repair`、`edit.commit`。
**内容**：
- 编辑模式创作流程（逐章写作 + 幕末批量审读；返修后前情刷新）
- 阅读闭环：Reader 按幕冷读（上下文含前幕已提交正文）→ Anti-AI 同幕全量扫描 → `edit.synthesize` 整体返修裁决 → repair → 复读 → commit（逐章）
- 分流与分级（同前）
- 最小正文核对权限（同前）
- 报告模板：冷读报告（按幕/目）、Anti-AI 扫描报告（按幕/目）、整体返修意见（分级 + 章节 + 怎么修 + 跨章关联含前情刷新标记 + 优先级）
- Commit 四步；提交后 `state.update`（逐章，同锚点覆盖刷新；幕末章含幕总结）
- 幕间校准：与 state.update 分工（正文事实→settings；规划核对→校准）

### cold-read-discipline.md
**定位**：冷读共享权威源。
**操作**：`edit.review`、`completion.inspect`。
**内容**：（同前，复读范围判定清单不变）

### edit-boundary.md
**定位**：局部编辑约束边界。
**消费者**：anti-ai、completion-editor。
**内容**：（同前）

### completion-quality.md
**定位**：完本质检。
**操作**：`completion.inspect`、`completion.revise`。
**内容**：（同前）

### volume-alignment.md
**定位**：整卷产物对齐。
**操作**：`alignment`。
**内容**：
- 只在作者明确要求时运行
- 检查幕纲、章纲和 Prompt 是否共同服务卷目标
- **状态文件与正文连续性检查**（state_history 缺失、信息持有矛盾即漂移）
- Context-pack 漂移核对
- 已接受正文不回写

### migration.md
**定位**：项目迁移。
**操作**：`migration.review`。
**内容**：
- 迁移入口：`python tools/migrate.py <旧> <新>`
- 迁移流程：create → 读报告 → 作者确认 → finalize → cleanup
- v0.2 长期阶段映射（prompts.ready/review → draft.write）；旧版 Prompt 标记 legacy，顺序链路触达时重建
- 安全边界：迁移期间不创建创作角色、不运行同步

### agent-return-spec.md
**定位**：agent 文件结构与返回规范权威源。
**消费者**：全部 agent 文件（按五要素组织）；新建/修改 agent 时参照。
**内容**：（同前）

---

## 三、角色功能说明（13 个）

> **`skill` / `知识挂载` 字段体例**：规划、Prompt、编辑类角色通过 frontmatter `skills:` 与 `knowledge:` 显式挂载模块和知识索引。`writer`、`reader`、`completion-reviewer` 三者下表标「无」属设计例外：它们由 dispatch 在创建时通过 base + Prompt（writer）或纯冷读输入（reader / completion-reviewer）注入上下文，实行零知识隔离，因此 frontmatter 不带 `skills:` 字段。下表的「skill」「知识挂载」列对这三者分别记为「无（上下文由 base + Prompt 组成）」「无（不接触 knowledge/）」等，是 frontmatter 体例外在权威表述。
>
> **文件结构规范**：所有 agent 文件按 `skills/agent-return-spec.md` 的五要素结构组织（身份与边界 / 本步任务 / 本步重点 / 调用与输入 / 完成判定与返回），返回覆盖四要素（写入产物 / 返回摘要 / 下一跳信号 / 失败冲突证据）。下表是各角色在对应派发卡中的输入、返回与写入的权威速查。

### novel-agent
- **类别**：顶层调度器（同时持有控制面权限和可调度角色身份）
- **skill**：`skills/dispatch.md`
- **知识挂载**：`.agent/status.yaml`（控制面读取）
- **输入**：story.md → status → order → dispatch
- **行为**：按 operation 加载模块 → 创建 subagent → 收回产物 → 判断 → 更新状态
- **写入权限**：独占 `.agent/`、`texts/`（edit.commit）、task 元数据、run-log

### volume-planner
- **类别**：规划
- **skill**：`skills/planning.md`
- **知识挂载**：webnovel、genre、style、plot、character
- **输入**：story.md、作者方向、现有设定
- **返回**：卷纲、事实缺口、作者确认项
- **写入**：`volumes/volume-N.md`、分配的 settings

### act-planner
- **类别**：规划
- **skill**：`skills/act-planning.md`
- **知识挂载**：webnovel、genre、plot、character
- **输入**：卷纲 → 项目事实 → 相邻幕接口 → 正文入口
- **返回**：写入路径、幕内事实概要、相邻幕接口、无法成立的证据
- **写入**：`acts/volume-N-acts.md` 或 `acts/vol-N-act-K.md`

### chapter-planner
- **类别**：规划
- **skill**：`skills/planning.md`
- **知识挂载**：webnovel、genre、plot、scene（按每场主导任务读对应场景方法）、character
- **输入**：卷纲、当前幕纲、7 个 setting 文件（含 character-setting state_history）、相邻接口、正文入口
- **返回**：章纲路径、承接摘要、需由 Prompt 携带的关键事实、规划冲突
- **写入**：`chapters/vol-N-ch-M.md`（9 必填字段，含 info_gap/chapter_end_state）；幕级承接快照 `chapters/vol-N-act-K-handoff.md`（含 start_state/end_state 摘要，唯一落位 `chapters/`）

### prompt-crafter
- **类别**：Prompt 创建
- **skill**：`skills/prompt.md`（首任务 + `skills/context-pack.md`）
- **知识挂载**：webnovel、genre、scene、plot、character（首任务建包时读取，后续读 pack）
- **输入**：幕级复用资料包 act-pack（先核 source hash；本幕稳定资料）、本章章纲、**上一章真实正文（必读，同幕读全文 / 跨幕首章另读上一幕幕总结）**、角色档案 state_history 最新块；包失效时回退完整读取（context-pack、幕纲、handoff、7 个 setting 文件）
- **返回**：Prompt 路径、本章承接摘要、自检结论表（七核对点）、事实缺口或上游冲突；本卷首任务另返建包摘要
- **写入**：`prompts/vol-N-ch-M.md`（contract-4 六块，frontmatter 记录 preceding_source）；首任务另写 `settings/context-pack.md`

### prompt-reviewer
- **类别**：Prompt 细节审查（**按需派发**：顶层轻量审查发现明确问题、作者要求，或幕内首章/返修重写章被顶层点名时）
- **skill**：`skills/prompt.md`「两级审查 · 细节审查」
- **知识挂载**：无
- **输入**：目标 Prompt + 顶层指出的疑点 → `preceding_source` 对应上一章真实正文 → 幕纲和章纲 → 角色档案 state_history
- **返回**：PASS / FIX / STOP 结构化短报告（四类语义结论，机械问题转 micro-fix）
- **写入**：不写任何产物（报告写入当前 task）

### writer
- **类别**：正文写作
- **skill**：无（上下文由 base + Prompt 组成）
- **知识挂载**：无（不接触 knowledge/）
- **输入**：单章 writer base + 单章 Prompt
- **返回**：固定短状态或失败原因；正文只写目标文件，不在返回消息中回显
- **写入**：`drafts/vol-N-ch-M.md` 或 task candidate；空返回先做产物检查，缺失/截断最多自动重试一次

### reader
- **类别**：正文阅读
- **skill**：`skills/review-archive.md` + `skills/cold-read-discipline.md`
- **知识挂载**：无（保护冷读，首读后按需追查）
- **输入**：本幕 draft、已接受正文或候选（上下文含前幕已提交正文）
- **返回**：幕级 verdict、已成立处、正文证据、根因、最小处理范围、保留项、建议处理角色、接受候选、仍未解决的问题
- **写入**：不写项目产物

### continuity-updater
- **类别**：状态回流
- **skill**：`skills/state-sync.md`
- **知识挂载**：无
- **输入**：本章验收稿/定稿、章纲（chapter_end_state/设定变更通知）、幕纲（设定变更通知）、既有 settings/；幕末章另含本幕全部正文
- **返回**：状态同步摘要（追加清单、消费/保留通知、与 chapter_end_state 的偏差清单；幕末章另含幕总结路径）
- **写入**：`settings/character-setting/*.md`（state_history 状态块）、`timeline.md`、`foreshadowing.md`；移除已消费通知块；幕末章生成 `summaries/vol-N-act-K.md`

### anti-ai
- **类别**：表达处理（报告 + 编辑，编辑模式内两模式）
- **skill**：`skills/edit-boundary.md`
- **知识挂载**：`knowledge/anti-ai/index.md`
- **输入**：报告模式（edit.anti-ai）读同幕章节正文；编辑模式（edit.repair）读返修意见中的表达问题点名
- **返回**：报告模式返回 Anti-AI 报告（按幕/目，不动文）；编辑模式 返回局部编辑候选
- **写入**：task 报告 / task 候选

### edit-synthesizer
- **类别**：编辑模式整体返修裁决
- **skill**：`skills/review-archive.md`
- **知识挂载**：无（以两份报告为主，不对正文全面重读；仅报告分歧/断言需验证时只读关键段落核对证据）
- **输入**：Reader 冷读报告 + Anti-AI 报告（同幕章节）；必要承接与已确认事实
- **返回**：整体返修意见——来源归属、严重等级（严重/中等/轻微）、修哪章怎么修、跨章关联、优先级、分流建议；最小核对范围注明
- **写入**：不写正文/规划/`texts/`（仅返回报告供顶层持久化）

### completion-reviewer
- **类别**：完本质检
- **skill**：`skills/completion-quality.md` + `skills/cold-read-discipline.md`
- **知识挂载**：无（保护冷读）
- **输入**：当前 task 指定的 `texts/`
- **返回**：完本报告、分流和最小返修范围
- **写入**：不写正文、规划或状态

### completion-editor
- **类别**：完本编辑
- **skill**：`skills/completion-quality.md` + `skills/edit-boundary.md`
- **知识挂载**：无
- **输入**：被点名章节 + 问题卡 + 相邻正文 + 已确认事实
- **返回**：EDIT 候选或 REGENERATE 建议
- **写入**：task 候选

---

## 四、知识入口速查

知识库按两层结构组织：**通用写作底座**（跨题材，回答"怎么写"）+ **类型风格知识**（题材专属，回答"这个题材的期待与禁忌"）。消费顺序：底座先行、类型叠加。

### 通用写作底座（跨题材）

| 入口文件 | 包含 | 消费者 |
|---------|------|--------|
| `knowledge/webnovel/index.md` | 连载交付、章节最低交付、钩点与节奏（含 fanqie 基线，跨题材默认叠加） | vol/act/ch planner、prompt-crafter；Reader 冷读后 |
| `knowledge/plot/index.md` | 13 个剧情方法（冲突、钩子、幕结构、拆幕等） | vol/act/ch planner、prompt-crafter |
| `knowledge/scene/index.md` | 16 个场景方法（对白、对抗、自包含 Prompt 等） | prompt-crafter；Reader 冷读后 |
| `knowledge/character/index.md` | 3 个角色方法（决策、对手、弧光） | vol/act/ch planner、prompt-crafter |
| `knowledge/style/index.md` | 8 个文风原型 | volume-planner（文风形成阶段） |

### 类型风格知识（题材专属，叠加辅助）

| 入口文件 | 包含 | 消费者 |
|---------|------|--------|
| `knowledge/genre/index.md` | 25 个题材的画像入口（含年代重生；只写差异化，底座规则自动叠加） | vol/act/ch planner、prompt-crafter |
| `knowledge/anti-ai/index.md` | AI 表达规则（通用 + 25 题材） | anti-ai（edit.anti-ai 全量扫描 / edit.repair编辑模式） |
| `knowledge/index.md` | 主索引：两层结构声明与消费规则 | 所有 agent 按需引用 |

---

## 五、关键模板

### story.md
项目核心文件。字段：
- `skill_version: 5.3`
- `runtime_profile: novel-pro-0.3`
- `genre_id`、`parent_genre`
- `author_confirmed`（卷级布尔值，prompt-crafter 前置检查）
- 分卷规划表

### status.yaml
长期状态文件。字段：
- `cursor.step`（8 个有效值：outline.volume/outline.acts/outline.chapters/draft.write/drafts.ready/volume.complete/book.complete/migration.review）
- `migration` 节点（来源、报告、恢复阶段、文件计数、清理状态）

### order.yaml
临时任务文件。字段：
- `task_id`、`operation`、`status`（idle/running/interrupted/completed）
- `volume`、`scope`、`batch`、`subtasks`、`attempt`、`phase`
- 顺序链路：`current_chapter`、`prompt_path`、`draft_path`、`prompt_version`、`state_delta`；`context`（含 `act_pack_path`/`act_pack_hash`，幕级复用资料包）；可选 `session`、`retry`、`usage`（task-local `usage.jsonl` 路径与最后 call_id）

### novel-base.md
Writer base 模板。两部分结构：

**第一部分 · 主代理构造指南**：base 是什么、何时构造、怎么构造、构造纪律（含"不复制 Prompt 内容"原则）。

**第二部分 · 单章 base 参考模板**，7 个节：
1. 身份 — writer 的人格与职责
2. 当前任务 — mode、chapter、prompt、output、repair_focus（每章填写，其余通用节保留）
3. 写作方式 — 基于 Prompt 行动而非大纲
4. 真实展开 — 具体空间、人物选择、对白、情绪、余波
5. 展开工具箱 — 场景展开通用要点（防流程化、双方目标、信息密度等）
6. 文风执行 — 以 Prompt 内承载的声线材料（「本章故事」叙述示范 + 各场「本场声线」落点；旧版 contract-2 Prompt 以「本章质感」为准）为唯一指令源 + 项目级声线硬规则（标点/禁用句式/章末纪律）
7. 交付 — 纯正文 + 返回自检陈述（3-4 行）

base 与 Prompt 职责分开：base 提供通用写作框架，Prompt 提供本章内容与声线；base 不复制 Prompt 内容。

### context-pack.md
知识预制包模板。8 个节：
1. 读者与节奏基线
2. 题材执行要点
3. 冲突、钩点与节奏方法
4. 场景写法工具箱（按场景性质分条索引，供逐场溶解取用；含自包含 Prompt 方法）
5. 人物决策与对手压力
6. 文风提取接口（风格提示词指示句 + 两层提取 + 文章结构）
7. 禁用与边界
8. 使用纪律

---

## 六、工具链

| 工具 | 用途 | 输入 | 输出 |
|------|------|------|------|
| `init.py` | 初始化新项目 | 目标路径 + 题材编号 | 项目骨架 + 运行时资源 |
| `migrate.py` | 旧版项目迁移 | 旧项目路径 + 新项目路径 | 新项目 + 迁移报告 |
| `sync_runtime.py` | 同步 runtime 到已有项目 | 项目路径 | 更新的 agents/skills/templates |
| `runtime_manifest.py` | 部署清单（供其他工具引用） | — | 文件列表 |
| `context_cache.py` | 建立/检查派生上下文 hash 清单 | cache 类型 + 来源文件 | cache manifest / stale 状态 |
| `prompt_lint.py` | Prompt 确定性结构预检 | Prompt 路径 | text/JSON lint 结果 |
| `state_delta.py` | 按章节锚点写入/检查 task-local delta | 项目根 + task + delta JSON | chapter-delta/working-state |
| `usage_report.py` | 汇总增量与累计 usage | JSON/JSONL 调用账本 | Markdown/JSON 报告 |
| `_common.py` | 共享工具函数 | — | read_text / is_relative_to / looks_like_skill_root |
