# 编辑模式（Editing Mode）：Reader、返修与提交

<!-- changed_in: 0.3.0 -->

Reader 是编辑模式的内容裁判，按**幕**批量冷读（幕末统一审读）。写作模式不加载本文件，也不运行 Reader 或 anti-AI。编辑模式的完整定义（工作目标/流程/调度）见 `SKILL.md` 的「编辑模式」节。

本模块的报告和候选由角色返回，只有 `novel-agent` 可以把报告写入 `.agent/tasks/<task-id>/`、更新 order/run-log，或把最终接受正文提交到 `texts/`。Reader、anti-AI 不直接推进状态。

冷读协议、`HARD FIX: synopsis delivery` 定义、分流语义（IGNORE/EDIT/REGENERATE）和复读纪律以 `skills/cold-read-discipline.md` 为共享权威源。本文件只定义编辑模式的阅读闭环、返修路由和提交流程。

## 编辑模式阅读闭环

### 编辑模式创作流程

```text
outline.chapters（章纲完成，顺序链路）
→ 逐章写作（幕内草稿按序形成，不立即审读）：
   第 M 章：`prompt.create`（读 act-pack + 本章动态资料；前情取自上一章草稿全文 + 状态文件）→ 顶层轻量审查（按需 `prompt.review` 细节审查）
   → `edit.write`：writer ×1 写草稿 drafts/vol-N-ch-M.md
→ 幕末批量审读（幕内全部草稿形成后）：
   → `edit.review`：Reader 按幕顺序冷读全部草稿（上下文含前幕已提交正文），出冷读报告
   → `edit.anti-ai`：Anti-AI 全量扫描同幕章节，出 Anti-AI 报告（不动文）
   → `edit.synthesize`：edit-synthesizer 读两份报告，分级(严重/中等/轻微)，给整体返修意见
       （明确修哪章、怎么修、问题归属冷读/anti-ai、跨章关联与优先级）
   → `edit.repair`：按整体返修意见整体返修
   ├─ 严重(REGENERATE) → 新 writer / prompt-crafter / planner
   └─ 中等/轻微表达 → anti-ai 编辑模式（局部候选）
   → 受影响范围重新顺序冷读（Reader 复读）
   → 无未解决问题时 `edit.commit`（逐章写入 `texts/`）
   → `state.update`（逐章，从定稿回流状态；同锚点旧块覆盖刷新）→ 幕总结
→ 下一幕
```

**返修后的前情刷新**：幕末审读中若某章被 `REGENERATE` 重写并改变了既定事实，其后继章的 Prompt 前情源已变——从被重写章的后一章开始，按顺序链路恢复规则重做 `prompt.create`（前情取自重写后的真实正文）与 `edit.write`；不重做已经成立的章。

每次返修都必须重新顺序阅读受影响范围；不能只检查原报告中的标签是否消失。`HARD FIX`、`IGNORE`、`EDIT`、`REGENERATE` 只由 Reader 或完本 Reader 基于实际正文产生，脚本不能推导。

### 阅读闭环步骤（六步执行表）

顶层按以下六步派发（幕末批量）；每步的「读/写/判定」是精确接口：

| 步骤 | operation | 角色 | 读 | 写 | 判定 → 下一跳 |
|---|---|---|---|---|---|
| 1 | `edit.write`（幕内逐章） | writer ×1（每章） | 单章 base + 目标 Prompt | `drafts/vol-N-ch-M.md` | 每章草稿完成后轻量 `state.update phase: delta`（不写 settings）；幕内全部草稿形成 → 步骤 2 |
| 2 | `edit.review` | reader ×1（一幕） | 先只读本幕草稿（冷读，上下文含前幕已提交正文），首读后才读 continuity contract 与诊断知识 | 冷读报告 | 报告给出 verdict 与复读范围 → 步骤 3 |
| 3 | `edit.anti-ai` | anti-ai ×1（同幕） | 同幕章节正文、`knowledge/anti-ai/index.md` | Anti-AI 报告 | 每章全量扫描列全 → 步骤 4 |
| 4 | `edit.synthesize` | edit-synthesizer ×1 | 两份报告；分歧/断言处可最小正文核对 | 整体返修意见 | 问题全部分级归属 → 步骤 5 或直接 `edit.commit` |
| 5 | `edit.repair` | 按分流创建（writer / prompt-crafter / planner / anti-ai） | 整体返修意见 + 受影响正文 | draft candidate / 修复 Prompt / 重建规划 / 表达候选 | 候选完成 → 步骤 6 复读 |
| 6 | `edit.commit` | novel-agent 自身 | 已复读接受候选、task 报告、目标路径 | `texts/vol-N-ch-M.md`（逐章）、控制面文件 | 预检通过 → `state.update`（逐章）→ 下一幕 / `volume.complete` |

