---
name: novel-pro
version: "0.2.3-pro"
description: "novel-pro 中文长篇小说创作 Skill，是可独立运行的文学内核：题材初始化、卷幕章规划、单章 Prompt 与 writer、写作模式草稿、编辑模式（Reader 冷读 + Anti-AI 全量扫描 + 整体返修裁决）返修、显式 Prompt 审查、完本质检与整卷对齐。与 Novel Desk 协作时，只通过项目根目录 TASKS.md 交接作者请求；先汇总 pending 范围与 Skill 路径、等待作者确认，再按既有流程执行并回写结果。仅支持当前 runtime_profile: novel-pro-0.2；旧项目必须完整迁移。"
agent_created: true
---

# novel-pro v0.2

发行号：`0.2.3-pro`。当前项目必须使用 `story.md` 的 `skill_version: 5.2` 与 `runtime_profile: novel-pro-0.2`。

这是中文长篇小说创作 Skill。它用卷、幕和章纲保持长线连续性，用幕级 Prompt 创建保持阶段理解，用单章 writer 保留每章的创作注意力，再由 Reader 对真实正文作出文学判断。

## 产品位置与本地协作

`novel-pro` 是可独立运行的文学内核：Agent Host 加本地项目文件夹即可执行完整创作流程。Novel Desk 是可选的本地作者工作台，只提供文件编辑、快照、报告展示和作者请求入口；它不启动 Runtime、不连接 MCP，也不调度或监控 Agent。

Desk 存在时，项目根目录 `TASKS.md` 是唯一的作者到 Agent 外壳交接文件，不是第二套创作状态机。`TASKS.md` 的字段定义、状态流转与所有权边界以 `templates/TASKS.md` 为权威源，本节只描述处理流程。收到“处理任务清单”或发现 Desk 创建的任务时：

1. 读取全部 `pending` 项，核对 `source.path`、`source.content_hash`、可选 `source.anchor` 和 `scope`；来源已变化时先重读并向作者说明差异。
2. 汇总拟处理的文件、范围和将采用的既有 Skill `operation`，等待作者在 Agent 对话中明确确认。
3. 确认后才把相应项更新为 `in_progress`，并按本 Skill 原有的规划、Prompt、写作、编辑模式、Reader、完本或迁移流程执行。
4. 把候选和报告写入既有 Skill 产物位置；完成、受阻或取消时更新同一项的 `status`、`result.summary` 和 `result.files`。

没有 Desk 时，Skill 不要求 `TASKS.md`，原有对话式使用方式保持不变。完整迁移不自动搬运 `TASKS.md`：旧项目保留作为协作历史，新项目在第一次创建 Desk 任务时才生成新的清单。

## 版本门禁与项目迁移

版本门禁的完整判定条件以 `skills/dispatch.md` 的“版本与迁移边界”为准。概要：发现旧项目特征（`story.yaml`、缺少或错误 `runtime_profile`、缺少迁移字段）时停止创作，提示作者完成完整项目迁移；`cursor.step: migration.review` 表示迁移目标尚未 finalize，只允许阅读报告和处理迁移。

从当前开发版运行：

```text
python tools/migrate.py <旧项目> <新项目>
```

迁移会在新目录重新初始化当前项目，搬运故事、设定、规划、Prompt、草稿和正文，写入 `.migration/report.md` 与机器可读报告，并列出已完成文件、新版缺失内容文件、未映射旧文件和可清理旧运行时文件。旧项目创建阶段保持不变。作者核对报告后运行 `finalize`，再按报告运行 `cleanup --confirm`；清理不删除正文、规划、设定、任务历史或未映射文件。

## 创作主线

```text
确认题材
→ 初始化骨架
→ 卷纲与本卷必要设定
→ 整卷幕地图与详细幕纲
→ 按幕形成章纲
→ 按幕或连续批次创建单章 Prompt
→ prompts.ready
→ 写作模式或编辑模式
```

