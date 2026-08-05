# novel-pro 项目框架说明

发行号 `0.3.0-pro`，skill_version `5.3`，runtime_profile `novel-pro-0.3`。

本文档供维护者理解系统结构。修改任何组件前，先读本文档了解其在整体中的位置和约束。

---

## 一、定位

`novel-pro` 是一个**中文长篇小说创作操作系统**（Skill），可独立运行——Agent Host 加载本 Skill，配合本地项目文件夹即可执行完整创作流程。

它不只是一个 Prompt 模板集。它拥有自己的状态机、角色分工、卷/幕/章三层规划结构，以及从题材初始化到正文定稿的完整管线。

Novel Desk 是可选的本地作者工作台。Desk 存在时，双方仅通过项目根目录 `TASKS.md` 交接作者请求（schema 权威源：`templates/TASKS.md`）。没有 Desk 时，Skill 通过对话式交互运行，功能不变。

---

## 二、分层架构

```
  tools/          开发态工具（init / migrate / sync）
    │
  templates/      第零层：初始化模板（定义项目的初始骨架）
    │
  ┌────────────────────────────────────────────────┐
  │  L1 控制面    status.yaml + order.yaml         │
  │              + dispatch.md + novel-agent         │
  ├────────────────────────────────────────────────┤
  │  L2 流程规则   skills/（15 个模块）              │
  ├────────────────────────────────────────────────┤
  │  L3 角色执行   agents/（13 个角色）              │
  ├────────────────────────────────────────────────┤
  │  L4 知识库    knowledge/（7 主题，102 文件）       │
  └────────────────────────────────────────────────┘
    │
  volumes/ acts/ chapters/ prompts/ drafts/ texts/ settings/ .agent/
  项目产物
```

### L1：控制面

负责"在什么状态、触发什么操作、创建什么角色"。**novel-agent 是唯一写入者**。

- **status.yaml**：长期创作位置。记录 `cursor.step`（8 个阶段）。
- **order.yaml**：临时任务窗口。记录 `order.operation`（18 种操作）与顺序链路的 `current_chapter`。
- **dispatch.md**：派发契约。18 张操作派发卡定义每个 operation 的触发、模块、角色、输入、输出、完成判定、下一跳和恢复。
- **novel-agent**：顶层调度器。读取 status/order → 查 dispatch 派发卡 → 加载 skill 模块 → 创建 subagent → 收回产物 → 判断 → 更新状态。

### L2：流程规则

定义"怎么做"。15 个 skill 模块（按修改后状态列出）：

| 模块 | 被哪些 operation 加载 | 职责 |
|------|---------------------|------|
| `dispatch.md` | 启动时由 novel-agent 加载 | 状态机、派发卡、所有权、恢复规则 |
| `planning.md` | `outline.volume`, `outline.chapters` | 卷纲形成、章纲形成（info_gap/章末状态快照/设定变更通知）、文风确认 |
| `act-planning.md` | `outline.act-map`, `outline.act` | 幕地图、详细幕纲、幕间承接 |
| `prompt.md` | `prompt.create`, `prompt.review` | 单章 Prompt 创建（前情三件套/角色初始状态）、默认逐章审计 |
| `context-pack.md` | 首个 `prompt.create` 任务 | 知识预制包的建包/用包/重建 |
| `state-sync.md` | `state.update` | 状态回流：角色状态/时间线/伏笔/设定变更通知消费 |
| `writer-construction.md` | `write.draft`, `edit.write` | writer base 构造规范 |
| `writing.md` | `write.draft`, `edit.write` | 顺序链路调度、真实展开原则 |
| `review-archive.md` | `edit.review`, `edit.anti-ai`, `edit.synthesize`, `edit.repair`, `edit.commit` | 编辑模式幕末批量阅读闭环、Anti-AI 全量扫描、整体返修裁决、分流返修与正文提交 |
| `cold-read-discipline.md` | `edit.review`, `completion.inspect` | 冷读协议、HARD FIX 定义、分流语义 |
| `edit-boundary.md` | `edit.anti-ai`（报告边界）, `edit.repair`（表达分流）, `completion.revise` | 局部编辑约束边界 |
| `completion-quality.md` | `completion.inspect`, `completion.revise` | 完本质检范围与返修路由 |
| `volume-alignment.md` | `alignment` | 整卷产物对齐（含状态文件连续性检查） |
| `migration.md` | `migration.review` | 项目迁移流程 |
| `agent-return-spec.md` | 全部 agent 文件 | agent 文件五要素结构与返回四要素规范 |

