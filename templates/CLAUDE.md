---
template_version: "0.2.3"
description: "项目配置文件，定义 novel-pro 项目的运行规则和流程"
---

# {{project_name}} - novel-pro v0.2

**项目类型**：中文长篇小说创作项目  
**题材**：{{genre}}  
**Runtime Profile**：`novel-pro-0.2`  
**入口 Agent**：`novel-agent`

## 核心工作原理

`novel-agent` 作为顶层调度器，先读取 `skills/dispatch.md`，再按当前 `operation` 加载对应的阶段模块（skills/agents/knowledge）。规划、Prompt、写作、阅读和提交规则按需进入上下文，不整套常驻，确保每个 agent 只获得完成自身任务所需的上下文。

## 创作主线流程

```text
确认题材
  ↓
初始化骨架（tools/init.py）
  ↓
outline.volume：卷纲与必要设定
  ↓
outline.acts：幕地图 + 详细幕纲
  ↓
outline.chapters：按幕形成章纲
  ↓
prompt.create：按幕或批次创建单章 Prompt
  ↓
prompts.ready（所有 Prompt 形成）
  ↓
写作模式（快速草稿） 或 编辑模式（文学验收）
```

### 状态层级说明

**长期状态**（`.agent/status.yaml`）：
- `outline.volume`、`outline.acts`、`outline.chapters`、`prompts.ready`
- `draft.write`、`drafts.ready`、`review`
- `volume.complete`、`book.complete`
- `migration.review`（迁移期间）

**临时操作**（`.agent/order.yaml`）：
- `outline.act-map`、`outline.act`（属于 `outline.acts` 阶段内）
- `prompt.create`、`write.draft`、`edit.write`、`edit.review` 等

**旁路操作**（不改变长期 cursor）：
- `prompt.review`（显式 Prompt 审查）
- `completion.inspect`、`completion.revise`（显式完本质检）
- `alignment`（整卷产物对齐）

## 版本门禁与项目迁移

### 启动检查

启动时必须先读取：
1. `story.md` 的 `runtime_profile` 字段
2. `.agent/status.yaml` 的 `migration` 节点

### 触发迁移的条件

发现以下任一情况时，停止正常创作和运行时同步：
- 存在 `story.yaml`（旧版标志）
- 缺少 `runtime_profile` 字段
- `runtime_profile` 不是 `novel-pro-0.2`
- `.agent/status.yaml` 缺少完整 `migration` 节点

`cursor.step: migration.review` 表示迁移目标尚未 finalize：此时只允许阅读 `.migration/report.md`、处理迁移操作和等待作者确认，不得推进创作阶段或运行 `sync_runtime.py`。

### 迁移流程

```bash
# 从当前开发版运行迁移工具
python tools/migrate.py <旧项目路径> <新项目路径>
```

**迁移步骤**：
1. 在新目录重新初始化当前版本项目
2. 搬运故事、设定、规划、Prompt、草稿和正文
3. 生成 `.migration/report.md` 和机器可读报告
4. 列出已完成文件、缺失内容、未映射旧文件、可清理文件

**作者操作**：
1. 核对 `.migration/report.md`
2. 运行 `python tools/migrate.py finalize <新项目>`
3. 按报告运行 `python tools/migrate.py cleanup <新项目> --confirm`

**注意**：清理只处理报告列出的旧运行时文件（`.agent/`、`.claude/`），不删除正文、规划、设定、任务历史或未映射文件。

## Prompt 创建规则

### 前置条件

创建 Prompt 前必须确认：
- `story.md` 目标卷的 `author_confirmed` 字段为 `true`
- 为 `false` 或缺失时，只请求作者确认，不创建 Prompt

### 创建粒度

- **任务范围**：一次处理一幕或一个连续批次
- **产出**：范围内每章分别写入 `prompts/vol-N-ch-M.md`
- **完成标志**：长期目标范围内的 Prompt 全部形成后才进入 `prompts.ready`

### Prompt 审查

- **触发时机**：仅当用户明确要求审核提示词时
- **处理角色**：prompt-reviewer
- **不参与**：不参与 `prompts.ready` 的形成判定，不作为默认步骤

## Writer Base 构造

进入写作模式或编辑模式时：

1. 顶层读取 `templates/runtime/novel-base.md`（部署后位于 `.claude/skill-resources/templates/novel-base.md`）
2. 为每章构造独立的 writer base（通用框架 + 当前任务）
3. 创建独立 writer 并交付：单章 base + 单章 Prompt
4. Writer 不读知识库、设定或规划，完全依赖 base + Prompt

**关键原则**：
- 每章独立 base、独立 writer、独立输出
- Base 与 Prompt 职责分离（base=框架，Prompt=内容）
- 声线材料全在 Prompt 内，不写入 base

## 两种创作模式

### 写作模式（Writing Mode）

**目标**：快速产出未经 Reader 验收的草稿

**流程**：
```text
prompts.ready
  ↓
write.draft：为每章构造 base + 创建 writer
  ↓
writer 写入 drafts/vol-N-ch-M.md
  ↓
顶层阅读草稿（接受/重派/回退）
  ↓
drafts.ready
```

**特点**：
- 批量派发 writer，但保持单章独立上下文
- 顶层实际阅读草稿后做判断（不只看字段/字数）
- 不进入 Reader、Anti-AI、edit-synthesizer 流程
- 不写入 `texts/`

### 编辑模式（Editing Mode）

**目标**：经完整文学验收，产出可发布正文

