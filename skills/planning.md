# Planning

小说项目从题材选择开始。初始化根据题材建立项目骨架，并把长期 cursor 放在 `outline.volume`。真正的创作依次完成卷纲与设定、幕结构、章纲和 Prompt；每一层只展开下一层需要的内容。`outline.acts` 是长期幕阶段，`outline.act-map` 和 `outline.act` 只是该阶段的临时 operation。

## 规划链执行入口（先读这一节）

顶层派发规划链任一 operation 前，按下列链路逐行执行；每行的「读/写」是精确文件接口，「判定」是完成条件。知识调用见下方「知识库方法映射」。

| 步骤 | operation | 角色 | 读 | 写 | 判定 → 下一跳 |
|---|---|---|---|---|---|
| 1 | `outline.volume` | volume-planner ×1 | `story.md`、作者方向、`knowledge/style/index.md`（文风起点）、题材知识 | `volumes/volume-N.md`（`volume_contract: 1`）+ 分配的 `settings/` | 卷纲 8 字段完整、`writing-style.md` 含基准样章、作者确认 → `outline.act-map` |
| 2 | `outline.act-map` | act-planner ×1 | 已确认卷纲、设定、`knowledge/plot/act-decomposition.md` | `acts/volume-N-acts.md` | 幕地图覆盖整卷、与卷纲无冲突 → `outline.act` |
| 3 | `outline.act` | act-planner ×1 | 卷纲、幕地图、项目事实、相邻幕接口 | `acts/vol-N-act-K.md`（11 字段） | start_state 承接上一幕、end_state 可被下一幕承接 → `outline.chapters` |
| 4 | `outline.chapters` | chapter-planner ×1 | 卷纲、当前幕纲、`knowledge/scene/index.md`（按主导任务）、plot/character 知识、正文入口 | `chapters/vol-N-ch-M.md`（9 必填字段 + 可选引导）+ 幕级承接快照 `chapters/vol-N-act-K-handoff.md` | 幕内承接顺序复读无冲突 → 顺序链路（写作模式 `write.draft` 或编辑模式 `edit.write`） |

**知识库方法映射**（规划链按需调用；底座先行、类型叠加，见 `knowledge/index.md`）：

| 步骤 | 底座层方法（怎么写） | 类型层（题材期待） |
|---|---|---|
| `outline.volume` | `webnovel/index.md`（连载基线）、`plot/index.md`（冲突/承诺/结构）、`character/index.md`（弧线）、`style/index.md`（文风原型，仅形成阶段） | `genre/index.md`（题材画像叠加） |
| `outline.act-map` / `outline.act` | `plot/act-decomposition.md`（第零步+六步拆幕、边界信号、验证清单、反模式）、`plot/continuity.md`（幕间承接） | `genre/index.md`（幕形态差异叠加） |
| `outline.chapters` | `scene/index.md`（按主导任务：dialogue/confrontation/transition/inner-thought/pov/scene-truth）、`plot/index.md`（conflict/hooks/pacing/foreshadowing）、`character/index.md`（decision-engine/arc-continuity） | `genre/index.md`（本幕题材节奏） |
| `prompt.create` | `scene/self-contained-prompt.md`（自检协议）、`scene/index.md` + `plot/index.md` + `character/index.md`（经 context-pack 压缩入包）、`webnovel/index.md`（fanqie 基线入包） | `genre/index.md`（题材画像经 pack 叠加） |

方法名不写进产物；只写人物选择、事件因果和读者期待（见 `knowledge/index.md` 使用纪律）。

## 卷纲与设定

volume-planner 一次负责一卷。它从作者提供的故事种子、题材、主角欲望、核心阻力、故事环境和关键规则出发，与作者确认：

- 本卷目标与失败代价。
- 冲突如何分阶段发展。
- 主要人物的选择、关系变化和卷末状态。
- 本卷需要兑现或保留的承诺。
- 本卷事件成立所需的世界、人物、能力、资源、时间、空间和表达设定。

