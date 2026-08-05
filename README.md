# novel-pro v0.3 (`0.3.0-pro`)

novel-pro 中文长篇小说创作 Skill，是可独立运行的文学内核。当前项目必须使用 `runtime_profile: novel-pro-0.3`。项目从题材和卷纲开始，用幕与章纲组织长线内容，再用**顺序链路**逐章创建 Prompt（前情上下文直接取自上一章真实正文）、逐章写作/编辑并回流状态，由主代理为每章构造 writer base 并派发独立 writer。

## 🚀 快速开始

### 初始化项目
```text
python tools/init.py <project-path> --genre <题材编号>
```

### 创作主线
```text
确认题材 -> 初始化骨架
-> outline.volume：卷纲与必要设定
-> outline.acts：整卷幕地图与详细幕纲
-> outline.chapters：章纲（含信息差轨迹/章末状态快照）
-> 顺序链路（逐章推进）：
   第 M 章：prompt.create（读上一章真实正文 + 状态文件）
   -> prompt.review（默认审计 9 维度）
   -> 写作模式 write.draft 或 编辑模式 edit.write → … → edit.commit
   -> state.update（状态回流：角色状态/时间线/伏笔/通知消费）
   -> 第 M+1 章
-> 写作模式终点 drafts.ready / 编辑模式逐章提交至 volume.complete
```

### 两种创作模式
- **写作模式**：顺序链路中逐章快速产出草稿到 `drafts/`，适合先看全貌
- **编辑模式**：逐章写作、幕末批量审读，经 Reader 冷读 + Anti-AI 扫描 + 整体返修，产出到 `texts/`，适合精修到可发布

### 新手入门
- 📖 **[15分钟快速开始指南](docs/getting-started.md)** - 从0到第一章
- 📝 **[模板填写指引](docs/templates-guide.md)** - 每个字段的详细说明
- 📚 **[示例文档](docs/examples.md)** - 完整的卷纲/幕纲/Prompt/报告示例

## 版本门禁与完整迁移

门禁判定条件以 `skills/dispatch.md` 的“版本与迁移边界”为准。概要：旧项目（`story.yaml`、缺少或错误 profile、缺少迁移字段）不直接兼容，也不允许继续走运行时同步；先从当前开发版运行：

```text
python tools/migrate.py <旧项目> <新项目>
```

迁移入口会重新初始化新项目、搬运对应内容、生成差异报告。核对 `.migration/report.md` 后执行 `finalize <新项目>`，再按报告执行 `cleanup <新项目> --confirm`。源项目在报告核对前保持不变。v0.2 迁移的旧版 Prompt（contract-3）标记为 legacy，顺序链路首次触达对应章节时回 `prompt.create` 重建。

## Novel Desk 与 TASKS.md 协作

Novel Desk 是可选的本地作者工作台，不是 Agent 控制台：它不启动 Runtime、不连接 MCP、不调度 Agent。`novel-pro` 可完全脱离 Desk 运行；使用 Desk 时，双方只通过同一个项目文件夹协作。

项目根目录 `TASKS.md` 是唯一的作者到 Agent 外壳交接文件。`TASKS.md` 的字段定义、状态流转（`pending` -> `in_progress` -> `completed` / `blocked` / `cancelled`）与所有权边界以 `templates/TASKS.md` 为权威源。收到“处理任务清单”后，Agent 必须先读取所有 `pending` 项，核对 `source.path`、`source.content_hash` 和可选 `source.anchor`，汇总拟处理范围与将采用的既有 Skill `operation`，并等待作者明确确认。确认后才更新任务为 `in_progress`，按原有文学流程执行，最后回写 `status`、`result.summary` 与 `result.files`。

## 主线：顺序链路

```text
确认题材 → 初始化骨架
→ `outline.volume`：卷纲与必要设定
→ `outline.acts`：整卷幕地图与详细幕纲
→ 章纲（蓝图，按幕批量形成）
→ 顺序链路（draft.write，逐章推进）：
   prompt.create（单章）
   → prompt.review（默认审计）
   → write.draft（写作模式）或 edit.* 闭环（编辑模式）
   → state.update（状态回流）
→ drafts.ready 或 volume.complete
```

**设计核心**：Prompt 不再提前批量创建，而是跟随正文顺序逐章创建。第 M 章 Prompt 的「前情上下文」三件套（上章结尾画面/情绪残留/缺口）直接取自第 M-1 章真实验收稿/定稿，「角色初始状态」取自已回流的状态文件（角色 `state_history`/时间线/伏笔台账）——提示词永远建立在真实上文与最新状态之上，从机制上消除前后文矛盾。每章 Prompt 落盘后由 prompt-reviewer 独立审计（9 维度），通过才进入写作。本卷首个 Prompt 创建任务会从知识库裁剪压缩出 `settings/context-pack.md` 预制包，后续任务读包替代知识下钻。

## Writer 派发

`templates/runtime/novel-base.md` 是主代理使用的 writer base 模板，分两部分：**构造指南**（base 是什么/何时构造/怎么构造/纪律）+ **参考模板**（标准结构）。主代理为每章生成单章 base，再创建 writer，并把该章 Prompt 交给它。

```text
novel-base template
→ chapter writer base
→ one writer + one Prompt
→ one draft
```

