# novel-pro v0.2 (`0.2.3-pro`)

novel-pro 中文长篇小说创作 Skill，是可独立运行的文学内核。当前项目必须使用 `runtime_profile: novel-pro-0.2`。项目从题材和卷纲开始，用幕与章纲组织长线内容，用幕级任务创建单章 Prompt，再由主代理为每章构造 writer base 并派发独立 writer。

## 版本门禁与完整迁移

门禁判定条件以 `skills/dispatch.md` 的“版本与迁移边界”为准。概要：旧项目（`story.yaml`、缺少或错误 profile、缺少迁移字段）不直接兼容，也不允许继续走运行时同步；先从当前开发版运行：

```text
python tools/migrate.py <旧项目> <新项目>
```

迁移入口会重新初始化新项目、搬运对应内容、生成差异报告。核对 `.migration/report.md` 后执行 `finalize`，再按报告执行 `cleanup --confirm`。源项目在报告核对前保持不变。

## Novel Desk 与 TASKS.md 协作

Novel Desk 是可选的本地作者工作台，不是 Agent 控制台：它不启动 Runtime、不连接 MCP、不调度 Agent。`novel-pro` 可完全脱离 Desk 运行；使用 Desk 时，双方只通过同一个项目文件夹协作。

项目根目录 `TASKS.md` 是唯一的作者到 Agent 外壳交接文件。`TASKS.md` 的字段定义、状态流转（`pending` -> `in_progress` -> `completed` / `blocked` / `cancelled`）与所有权边界以 `templates/TASKS.md` 为权威源。收到“处理任务清单”后，Agent 必须先读取所有 `pending` 项，核对 `source.path`、`source.content_hash` 和可选 `source.anchor`，汇总拟处理范围与将采用的既有 Skill `operation`，并等待作者明确确认。确认后才更新任务为 `in_progress`，按原有文学流程执行，最后回写 `status`、`result.summary` 与 `result.files`。

## 主线

```text
确认题材 → 初始化骨架
→ `outline.volume`：卷纲与必要设定
→ `outline.acts`：整卷幕地图与详细幕纲
→ 章纲
→ 按幕或批次创建单章 Prompt
→ prompts.ready
→ 写作模式或编辑模式
```

Prompt 创建任务处理一幕或一个连续批次，最终仍是一章一个 `prompts/vol-N-ch-M.md`。Prompt reviewer 只在用户明确要求审核提示词时启动。本卷首个 Prompt 创建任务会从知识库裁剪压缩出 `settings/context-pack.md` 预制包，后续任务读包替代知识下钻，减少重复读取。

## Writer 派发

`templates/runtime/novel-base.md` 是主代理使用的 writer base 模板，分两部分：**构造指南**（base 是什么/何时构造/怎么构造/纪律）+ **参考模板**（标准结构）。主代理为每章生成单章 base，再创建 writer，并把该章 Prompt 交给它。

```text
novel-base template
→ chapter writer base
→ one writer + one Prompt
→ one draft
```

base 与 Prompt 职责分开：base 提供通用写作框架（身份、写作方式、真实展开、展开工具箱、项目级声线禁区、交付）；Prompt 提供本章剧情、承接、文风、题材与收束（含「本章质感」声线指令）。base 不复制 Prompt 内容，本章声线以 Prompt 为唯一指令源。

## 写作模式

写作模式从 `prompts.ready` 开始，为目标范围内每章创建独立 writer，输出未经 Reader 文学验收的草稿到 `drafts/`。顶层仍阅读实际文字并决定接受、重派或返回 Prompt 创建；写作模式不进入编辑模式 Reader、表达编辑和 `texts/` 提交链。全部目标草稿形成后进入 `drafts.ready`。

## 编辑模式

编辑模式同样从 `prompts.ready` 开始：