步骤 5 与步骤 6 之间强制经过 Reader 复读（按 `skills/cold-read-discipline.md` 复读范围判定清单重新顺序冷读）；未复读接受的候选不得提交。

各步执行要点：

- Reader 先只读本幕草稿（前幕已提交正文作为上下文已读），按章顺序作为目标读者冷读，记录理解、期待、疑问、情绪和幕末感受；首读完成后才读取当前幕 continuity contract 和必要诊断知识，追查正文中真实出现的问题。
- 冷读报告先写成立处和真实阅读体验，再引用正文证据，给出根因、受影响章节、最小处理方式和复读范围；Reader 不直接改文或派发角色。
- anti-ai 对**同幕章节**做全量表达扫描，不依赖 Reader 点名，产出按幕(目)的 Anti-AI 报告（只列证据，不动文）。
- edit-synthesizer 综合裁决时对每个问题标注来源（冷读 / Anti-AI），评估严重等级（严重/中等/轻微），给出整体返修意见——明确修哪一章、怎么修、跨章关联与优先级，并给出分流建议（REGENERATE → writer/prompt-crafter/planner；局部表达 → anti-ai 编辑模式）。
- `edit.repair` 按整体返修意见执行；严重问题走 REGENERATE，中等/轻微表达问题由 anti-ai 编辑模式产出局部候选。内容问题交全新 writer；表达问题由 anti-ai 在 repair 阶段按意见执行。

`HARD FIX: synopsis delivery` 的判定标准见 `skills/cold-read-discipline.md`。编辑模式中，Reader 标记 HARD FIX 经 `edit.synthesize` 归为严重后，在 `edit.repair` 由新 writer 重写受影响章节；事实点齐全、字数达标或幕终点正确都不能抵消这个失败。

## 分流与分级（由 `edit.synthesize` 裁决）

`edit-synthesizer` 综合冷读报告与 Anti-AI 报告后，对每个问题给出：

- **来源归属**：标注问题来自 `冷读`（Reader）还是 `Anti-AI`（表达扫描），二者可能指向同一章的不同层面。
- **严重等级**：
  - `严重`：核心因果、人物动机、信息时序、场景骨架、跨章承接或 Prompt 设计失败，必须 REGENERATE。
  - `中等`：明显阻碍阅读的理解偏差、结构松散或较重的模板化表达，需改写或重写局部。
  - `轻微`：局部措辞、机械重复、解释腔或不自然对白，由 anti-ai 编辑模式局部处理。
- **分流建议**：
  - `REGENERATE`：正文执行失败 → 新 writer（原 Prompt）；Prompt 设计不足 → prompt-crafter 修 Prompt → 新 writer；上游规划冲突 → 对应 planner。
  - 局部表达（中等/轻微）→ anti-ai 编辑模式产出候选。
  - 正文成立 → `IGNORE`，不创建返修。

`IGNORE`/`EDIT`/`REGENERATE` 语义以 `skills/cold-read-discipline.md` 为准；anti-AI 与 completion-editor 共同执行 `skills/edit-boundary.md`。表达问题与内容问题不能合并成一个返修任务；跨章事实或核心因果问题必须走 `REGENERATE`；边界不清时保留原候选，交 Reader 复读判断。始终以正文证据和根因分流为准。

## 编辑模式 Anti-AI 全量扫描

`edit.anti-ai` 由顶层在 `edit.review` 之后派发 anti-ai，对**同幕章节**做表达扫描（幕末批量审读）。它不再等待 Reader 点名，而是主动全量扫描 Reader 读过的本幕全部章节，按幕(目)识别 AI 味、模板化表达、解释腔、机械重复、不自然对白等问题，产出按幕(目)组织的 Anti-AI 报告。此阶段 anti-ai 只列证据与原句定位、标注严重倾向与是否越出局部编辑边界，不直接改正文，也不写 `texts/`；实际编辑在 `edit.repair` 阶段按 `edit.synthesize` 的整体返修意见执行。扫描可挂载 `knowledge/anti-ai/index.md`（通用与题材规则）。

## 整体返修裁决 edit.synthesize

`edit.synthesize` 由顶层派发 edit-synthesizer，读取 Reader 冷读报告与 Anti-AI 报告，以两份报告为主要依据做综合裁决：对每个问题标注来源（冷读 / Anti-AI），评估严重等级（严重/中等/轻微），明确修哪一章、怎么修，指出跨章关联与处理优先级，并给出分流建议（REGENERATE 类交 writer/prompt-crafter/planner；局部表达类交 anti-ai 编辑模式）。冷读发现的重大内容问题（HARD FIX、核心因果失败）归为严重；Anti-AI 发现的纯表达问题多为中等/轻微，但若整章声线失真可升级。裁决结果写入 task，供 `edit.repair` 直接执行。两份报告对所有章节均无问题时，顶层跳过 `edit.repair` 直接 `edit.commit`。

