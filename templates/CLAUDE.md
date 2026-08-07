---
template_version: "0.3.0"
description: "项目配置文件，定义 novel-pro 项目的运行规则和流程"
---

# {{project_name}} - novel-pro v0.3

**项目类型**：中文长篇小说创作项目  
**题材**：{{genre}}  
**Runtime Profile**：`novel-pro-0.3`  
**入口 Agent**：`novel-agent`

## 核心工作原理

`novel-agent` 作为顶层调度器，先读取 `skills/dispatch.md`，再按当前 `operation` 加载对应的阶段模块（skills/agents/knowledge）。规划、Prompt、写作、阅读、状态同步和提交规则按需进入上下文，不整套常驻，确保每个 agent 只获得完成自身任务所需的上下文。

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
outline.chapters：按幕形成章纲（含信息差轨迹/章末状态快照）
  ↓
幕首章前：顶层建幕级复用资料包 act-pack（.agent/cache/vol-N-act-K-act-pack.md）
  ↓
顺序链路（draft.write，逐章推进）：
  第 M 章：
  prompt.create（读 act-pack + 本章动态资料；上一章真实正文 → 前情三件套；state_history 最新块 → 角色初始状态）
    ↓
  prompt_lint.py 结构预检 → 顶层轻量审查（无明确问题直接进写作）
    ↓
  发现明确问题或作者要求 → prompt.review（细节审查）
    ↓
  写作模式 write.draft（快速草稿） 或 编辑模式 edit.write → edit.review → edit.anti-ai
    → edit.synthesize → edit.repair → edit.commit（文学验收）
    ↓
  state.update phase: delta（工作态增量）/ phase: commit（最终 texts 回流）
    ↓
  第 M+1 章
```

**核心设计**：Prompt 不再提前批量创建，而是跟随正文顺序逐章创建——第 N+1 章 Prompt 的前情上下文直接取自第 N 章真实验收稿/定稿，角色初始状态取自已回流的状态文件。这是提示词质量与前后文一致性的根本保证。

### 状态层级说明

**长期状态**（`.agent/status.yaml`）：
- `outline.volume`、`outline.acts`、`outline.chapters`、`draft.write`（顺序链路）
- `drafts.ready`、`volume.complete`、`book.complete`
- `migration.review`（迁移期间）

**临时操作**（`.agent/order.yaml`）：
- `outline.act-map`、`outline.act`（属于 `outline.acts` 阶段内）
- `prompt.create`、`prompt.review`、`write.draft`、`edit.write`、`edit.review`、`edit.anti-ai`、`edit.synthesize`、`edit.repair`、`edit.commit`、`state.update`（顺序链路，逐章推进，`current_chapter` 记录当前章）

**旁路操作**（不改变长期 cursor）：
- `completion.inspect`、`completion.revise`（显式完本质检）
- `alignment`（整卷产物对齐）

## 与 Novel Desk 的交接（TASKS.md）

Novel Desk 存在时，项目根目录 `TASKS.md` 是唯一的作者到 Agent 外壳交接文件，不是第二套创作状态机。字段定义、状态流转与所有权边界以 `templates/TASKS.md` 为权威源。收到"处理任务清单"或发现 Desk 创建的任务时：

1. 读取全部 `pending` 项，核对 `source.path`、`source.content_hash`、可选 `source.anchor` 和 `scope`；来源已变化时先重读并向作者说明差异。
2. 汇总拟处理的文件、范围和将采用的既有 operation，等待作者在对话中明确确认。
3. 确认后才把相应项更新为 `in_progress`，并按本文件既有的规划、Prompt、写作、编辑、Reader、完本或迁移流程执行。
4. 把候选和报告写入既有产物位置；完成、受阻或取消时更新同一项的 `status`、`result.summary` 和 `result.files`。

没有 Desk 时，Skill 不要求 `TASKS.md`，原有对话式使用方式保持不变。迁移不自动搬运 `TASKS.md`：旧项目保留作为协作历史，新项目在第一次创建 Desk 任务时才生成新的清单。

## 版本门禁与项目迁移

### 启动检查

启动时必须先读取：
1. `story.md` 的 `runtime_profile` 字段
2. `.agent/status.yaml` 的 `migration` 节点

### 触发迁移的条件

发现以下任一情况时，停止正常创作和运行时同步：
- 存在 `story.yaml`（旧版标志）
- 缺少 `runtime_profile` 字段
- `runtime_profile` 不是 `novel-pro-0.3`
- `.agent/status.yaml` 缺少完整 `migration` 节点

`cursor.step: migration.review` 表示迁移目标尚未 finalize：此时只允许阅读 `.migration/report.md`、处理迁移操作和等待作者确认，不得推进创作阶段或运行 `sync_runtime.py`。

### 迁移流程

```bash
# 从当前版本运行迁移工具
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

