# novel-pro 接口功能参考

本文档描述每个操作（operation）、技能模块（skill module）、角色（agent）和知识入口的实际功能与接口约定。供开发时查阅。

---

## 一、操作派发卡索引（15 张）

dispatch.md 中的每张派发卡定义了 operation 的完整契约。九字段格式：触发 → 加载模块 → 创建角色 → 角色输入 → 允许写入 → 返回顶层 → 完成判定 → 下一跳 → 恢复入口。

### outline.volume
- **触发**：初始化或上一卷完成；卷纲与设定/文风尚未确认
- **加载模块**：`skills/planning.md`
- **角色**：volume-planner ×1
- **输入**：story.md、作者方向、现有设定、必要知识；文风未形成时读 `knowledge/style/`
- **允许写入**：`volumes/volume-N.md`；分配的 `settings/` 与人物设定
- **返回**：卷纲、事实缺口、作者确认项
- **完成**：卷纲、设定和文风交作者确认
- **下一跳**：`outline.acts`

### outline.act-map
- **触发**：卷纲/设定/文风确认
- **加载模块**：`skills/act-planning.md`
- **角色**：act-planner ×1
- **输入**：卷纲、`genre-setting.md`、`world-setting.md`、人物设定、`foreshadowing.md`、`timeline.md`、相邻正文、必要知识
- **允许写入**：`acts/volume-N-acts.md`
- **返回**：全卷阶段地图和幕边界
- **完成**：幕地图覆盖整卷，与卷纲无冲突
- **下一跳**：`outline.act` 或 `outline.chapters`

### outline.act
- **触发**：幕地图完成，按幕分解
- **加载模块**：`skills/act-planning.md`
- **角色**：act-planner ×1
- **输入**：卷纲、幕地图、项目事实、相邻幕接口、正文入口
- **允许写入**：`acts/vol-N-act-K.md`
- **返回**：写入路径、幕内事实概要、相邻幕接口、无法成立的证据
- **完成**：目标范围内幕任务与接口共同成立
- **下一跳**：`outline.chapters`

### outline.chapters
- **触发**：当前幕纲成立
- **加载模块**：`skills/planning.md`
- **角色**：chapter-planner ×1
- **输入**：卷纲、当前幕纲、`genre-setting.md`、`world-setting.md`、`character-setting/`、`writing-preferences.md`、`foreshadowing.md`、`timeline.md`、相邻接口、正文入口
- **允许写入**：`chapters/vol-N-ch-M.md`
- **返回**：章纲路径、承接摘要、需由 Prompt 携带的关键事实、规划冲突
- **完成**：目标范围内章纲全部形成
- **下一跳**：`prompt.create`

### prompt.create
- **触发**：cursor 在 `outline.chapters` 且章纲形成
- **加载模块**：`skills/prompt.md`；首任务追加 `skills/context-pack.md`
- **角色**：prompt-crafter ×1
- **输入**：context-pack（首任务为知识库原文）、幕纲、章纲、`writing-style.md`、`genre-setting.md`、`world-setting.md`、人物设定、`writing-preferences.md`、`foreshadowing.md`、`timeline.md`、承接入口
- **允许写入**：`prompts/vol-N-ch-M.md`；首任务另写 `settings/context-pack.md`
- **返回**：Prompt 路径、每章承接摘要、事实缺口或上游冲突
- **完成**：范围内每章 Prompt 落盘且顶层读过
- **下一跳**：下一批次或 cursor 进 `prompts.ready`

### prompt.review（旁路）
- **触发**：用户明确提出审核提示词
- **加载模块**：`skills/prompt.md` 末节
- **角色**：prompt-reviewer ×1
- **输入**：目标 Prompt + 对应幕纲和章纲
- **允许写入**：不写任何产物
- **返回**：PASS / FIX / STOP 报告
- **完成**：报告给出明确结论
- **下一跳**：返回作者/顶层，不改变主线

