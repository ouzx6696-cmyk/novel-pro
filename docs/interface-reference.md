# novel-pro 接口功能参考

本文档描述每个操作（operation）、技能模块（skill module）、角色（agent）和知识入口的实际功能与接口约定。供开发时查阅。

---

## 一、操作派发卡索引（17 张）

dispatch.md 中的每张派发卡定义了 operation 的完整契约。九字段格式：触发 → 加载模块 → 创建角色 → 角色输入 → 允许写入 → 返回顶层 → 完成判定 → 下一跳 → 恢复入口。

### outline.volume
- **触发**：初始化或上一卷完成；卷纲与设定/文风尚未确认
- **加载模块**：`skills/planning.md`
- **角色**：volume-planner ×1
- **输入**：story.md、作者方向、现有设定、必要知识；文风未形成时读 `knowledge/style/`
- **允许写入**：`volumes/volume-N.md`（按 `templates/volumes/volume-N.md` 字段 schema，`volume_contract: 1`）；分配的 `settings/` 与人物设定
- **返回**：卷纲（含主导驱动力/冲突阶梯/信息差弧线等驱动字段）、事实缺口、作者确认项
- **完成**：卷纲 contract 字段完整、`writing-style.md` 已含基准样章（缺样章不进下一阶段）、设定和文风交作者确认
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
- **允许写入**：`chapters/vol-N-ch-M.md`；完成本幕后额外写入幕级承接快照 `chapters/vol-N-act-K-handoff.md`
- **返回**：章纲路径、承接摘要、需由 Prompt 携带的关键事实、规划冲突
- **完成**：目标范围内章纲全部形成
- **下一跳**：`prompt.create`

### prompt.create
- **触发**：cursor 在 `outline.chapters` 且章纲形成
- **加载模块**：`skills/prompt.md`；首任务追加 `skills/context-pack.md`
- **角色**：prompt-crafter ×1
- **输入**：context-pack（首任务为知识库原文）、幕级承接快照 `chapters/vol-N-act-K-handoff.md`（唯一落位路径；优先；缺失或不一致时以幕纲+章纲为准）、幕纲、章纲、`writing-style.md`、`genre-setting.md`、`world-setting.md`、人物设定、`writing-preferences.md`、`foreshadowing.md`、`timeline.md`、承接入口；批次任务另含上一批次出口摘要
- **允许写入**：`prompts/vol-N-ch-M.md`；首任务另写 `settings/context-pack.md`
- **返回**：Prompt 路径、每章承接摘要、自检结论表（六核对点含字段完整性）、事实缺口或上游冲突；本卷首任务另返建包摘要；批次任务另返批次出口摘要
- **完成**：范围内每章 Prompt 落盘且顶层逐一读过（存在 ≠ 通过；顶层逐行核对自检表、对标记"成立"章节抽读原文 2-3 章复核），并已读 handoff 与幕纲/章纲核对一致，自检结论表无未解释缺口
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

### write.draft
- **触发**：`prompts.ready` 且作者选择写作模式
- **加载模块**：`skills/writing.md` + `skills/writer-construction.md`
- **角色**：writer ×N（每章独立）
- **输入**：单章 writer base + 目标 Prompt
- **允许写入**：`drafts/vol-N-ch-M.md`
- **返回**：完整纯正文或失败原因
- **完成**：当前窗口完成
- **下一跳**：`drafts.ready`

### edit.write
- **触发**：`prompts.ready` 进入编辑模式
- **加载模块**：`skills/writing.md` + `skills/writer-construction.md`
- **角色**：writer ×N
- **输入/输出**：同 write.draft
- **完成**：当前窗口完成
- **下一跳**：`edit.review`

### edit.review
- **触发**：`edit.write` 完成
- **加载模块**：`skills/review-archive.md` + `skills/cold-read-discipline.md`
- **角色**：reader ×1
- **输入**：当前幕正文和候选；首读后才读契约、Prompt、知识
- **允许写入**：不写项目产物
- **返回**：按幕(目)组织的冷读报告——幕级 verdict、已成立处、正文证据、根因、最小处理范围、保留项、建议处理角色、接受候选、复读范围
- **完成**：受影响范围全部顺序复读，无未解决问题或已分流
- **下一跳**：`edit.anti-ai`

### edit.anti-ai
- **触发**：`edit.review` 完成（冷读报告已返回）
- **加载模块**：`skills/review-archive.md`（Anti-AI 全量扫描章节）+ `skills/edit-boundary.md`
- **角色**：anti-ai ×1（范围 = 与 `edit.review` 同一批章节，全量扫描）
- **输入**：Reader 读过的同批章节正文；`knowledge/anti-ai/index.md`；不依赖 Reader 点名
- **允许写入**：当前 task 的 Anti-AI 报告（按幕/目组织）；不直接改正文、不写 `texts/`
- **返回**：按幕(目)的 Anti-AI 报告——每章列出 AI 味/模板化/解释腔/机械重复/不自然对白等证据、原句定位、严重倾向（严重/中等/轻微）、是否越界
- **完成**：同批每章均经全量扫描并列于报告
- **下一跳**：`edit.synthesize`