卷纲写入 `volumes/volume-N.md`，按 `templates/volumes/volume-N.md` 的字段 schema（`volume_contract: 1`）组织：

```markdown
## 本卷目标与失败代价
## 主导驱动力        （五型：悬疑/威胁/目标/关系/信息差，决定整卷节奏）
## 卷级冲突阶梯      （2-4 层 + 转折点 + 对应幕，逐层加压）
## 卷级信息差弧线    （起点→终点 + 逐幕推进，谁在何时知道什么）
## 人物弧线          （选择困境→变化→卷末状态，关系移动）
## 承诺清单          （兑现 / 保留 / 埋下待收的悬念）
## 卷末状态          （供下一卷承接的具体状态）
## 设定需求          （只列会实际影响行动和选择的）
```

卷纲是驱动引擎不是内容清单：主导驱动力决定节奏，冲突阶梯决定幕序，信息差弧线决定信息流动。字段链对齐——冲突阶梯 → 幕纲 `conflict_development`；信息差弧线 → 幕纲 `start_state`/`end_state` → 章纲 `info_gap`（信息差轨迹）→ Prompt「前情上下文」「角色初始状态」「人物动机与情绪」；承诺清单 → 幕纲 `promises` → 章纲 `reader_effect`。已存在旧格式卷纲（缺 schema）时按缺字段回退：冲突阶梯从幕地图反推、信息差弧线从幕纲归纳；不强制全量重写。

volume-planner 同时负责形成 `settings/writing-style.md`。它按模板中的填写指引，从作者提供的声线样本出发，与作者共同确认**两个部分**：第一部分「本书写作基调与创作逻辑」（叙事者/语言气质/情绪处理/信息差管理/节奏/群像/事实纪律/文章结构——逐章生效的创作决策依据）与第二部分「写作技巧」（基准样章、对照示范、逐项指示句、声线禁区——逐场溶解的执行技法）。**基准样章是文风的硬闸门**：`settings/writing-style.md` 缺基准样章或样章只是占位符/抽象形容词时，不进入下一阶段——volume-planner 先请作者提供一段旧作/参考方向，或针对同一小场景写两种原创短试写让作者选择，再把选择沉淀为项目样章；这是创作确认，不是脚本门禁。文风文件经作者确认后锁定；后续卷需要微调时，由当卷 volume-planner 提出变更、作者确认，不静默修改。

规划阶段还要读取并承接项目的事实接口：`genre-setting.md` 的题材边界、`world-setting.md` 的规则、`character-setting/` 的人物事实、`writing-preferences.md` 的作者确认偏好、`foreshadowing.md` 的伏笔状态和 `timeline.md` 的时间事实。它们只记录会改变后续行动、理解或承接的内容；不能把未发生的正文写成事实。

创作知识的消费按知识库两层结构进行（见 `knowledge/index.md`）：**通用写作底座**（webnovel 连载基线、plot/scene/character 方法）回答"怎么写"，跨题材跨卷稳定，规划角色按任务读取；**类型风格知识**（genre 题材画像）回答"这个题材的期待与边界"，按 `genre_id` 叠加在底座之上。规划层只提取当前范围相关的部分，不把知识正文整段复制进产物。

本卷需要的设定由顶层明确分配给 volume-planner 一并形成。设定只记录本卷创作会实际使用的事实和作者方向。作者确认卷纲、必要设定和文风后，在 `story.md` 对应卷行将现有 `author_confirmed` 设为 `true`；这是唯一确认事实，cursor 才进入 `outline.acts`。

## 文风原型调用

当作者需要文风起点时，先读取 `knowledge/style/index.md`，根据目标读者体感选择一个主原型；只有确实互补时才读取一个辅原型。原型只用于帮助 volume-planner 和作者形成项目自己的 `settings/writing-style.md`，不得直接写入 Prompt 或交给 writer。

提炼时保留叙事距离、句法呼吸、对白关系、感官取舍、情绪落点和章末习惯，去掉所有来源印记与机械阈值。项目样章必须使用自己的角色、空间、关系和事件；作者确认后，后续文风以项目文件为唯一权威。