- **任务范围**：一次一章，跟随正文顺序创建（顺序链路）
- **必读上文**：上一章真实正文（验收稿 `drafts/` 或已提交正文 `texts/`）的结尾，提取前情三件套（上章结尾画面/情绪残留/缺口）；可选读取 hash 有效的 chapter-delta
- **稳定资料**：幕级复用资料包 `.agent/cache/vol-N-act-K-act-pack.md`（顶层幕首章前建立；每章只读此包 + 本章动态资料）；包缺失或失效时回退完整读取（context-pack、幕纲、handoff、`settings/` 六件套）
- **必读状态**：角色档案 `state_history` 最新块（稳定事实在 act-pack 内）
- **产出**：`prompts/vol-N-ch-M.md`（`prompt_contract: 4`，六块：前情上下文/本章故事/角色初始状态/人物动机与情绪/场景展开/必守事实与边界；frontmatter 记录 `preceding_source`）
- **完成标志**：本章 Prompt 落盘、自检表无缺口、顶层读过、审查通过后进入本章写作；不存在"全部 Prompt 就绪"的批量节点

### Prompt 两级审查

- **顶层轻量审查（默认）**：每章 Prompt 落盘并 lint 后执行（不创建子代理）——核对 lint 结果、语义自检表与上一章正文承接；无明确问题直接进入写作/编辑链路
- **prompt.review 细节审查（按需）**：轻量审查发现明确问题（lint 错误超 micro-fix 边界、语义自检缺口、前情/信息差/可执行性存疑）、作者要求强制，或幕内首章/返修重写章被顶层点名时，才派发 prompt-reviewer 审计真实前情、层间一致、信息差和核心场景可执行性（作者明确放行时可跳过，顶层在 order 记录）
- **结论**：`PASS` → 写作/编辑链路；机械问题且在 3 处以内 → micro-fix 后重跑 lint；`FIX` → 返回 prompt-crafter 修复后重审；`STOP` → 交规划层

## 状态同步（state.update）

每章草稿完成后由 continuity-updater 先返回 chapter-delta；编辑模式 `edit.commit` 后再从最终 `texts/` 执行正式状态回流：

- 向角色档案 `state_history` 节追加状态变更块（位置/状态/关系/能力/信息持有）
- 向 `timeline.md` 追加章节锚点时间线条目
- 推进 `foreshadowing.md` 伏笔台账
- 消费章纲/幕纲中的「设定变更通知」块
- **幕末章额外生成幕末正文总结 `summaries/vol-N-act-K.md`**（事件链带章节锚点/人物状态/信息差/伏笔/未闭合张力/幕末承接帧）

chapter-delta/working-state 只作为下一章的临时增量；正式 settings 只由最终 `texts/` 回流。缓存或 delta 缺失时，prompt-crafter 回退到完整上一章正文和既有状态文件。幕总结仍是派生缓存，事实以 settings/ 与正文为准。正式回流按章节锚点追加/覆盖，重复执行不产生重复内容。

## Writer Base 构造

进入写作模式或编辑模式时：