### fast.write
- **触发**：`prompts.ready` 且作者选择 Fast
- **加载模块**：`skills/writing.md` + `skills/writer-construction.md`
- **角色**：writer ×N（每章独立）
- **输入**：单章 writer base + 目标 Prompt
- **允许写入**：`drafts/vol-N-ch-M.md`
- **返回**：完整纯正文或失败原因
- **完成**：当前窗口完成
- **下一跳**：`drafts.ready`

### full.write
- **触发**：`prompts.ready` 进入 Full
- **加载模块**：`skills/writing.md` + `skills/writer-construction.md`
- **角色**：writer ×N
- **输入/输出**：同 fast.write
- **完成**：当前窗口完成
- **下一跳**：`full.review`

### full.review
- **触发**：`full.write` 完成
- **加载模块**：`skills/review-archive.md` + `skills/cold-read-discipline.md`
- **角色**：reader ×1
- **输入**：当前幕正文和候选；首读后才读契约、Prompt、知识
- **允许写入**：不写项目产物
- **返回**：幕级 verdict、已成立处、正文证据、根因、最小处理范围、保留项、建议处理角色、接受候选、复读范围
- **完成**：受影响范围全部顺序复读
- **下一跳**：`full.repair` 或 `full.commit`

### full.repair
- **触发**：`full.review` 发现未解决问题
- **加载模块**：`skills/review-archive.md`；表达分流到 `skills/edit-boundary.md`
- **角色**：按根因分流（新 writer / prompt-crafter / planner / anti-ai）
- **输入**：Reader 报告与受影响正文
- **允许写入**：按分流写 draft candidate / 修复 Prompt / 重建规划 / 表达候选
- **返回**：分流结果与最小返修范围
- **完成**：每个候选完成并进入复读
- **下一跳**：Reader 重新顺序阅读受影响范围

### full.commit
- **触发**：受影响范围复读后无未解决问题
- **加载模块**：`skills/review-archive.md`
- **角色**：novel-agent 自身（无 subagent）
- **输入**：已复读接受候选、task 报告、目标路径
- **允许写入**：`texts/`、控制面文件、run-log、task 收尾
- **返回**：提交结果和下一长期阶段
- **完成**：预检通过
- **下一跳**：下一范围、`volume.complete` 或 `book.complete`

### completion.inspect（旁路）
- **触发**：作者要求显式全书冷读
- **加载模块**：`skills/completion-quality.md` + `skills/cold-read-discipline.md`
- **角色**：completion-reviewer ×1
- **输入**：当前 task 指定的 `texts/`；首读后才读根因资料
- **允许写入**：不写正文、规划或状态
- **返回**：完本报告、分流和最小返修范围
- **完成**：按幕冷读全书并追查根因
- **下一跳**：`completion.revise` 或完成

### completion.revise（旁路）
- **触发**：`completion.inspect` 报告点名最小范围
- **加载模块**：`skills/completion-quality.md` + `skills/edit-boundary.md`
- **角色**：completion-editor ×1
- **输入**：被点名章节、问题卡（`{章节路径, IGNORE/EDIT/REGENERATE, 根因类别, 具体问题描述, 编辑约束}`）、相邻正文和已确认事实
- **允许写入**：当前 task 的局部完整候选
- **返回**：EDIT 候选或 REGENERATE 建议
- **完成**：候选经受影响范围和全书承接复读
- **下一跳**：completion-reviewer 复读

### alignment（旁路）
- **触发**：作者明确要求整卷产物对齐
- **加载模块**：`skills/volume-alignment.md`
- **角色**：各产物拥有者按范围分配
- **输入**：已接受正文与尚未执行的幕纲、章纲、Prompt
- **允许写入**：各自拥有的规划/Prompt（已接受正文不回写）
- **返回**：对齐后的产物差异
- **完成**：尚未执行产物与已接受正文一致
- **下一跳**：返回顶层，不改变主线

### migration.review（临时占用 cursor）
- **触发**：`cursor.step: migration.review`
- **加载模块**：`skills/migration.md`
- **角色**：novel-agent 自身
- **输入**：`.migration/report.md`、迁移状态节点
- **允许写入**：不写创作产物；finalize 后更新迁移节点
- **返回**：迁移确认结论
- **完成**：作者完成 finalize
- **下一跳**：恢复 `migration.resume_step`

---

