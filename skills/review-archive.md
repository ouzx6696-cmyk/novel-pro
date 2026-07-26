# Reader、返修与提交

<!-- changed_in: 0.2.3 -->

Reader 是 Full 模式的内容裁判，按完整幕阅读。Fast 不加载本文件，也不运行 Reader 或 anti-AI。

本模块的报告和候选由角色返回，只有 `novel-agent` 可以把报告写入 `.agent/tasks/<task-id>/`、更新 order/run-log，或把最终接受正文提交到 `texts/`。Reader、anti-AI 不直接推进状态。

冷读协议、`HARD FIX: synopsis delivery` 定义、分流语义（IGNORE/EDIT/REGENERATE）和复读纪律以 `skills/cold-read-discipline.md` 为共享权威源。本文件只定义 Full 模式的阅读闭环、返修路由和提交流程。

## Full 阅读闭环

### Full 创作流程

```text
prompts.ready
→ `full.write`
→ `full.review`：Reader 按幕首读
→ `full.repair`：按正文证据分流
   ├─ IGNORE → 下一章或 full.commit（无返修）
   ├─ EDIT → anti-ai（表达问题，仅局部编辑）
   └─ REGENERATE → 按根因分流：
        ├─ 正文执行问题 → 新 writer + 原 Prompt
        ├─ Prompt 问题 → prompt-crafter 修 Prompt → 新 writer
        └─ 规划冲突 → 对应 planner → 重建下游产物
→ 受影响范围重新顺序阅读
→ 无未解决问题时 `full.commit`
→ `texts/vol-N-ch-M.md`
```

每次返修都必须重新顺序阅读受影响范围；不能只检查原报告中的标签是否消失。`HARD FIX`、`IGNORE`、`EDIT`、`REGENERATE` 只由 Reader 或完本 Reader 基于实际正文产生，脚本不能推导。

### 阅读闭环步骤

1. 顶层收齐正文完整、没有混入说明的 draft/candidate 或已接受 `texts/`，按叙事顺序为每幕派发独立 Reader。
2. Reader 先只读当前幕正文，作为目标读者冷读，记录理解、期待、疑问、情绪和幕末感受。
3. 首读完成后才读取当前幕 continuity contract 和必要诊断知识，追查正文中真实出现的问题。
4. 报告先写成立处和真实阅读体验，再引用正文证据，给出根因、受影响章节、最小处理方式和复读范围；Reader 不直接改文或派发角色。
5. 内容问题交全新 writer；表达问题只有 Reader 点名后才交 anti-AI。

`HARD FIX: synopsis delivery` 的判定标准见 `skills/cold-read-discipline.md`。Full 模式中，Reader 标记 HARD FIX 后，顶层必须创建新 writer 重写受影响章节；事实点齐全、字数达标或幕终点正确都不能抵消这个失败。

## 分流

- `IGNORE`：正文成立，保留原文，不创建返修。
- `EDIT`：边界清楚的局部表达、局部可信度、局部连续性或清晰度问题；普通 Full 的表达问题交 anti-AI，显式 `completion.revise` 才交 completion-editor。若连续性涉及跨章事实或核心因果，升级为 `REGENERATE`。
- `REGENERATE`：核心因果、人物动机、信息时序、场景骨架、跨章承接或 Prompt 设计失败。Reader 同时标明根因位置：正文执行失败时，顶层加载 `skills/writing.md`，使用原 Prompt 交全新 writer；Prompt 设计不足先由 prompt-crafter 修复受影响 Prompt；上游规划冲突返回对应 planner。

anti-AI 与 completion-editor 共同执行 `skills/edit-boundary.md`，本文件不另建禁止列表。表达问题与内容问题不能合并成一个返修任务；跨章事实或核心因果问题必须走 `REGENERATE`；边界不清时保留原候选，交 Reader 判断。上述 HARD FIX 表现是非穷尽示例，始终以正文证据和根因分流为准。

## 复读

每次返修后重新派发 Reader：局部章节变化从受影响章节前一章开始顺序复读；跨章节或跨幕变化复读当前整幕；Prompt 或幕纲变化先由拥有该产物的角色完成修复并由顶层阅读确认，再重新写作。复读是新的整体冷读，必须重新判断人物信息、场景因果、阅读节奏、期待变化和幕终点，不能只验证原问题卡。未复读接受的候选不得提交。

报告至少保留：

```markdown
verdict: PASS / FIX / STOP
act: vol-1-act-2

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

## Commit

Full 提交由顶层执行确定性文件操作：

1. 只读取 Reader 报告中列出的接受候选；`IGNORE` 章节必须把实际复读的原始 `drafts/` 或 `texts/` 路径列为接受来源。
2. 确认全部候选是纯小说正文，再预检全部目标路径；任一候选混入说明、正文不完整，或目标存在且内容不同时，在写入前停止，不覆盖任何目标。
3. 所有预检通过后写入 `texts/vol-N-ch-M.md`。
4. 全部写入成功后清理当前 task 的返修候选和临时报告，并删除该 task 明确列出的已消费 draft；失败保留现场供 order 恢复。

`texts/` 是接受正文的项目输出路径。其他正文路径的维护由项目工具单独处理，不进入 Reader、返修和提交的创作上下文。

## 幕间校准

提交当前幕后比较 `texts/` 的实际终点与下一幕 `start_state`：一致时直接推进；有真实偏差时只校准尚未执行的幕纲、章纲和 Prompt。已接受正文不回写；没有偏差不启动空校准角色。