初始化只建立项目骨架。新项目从 `outline.volume` 开始，依次完成卷纲、幕纲、章纲和 Prompt。Prompt 全部形成后才进入自动写作。

## 任务粒度

- volume-planner 一次负责一卷。
- act-planner 一次负责整卷幕地图或一个详细幕。
- chapter-planner 一次负责一幕章纲；完成本幕后额外生成幕级承接快照。
- prompt-crafter 一次负责一幕；长幕时一次负责一个连续批次。
- 每章形成一个独立 Prompt 文件。
- writer 一次负责一章。
- Reader 一次顺序阅读一幕。
- completion-reviewer 按叙事顺序一次一幕地冷读全书（显式完本任务）。

批量用于减少调度等待，同时保留真实创作范围：Prompt 创建共享幕级理解（经幕级承接快照），writer 保持单章独立上下文，Reader 保持幕级连续阅读。

## 角色地图

| 类别 | 角色 | 任务范围 |
|---|---|---|
| 顶层调度 | `novel-agent` | 阶段调度、writer base、恢复与提交 |
| 规划 | `volume-planner`、`act-planner`、`chapter-planner` | 卷纲、幕纲与章纲 |
| Prompt | `prompt-crafter`、`prompt-reviewer` | Prompt 创建与用户显式要求的审核 |
| 正文 | `writer`、`reader` | 单章创作与整幕冷读复读 |
| 表达 | `anti-ai` | 编辑模式全量表达扫描报告 + 按返修意见的局部编辑候选 |
| 返修裁决 | `edit-synthesizer` | 综合两份报告，分级并给整体返修意见 |
| 完本 | `completion-reviewer`、`completion-editor` | 显式完本阅读与局部 EDIT 候选 |

## Prompt 创建

prompt-crafter 先读取目标卷 `story.md` 的 `author_confirmed`。缺失或为 `false` 时返回作者确认需求，不创建 Prompt。确认后从当前幕纲、任务范围内的章纲、有效承接、人物设定、项目文风、作者偏好、伏笔、时间线、题材和相关创作知识建立完整理解，再顺序写出范围内每章的 `prompts/vol-N-ch-M.md`。

每份 Prompt 把章纲转成人物可以执行的行动过程：目标、筹码、阻力、策略、反制、转折、选择、后果和下一步触发。文风与题材在创建阶段转化为本章的表达材料；下游只使用项目 `settings/writing-style.md`，不直接读取文风原型。

普通幕由一个 prompt-crafter 创建全部 Prompt。长幕按叙事子阶段切成连续批次，每个批次创建多章独立 Prompt。长期目标范围内的 Prompt 全部完成后进入 `prompts.ready`。

## 显式 Prompt 审查

Prompt reviewer 只响应用户明确的审核提示词请求。它先独立阅读目标 Prompt，再读取所在幕纲和对应章纲，形成 `PASS`、`FIX` 或 `STOP` 报告。

Prompt 审查是按需能力，不参与 `prompts.ready` 的形成，也不作为写作模式或编辑模式的默认步骤。

## Writer Base

`templates/runtime/novel-base.md` 是主代理构造 writer 子代理的模板，分两部分：**第一部分是主代理构造指南**（base 是什么、何时构造、怎么构造、纪律），**第二部分是单章 base 参考模板**。进入 写作、编辑模式 首稿或内容返修时，主代理先读第一部分获得构造方法，再按第二部分模板结合目标章节、任务模式、Prompt、输出位置和明确的返修焦点写成单章 writer base。

base 与 Prompt 职责严格分开：**base 提供通用写作框架**（身份、写作方式、真实展开、展开工具箱、项目级声线禁区、交付），**Prompt 提供本章专属内容**（承接、人物、场景、本章质感）。base 不复制 Prompt 的章节内容与质感；本章声线以 Prompt「本章质感」为唯一指令源。主代理构造时对 Prompt 质感做核对，空泛时返回缺口。