### L3：角色执行

13 个 agent。每个 agent 声明了自己的 skill 模块和知识挂载。角色之间的上下文隔离是刻意的：

- **novel-agent**：唯一调度器。自身在 `edit.commit` 和 `migration.review` 中可被作为 subagent 创建。
- **volume-planner / act-planner / chapter-planner**：规划层。写规划产物。
- **prompt-crafter / prompt-reviewer**：Prompt 层。prompt-crafter 单章创建（前情取自真实正文）；prompt-reviewer 默认逐章独立审计（9 维度）。
- **writer / reader**：写作层。writer 只收 base + Prompt（不接触知识库）；reader 按幕冷读，首读不预挂知识。
- **continuity-updater**：状态层。每章验收/提交后从正文回流状态到 `settings/`（state_history/时间线/伏笔/通知消费）。
- **anti-ai / edit-synthesizer / completion-reviewer / completion-editor**：质检层。分别处理表达扫描与编辑、整体返修裁决、完本审查、完本编辑。

### L4：知识库

102 个文件，按 **两层结构** 组织：

- **通用写作底座**（跨题材、跨卷不变，回答"怎么写"）：webnovel（连载基线，含 fanqie-baseline）、plot（13 方法）、scene（16 方法）、character（3 方法）、style（8 文风原型）。
- **类型风格知识**（题材专属，回答"这个题材的读者期待与禁忌"）：genre（27，25 个题材画像 + 索引 + 跨题材融合，含 0.2.3-pro 新增的 `era-rebirth` 年代重生）、anti-ai（28，通用规则 + 25 个题材表达规则）。

核心消费模式（底座先行、类型叠加）：

- **规划角色**按任务读底座方法，再按 `genre_id` 叠加题材画像（建立卷纲、拆幕、形成章纲）
- **prompt-crafter** 首任务压缩"底座方法 + 题材差异"为 `context-pack.md`，后续任务读 pack
- **writer** 不接触知识库（通过自包含 Prompt 获取一切）
- **Reader** 首读不接触（冷读后才按需追查根因知识）

知识库不定义流程字段，不做质量门禁，只提供"怎么写"的判断依据。例外：`knowledge/scene/self-contained-prompt.md`（Prompt 自检协议）与 `knowledge/plot/act-decomposition.md`（拆幕方法论）虽位于 knowledge/，但已被 skills/ 硬引用为流程规则；两个文件头部均带"流程边界标注"，改动时必须同步核对引用方，不能按纯知识随意修改。

### 第零层：初始化模板

`templates/` 目录定义项目初始化时的骨架。初始化后部署到项目的 `.claude/` 和项目根目录。包含：

- `story.md`、`CLAUDE.md`：项目级入口
- `.agent/status.yaml`、`.agent/order.yaml`、`.agent/run-log.yaml`：控制面模板
- `settings/`：7 个设定模板
- `runtime/novel-base.md`：writer base 模板

### 外挂层：开发态工具

`tools/` 目录的 Python 脚本（init.py、migrate.py、sync_runtime.py、runtime_manifest.py、_common.py）。独立于 Agent 运行时，执行文件操作。

---

## 三、核心数据流

### 规划链（volume → act → chapter）

```
story.md（题材方向）
→ volume-planner → volumes/volume-N.md + settings/（卷纲、设定、文风）
→ act-planner → acts/volume-N-acts.md + acts/vol-N-act-K.md（幕地图、幕纲）
→ chapter-planner → chapters/vol-N-ch-M.md（章纲：goal/reader_effect/conflict/characters/info_gap/scenes/must_hold/chapter_end_state/ends_with + 设定变更通知）
→ 幕级承接快照 chapters/vol-N-act-K-handoff.md（派生摘要）
```

