# TASKS.md

<!--
  本文件是 Novel Desk 与 novel-pro 顶层之间的作者请求交接清单的 schema 权威源。
  项目根目录的 TASKS.md 由 Desk 在首次创建任务时生成，按本模板结构与字段约束填写。
  协议语义（字段定义、状态流转、所有权边界）以本文件为唯一权威；SKILL.md、
  README.md、skills/dispatch.md 的「TASKS.md」节均为指向本文件的指针，不重复定义字段。

  生成时机：新项目首次创建 Desk 任务时生成；初始化（tools/init.py）不预生成，
  迁移也不自动搬运（旧项目保留历史，新项目首次 Desk 任务时再生成）。
  适用条件：仅 Novel Desk 存在时需要；无 Desk 时 Skill 不要求本文件。
-->

## 协议

- **唯一交接文件**：项目根目录 `TASKS.md` 是作者到 Agent 外壳的唯一交接入口，不是第二套创作状态机。
- **状态流转**：`pending` → `in_progress` → `completed` / `blocked` / `cancelled`。只有作者在 Agent 对话中明确确认后，才把 `pending` 改为 `in_progress`。
- **所有权边界**：不替代 `.agent/status.yaml`、`.agent/order.yaml` 或 `.agent/tasks/`，不写长期 cursor，不替代 order/task/run-log，不改变任何角色所有权。`texts/` 仍只能通过原有 Reader 接受与 `edit.commit` 边界写入。
- **处理流程**：确认后按本 Skill 原有的规划、Prompt、写作、编辑模式、Reader、完本或迁移流程执行；候选和报告写入既有 Skill 产物位置；完成、受阻或取消时回写同一项的 `status`、结果说明和结果文件路径。
- **迁移**：完整迁移不自动搬运 `TASKS.md`；旧项目保留作为协作历史，新项目首次创建 Desk 任务时再生成新清单。

## 字段定义

每个任务项为一个二级标题，标题文本为任务简述；frontmatter 记录结构化字段。

### status

任务状态。有效值：`pending` | `in_progress` | `completed` | `blocked` | `cancelled`。

- `pending`：Desk 已写入、尚未经作者确认。
- `in_progress`：作者已确认，正在按既有文学流程执行。
- `completed`：已完成，回写 `result.summary` 与 `result.files`。
- `blocked`：受阻无法完成，回写 `result.summary` 说明原因。
- `cancelled`：取消处理，回写 `result.summary`。

### source

作者请求的来源定位，用于核对请求是否发生变化。

- `source.path`：来源文件路径（必填）。
- `source.content_hash`：来源内容的 hash（必填）；执行前重新核对，hash 变化时先重读并向作者说明差异。
- `source.anchor`：可选锚点（章节、幕、行等）。

### scope

请求处理范围（自由文本，描述拟处理的文件、章节、幕或操作范围）。

### operation

将采用的既有 Skill operation（如 `outline.volume`、`prompt.create`、`write.draft`、`edit.review`、`completion.revise`、`alignment` 等）。仅作汇总与确认用，不创建新 operation 类型。

### result

完成后回写。`status` 为 `completed` / `blocked` / `cancelled` 时填写。

- `result.summary`：结果说明（完成内容、受阻原因或取消原因）。
- `result.files`：结果文件路径列表（写入既有 Skill 产物位置，如 `volumes/`、`prompts/`、`drafts/`、`texts/` 等）。

## 任务项模板

```markdown
## {任务简述}

status: pending
source:
  path: {来源文件路径}
  content_hash: {来源内容 hash}
  anchor: {可选锚点}
scope: {拟处理范围说明}
operation: {将采用的既有 Skill operation}
result:
  summary: {完成/受阻/取消后回写}
  files: [{结果文件路径}]
```

## 示例

### 示例1：修订已发布章节
```markdown
## 修订第 2 卷第 3 章高潮节奏

status: pending
source:
  path: texts/vol-2-ch-3.md
  content_hash: sha256:abc123...
  anchor: ch-3 后半
scope: 第 2 卷第 3 章，高潮强度不足、强弱交替失衡
operation: completion.revise
result:
  summary:
  files: []
```