主代理使用这份 base 创建独立 writer，并交付一个目标 Prompt。writer 的完整创作上下文由单章 base 与单章 Prompt 组成。

## 写作模式（Writing Mode）

**工作目标**：从 `prompts.ready` 批量生成未经 Reader 文学验收的草稿，产出到 `drafts/`，完成于 `drafts.ready`。它交付"可读的创作过程"——每章草稿是人物行动、阻力、选择与后果的完整展开，但尚未经过编辑模式的文学验收、表达扫描与正文提交。适合：快速推进情节、先产出再精修、作者需要先看到内容全貌。

**工作流程**：
```text
prompts.ready
→ write.draft：每章构造 writer base + 独立 writer
→ writer 写 drafts/vol-N-ch-M.md（附展开自检陈述）
→ 顶层按阅读信号清单三向判定（接受 / 同一 Prompt 重派 / 回退 prompt.create）
→ 全部目标草稿形成
→ drafts.ready（写作模式终点）
```

**调度机制**：顶层从 `prompts.ready` 出发，为目标范围内每章构造单章 base 并创建独立 writer；批次只安排 writer 并发，已有草稿保留，当前批次只派发未完成章节。顶层阅读实际草稿后选择接受、重派或回退，文件存在/字段齐全/字数达标都不能替代这次阅读。写作模式不进入编辑模式链：不加载 Reader、anti-ai、edit-synthesizer，不写 `texts/`。作者后续可继续编辑模式精修草稿。每步精确的读/写/判定见 `skills/writing.md` 的「执行入口」，构造 base 的方法见 `templates/runtime/novel-base.md` 第一部分。

## 编辑模式（Editing Mode）

**工作目标**：从 `prompts.ready` 经过完整的"写 → 读 → 扫 → 裁 → 修 → 提交"闭环，产出经 Reader 文学验收并写入 `texts/` 的正文。它交付"已验收的正文"——每一章都经过内容冷读、表达全量扫描、分级裁决与按证据返修，目标是正文达到作者可接受、可发布的完成度。

**工作流程**：
```text
prompts.ready
→ edit.write：writer ×N 写首稿 drafts/
→ edit.review：Reader 按幕冷读，出冷读报告
→ edit.anti-ai：Anti-AI 全量扫描同批章节，出 Anti-AI 报告（不动文）
→ edit.synthesize：edit-synthesizer 读两份报告，分级（严重/中等/轻微）并给整体返修意见
→ edit.repair：按整体返修意见分流返修
    ├─ 严重(REGENERATE) → 新 writer / prompt-crafter / planner
    └─ 中等/轻微表达 → anti-ai 编辑模式（edit-boundary）
→ Reader 按复读范围判定清单重新顺序冷读
→ 无未解决问题时 edit.commit → texts/vol-N-ch-M.md
```

**调度机制**：`edit.write` 使用与写作模式相同的单章 writer 创建方式；已存在的 draft 由顶层实际阅读后决定是否进入编辑链。`edit.review` 由 Reader 按幕顺序冷读，`edit.anti-ai` 随后对同批章节全量扫描表达问题；`edit.synthesize` 综合两份报告给出整体返修意见（含最小正文核对权限），顶层据此选择返修路径（原 Prompt 重派 / prompt-crafter 修 Prompt / planner 调整 / anti-ai 表达编辑）。每次返修后 Reader 按判定清单复读；复读通过后 `edit.commit` 由 novel-agent 预检并写入 `texts/`。完整时序、分流与复读纪律见 `skills/dispatch.md` 的「创作循环」与 `skills/review-archive.md`；每步精确的读/写/判定见 `skills/review-archive.md` 的「阅读闭环步骤（六步执行表）」。

## 阅读与质量

