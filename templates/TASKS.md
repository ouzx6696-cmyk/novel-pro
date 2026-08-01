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

```markdown
## 修订第 2 卷第 3 章高潮节奏

status: pending
source:
  path: texts/vol-2-ch-3.md
  content_hash: sha256:...
  anchor: ch-3 后半
scope: 第 2 卷第 3 章，高潮强度不足、强弱交替失衡
operation: completion.revise
result:
  summary:
  files: []
```
