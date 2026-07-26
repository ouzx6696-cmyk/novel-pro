# novel-pro 项目框架说明

发行号 `0.2.2-pro`，skill_version `5.2`，runtime_profile `novel-pro-0.2`。

本文档供维护者理解系统结构。修改任何组件前，先读本文档了解其在整体中的位置和约束。

---

## 一、定位

`novel-pro` 是一个**中文长篇小说创作操作系统**（Skill），可独立运行——Agent Host 加载本 Skill，配合本地项目文件夹即可执行完整创作流程。

它不只是一个 Prompt 模板集。它拥有自己的状态机、角色分工、卷/幕/章三层规划结构，以及从题材初始化到正文定稿的完整管线。

Novel Desk 是可选的本地作者工作台。Desk 存在时，双方仅通过项目根目录 `TASKS.md` 交接作者请求。没有 Desk 时，Skill 通过对话式交互运行，功能不变。

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
  │  L2 流程规则   skills/（14 个模块）              │
  ├────────────────────────────────────────────────┤
  │  L3 角色执行   agents/（11 个角色）              │
  ├────────────────────────────────────────────────┤
  │  L4 知识库    knowledge/（7 主题，88 文件）       │
  └────────────────────────────────────────────────┘
    │
  volumes/ acts/ chapters/ prompts/ drafts/ texts/ settings/ .agent/
  项目产物