### edit.synthesize
- **触发**：`edit.anti-ai` 完成（两份报告齐备）
- **加载模块**：`skills/review-archive.md`（整体返修裁决章节）
- **角色**：edit-synthesizer ×1
- **输入**：Reader 冷读报告 + Anti-AI 报告（同批章节）；必要承接与已确认事实
- **允许写入**：当前 task 的整体返修意见（分级 + 章节 + 怎么修 + 问题归属 + 优先级）；不写正文/规划/`texts/`
- **返回**：整体返修意见——标注来源（冷读/Anti-AI）、严重等级（严重/中等/轻微）、修哪章怎么修、跨章关联与优先级、分流建议
- **完成**：所有问题均被分级、归属并给出可执行返修意图
- **下一跳**：`edit.repair` 或 `edit.commit`（无返修项时直接提交）

### edit.repair
- **触发**：`edit.synthesize` 完成（整体返修意见已返回，且存在需返修项）
- **加载模块**：`skills/review-archive.md`（按整体返修意见执行）；表达编辑分流到 `skills/edit-boundary.md`
- **角色**：按返修意见分流建议创建 → 严重(REGENERATE)：新 writer / prompt-crafter / planner；中等/轻微表达：anti-ai（编辑模式）
- **输入**：整体返修意见 + 受影响正文 + 必要承接与 Prompt；整体返修考虑跨章关联与处理优先级
- **允许写入**：按分流写 draft candidate / 修复 Prompt / 重建规划 / 表达候选
- **返回**：各候选完成状态与最小返修范围
- **完成**：每个候选完成并进入复读
- **下一跳**：Reader 重新顺序阅读受影响范围

### edit.commit
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
- 版本门禁（L7-13）
- 长期 cursor 表（L21-34）
- 临时 order 表（L40-58）
- 所有权总则（L255-257）
- 17 张操作派发卡（L68-253）
- 项目事实承接表（L263-273）
- 创作循环路由指针（L278-284）
- 恢复规则（L306-313）

### planning.md
**定位**：卷纲与章纲规划规则。
**操作**：`outline.volume`、`outline.chapters`。
**内容**：
- **规划链执行入口**：5 步链路表（outline.volume → act-map → act → chapters → prompt.create 的读/写/判定）+ 知识库方法映射表（每步底座/类型层调用）
- 卷纲形成：按 `templates/volumes/volume-N.md` 字段 schema（`volume_contract: 1`）——本卷目标与失败代价、主导驱动力（五型）、卷级冲突阶梯（2-4 层+转折点+对应幕）、卷级信息差弧线、人物弧线、承诺清单、卷末状态、设定需求
- 设定形成：`genre-setting.md`、`world-setting.md`、`character-setting/`、`writing-preferences.md`
- 文风形成：从 `knowledge/style/` 选原型 → 改为项目 `settings/writing-style.md`；缺基准样章不进下一阶段（样章闸门）
- 章纲形成：将幕的阶段变化拆为连续可执行章纲，每章包含 goal/reader_effect/conflict/characters/scenes/must_hold/ends_with；可选引导——key_points（段落级三锚点+字数倒推）、must_hold 三清单（must_resolve/must_hold/partial_advance）、characters 信息差轨迹、场景知识指引（按每场主导任务读 `knowledge/scene/index.md`）
- author_confirmed 机制

### act-planning.md
**定位**：幕规划规则。
**操作**：`outline.act-map`、`outline.act`。
**内容**：
- **幕规划执行入口**：2 步链路表（act-map → act 的读/写/判定）+ 知识调用（act-decomposition 拆幕、continuity 幕间承接、genre 题材幕形态叠加）
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
- 创作上下文：首任务建 context-pack，后续读 pack；幕级理解优先读幕级承接快照（含 start_state/end_state 摘要）
- 建包返回摘要：本卷首任务返回题材执行要点/边界/来源/一致性声明
- 单章 Prompt 模板（四节）：本章故事（含承接收束）、人物动机与情绪、场景展开（场景叙述/行动脉络/本场怎么写/本场声线）、必守事实与边界；叙述型自包含生成包，声线与技法逐场溶解
- 四步转化法（章纲 → Prompt 的过程）：锚定角色 → 锚定信息差 → 锚定情绪递进 → 溶解输出；与自检七项衔接（四步是写的过程、自检是写完的检查）
- 场景权重标注：每章 1 核心场景 + 至多 1 低权重转场（≤100 字）
- 案例骨架：单章 Prompt 四节结构示范（每节的信息粒度与职责，非固定文案）
- 自检结论：返回时按章附一行式自检表（六核对点：must_hold 落入/故事连贯含承接收束/动机情绪有递进/场景有行动-反制-选择-余波/每场声线有落点且不复诵/字段完整性）
- 幕内连续性；批次出口摘要（承接入口/已锁事实/末章 ends_with/注意点）
- 完成语义：全部 Prompt 落盘后 cursor 进 `prompts.ready`
- 显式 Prompt 审查规则
- 引用 `knowledge/scene/self-contained-prompt.md` 作为自包含方法论