1. 顶层读取 `templates/runtime/novel-base.md`（部署后位于 `.claude/skill-resources/templates/novel-base.md`）
2. 为每章构造动态 writer 任务；可复用 hash 有效且不含剧情的 `writer-profile`
3. 创建独立 writer 并交付：单章 base + 单章 Prompt
4. Writer 不读知识库、设定或规划，完全依赖 base + Prompt

**关键原则**：
- 每章独立动态任务、独立 writer、独立输出；profile 失效时回退完整构造
- Base 与 Prompt 职责分离（base=框架，Prompt=内容）
- 声线材料全在 Prompt 内，不写入 base

## 两种创作模式

### 写作模式（Writing Mode）

**目标**：顺序链路中逐章快速产出未经 Reader 验收的草稿

**流程**：
```text
第 M 章：
prompt.create（读 act-pack + 本章动态资料；上一章真实正文 → 前情三件套）
  ↓
prompt_lint.py 结构预检 → 顶层轻量审查（无明确问题直接进写作；明确问题或作者要求 → prompt.review 细节审查）
  ↓
write.draft：构造 base + 创建 writer
  ↓
writer 写入 drafts/vol-N-ch-M.md
  ↓
顶层阅读草稿（接受/重派/回退）
  ↓
接受 → state.update phase: delta（生成 chapter-delta，不写 settings）
  ↓
第 M+1 章
```

**特点**：
- 逐章串行，一章验收后才创建下一章 Prompt
- 顶层实际阅读草稿后做判断（不只看字段/字数）
- 不进入 Reader、Anti-AI、edit-synthesizer 流程
- 不写入 `texts/`

### 编辑模式（Editing Mode）

**目标**：逐章写作、幕末批量审读，经完整文学验收，产出可发布正文