文件存在、字段齐全、字数、评分、关键词、覆盖率和脚本输出不能代替文学判断。Prompt、正文和返修质量来自角色对人物行动、因果、信息变化、关系压力、情绪推进和真实阅读体验的完整阅读。

质量判断的顺序是：先读正文产生真实反应，再判断人物和场景是否成立，最后追查 Prompt、规划或表达根因。优先保留已经有生命力的语气、动作和关系细节；返修只处理正文已经证明的问题，不为满足清单而制造新句子。

脚本服务初始化、当前项目运行时同步、完整项目迁移和文件安全，仅此，不承担文学评分、关键词门禁、字数达标或 AI 味判定。Reader 首读正文后再追查规划、Prompt 或表达根因。内容问题交新的 writer，表达问题由 anti-ai 在 edit.repair 阶段按 edit.synthesize 整体返修意见执行。

## 状态与文件

长期 `.agent/status.yaml` 记录：`outline.volume`、`outline.acts`、`outline.chapters`、`prompts.ready`、`draft.write`、`drafts.ready`、`review`、`volume.complete`、`book.complete`；迁移期间使用 `migration.review`，并在 `migration` 节点记录迁移来源、报告、恢复阶段、文件计数和清理状态。

临时 `.agent/order.yaml` 记录当前 operation、phase、卷幕、章节范围、批次、subtasks、attempt、反馈路径和任务状态。
`.agent/tasks/<task-id>/` 保存当前任务的报告、候选与恢复现场；`.agent/run-log.yaml` 只记录重大失败、中断、重写和作者决策。

`outline.acts` 是长期 cursor 阶段；`outline.act-map` 和 `outline.act` 是该阶段内的临时 operation，不属于长期 cursor。显式完本使用 `completion.inspect`、`completion.revise`，整卷产物对齐使用 `alignment`；这些旁路 operation 不建立第二套长期状态。

`novel-agent` 独占上述控制面文件、task 元数据、run-log 和 `edit.commit` 对 `texts/` 的写入。规划角色、prompt-crafter、writer、Reader 和编辑角色只能写 dispatch 规定的规划产物、Prompt、draft、candidate 或返回报告；角色返回后由顶层阅读并持久化。

- `volumes/`、`acts/`、`chapters/`：已确认规划。
- `chapters/vol-N-act-K-handoff.md`：幕级承接快照（chapter-planner 生成，prompt-crafter 消费，派生摘要）。
- `prompts/vol-N-ch-M.md`：单章 Prompt。
- `drafts/vol-N-ch-M.md`：未经 Reader 文学验收的草稿。
- `texts/vol-N-ch-M.md`：Reader 接受后的正文。

项目事实接口由规划层形成并按章承接：`settings/genre-setting.md`、`world-setting.md`、`character-setting/`、`writing-preferences.md`、`foreshadowing.md`、`timeline.md` 和确认后的 `writing-style.md`。writer 不回读原始文风原型或无关设定。

## 路由（按 operation 索引）

派发的总规则与恢复见 `skills/dispatch.md`。每个 `order.operation` 对应的阶段模块与角色如下；详细触发、输入与恢复见 dispatch 的「操作派发卡」。

| `order.operation` | 加载模块 | 角色 |
|---|---|---|
| `outline.volume` | `skills/planning.md` | volume-planner |
| `outline.act-map` | `skills/act-planning.md` | act-planner |
| `outline.act` | `skills/act-planning.md` | act-planner |
| `outline.chapters` | `skills/planning.md` | chapter-planner |
| `prompt.create` | `skills/prompt.md`（首任务 + `skills/context-pack.md`） | prompt-crafter |
| `prompt.review` | `skills/prompt.md` | prompt-reviewer |
| `write.draft` | `skills/writing.md` + `skills/writer-construction.md` | writer ×N |
| `edit.write` | `skills/writing.md` + `skills/writer-construction.md` | writer ×N |
| `edit.review` | `skills/review-archive.md` + `skills/cold-read-discipline.md` | reader |
| `edit.anti-ai` | `skills/review-archive.md`（+ `skills/edit-boundary.md`） | anti-ai |
| `edit.synthesize` | `skills/review-archive.md` | edit-synthesizer |
| `edit.repair` | `skills/review-archive.md`（表达 → `skills/edit-boundary.md`） | 按整体返修意见分流 |
| `edit.commit` | `skills/review-archive.md` | novel-agent |
| `completion.inspect` | `skills/completion-quality.md` + `skills/cold-read-discipline.md` | completion-reviewer |
| `completion.revise` | `skills/completion-quality.md` + `skills/edit-boundary.md` | completion-editor |
| `alignment` | `skills/volume-alignment.md` | 各产物拥有者 |
| `migration.review` | `skills/migration.md` | novel-agent |