**最小正文核对权限**：当两份报告对同一章存在分歧，或某条断言（如 HARD FIX、声线失真）需要定位正文证据才能分级时，edit-synthesizer 允许只读该章的关键段落核对证据，不作全面重读；核对范围必须写入整体返修意见（"已核对 vol-N-ch-M 第 X 场景"）。分级仍以两份报告为主，正文核对只用于消除分歧与确认证据，不引入报告未列的新问题。

## 复读

每次返修后重新派发 Reader，按 `skills/cold-read-discipline.md` 的「复读范围判定清单」确定范围（单章局部 EDIT 自受影响章前一章复读；单章 REGENERATE 自前一章至该章；跨章/跨幕复读整幕；Prompt 或幕纲变化先修产物、顶层确认、再写作复读）。复读是新的整体冷读，必须重新判断人物信息、场景因果、阅读节奏、期待变化和幕终点，不能只验证原问题卡。未复读接受的候选不得提交。

报告至少保留：

```markdown
verdict: PASS / FIX / STOP
act: vol-N-act-K

## 已成立处
{哪些人物、动作、关系、声音或场景已经成立，应当保留}

## 首读
{真实阅读反应}

## 问题与处理
- {章节}: {正文证据} -> {读者影响} -> {最可能根因} -> {建议处理角色: writer/prompt-crafter/planner/anti-ai} -> {最小处理}

## 不应改变
{返修时必须保留的语气、动作、留白、事实或人物选择}

## 仍未解决
{经过本轮返修和复读后仍未闭合的问题，需在下一轮或升级后处理}

## 最终复读
{PASS / FIX / STOP 与仍保留的事实}

## 接受候选
- {章节}: {task 候选路径}
```

存在未解决 HARD FIX、幕终点未成立或候选未通过最终复读时，不能提交接受正文。

## Anti-AI 扫描报告（按幕/目）

```markdown
act: vol-N-act-K
scanned: 全量（Reader 读过同幕章节）

### ch-M（章）
- 等级: 严重 / 中等 / 轻微
- 证据: {原句定位} -> {AI 味表现: 解释腔 / 模板化 / 机械重复 / 不自然对白 / ...}
- 边界: 局部可编辑 / 越界(需 REGENERATE 或交上游)
- 处理倾向: anti-ai 编辑(局部) / 升级
```

## 整体返修意见（edit.synthesize）

```markdown
act: vol-N-act-K

### 严重（优先处理）
- ch-M: {来源: 冷读/anti-ai} {问题} -> REGENERATE -> {writer/prompt-crafter/planner} -> {怎么修}

### 中等
- ch-Q: {来源} {问题} -> 改写局部 -> {要点}

### 轻微
- ch-R: {来源: anti-ai} {问题} -> anti-ai 编辑模式-> {局部处理}

### 跨章关联
{哪些章的问题相互牵连，需一并处理或保持一致性；REGENERATE 是否改变既定事实、是否触发后继章前情刷新}

### 优先级与执行顺序
{按严重等级与跨章关联排定的返修顺序}
```

## Commit

编辑模式提交由顶层执行确定性文件操作：

1. 只读取 Reader 报告中列出的接受候选；`IGNORE` 章节必须把实际复读的原始 `drafts/` 或 `texts/` 路径列为接受来源。
2. 确认全部候选是纯小说正文，再预检全部目标路径；任一候选混入说明、正文不完整，或目标存在且内容不同时，在写入前停止，不覆盖任何目标。
3. 所有预检通过后写入 `texts/vol-N-ch-M.md`。
4. 全部写入成功后清理当前 task 的返修候选和临时报告，并删除该 task 明确列出的已消费 draft；失败保留现场供 order 恢复。

`texts/` 是接受正文的项目输出路径。其他正文路径的维护由项目工具单独处理，不进入 Reader、返修和提交的创作上下文。

提交完成后进入 `state.update`（`skills/state-sync.md`）：continuity-updater 从本章定稿正文回流状态（角色 `state_history` 追加、时间线条目、伏笔台账推进、设定变更通知消费），随后下一章 `prompt.create` 直接读取最新状态。

## 幕间校准

提交当前幕后比较 `texts/` 的实际终点与下一幕 `start_state`：一致时直接推进；有真实偏差时只校准尚未执行的幕纲、章纲和 Prompt。已接受正文不回写；没有偏差不启动空校准角色。幕间校准与 `state.update` 分工：状态同步把正文事实写入 `settings/`，幕间校准核对规划产物与正文是否一致。