```text
edit.write → edit.review（Reader 按幕冷读报告）
→ edit.anti-ai（Anti-AI 全量扫描同批章节报告）
→ edit.synthesize（整体返修裁决：分级 + 修哪章怎么修 + 问题归属）
→ edit.repair（按整体返修意见整体返修）→ edit.commit
```

Reader 按幕(目)冷读出冷读报告；anti-ai 随后全量扫描同批章节出 Anti-AI 报告（不动文）；edit-synthesizer 综合两份报告，标注问题来源（冷读/Anti-AI）、评估严重等级（严重/中等/轻微），给出整体返修意见（明确修哪章、怎么修、跨章关联与优先级）；`edit.repair` 据此整体返修，接受正文写入 `texts/`。

## 运行态

- `.agent/status.yaml`：长期创作阶段和迁移状态。
- `.agent/order.yaml`：当前任务、范围、批次与 subtasks。
- `.agent/tasks/<task-id>/`：报告、候选和恢复现场。
- `.agent/run-log.yaml`：重大失败、中断、重写和作者决策。

新项目初始化后的 cursor 为 `outline.volume`。初始化只创建骨架，卷纲和必要设定由 volume-planner 与作者共同形成。

## 初始化

```text
python tools/init.py <project-path> --genre <题材编号>
```

初始化接受不存在的目录或空目录，并部署项目骨架与运行时资源。

## 角色

| 角色 | 任务范围 |
|---|---|
| `novel-agent` | 顶层阶段调度、writer base 构造、恢复与提交 |
| `volume-planner` | 一卷卷纲与必要设定 |
| `act-planner` | 整卷幕地图或一个详细幕 |
| `chapter-planner` | 一幕全部章纲 |
| `prompt-crafter` | 一幕或一个连续批次的多章 Prompt |
| `prompt-reviewer` | 用户显式要求的 Prompt 审查 |
| `writer` | 一章草稿或内容返修 |
| `reader` | 一幕（目）冷读与复读 |
| `anti-ai` | 编辑模式全量表达扫描报告 + 按返修意见的局部编辑候选 |
| `edit-synthesizer` | 综合两份报告，分级并给整体返修意见 |
| `completion-reviewer` | 显式完本阅读 |
| `completion-editor` | 显式完本任务中的局部编辑 |

脚本只处理初始化、当前项目同步、完整迁移和文件安全，不做文学评分、关键词门禁或 AI 味判定。小说质量由创作角色与 Reader 对实际文字的顺序阅读、人物选择、场景过程和阅读体验判断。

`novel-agent` 独占 `.agent/status.yaml`、`.agent/order.yaml`、`.agent/tasks/<task-id>/` 元数据、`.agent/run-log.yaml` 和 `edit.commit` 对 `texts/` 的写入。其他角色只写自己的规划产物、Prompt、draft 或 task candidate，Reader、completion-reviewer 和 prompt-reviewer 只返回报告。

## 文档

- **[`docs/framework-overview.md`](docs/framework-overview.md)** — 架构、数据流、状态机、版本体系、扩展机制
- **[`docs/interface-reference.md`](docs/interface-reference.md)** — 操作契约、模块功能、角色接口、知识入口、模板结构

## 操作与路径

初始化流程统一理解为：确认题材 → 初始化骨架 → 从 `outline.volume` 开始规划。`outline.acts` 是长期创作阶段；`outline.act-map`、`outline.act` 是该阶段中的临时 operation。显式能力还包括全书质检 `completion.inspect`、完本返修 `completion.revise` 和整卷产物对齐 `alignment`，它们不改变长期 cursor。

仓库说明使用源码路径 `skills/`、`agents/`、`templates/runtime/`。初始化后，这些资源分别部署到项目的 `.claude/skill-resources/` 和 `.claude/agents/`，因此项目内 `CLAUDE.md` 使用部署路径。项目设定由规划层形成，prompt-crafter 按章消费；writer 不直接读取原型库。`tools/init.py` 是发行清单中的初始化入口；源码仓库的开发验证资产不进入发行文件清单。