仓库文档使用源码路径 `skills/`、`agents/`、`templates/runtime/`。初始化项目时，运行时资源会改写到 `.claude/skill-resources/` 与 `.claude/agents/`；部署后的 `CLAUDE.md` 使用部署路径。

## 维护文档

以下文档位于 `docs/` 目录，供开发与维护时查阅：

- **[`docs/framework-overview.md`](docs/framework-overview.md)** — 项目整体框架说明。涵盖：四层架构模型、数据流（规划链/写作链/阅读链/知识链）、状态机（10 阶段 cursor + 17 种 operation）、版本体系、扩展机制、文件清单。修改系统结构前先读本文档。
- **[`docs/interface-reference.md`](docs/interface-reference.md)** — 接口功能参考。涵盖：17 张操作派发卡的完整契约、14 个 skill 模块的功能说明、12 个 agent 角色的输入/输出/权限、8 个知识入口的消费者表、5 个关键模板的结构、工具链用法。开发新功能或排查接口问题时查阅。

## 扩展契约

本 Skill 的设计支持以下三类扩展，每种扩展遵循固定的文件操作约定。

### 添加新 operation
1. `dispatch.md` 按九字段模板（触发 → 加载模块 → 创建角色 → 角色输入 → 允许写入 → 返回顶层 → 完成判定 → 下一跳 → 恢复入口）加一张派发卡
2. `skills/` 加对应流程模块
3. `agents/` 加对应角色（可复用现有角色则不需新建）
4. 新 operation 如果是旁路（不改变 `cursor.step`），在 `dispatch.md` 的旁路声明中列出；如果要改变 cursor，在长期 cursor 表中加一行
5. 本文档路由表加一行

### 添加新知识主题
1. `knowledge/` 建新目录，包含 `index.md` 和子方法文件
2. 先判定归属层：通用写作方法进底座层（webnovel/plot/scene/character/style 类），题材专属差异进类型层（genre/anti-ai 类）
3. `knowledge/index.md` 对应层表格加一行，注明入口路径和消费者
4. 需要该知识的 agent 在 frontmatter 的 `knowledge:` 中挂载
5. `skills/context-pack.md` 打包来源更新（底座方法进建包必选或清单，类型知识按题材叠加）

### 添加新题材
1. `knowledge/genre/index.md` 注册 `genre_id`，标注父题材
2. `knowledge/genre/` 加题材画像文件（只写差异化：读者期待、世界逻辑、失败模式、表达禁忌；不重复底座规则，连载基线等由通用底座自动叠加）
3. `knowledge/anti-ai/genre/` 加对应反 AI 规则文件
4. `knowledge/genre/index.md` 的"通用写作底座"声明确认覆盖新题材（无需逐文件重复 fanqie 引用）

### 不变量约束
所有扩展不得破坏以下三个不变量：
- **cursor 状态机**：10 阶段结构不变，新 operation 归入已有 cursor 下或声明为旁路
- **所有权边界**：novel-agent 仍是唯一控制面写入者
- **冷读纪律**：Reader 和 completion-reviewer 首读仍然不预挂知识