### context-pack.md
**定位**：知识预制包规则。
**消费者**：本卷首个 `prompt.create` 任务的 prompt-crafter。
**内容**：
- 形成者：本卷第一个 prompt.create 任务的 prompt-crafter
- 消费者：本卷后续所有 prompt.create 任务
- 建包：通用写作底座（webnovel 连载基线 + scene/plot/character 索引与子文件）+ 类型风格知识（genre 画像叠加），压缩为 8 节
- 建包子文件选择清单：按卷叙事重心（冲突/人物/事件/开篇）映射 scene/plot/character 必选子文件，每类 1-3 个
- 用包：后续任务读 1 个文件替代 8-18 个文件
- 补包：未覆盖时单点补读
- 重建：换卷 / genre-setting 或 writing-style 重确认 / alignment 发现漂移

### writer-construction.md
**定位**：writer base 构造规范。
**操作**：`write.draft`、`edit.write`。
**内容**：
- novel-agent 如何从 `templates/runtime/novel-base.md` 构造单章 writer base（模板分两部分：构造指南 + 参考模板）
- 实例化使用 4 项信息：章节标识、任务模式、Prompt 路径、输出路径、返修焦点
- 声线核对（不写入 base）：构造时核对 Prompt「本章故事」叙述能示范项目声线且各场「本场声线」为可执行落点，空泛时返回缺口；声线以 Prompt 内承载材料（叙述示范 + 各场落点）为唯一指令源，不复制进 base
- base 建立身份和创作边界（通用框架），Prompt 提供本章内容与声线
- 单章独立：每章独立 base、独立 Prompt、独立上下文、独立输出

### writing.md
**定位**：写作/编辑模式调度与写作原则。
**操作**：`write.draft`、`edit.write`。
**内容**：
- 写作模式流程图：prompts.ready → writer → drafts → 顶层阅读 → drafts.ready
- 写作模式调度：批次组织、已写保留、只派未完成章节、顶层阅读判断
- 写作模式阅读信号清单：接受信号 / 重派信号 / 回退信号
- 编辑模式调度：全稿 writer 派发、完成后到 edit.review
- 真实展开原则：5 条写作原则（具体空间、人物选择、对白回应、情绪显现、选择余波）

### review-archive.md
**定位**：编辑模式阅读闭环。
**操作**：`edit.review`、`edit.anti-ai`、`edit.synthesize`、`edit.repair`、`edit.commit`。
**内容**：
- 编辑模式创作流程（六步：edit.write → edit.review → edit.anti-ai → edit.synthesize → edit.repair → edit.commit）
- 阅读闭环：Reader 按幕(目)冷读 → Anti-AI 全量扫描报告 → `edit.synthesize` 整体返修裁决 → repair → 复读 → commit
- 分流与分级（由 `edit.synthesize` 裁决）：来源归属 + 严重等级（严重/中等/轻微）+ 分流建议
- 最小正文核对权限：edit-synthesizer 仅对报告分歧/断言需验证的章节只读关键段落，核对范围写入返修意见
- 报告模板：冷读报告（7 节）、Anti-AI 扫描报告（按幕/目）、整体返修意见（分级 + 章节 + 怎么修 + 跨章关联 + 优先级）
- Commit 四步：读取接受候选 → 预检 → 写入 → 清理
- 幕间校准：比较终点与下一幕 start_state

### cold-read-discipline.md
**定位**：冷读共享权威源。
**操作**：`edit.review`、`completion.inspect`。
**内容**：
- 冷读协议：先读正文 → 产生反应 → 判断成立 → 追查根因
- HARD FIX 定义（synopsis delivery）
- 分流语义（IGNORE：保留 / EDIT：局部编辑 / REGENERATE：重写）
- 复读纪律：重新顺序阅读，不只看原标签
- 复读范围判定清单：局部 EDIT / 单章 REGENERATE / 跨章跨幕 / Prompt 修复 / completion 全书复读