## 二、技能模块功能说明（14 个）

### dispatch.md
**定位**：控制面权威源。定义状态机、操作派发卡、所有权总则、恢复规则。
**消费者**：novel-agent（启动时全量加载）。
**关键内容**：
- 版本门禁（L7-11）
- 长期 cursor 表（L19-31）
- 临时 order 表（L38-54）
- 所有权总则（L58）
- 15 张操作派发卡（L64-229）
- 项目事实承接表（L237-249）
- 创作循环路由指针（L252-261）
- 恢复规则（L263-273）

### planning.md
**定位**：卷纲与章纲规划规则。
**操作**：`outline.volume`、`outline.chapters`。
**内容**：
- 卷纲形成：卷目标、冲突阶段、人物弧线、承诺、卷末状态
- 设定形成：`genre-setting.md`、`world-setting.md`、`character-setting/`、`writing-preferences.md`
- 文风形成：从 `knowledge/style/` 选原型 → 改为项目 `settings/writing-style.md`
- 章纲形成：将幕的阶段变化拆为连续可执行章纲，每章包含 conflict、scenes、must_hold、承接信息
- author_confirmed 机制

### act-planning.md
**定位**：幕规划规则。
**操作**：`outline.act-map`、`outline.act`。
**内容**：
- 整卷幕地图：幕的阶段顺序、叙事功能、起点/终点、主要冲突
- 详细幕纲：`dramatic_task`、`start_state`、`conflict_development`、`character_arcs`、`information`、`emotional_curve`、`promises`、`setting_constraints`、`continuity_contract`、`chapter_roles`、`end_state`
- 幕间承接：按叙事顺序检查上一幕终点、当前幕起点和下一幕入口
- 引用 `knowledge/plot/act-decomposition.md` 作为拆幕方法论

### prompt.md
**定位**：单章 Prompt 创建与审查规则。
**操作**：`prompt.create`、`prompt.review`。
**内容**：
- 作者确认前置条件（`author_confirmed` 检查）
- 任务范围：一幕或一个连续批次，最终一章节一个 Prompt 文件
- 创作上下文：首任务建 context-pack，后续读 pack
- 单章 Prompt 模板（7 字段）：本章要完成的变化、承接现场、人物发动机、场景推进、必守事实与边界、收束画面、本章质感
- 幕内连续性
- 完成语义：全部 Prompt 落盘后 cursor 进 `prompts.ready`
- 显式 Prompt 审查规则
- 引用 `knowledge/scene/self-contained-prompt.md` 作为自包含方法论

### context-pack.md
**定位**：知识预制包规则。
**消费者**：本卷首个 `prompt.create` 任务的 prompt-crafter。
**内容**：
- 形成者：本卷第一个 prompt.create 任务的 prompt-crafter
- 消费者：本卷后续所有 prompt.create 任务
- 建包：读取 5 个知识索引并下钻（唯一一次全量），压缩为 8 节
- 用包：后续任务读 1 个文件替代 8-18 个文件
- 补包：未覆盖时单点补读
- 重建：换卷 / genre-setting 或 writing-style 重确认 / alignment 发现漂移

### writer-construction.md
**定位**：writer base 构造规范。
**操作**：`fast.write`、`full.write`。
**内容**：
- novel-agent 如何从 `templates/runtime/novel-base.md` 构造单章 writer base
- 实例化使用 5 项信息：章节标识、任务模式、Prompt 路径、输出路径、返修焦点
- base 建立身份和创作边界，Prompt 提供故事内容
- 单章独立：每章独立 base、独立 Prompt、独立上下文、独立输出

### writing.md
**定位**：Fast/Full 调度与写作原则。
**操作**：`fast.write`、`full.write`。
**内容**：
- Fast 流程图：prompts.ready → writer → drafts → 顶层阅读 → drafts.ready
- Fast 调度：批次组织、已写保留、只派未完成章节、顶层阅读判断
- Full 调度：全稿 writer 派发、完成后到 full.review
- 真实展开原则：5 条写作原则（具体空间、人物选择、对白回应、情绪显现、选择余波）