章纲仍是蓝图；Prompt 不再由规划链批量产生，而是由顺序链路逐章创建。

### 顺序链路（draft.write 阶段，逐章循环 + 幕末批量审读）

```
写作模式（每章小循环）：
第 M 章：prompt-crafter → prompts/vol-N-ch-M.md（contract-4 六块）
  ↑ 前情三件套取自上一章真实正文（同幕全文；跨幕读幕总结）；角色初始状态取自已回流的状态文件
→ prompt-reviewer → 默认逐章审计（9 维度）→ PASS/FIX/STOP
→ writer → drafts/ → 顶层阅读三向判定 → continuity-updater → state.update（状态回流）→ 第 M+1 章

编辑模式（逐章写作 + 幕末批量审读）：
第 M 章：prompt.create（前情取自上一章草稿全文）→ prompt.review → edit.write（writer ×1 写草稿）
→ 幕内全部草稿形成后：
  reader 按幕冷读 → anti-ai 同幕全量扫描 → edit-synthesizer 整体裁决
  → edit.repair 分流返修（REGENERATE 改变既定事实 → 后继章前情刷新）→ Reader 复读
  → edit.commit（逐章）→ state.update（逐章，同锚点覆盖刷新；幕末章含幕总结）→ 下一幕
```

每一次传递是**信息密度增加而非复制**。Prompt 嵌入全部此刻上下文（真实上文 + 当前状态），变成 writer 可执行的行动过程。

### 状态回流链（正文 → settings/幕总结 → 下一章 Prompt）

```
正文（验收稿 drafts/ 或定稿 texts/）
→ continuity-updater（state.update，按章锚点追加，幂等）
→ settings/character-setting/*.md（state_history 状态块）+ timeline.md（章节锚点条目）+ foreshadowing.md（台账推进）
  + 消费章纲/幕纲「设定变更通知」块
→ 幕末章额外生成 summaries/vol-N-act-K.md（幕末正文总结：事件链/人物状态/信息差/伏笔/未闭合张力/幕末承接帧）
→ 下一章 prompt-crafter：同幕读上一章全文（质感与承接）；跨幕首章读幕总结（导航）+ 上一章结尾帧
```

这是"当前状态"系统：每章验收后状态文件即反映最新事实，幕末章后幕总结压缩全幕发生的事，下一章 Prompt 永远读到最新状态——前后文矛盾的机制性解法。幕总结是**派生缓存非真相源**：每条带章节锚点，事实以正文与 `settings/` 为准。

### 阅读链（编辑模式 reader → anti-ai → synthesize → repair → commit）

```
幕内草稿全部形成（逐章 edit.write）
→ reader 按幕顺序冷读（上下文含前幕已提交正文，出冷读报告）
→ anti-ai 同幕章节全量扫描（出 Anti-AI 报告，不动文）
→ edit-synthesizer 读两份报告：标注来源 + 评估严重等级(严重/中等/轻微) + 给整体返修意见
→ edit.repair 按意见整体返修（严重 REGENERATE / 中等轻微 anti-ai 编辑；改变既定事实时后继章前情刷新）
→ 受影响范围复读 → edit.commit（逐章）→ texts/ → state.update（逐章）→ 下一幕
```

### 知识链（knowledge → context-pack → prompt-crafter）

```
通用写作底座（webnovel/plot/scene/character 索引 + 按叙事重心选子文件）
+ 类型风格知识（genre 索引 + 当前题材画像叠加）
→ 本卷首个 prompt.create 裁剪压缩
→ settings/context-pack.md（1 个文件）
→ 本卷后续 prompt.create 读 pack 替代 8-18 个原始文件
→ 换卷/换题材/文风重确认/alignment 发现漂移时重建
```

---

## 四、状态机

### 长期 cursor（8 阶段）

```
outline.volume → outline.acts → outline.chapters
→ draft.write（顺序链路：Prompt 创建/审计/写作/编辑闭环/状态同步逐章交错）
→ drafts.ready（写作模式终点）→ volume.complete → book.complete
+ migration.review（迁移专用，临时占用 cursor）
```