### 示例2：完善卷纲（已完成）
```markdown
## 完善第 1 卷人物弧线

status: completed
source:
  path: volumes/volume-1.md
  content_hash: sha256:def456...
  anchor: ## 人物弧线
scope: 第 1 卷卷纲，人物弧线部分太抽象，需要具体到每幕状态变化
operation: outline.volume
result:
  summary: 已补充主角和主要配角的三阶段弧线（起点→压力测试→转折），每幕状态清晰可检验
  files: [volumes/volume-1.md]
```

### 示例3：审查Prompt（按需细节审查）
```markdown
## 审查第 5 章 Prompt 可执行性

status: blocked
source:
  path: prompts/vol-1-ch-5.md
  content_hash: sha256:ghi789...
scope: 第 1 卷第 5 章 Prompt，担心场景展开太简略
operation: prompt.review
result:
  summary: FIX - Prompt 缺少核心场景的具体行动脉络（主角如何试探、对手如何反制）。建议先完善 Prompt 再创建 writer。
  files: []
```

### 示例4：批量创建章纲
```markdown
## 创建第 2 幕全部章纲

status: in_progress
source:
  path: acts/vol-1-act-2.md
  content_hash: sha256:jkl012...
scope: 第 1 卷第 2 幕的章纲（预估 8-10 章）
operation: outline.chapters
result:
  summary:
  files: []
```

## Agent 处理流程详解

### 1. 读取与验证阶段

> 以下为流程示意伪代码，非可执行接口。

```python
# 顶层读取项目根目录 TASKS.md
tasks = parse_tasks("TASKS.md")
pending_tasks = [t for t in tasks if t.status == "pending"]

if not pending_tasks:
    return "没有待处理任务"

# 核对每个任务的来源文件
for task in pending_tasks:
    source_file = read(task.source.path)
    current_hash = compute_hash(source_file)
    
    if current_hash != task.source.content_hash:
        # 来源已变化，向作者说明
        notify_author(f"""
        任务「{task.title}」的来源文件已变化：
        - 路径：{task.source.path}
        - 原哈希：{task.source.content_hash}
        - 当前哈希：{current_hash}
        
        请确认是继续处理还是更新任务。
        """)
        continue
```

### 2. 汇总与确认阶段

> 以下为流程示意伪代码，非可执行接口。

```python
# 汇总所有待处理任务的范围和操作
summary = []
for task in valid_pending_tasks:
    summary.append({
        "任务": task.title,
        "范围": task.scope,
        "操作": task.operation,
        "预估时间": estimate_time(task.operation),
        "影响文件": estimate_files(task.operation, task.scope)
    })

# 向作者展示汇总
present_to_author(f"""
待处理任务汇总（共 {len(summary)} 个）：

{format_table(summary)}

这些任务将按既有 Skill 流程执行：
- 规划类任务会调用对应 planner
- Prompt 类任务会调用 prompt-crafter/reviewer
- 写作类任务会创建 writer
- 编辑类任务会进入 Reader + Anti-AI 流程

是否确认执行？
""")

# 等待作者明确确认
if not author_confirms():
    return "等待确认"
```

### 3. 执行与回写阶段

> 以下为流程示意伪代码，非可执行接口。

```python
# 作者确认后，逐个执行
for task in confirmed_tasks:
    # 更新状态为 in_progress
    task.status = "in_progress"
    write_tasks()
    
    try:
        # 按既有 Skill operation 派发
        result = dispatch(
            operation=task.operation,
            scope=parse_scope(task.scope),
            source=task.source.path
        )
        
        # 完成后回写
        task.status = "completed"
        task.result.summary = result.summary
        task.result.files = result.output_files
        
    except BlockedError as e:
        # 受阻
        task.status = "blocked"
        task.result.summary = str(e)
        task.result.files = []
        
    except CancelledError:
        # 取消
        task.status = "cancelled"
        task.result.summary = "已取消"
        task.result.files = []
    
    finally:
        write_tasks()
```

## 常见任务类型映射表