### edit-boundary.md
**定位**：局部编辑约束边界。
**消费者**：anti-ai、completion-editor。
**内容**：
- 禁止项：新增场景/线索/伏笔/字数、改剧情/人物选择/POV/信息顺序、做词频/AI味评分或统一润色
- 边界无法确认时保留原文
- 区分 anti-AI（普通编辑模式 表达）与 completion-editor（完本 EDIT）

### completion-quality.md
**定位**：完本质检。
**操作**：`completion.inspect`、`completion.revise`。
**内容**：
- completion.inspect 流程：scope → cold read by act → whole-book reread → evidence trace → synthesize
- completion.revise 流程：scope → assess → plan → candidate → holistic reread → whole-book reread
- 分流路由：EDIT → completion-editor；REGENERATE → 新 writer / prompt-crafter / planner
- 普通编辑模式 表达仍走 anti-ai；只有显式 completion.revise 才走 completion-editor

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
**定位**：agent 文件结构与返回规范权威源。
**消费者**：全部 agent 文件（按五要素组织）；新建/修改 agent 时参照。
**内容**：
- 五要素结构：身份与边界 / 本步任务 / 本步重点 / 调用与输入 / 完成判定与返回
- 返回四要素：写入产物、返回摘要、下一跳信号、失败/冲突证据
- 引用与一致性：agent 与 dispatch 派发卡、SKILL.md 路由表、interface-reference 角色表三方对齐规则

---

## 三、角色功能说明（12 个）

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
- **输入**：卷纲、当前幕纲、7 个 setting 文件、相邻接口、正文入口
- **返回**：章纲路径、承接摘要、需由 Prompt 携带的关键事实、规划冲突
- **写入**：`chapters/vol-N-ch-M.md`；幕级承接快照 `chapters/vol-N-act-K-handoff.md`（含 start_state/end_state 摘要，唯一落位 `chapters/`）

### prompt-crafter
- **类别**：Prompt 创建
- **skill**：`skills/prompt.md`（首任务 + `skills/context-pack.md`）
- **知识挂载**：webnovel、genre、scene、plot、character（首任务建包时读取，后续读 pack）
- **输入**：context-pack、幕级承接快照（优先）、幕纲、章纲、7 个 setting 文件、承接入口；批次任务另含上一批次出口摘要
- **返回**：Prompt 路径、承接摘要、自检结论表、事实缺口或上游冲突；本卷首任务另返建包摘要；批次任务另返批次出口摘要
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
- **类别**：表达处理（报告 + 编辑，编辑模式内两模式）
- **skill**：`skills/edit-boundary.md`
- **知识挂载**：`knowledge/anti-ai/index.md`
- **输入**：报告模式（edit.anti-ai）读同批章节正文；编辑模式（edit.repair）读返修意见中的表达问题点名
- **返回**：报告模式返回 Anti-AI 报告（按幕/目，不动文）；编辑模式 返回局部编辑候选
- **写入**：task 报告 / task 候选

### edit-synthesizer
- **类别**：编辑模式整体返修裁决
- **skill**：`skills/review-archive.md`
- **知识挂载**：无（以两份报告为主，不对正文全面重读；仅报告分歧/断言需验证时只读关键段落核对证据）
- **输入**：Reader 冷读报告 + Anti-AI 报告（同批章节）；必要承接与已确认事实
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
Writer base 模板。两部分结构：

**第一部分 · 主代理构造指南**：base 是什么、何时构造、怎么构造、构造纪律（含"不复制 Prompt 内容"原则）。

**第二部分 · 单章 base 参考模板**，7 个节：
1. 身份 — writer 的人格与职责
2. 当前任务 — mode、chapter、prompt、output、repair_focus（每章填写，其余通用节保留）
3. 写作方式 — 基于 Prompt 行动而非大纲
4. 真实展开 — 具体空间、人物选择、对白、情绪、余波
5. 展开工具箱 — 场景展开通用要点（防流程化、双方目标、信息密度等）
6. 文风执行 — 以 Prompt 内承载的声线材料（「本章故事」叙述示范 + 各场「本场声线」落点；contract-2 以「本章质感」为准）为唯一指令源 + 项目级声线硬规则（标点/禁用句式/章末纪律）
7. 交付 — 纯正文 + 返回自检陈述（3-4 行）

base 与 Prompt 职责分开：base 提供通用写作框架，Prompt 提供本章内容与声线；base 不复制 Prompt 内容。

### context-pack.md
知识预制包模板。8 个节：
1. 读者与节奏基线
2. 题材执行要点
3. 冲突、钩点与节奏方法
4. 场景写法工具箱（按场景性质分条索引，供逐场溶解取用；含自包含 Prompt 方法）
5. 人物决策与对手压力
6. 文风提取接口（全章基调 + 逐场落点两层提取）
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