## 风格蒸馏

`settings/writing-style.md` 就是项目的**风格提示词**，可被作者**随时触发更新**（不限于规划阶段）：作者提出"蒸馏文风 / 上传样例文章 / 生成风格提示词 / 调整声线"时，由 volume-planner 执行四步蒸馏——①脱敏提取样例的创作风格（句法节奏/叙事距离/感官/对白/情绪/收束）与来源印记删除；②**分层落位**：按归属标准（写进章节叙述之前需要决策的 → 第一部分；落笔时直接执行的 → 第二部分）把特征分入两部分的对应节，结构写法进 1.3；③结合当前小说（`genre-setting.md` 题材、`story.md` 主线、已接受正文）适配；④把全部特征写成**可执行指示句**，更新 `settings/writing-style.md` 对应节，交作者确认后锁定。

蒸馏的原则与"低自由度"：风格提示词用**明确、具体、无歧义的指示句**书写，不用抽象形容词——抽象词留给执行者的自由度过大，是声线漂移与质量波动的根源。蒸馏后的提示词锁定每章写法依据：prompt-crafter 自由书写叙述与声线落点，但"写成什么样"由指示句约束，跨章稳定由同一份提示词保证。详细步骤见 `templates/settings/writing-style.md`「填写指引 · 路径二：风格蒸馏」；`author_confirmed` 确认语义与卷纲一致。

蒸馏是增强而非门禁：作者未提出时，项目按既有流程工作；已蒸馏后，prompt-crafter 以指示句为唯一声线依据。未蒸馏或文风为占位符时，仍按 `skills/prompt.md` 的缺口规则返回顶层，不自行补成通用腔。

规划不只回答“发生什么”，还要让下游知道“人在现场怎样经历它”。每个层级都优先确认：

- 当前人物此刻想得到什么、想避免什么，以及为什么不能等到以后再处理。
- 阻力如何通过别人的目标、空间、时间、资源或关系压力实际作用到行动上。
- 人物为了推进事情会隐藏、误判、保护什么，选择之后会失去什么或留下什么余波。
- 读者应该在变化发生时感到什么；这种感受来自事件后果和人物反应，不来自抽象标签。

这些问题是创作判断，不是额外字段或脚本门禁。规划可以保留空白和不确定性，只要关键选择的因果能够被正文经历。

## 幕结构

act-planner 先建立 `acts/volume-N-acts.md`，确定整卷各幕的阶段顺序、功能、自然边界和幕间接口；再按叙事顺序完成每个 `acts/vol-N-act-K.md`。

幕纲负责一段完整的状态变化：从哪些人物、关系、信息和局势开始，冲突怎样建立、加压和转向，人物作出什么选择，最终留下怎样的下一幕入口。

## 章纲

chapter-planner 一次处理一幕。它读取卷纲、当前幕纲、相邻幕接口和已经接受的正文入口，顺序形成该幕全部章纲。

每章至少交付：

```markdown
## goal
本章必须完成的故事、关系或认知变化。
## reader_effect
本章回应、加深或转移的读者期待。
## conflict
关键人物各自的目标、筹码、阻力与不能退让的理由。
## characters
人物的已知、未知、误判、关系位置和章末变化。
## info_gap（必填）
信息差轨迹：逐角色 知道/不知道 清单 + 信息差关系（谁 vs 谁）+ 信息差变化（开场→结尾）。
## scenes
每场的入场状态、行动目标、对方目标或真实阻力、策略、反制、转折、选择、结果与下一步触发；关键场景再补充 POV 人物当下注意的空间/物件、没有说出口的意图和选择留下的余波。建议每场标注主导性质（对峙/试探/日常/追逐/独处/转场），供 prompt-crafter 判断「本场怎么写」的技法落点。
## must_hold
本章承接的事实、动机、POV、关系、信息差和幕级约束。
## chapter_end_state（必填）
章末状态快照：本章结束后每个出场角色的位置/状态/关系/能力变更，写"从什么变成什么"。
## ends_with
最终动作或画面，以及下一章需要承接的状态。
```