| 任务类型 | scope 典型格式 | 映射 operation | 处理角色 | 预估时间 |
|---|---|---|---|---|
| 创建/完善卷纲 | "第 N 卷卷纲" | outline.volume | volume-planner | 10-15分钟 |
| 创建幕地图 | "第 N 卷幕地图" | outline.act-map | act-planner | 5-10分钟 |
| 创建/完善详细幕纲 | "第 N 卷第 K 幕" | outline.act | act-planner | 5-8分钟 |
| 创建章纲 | "第 N 卷第 K 幕章纲" | outline.chapters | chapter-planner | 3-5分钟/幕 |
| 创建 Prompt | "第 N 卷第 K 幕 Prompt" | prompt.create | prompt-crafter | 5-10分钟/幕 |
| 审查 Prompt | "第 N 卷第 M 章 Prompt" | prompt.review | prompt-reviewer（按需：顶层轻量审查发现明确问题或作者要求时） | 2-3分钟/章 |
| 写作模式草稿 | "第 N 卷第 M 章草稿" | write.draft | writer | 3-5分钟/章 |
| 编辑模式首稿 | "第 N 卷第 K 幕" | edit.write → ... → edit.commit | writer + reader + anti-ai | 20-30分钟/幕 |
| 返修表达问题 | "第 N 卷第 M 章表达" | edit.repair (表达) | anti-ai | 3-5分钟/章 |
| 返修内容问题 | "第 N 卷第 M 章内容" | edit.repair (内容) | writer | 5-8分钟/章 |
| 完本质检 | "第 N 卷全卷" | completion.inspect | completion-reviewer | 15-20分钟/卷 |
| 整卷对齐 | "第 N 卷产物对齐" | alignment | 各产物拥有者 | 5-10分钟 |

## 常见问题（FAQ）

### Q1: Novel Desk 是什么？必须使用吗？
A: Novel Desk 是可选的本地作者工作台，提供文件编辑、快照、报告展示和任务入口功能。它不启动 Runtime、不连接 MCP、不调度 Agent。没有 Desk 时，可以继续使用原有的对话式方式，不需要 TASKS.md。

### Q2: 任务状态什么时候更新？
A: 
- `pending`：Desk 创建任务时自动设置
- `in_progress`：作者在 Agent 对话中明确确认后，Agent 更新
- `completed/blocked/cancelled`：任务执行完成/受阻/取消后，Agent 回写

### Q3: 如何取消任务？
A: 可以手动将 `status` 改为 `cancelled`，或在 Desk 中操作。Agent 下次读取时会跳过已取消任务。

### Q4: 任务可以有依赖关系吗？
A: 可以。Agent 读取时会检查前置条件（如 Prompt 创建需要章纲存在，编辑模式需要 Prompt 存在）。缺少前置时会标记 `blocked` 并说明原因。

### Q5: 多个任务会并行执行吗？
A: 不会。Agent 按顺序执行，确保每个任务完成后再执行下一个。但同一个 operation 内部（如多章 writer）可以并发。

### Q6: 任务失败会影响项目状态吗？
A: 不会。任务只是触发既有流程的入口，受阻的任务会标记 `blocked` 但不会修改 `.agent/status.yaml` 等控制面文件。

### Q7: 如何批量处理任务？
A: 可以创建多个 `pending` 任务，Agent 会汇总后一次性展示，等待作者确认后批量执行。

### Q8: 来源文件的 hash 如何计算？
A: 使用 SHA256 算法计算文件内容哈希。Desk 创建任务时自动计算，Agent 执行前重新验证。

### Q9: 任务结果写到哪里？
A: 写入既有 Skill 产物位置：
- 规划类 → `volumes/`, `acts/`, `chapters/`
- Prompt类 → `prompts/`
- 草稿类 → `drafts/`
- 正文类 → `texts/`（需经 Reader 验收）

### Q10: 旧项目迁移时 TASKS.md 会搬运吗？
A: 不会。旧项目的 TASKS.md 保留作为协作历史，新项目在首次创建 Desk 任务时生成新清单。