**完整流程**：
```text
逐章写作（幕内草稿按序形成，不立即审读）：
第 M 章：prompt.create（读 act-pack + 本章动态资料；前情取自上一章草稿全文 + 可选 chapter-delta）→ prompt_lint.py → 顶层轻量审查（按需 prompt.review）
  ↓
edit.write：writer ×1 写草稿 drafts/ → state.update phase: delta
  ↓
幕末批量审读（幕内全部草稿形成后）：
edit.review：Reader 按幕冷读（上下文含前幕已提交正文）→ 冷读报告
  ↓
edit.anti-ai：Anti-AI 同幕章节全量扫描 → Anti-AI 报告
  ↓
edit.synthesize：综合两份报告 → 整体返修意见（分级+分流，含前情刷新标记）
  ↓
edit.repair：按返修意见整体返修
  ├─ 严重(REGENERATE) → writer/prompt-crafter/planner（改变既定事实时后继章前情刷新）
  └─ 中等/轻微表达 → anti-ai 编辑模式
  ↓
Reader 按判定清单复读受影响范围
  ↓
edit.commit：逐章写入 texts/vol-N-ch-M.md
  ↓
state.update phase: commit（逐章从最终 texts 定稿回流，同锚点覆盖刷新）→ 幕总结 → 下一幕
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
| `settings/character-setting/` | planner, prompt-crafter, continuity-updater | planner/prompt-crafter 从 `state_history` 倒读；continuity-updater 追加状态块 |
| `settings/writing-preferences.md` | planner, prompt-crafter | 提取当前章适用偏好 |
| `settings/foreshadowing.md` | planner, prompt-crafter, continuity-updater | 核对兑现、隐藏、余波；台账由 state.update 推进 |
| `settings/timeline.md` | planner, prompt-crafter, continuity-updater | 核对时间先后、人物可知范围；条目由 state.update 按章追加 |
| `settings/writing-style.md` | prompt-crafter | 提取叙述示范 + 逐场声线落点 |
| `settings/context-pack.md` | prompt-crafter（后续任务） | 读包替代知识库下钻 |
| `.agent/cache/*-act-pack.md` | prompt-crafter（幕内每章） | 顶层幕首章前建立的幕级复用资料包；每章读包 + 本章动态资料 |
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

### 状态传导链（当前状态系统）

```text
草稿（delta）→ task-local chapter-delta/working-state
最终正文（texts/）→ state.update phase: commit（continuity-updater，按章追加）
角色档案 state_history + timeline.md + foreshadowing.md（"当前状态"）
  + 幕末章生成 summaries/vol-N-act-K.md（幕末正文总结）
  ↓ prompt-crafter：读 act-pack（幕内稳定资料）；同幕读上一章全文（质感）；跨幕首章读幕总结（导航）
Prompt「前情上下文」+「角色初始状态」
  ↓ writer 执行
下一章正文
```

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
- `.agent/order.yaml`：当前 operation、范围、current_chapter、state_delta、可选 context/session/retry、subtasks
- `.agent/tasks/<task-id>/`：报告、候选、恢复现场
- `.agent/run-log.yaml`：重大失败、中断、作者决策

### 产物文件（分权写入）
- `volumes/`、`acts/`、`chapters/`：规划角色写入
- `prompts/`：prompt-crafter 写入
- `drafts/`：writer 写入
- `texts/`：novel-agent 通过 `edit.commit` 写入（仅此路径）
- `.agent/tasks/<task-id>/chapter-delta.yaml`、`working-state.yaml`：novel-agent 持久化 continuity-updater 返回的临时增量，不是真相源
- `settings/character-setting/`（state_history 节）、`timeline.md`、`foreshadowing.md`：continuity-updater 按章追加
- `summaries/`：continuity-updater 在幕末章生成幕末正文总结

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
- Prompt 质量：顶层轻量审查（默认）；明确问题时 prompt-reviewer 读 Prompt + 真实上文判断可执行性与前情落地
- 正文质量：Reader 冷读正文后做文学判断
- 表达质量：Anti-AI 扫描正文中的实际表达问题
- 返修决策：edit-synthesizer 综合两份报告分级裁决
- 状态质量：continuity-updater 从正文回流事实，alignment 核对状态文件与正文连续性

**判断顺序**：
1. 先读正文产生真实阅读反应
2. 再判断人物和场景是否成立
3. 最后追查 Prompt、规划或表达根因

## 恢复机制

中断后恢复流程：

1. **读取现场**：status、order、当前 task、run-log 相关记录
2. **定位断点**：按 order 的 `current_chapter` 定位当前章，按该章产物状态决定恢复步骤（Prompt 缺失或前情过期 → `prompt.create`；Prompt 在未 lint/轻量审查 → 先预检再顶层轻量审查，有明确问题且未细节审查 → `prompt.review`；Writer 空返回先检查目标文件，缺失/截断才用相同 Prompt/profile 自动重试一次；草稿缺失 → 重派 writer；草稿完成但 `state_delta.captured: false` → `state.update phase: delta`；正文已提交但 `state_delta.committed: false` → `state.update phase: commit`）
3. **保留产物**：已经形成的规划/Prompt/draft/候选保持原状
4. **继续未完成**：从该章的最小恢复入口继续
5. **不重建已成立**：已经由顶层阅读确认的范围不重做

## 常见问题

**Q: 如何初始化新项目？**
A: 运行 `python tools/init.py`，按提示填写题材和项目名。

**Q: 旧项目如何升级？**
A: 必须运行完整迁移：`python tools/migrate.py <旧> <新>`。

**Q: 如何选择写作模式还是编辑模式？**
A: 写作模式适合快速推进情节先看全貌；编辑模式适合精修到可发布水平。两种模式都运行在顺序链路上，逐章推进。

**Q: 为什么 Prompt 不提前创建了？**
A: 顺序链路让每一章 Prompt 的前情上下文直接取自上一章真实正文、角色初始状态取自已回流的状态文件——提示词永远建立在真实上文之上，避免批量创建时的承接失真与前后文矛盾。

**Q: 任务中断后如何恢复？**
A: 直接继续对话，novel-agent 会读取现场状态按 `current_chapter` 断点自动恢复。

**Q: Novel Desk 是什么？必须使用吗？**
A: 可选的本地工作台，提供文件编辑和任务入口。没有 Desk 也可以通过对话式使用。