`prompts.ready` 与 `review` 已废除：顺序链路下 Prompt 逐章创建，编辑模式逐章写作、幕末批量审读，二者都并入 `draft.write` 阶段，由 order 的 `current_chapter` 逐章推进。

### 临时 operation（18 种）

每个 operation 对应 dispatch.md 中的一张派发卡。operation 比 cursor 更细——例如 `outline.acts` 阶段内可依次执行 `outline.act-map` 和 `outline.act`；`draft.write` 阶段内逐章交替执行 `prompt.create`/`prompt.review`/`write.draft`（或 `edit.*` 链）/`state.update`。

旁路 operation（不改变 cursor）：`completion.inspect`、`completion.revise`、`alignment`。`prompt.review` 与 `state.update` 是顺序链路默认步骤（在 `draft.write` 内执行），不是旁路。

---

## 五、版本体系

三层版本号：

| 层级 | 字段 | 位置 | 含义 |
|------|------|------|------|
| skill 版本 | `skill_version: 5.3` | story.md | skill 逻辑版本，breaking change 时递增 |
| 项目兼容 | `runtime_profile: novel-pro-0.3` | story.md | 项目兼容版本，不匹配时拒绝运行 |
| 发行号 | `0.3.0-pro` | skill.json | 追踪具体发行 |

组件级可选锚点 `changed_in` 标记文件在哪个发行中被修改，便于升级 diff。

版本门禁在 `dispatch.md` 启动时执行：旧项目特征（`story.yaml`、错误 profile、缺迁移字段）停止创作并提示迁移。v0.2 项目迁移时，旧版批量 Prompt（contract-3）标记为 legacy，顺序链路首次触达对应章节时回 `prompt.create` 重建。

---

## 六、扩展机制

系统设计支持三类扩展，均通过已有结构实现：

1. **添加新 operation**：dispatch.md 加派发卡 → skills/ 加模块 → agents/ 加角色（或复用）
2. **添加新知识主题**：knowledge/ 建目录 + 索引 → knowledge/index.md 注册 → agent 挂载。新增知识先判定归属层——通用写作方法进底座层（webnovel/plot/scene/character/style 类），题材专属差异进类型层（genre/anti-ai 类）；底座方法改动影响所有题材，类型知识改动只影响对应题材。
3. **添加新题材**：genre/index.md 注册 → knowledge/genre/ 加画像 → anti-ai/genre/ 加规则。新题材只写差异化（读者期待、世界逻辑、失败模式、表达禁忌），不重复底座规则（连载基线等已由通用底座自动叠加）。

所有扩展必须遵守的不变量：

- **cursor 状态机**：8 阶段结构不变
- **所有权边界**：novel-agent 仍是唯一控制面写入者；continuity-updater 只追加 settings/ 状态历史区
- **冷读纪律**：Reader/completion-reviewer 首读不预挂知识
- **顺序链路**：Prompt 跟随正文顺序逐章创建，前情必须取自真实正文

---

## 七、文件清单（按功能分类）

### 控制面（运行时状态 + 规则）
- `SKILL.md`：入口文档
- `skills/dispatch.md`：派发契约
- `skills/agent-return-spec.md`：agent 返回规范

### 流程规则（skills/）
- `planning.md`、`act-planning.md`：规划规则
- `prompt.md`、`context-pack.md`：Prompt 创建与默认审计规则
- `state-sync.md`：状态回流规则
- `writer-construction.md`、`writing.md`：顺序链路与写作规则
- `review-archive.md`、`cold-read-discipline.md`、`edit-boundary.md`：阅读与编辑规则
- `completion-quality.md`、`volume-alignment.md`：质检规则
- `migration.md`：迁移规则

### 角色定义（agents/）
- 13 个 agent 文件

### 知识库（knowledge/）
- 7 个主题目录 + 1 个主索引

### 模板（templates/）
- 项目级模板 + 控制面模板 + 设定模板 + 运行时模板

### 工具（tools/）
- 5 个 Python 脚本