章纲字段的可选引导（兼容旧文件，缺失不强制）：

- **`## key_points`（可选）**：段落级引导，与 `scenes` 的场景级粒度互补。每条 2-3 句笔记体，覆盖 **感官/动作/判断** 三个锚点（人物看见什么、做什么、判断出什么）；条数按目标字数倒推（目标字数 ÷ 500）；对白密集章用 场景/对话/权力 变体（现场、谁在说、谁在试探或施压）。**写法对比**——反例「她走进来，气氛尴尬」，正例「她推门进来，外套上还挂着水珠，先看了一眼桌上的信，才开口要那杯茶」。key_points 是展开引导不是正文预写，不锁定对白原文。
- **`must_hold` 三清单（可选）**：拆为 `must_resolve`（本章必须闭合）/ `must_hold`（本章承接不变）/ `partial_advance`（部分推进、留待后章）；允许空 `[]`。旧版平铺文本仍被接受。

**信息差轨迹（`info_gap`）是必填**：缺少或过简时，从幕纲 `start_state`/`end_state` 与 `scenes` 的对抗结构反推本场信息状态，不因字段可选而跳过。它是 Prompt「角色初始状态」与施压点的上游依据，也是 state.update 核对正文信息变化的参照。

**章末状态快照（`chapter_end_state`）是必填**：每章结束后每个出场角色的位置、状态、关系与能力变更，写"从什么变成什么"的可检验状态。它是 state.update 从正文回流事实时的核对锚点；正文实际写作与快照不符时，以正文为准，由 state.update 修正并回告顶层。

**设定变更通知（可选）**：规划确认了会改变项目事实的变更（新角色、关系/能力/世界变化、时间线或伏笔新条目）时，在章纲末尾追加 `## 设定变更通知` 块（目标/类型/原因/详情）。通知不是事实——只有正文兑现并验收后，才由 `state.update` 消费通知并把变更写入 `settings/`，同时从源文件移除该块防止重复消费。详细规范见 `templates/chapters/vol-N-ch-M.md`「设定变更通知」节与 `skills/state-sync.md`。

场景知识指引：`scenes` 字段按每场主导任务消费场景写法底座（`knowledge/scene/index.md`）——对白主导读 `dialogue.md`、对抗主导读 `confrontation.md`、转场读 `transition.md`、情绪/内心读 `inner-thought.md`、POV 限知读 `pov.md`、场景现场感读 `scene-truth.md`；只提取当前场需要的判断依据，不把方法名写进章纲。

chapter-planner 顺序复读整幕章纲，确认第一章承接 `start_state`，最后一章交付 `end_state`，人物、信息、能力、资源和唯一事件在幕内连续。

章纲不是把正文预写成事件提要。它应留出人物临场反应、关系中的停顿和自然措辞的空间；只有会改变理解、行动或关系的事实才需要预先锁定。

## 交给顺序链路

顶层先按幕完成目标写作范围内的章纲，再进入**顺序链路**：Prompt 不再提前批量创建，而是跟随正文顺序逐章创建——先创建第 M 章 Prompt、写作并验收第 M 章后，才创建第 M+1 章 Prompt（其「前情上下文」直接取自第 M 章真实验收稿）。

顺序链路中每章一个小循环（写作模式）：`prompt.create`（读上一章真实正文 + 当前状态文件）→ `prompt.review`（默认逐章审计）→ `write.draft`（writer ×1）→ 顶层阅读判定 → `state.update`（从验收稿回流状态）→ 下一章。编辑模式**逐章写作、幕末批量审读**，`state.update` 在 `edit.commit` 后逐章执行。完整链路见 `skills/writing.md` 与 `skills/dispatch.md`。

每章仍形成独立的 `prompts/vol-N-ch-M.md`。全部目标章节完成草稿后进入 `drafts.ready`（写作模式终点）。规划层职责不变：章纲仍是蓝图，Prompt 以前一章真实正文为准；正文实际发展偏离章纲时，按既有"回退规划层"机制修正对应章纲。