**完整六步流程**：
```text
prompts.ready
  ↓
edit.write：writer ×N 写首稿 drafts/
  ↓
edit.review：Reader 按幕冷读 → 冷读报告
  ↓
edit.anti-ai：Anti-AI 全量扫描 → Anti-AI 报告
  ↓
edit.synthesize：综合两份报告 → 整体返修意见（分级+分流）
  ↓
edit.repair：按返修意见整体返修
  ├─ 严重(REGENERATE) → writer/prompt-crafter/planner
  └─ 中等/轻微表达 → anti-ai 编辑模式
  ↓
Reader 按判定清单复读受影响范围
  ↓
edit.commit：texts/vol-N-ch-M.md
```

**核心机制**：
- **双报告机制**：Reader 冷读报告 + Anti-AI 扫描报告
- **整体返修裁决**：edit-synthesizer 综合两份报告分级归属
- **分流返修**：根据问题严重程度选择返修路径
- **复读验证**：每次返修后重新顺序冷读

## 知识与设定消费规则

### 消费者映射表

| 文件类型 | 消费者 | 使用方式 |
|---|---|---|
| `settings/genre-setting.md` | volume/act/chapter-planner, prompt-crafter | 提取当前范围相关部分 |
| `settings/world-setting.md` | planner（规划阶段） | 交叉核对，Prompt 携带本章相关事实 |
| `settings/character-setting/` | planner, prompt-crafter | 选择当前人物事实，溶解到 Prompt |
| `settings/writing-preferences.md` | planner, prompt-crafter | 提取当前章适用偏好 |
| `settings/foreshadowing.md` | planner, prompt-crafter | 核对兑现、隐藏、余波 |
| `settings/timeline.md` | planner, prompt-crafter | 核对时间先后、人物可知范围 |
| `settings/writing-style.md` | prompt-crafter | 提取叙述示范 + 逐场声线落点 |
| `settings/context-pack.md` | prompt-crafter（后续任务） | 读包替代知识库下钻 |
| `knowledge/style/` | volume-planner（仅形成阶段） | 选择文风原型 |
| `knowledge/*` | planner, prompt-crafter | 按需加载，首任务打包进 context-pack |

### 文风传导链

```text
knowledge/style/（原型）
  ↓ volume-planner 与作者共同
settings/writing-style.md（项目文风，含基准样章）
  ↓ prompt-crafter 提取
Prompt「本章故事」叙述示范 + 各场「本场声线」落点
  ↓ writer 执行
正文实际声线
  ↓ Reader 从正文判断
冷读报告
```

**关键原则**：
- 文风原型只在形成阶段读取
- 确认后的 `settings/writing-style.md` 是唯一下游来源
- Writer 不读原型库，只执行 Prompt 内的声线材料

## 文件路径与部署

### 开发态路径（仓库源码）
- Agent：`agents/`
- Skills：`skills/`
- Knowledge：`knowledge/`
- Templates：`templates/`

### 部署态路径（项目运行时）
- Agent：`.claude/agents/`
- Skills：`.claude/skill-resources/skills/`
- Knowledge：`.claude/skill-resources/knowledge/`
- Templates：`.claude/skill-resources/templates/`

### 控制面文件（novel-agent 独占）
- `.agent/status.yaml`：长期 cursor 和 migration 状态
- `.agent/order.yaml`：当前 operation、范围、subtasks
- `.agent/tasks/<task-id>/`：报告、候选、恢复现场
- `.agent/run-log.yaml`：重大失败、中断、作者决策

### 产物文件（分权写入）
- `volumes/`、`acts/`、`chapters/`：规划角色写入
- `prompts/`：prompt-crafter 写入
- `drafts/`：writer 写入
- `texts/`：novel-agent 通过 `edit.commit` 写入（仅此路径）

## 质量判断原则

**脚本职责边界**：
- ✅ 初始化项目骨架
- ✅ 运行时文件同步
- ✅ 完整项目迁移
- ✅ 文件安全保障
- ❌ 不承担文学评分
- ❌ 不做关键词门禁
- ❌ 不做字数达标判定
- ❌ 不做 AI 味判定

**真实判断来源**：
- Prompt 质量：prompt-reviewer 读 Prompt 判断可执行性
- 正文质量：Reader 冷读正文后做文学判断
- 表达质量：Anti-AI 扫描正文中的实际表达问题
- 返修决策：edit-synthesizer 综合两份报告分级裁决

**判断顺序**：
1. 先读正文产生真实阅读反应
2. 再判断人物和场景是否成立
3. 最后追查 Prompt、规划或表达根因

## 恢复机制

中断后恢复流程：

1. **读取现场**：status、order、当前 task、run-log 相关记录
2. **加载模块**：按当前 operation 加载对应阶段模块
3. **保留产物**：已经形成的规划/Prompt/draft/候选保持原状
4. **继续未完成**：从各 operation 的最小恢复入口继续
5. **不重建已成立**：已经由顶层阅读确认的范围不重做

## 常见问题

**Q: 如何初始化新项目？**
A: 运行 `python tools/init.py`，按提示填写题材和项目名。

**Q: 旧项目如何升级？**
A: 必须运行完整迁移：`python tools/migrate.py <旧> <新>`。

**Q: 如何选择写作模式还是编辑模式？**
A: 写作模式适合快速推进情节先看全貌；编辑模式适合精修到可发布水平。

**Q: 如何查看当前创作进度？**
A: 查看 `.agent/status.yaml` 的 `cursor.step` 字段。

**Q: 任务中断后如何恢复？**
A: 直接继续对话，novel-agent 会读取现场状态自动恢复。

**Q: Novel Desk 是什么？必须使用吗？**
A: 可选的本地工作台，提供文件编辑和任务入口。没有 Desk 也可以通过对话式使用。