### review-archive.md
**定位**：Full 模式阅读闭环。
**操作**：`full.review`、`full.repair`、`full.commit`。
**内容**：
- Full 创作流程（流程图 + prose）
- 阅读闭环：Reader 按幕冷读 → 报告 → 分流 → 返修 → 复读 → commit
- 分流语义（IGNORE/EDIT/REGENERATE）委托给 `cold-read-discipline.md`
- 报告模板（7 节）：verdict、已成立处、首读、问题与处理、不应改变、仍未解决、最终复读、接受候选
- Commit 四步：读取接受候选 → 预检 → 写入 → 清理
- 幕间校准：比较终点与下一幕 start_state

### cold-read-discipline.md
**定位**：冷读共享权威源。
**操作**：`full.review`、`completion.inspect`。
**内容**：
- 冷读协议：先读正文 → 产生反应 → 判断成立 → 追查根因
- HARD FIX 定义（synopsis delivery）
- 分流语义（IGNORE：保留 / EDIT：局部编辑 / REGENERATE：重写）
- 复读纪律：重新顺序阅读，不只看原标签

### edit-boundary.md
**定位**：局部编辑约束边界。
**消费者**：anti-ai、completion-editor。
**内容**：
- 禁止项：新增场景/线索/伏笔/字数、改剧情/人物选择/POV/信息顺序、做词频/AI味评分或统一润色
- 边界无法确认时保留原文
- 区分 anti-AI（普通 Full 表达）与 completion-editor（完本 EDIT）

### completion-quality.md
**定位**：完本质检。
**操作**：`completion.inspect`、`completion.revise`。
**内容**：
- completion.inspect 流程：scope → cold read by act → whole-book reread → evidence trace → synthesize
- completion.revise 流程：scope → assess → plan → candidate → holistic reread → whole-book reread
- 分流路由：EDIT → completion-editor；REGENERATE → 新 writer / prompt-crafter / planner
- 普通 Full 表达仍走 anti-ai；只有显式 completion.revise 才走 completion-editor

### volume-alignment.md
**定位**：整卷产物对齐。
**操作**：`alignment`。
**内容**：
- 只在作者明确要求时运行
- 检查幕纲、章纲和 Prompt 是否共同服务卷目标
- Context-pack 漂移核对
- 已接受正文不回写

### migration.md
**定位**：项目迁移。
**操作**：`migration.review`。
**内容**：
- 迁移入口：`python tools/migrate.py <旧> <新>`
- 迁移流程：create → 读报告 → 作者确认 → finalize → cleanup
- 安全边界：迁移期间不创建创作角色、不运行同步

### agent-return-spec.md
**定位**：agent 返回描述规范。
**消费者**：新建 agent 时参照。
**内容**：
- 四要素：写入产物、返回摘要、下一跳信号、失败/冲突证据
- 已有 agent 不强制改写

---

## 三、角色功能说明（11 个）

### novel-agent
- **类别**：顶层调度器（同时持有控制面权限和可调度角色身份）
- **skill**：`skills/dispatch.md`
- **知识挂载**：`.agent/status.yaml`（控制面读取）
- **输入**：story.md → status → order → dispatch
- **行为**：按 operation 加载模块 → 创建 subagent → 收回产物 → 判断 → 更新状态
- **写入权限**：独占 `.agent/`、`texts/`（full.commit）、task 元数据、run-log

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
- **知识挂载**：webnovel、genre、plot、character
- **输入**：卷纲、当前幕纲、7 个 setting 文件、相邻接口、正文入口
- **返回**：章纲路径、承接摘要、需由 Prompt 携带的关键事实、规划冲突
- **写入**：`chapters/vol-N-ch-M.md`

### prompt-crafter
- **类别**：Prompt 创建
- **skill**：`skills/prompt.md`（首任务 + `skills/context-pack.md`）
- **知识挂载**：webnovel、genre、scene、plot、character（首任务建包时读取，后续读 pack）
- **输入**：context-pack、幕纲、章纲、7 个 setting 文件、承接入口
- **返回**：Prompt 路径、承接摘要、事实缺口或上游冲突
- **写入**：`prompts/vol-N-ch-M.md`；首任务另写 `settings/context-pack.md`