base 与 Prompt 职责分开：base 提供通用写作框架（身份、写作方式、真实展开、展开工具箱、项目级声线禁区、交付）；Prompt 提供本章专属内容（前情上下文、本章故事、角色初始状态、人物动机与情绪、场景展开、必守事实与边界，声线以叙述示范与逐场落点承载）。base 不复制 Prompt 内容，本章声线以 Prompt 内承载的声线材料为唯一指令源；contract-4 下「前情上下文」与「角色初始状态」是本章专属事实块，writer 不自行回读上一章正文。

## 写作模式

写作模式在顺序链路中逐章运行：一章的 Prompt 创建、审计、写作、验收、状态回流完成后才进入下一章。writer 输出未经 Reader 文学验收的草稿到 `drafts/`；顶层仍阅读实际文字并决定接受、重派或返回 Prompt 创建；接受后 `state.update` 从验收稿回流状态。写作模式不进入编辑模式 Reader、表达编辑和 `texts/` 提交链。全部目标草稿形成后进入 `drafts.ready`。

## 编辑模式

编辑模式**逐章写作、幕末批量审读**——写作保持顺序链路（每章 Prompt 前情直接取自上一章真实草稿全文），审读成本回到批量水平：

```text
逐章写作（幕内草稿按序形成）：
prompt.create → prompt.review（默认审计）→ edit.write（writer ×1 写草稿）
→ 幕末批量审读：
edit.review（Reader 按幕冷读，上下文含前幕已提交正文）
→ edit.anti-ai（Anti-AI 同幕章节全量扫描报告）
→ edit.synthesize（整体返修裁决：分级 + 修哪章怎么修 + 问题归属）
→ edit.repair（按整体返修意见分流返修；REGENERATE 改变既定事实时后继章前情刷新）
→ Reader 复读 → edit.commit（逐章）→ state.update（逐章，同锚点覆盖刷新）→ 幕总结
```

Reader 按幕冷读出冷读报告；anti-ai 随后全量扫描同幕章节出 Anti-AI 报告（不动文）；edit-synthesizer 综合两份报告，标注问题来源（冷读/Anti-AI）、评估严重等级（严重/中等/轻微），给出整体返修意见（明确修哪章、怎么修、跨章关联与优先级）；`edit.repair` 据此整体返修，接受正文逐章写入 `texts/`，随后 `state.update` 从定稿回流状态并生成幕总结。

## 状态同步（"当前状态"系统）

每章正文被接受（写作模式草稿验收）或提交（编辑模式 `edit.commit`）后，由 continuity-updater 执行 `state.update`：

- 向角色档案 `state_history` 节追加状态变更块（位置/状态/关系/能力/信息持有）
- 向 `timeline.md` 追加章节锚点时间线条目
- 推进 `foreshadowing.md` 伏笔台账
- 消费章纲/幕纲中的「设定变更通知」块

全部按章节锚点追加（幂等，只追加不覆盖，宁少删）。状态回流保证下一章 Prompt 读到"当前状态"，是前后文不矛盾的机制保障。

## 运行态

- `.agent/status.yaml`：长期创作阶段（9 阶段）和迁移状态。
- `.agent/order.yaml`：当前任务、范围、批次、`current_chapter`、`state_updated` 与 subtasks。
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
| `chapter-planner` | 一幕全部章纲（9 必填字段） |
| `prompt-crafter` | 单章 Prompt（顺序链路，前情取自真实正文） |
| `prompt-reviewer` | 单章 Prompt 独立审计（顺序链路默认步骤，9 维度） |
| `writer` | 一章草稿或内容返修 |
| `reader` | 单章冷读与复读（上下文含本章前全部已提交正文） |
| `continuity-updater` | 单章状态回流（state.update） |
| `anti-ai` | 编辑模式全量表达扫描报告 + 按返修意见的局部编辑候选 |
| `edit-synthesizer` | 综合两份报告，分级并给整体返修意见 |
| `completion-reviewer` | 显式完本阅读 |
| `completion-editor` | 显式完本任务中的局部编辑 |

脚本只处理初始化、当前项目同步、完整迁移和文件安全，不做文学评分、关键词门禁或 AI 味判定。小说质量由创作角色与 Reader 对实际文字的顺序阅读、人物选择、场景过程和阅读体验判断。

`novel-agent` 独占 `.agent/status.yaml`、`.agent/order.yaml`、`.agent/tasks/<task-id>/` 元数据、`.agent/run-log.yaml` 和 `edit.commit` 对 `texts/` 的写入。其他角色只写自己的规划产物、Prompt、draft 或 task candidate；continuity-updater 只追加 `settings/` 状态历史区；Reader、completion-reviewer 和 prompt-reviewer 只返回报告。

## 文档

### 入门与使用
- **[`docs/getting-started.md`](docs/getting-started.md)** - 新手15分钟快速开始指南
- **[`docs/templates-guide.md`](docs/templates-guide.md)** - 模板填写指引（每个字段的详细说明+示例）
- **[`docs/examples.md`](docs/examples.md)** - 完整示例集合（卷纲/幕纲/Prompt/文风/报告）
- **[`docs/editing-mode-guide.md`](docs/editing-mode-guide.md)** - 编辑模式指南（Reader 冷读 + Anti-AI 扫描 + 整体返修）

### 架构与开发
- **[`docs/framework-overview.md`](docs/framework-overview.md)** - 架构、数据流、状态机、版本体系、扩展机制
- **[`docs/interface-reference.md`](docs/interface-reference.md)** - 操作契约、模块功能、角色接口、知识入口、模板结构