```

### L1：控制面

负责"在什么状态、触发什么操作、创建什么角色"。**novel-agent 是唯一写入者**。

- **status.yaml**：长期创作位置。记录 `cursor.step`（10 个阶段）。
- **order.yaml**：临时任务窗口。记录 `order.operation`（15 种操作）。
- **dispatch.md**：派发契约。15 张操作派发卡定义每个 operation 的触发、模块、角色、输入、输出、完成判定、下一跳和恢复。
- **novel-agent**：顶层调度器。读取 status/order → 查 dispatch 派发卡 → 加载 skill 模块 → 创建 subagent → 收回产物 → 判断 → 更新状态。

### L2：流程规则

定义"怎么做"。14 个 skill 模块（按修改后状态列出）：

| 模块 | 被哪些 operation 加载 | 职责 |
|------|---------------------|------|
| `dispatch.md` | 启动时由 novel-agent 加载 | 状态机、派发卡、所有权、恢复规则 |
| `planning.md` | `outline.volume`, `outline.chapters` | 卷纲形成、章纲形成、文风确认 |
| `act-planning.md` | `outline.act-map`, `outline.act` | 幕地图、详细幕纲、幕间承接 |
| `prompt.md` | `prompt.create`, `prompt.review` | 单章 Prompt 创建、显式审查 |
| `context-pack.md` | 首个 `prompt.create` 任务 | 知识预制包的建包/用包/重建 |
| `writer-construction.md` | `fast.write`, `full.write` | writer base 构造规范 |
| `writing.md` | `fast.write`, `full.write` | Fast/Full 调度、真实展开原则 |
| `review-archive.md` | `full.review`, `full.repair`, `full.commit` | 阅读闭环、分流返修、正文提交 |
| `cold-read-discipline.md` | `full.review`, `completion.inspect` | 冷读协议、HARD FIX 定义、分流语义 |
| `edit-boundary.md` | `full.repair`（表达分流）, `completion.revise` | 局部编辑约束边界 |
| `completion-quality.md` | `completion.inspect`, `completion.revise` | 完本质检范围与返修路由 |
| `volume-alignment.md` | `alignment` | 整卷产物对齐 |
| `migration.md` | `migration.review` | 项目迁移流程 |
| `agent-return-spec.md` | 新建 agent 时参照 | agent 返回描述规范 |

### L3：角色执行

11 个 agent。每个 agent 声明了自己的 skill 模块和知识挂载。角色之间的上下文隔离是刻意的：

- **novel-agent**：唯一调度器。自身在 `full.commit` 和 `migration.review` 中可被作为 subagent 创建。
- **volume-planner / act-planner / chapter-planner**：规划层。写规划产物。
- **prompt-crafter / prompt-reviewer**：Prompt 层。写 Prompt 或返回审查报告。
- **writer / reader**：写作层。writer 只收 base + Prompt（不接触知识库）；reader 首读不预挂知识。
- **anti-ai / completion-reviewer / completion-editor**：质检层。分别处理表达问题、完本审查、完本编辑。

### L4：知识库

88 个文件，按 7 个主题组织。核心消费模式：

- **规划角色**按索引按需读取（需要知识来建立卷纲、拆幕、形成章纲）
- **prompt-crafter** 首任务全量读取 5 个索引，压缩为 `context-pack.md`，后续任务读 pack
- **writer** 不接触知识库（通过自包含 Prompt 获取一切）
- **Reader** 首读不接触（冷读后才按需追查根因知识）

知识库不定义流程字段，不做质量门禁，只提供"怎么写"的判断依据。

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

### 规划链（volume → act → chapter → prompt）

```
story.md（题材方向）
→ volume-planner → volumes/volume-N.md + settings/（卷纲、设定、文风）
→ act-planner → acts/volume-N-acts.md + acts/vol-N-act-K.md（幕地图、幕纲）
→ chapter-planner → chapters/vol-N-ch-M.md（章纲 + must_hold + 承接摘要）
→ prompt-crafter → prompts/vol-N-ch-M.md（自包含 Prompt）
```

每一次传递是**信息密度增加而非复制**。Prompt 嵌入全部此刻上下文，变成 writer 可执行的行动过程。

### 写作链（prompt → draft → text）

```
prompts.ready
→ Fast：writer → drafts/vol-N-ch-M.md → 顶层阅读 → drafts.ready
→ Full：writer → drafts/vol-N-ch-M.md → reader 冷读 → 分流返修 → commit → texts/vol-N-ch-M.md
```

### 阅读链（Full reader → repair → commit）

```
full.write 完成 → reader 按幕冷读 → 返回报告（verdict + 建议处理角色）
→ 分流：IGNORE（通过）/ EDIT（anti-ai）/ REGENERATE（新 writer / prompt-crafter / planner）
→ 受影响范围复读 → full.commit → texts/
```

### 知识链（knowledge → context-pack → prompt-crafter）

```
5 个知识索引 → 本卷首个 prompt.create 全量读取并裁剪
→ settings/context-pack.md（1 个文件）
→ 本卷后续 prompt.create 读 pack 替代 8-18 个原始文件
→ 换卷/换题材/文风重确认/alignment 发现漂移时重建
```

---

## 四、状态机

### 长期 cursor（10 阶段）

```
outline.volume → outline.acts → outline.chapters → prompts.ready
→ draft.write → drafts.ready（Fast 终点）
→ review → volume.complete → book.complete
+ migration.review（迁移专用，临时占用 cursor）
```

### 临时 operation（15 种）

每个 operation 对应 dispatch.md 中的一张派发卡。operation 比 cursor 更细——例如 `outline.acts` 阶段内可依次执行 `outline.act-map` 和 `outline.act`。

旁路 operation（不改变 cursor）：`completion.inspect`、`completion.revise`、`alignment`、`prompt.review`。

---

## 五、版本体系

三层版本号：

| 层级 | 字段 | 位置 | 含义 |
|------|------|------|------|
| skill 版本 | `skill_version: 5.2` | story.md | skill 逻辑版本，breaking change 时递增 |
| 项目兼容 | `runtime_profile: novel-pro-0.2` | story.md | 项目兼容版本，不匹配时拒绝运行 |
| 发行号 | `0.2.2-pro` | skill.json | 追踪具体发行 |

组件级可选锚点 `changed_in` 标记文件在哪个发行中被修改，便于升级 diff。

版本门禁在 `dispatch.md` 启动时执行：旧项目特征（`story.yaml`、错误 profile、缺迁移字段）停止创作并提示迁移。

---

## 六、扩展机制

系统设计支持三类扩展，均通过已有结构实现：

1. **添加新 operation**：dispatch.md 加派发卡 → skills/ 加模块 → agents/ 加角色（或复用）
2. **添加新知识主题**：knowledge/ 建目录 + 索引 → knowledge/index.md 注册 → agent 挂载
3. **添加新题材**：genre/index.md 注册 → knowledge/genre/ 加画像 → anti-ai/genre/ 加规则

所有扩展必须遵守的不变量：

- **cursor 状态机**：10 阶段结构不变
- **所有权边界**：novel-agent 仍是唯一控制面写入者
- **冷读纪律**：Reader/completion-reviewer 首读不预挂知识

---

## 七、文件清单（按功能分类）

### 控制面（运行时状态 + 规则）
- `SKILL.md`：入口文档
- `skills/dispatch.md`：派发契约
- `skills/agent-return-spec.md`：agent 返回规范

### 流程规则（skills/）
- `planning.md`、`act-planning.md`：规划规则
- `prompt.md`、`context-pack.md`：Prompt 创建规则
- `writer-construction.md`、`writing.md`：写作规则
- `review-archive.md`、`cold-read-discipline.md`、`edit-boundary.md`：阅读与编辑规则
- `completion-quality.md`、`volume-alignment.md`：质检规则
- `migration.md`：迁移规则

### 角色定义（agents/）
- 11 个 agent 文件

### 知识库（knowledge/）
- 7 个主题目录 + 1 个主索引

### 模板（templates/）
- 项目级模板 + 控制面模板 + 设定模板 + 运行时模板

### 工具（tools/）
- 5 个 Python 脚本