### prompt-reviewer
- **类别**：Prompt 审查（按需）
- **skill**：`skills/prompt.md`
- **知识挂载**：无
- **输入**：目标 Prompt → 对应幕纲和章纲
- **返回**：PASS / FIX / STOP 报告
- **写入**：不写任何产物

### writer
- **类别**：正文写作
- **skill**：无（上下文由 base + Prompt 组成）
- **知识挂载**：无（不接触 knowledge/）
- **输入**：单章 writer base + 单章 Prompt
- **返回**：完整纯正文或失败原因
- **写入**：`drafts/vol-N-ch-M.md` 或 task candidate

### reader
- **类别**：正文阅读
- **skill**：`skills/review-archive.md` + `skills/cold-read-discipline.md`
- **知识挂载**：无（保护冷读，首读后按需追查）
- **输入**：当前幕 draft、已接受正文或候选
- **返回**：幕级 verdict、已成立处、正文证据、根因、最小处理范围、保留项、建议处理角色、接受候选、仍未解决的问题
- **写入**：不写项目产物

### anti-ai
- **类别**：表达编辑（Reader 点名后）
- **skill**：`skills/edit-boundary.md`
- **知识挂载**：`knowledge/anti-ai/index.md`
- **输入**：Reader 点名的章节 + 表达问题焦点
- **返回**：局部编辑候选
- **写入**：task 候选

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

| 入口文件 | 包含 | 消费者 |
|---------|------|--------|
| `knowledge/index.md` | 主索引：定义各主题的消费者和消费规则 | 所有 agent 按需引用 |
| `knowledge/webnovel/index.md` | 连载交付、章节最低交付、钩点与节奏 | vol/act/ch planner、prompt-crafter；Reader 冷读后 |
| `knowledge/genre/index.md` | 24 个题材的画像入口 | vol/act/ch planner、prompt-crafter |
| `knowledge/style/index.md` | 8 个文风原型 | volume-planner（文风形成阶段） |
| `knowledge/plot/index.md` | 12 个剧情方法（冲突、钩子、幕结构、拆幕等） | vol/act/ch planner、prompt-crafter |
| `knowledge/scene/index.md` | 15 个场景方法（对白、对抗、自包含 Prompt 等） | prompt-crafter；Reader 冷读后 |
| `knowledge/character/index.md` | 3 个角色方法（决策、对手、弧光） | vol/act/ch planner、prompt-crafter |
| `knowledge/anti-ai/index.md` | AI 表达规则（通用 + 19 题材） | anti-ai（Reader 点名后） |

---

## 五、关键模板

### story.md
项目核心文件。字段：
- `skill_version: 5.2`
- `runtime_profile: novel-pro-0.2`
- `genre_id`、`parent_genre`
- `author_confirmed`（卷级布尔值，prompt-crafter 前置检查）
- 分卷规划表

### status.yaml
长期状态文件。字段：
- `cursor.step`（10 个有效值）
- `migration` 节点（来源、报告、恢复阶段、文件计数、清理状态）

### order.yaml
临时任务文件。字段：
- `task_id`、`operation`、`status`（idle/running/interrupted/completed）
- `volume`、`scope`、`batch`、`subtasks`、`attempt`、`phase`

### novel-base.md
Writer base 模板。7 个节：
1. 身份 — writer 的人格与职责
2. 当前任务 — mode、chapter、prompt、output、repair_focus
3. 创作上下文 — Prompt 已包含的内容清单
4. 写作方式 — 基于 Prompt 行动而非大纲
5. 真实展开 — 具体空间、人物选择、对白、情绪、余波
6. 文风执行 — 以 Prompt 的「本章质感」为准
7. 交付 — 纯正文、不混入说明

### context-pack.md
知识预制包模板。8 个节：
1. 读者与节奏基线
2. 题材执行要点
3. 冲突钩点与节奏方法
4. 场景写法工具箱（含自包含 Prompt 方法）
5. 人物决策与对手压力
6. 文风提取接口
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
| `_common.py` | 共享工具函数 | — | read_text / is_relative_to / looks_like_skill_root |
