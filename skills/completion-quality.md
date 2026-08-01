# Completion Quality

只在用户明确要求全书质检、全本质检、全书返修或完本修改时加载。它扩大阅读范围，但不改变“先读正文、后追根因”的原则，也不把完本任务变成规划字段盘点。

完本任务是当前 order/task 的旁路 operation，不改变长期 cursor。completion-reviewer 和 completion-editor 返回报告或候选；只有 `novel-agent` 持久化 task、控制面和最终提交。

冷读协议、`HARD FIX: synopsis delivery` 定义、分流语义（IGNORE/EDIT/REGENERATE）和复读纪律以 `skills/cold-read-discipline.md` 为共享权威源。本文件只定义完本任务的阅读范围、根因追溯和返修路由。

## 临时任务

完本任务使用 `completion.inspect` 或 `completion.revise`，范围、进度、报告和候选写入当前 `.agent/order.yaml` 与 `.agent/tasks/<task-id>/`，不增加长期 cursor 节点。

默认正文来源是 `texts/vol-N-ch-M.md`。存在其他正文来源时，由当前任务明确 source map；多个来源无法确定主次时暂停并由作者选择，不按文件名、时间或数量猜测。

`completion.inspect` 先按幕冷读全书，再按证据追查根因并写报告；`completion.revise` 只处理报告点名的最小范围，候选经受影响范围复读和全书承接复读后才结束。完本任务不改变长期 cursor，也不创建新的长期阶段。

## 先读正文

```text
completion.inspect
  -> scope
  -> prose cold read by act
  -> whole-book reread
  -> evidence trace
  -> synthesize
  -> complete
```

completion-reviewer 按叙事顺序冷读每幕正文。首读不看幕纲、章纲、Prompt、既有报告、诊断规则或问题清单，先记录：

- 读者在何处理解、误解或失去方向。
- 人物欲望、选择、关系和声音是否持续成立。
- 关键行动是否真实发生，还是被旁白或复盘概述。
- 信息、伏笔、能力、资源和世界规则如何被正文实际呈现。
- 期待、压力、情绪投入和未兑现承诺怎样跨章、跨幕变化。

长幕按自然叙事断点继续，不按固定字数切块。不得用关键词搜索、问题计数、字段覆盖或脚本扫描替代阅读。

## 全书复读与根因追溯

各幕首读完成后，按卷幕顺序重新阅读关键承接，观察人物弧线、信息时序、承诺兑现和返修影响。只有正文已经暴露真实问题时，才读取相关幕纲、章纲、Prompt、设定或既有报告追查根因：

- 规划本身不成立。
- 章纲拆解丢失因果或人物选择。
- Prompt 把行动压成事件标题，或遗漏关键承接。
- Prompt 成立但正文没有把场景写出来。
- 跨幕入口与已接受正文真实偏离。

根因分类服务返修范围，不是评分或问题计数。没有正文证据时，不因规划字段缺失制造返修。

需要创作知识帮助判断根因时，从 `knowledge/index.md` 选择与当前正文问题直接相关的最小入口；知识只解释已经出现的阅读问题，不预先生成检查清单。

## 汇总

汇总报告先写正文中已经成立的部分和真实阅读体验，再写有证据的问题：具体章节、正文表现、读者影响、最可能根因、最小返修范围和需要作者取舍之处。报告写入当前 task，不直接修改正文或规划。

完本任务不是把全书改成同一种“正确文风”。跨章比较时优先看人物声音是否从选择和关系中持续生长、章节是否有不同的呼吸，以及哪些差异是 POV、人物处境或场景功能需要的。没有实际阅读损害的粗粝、停顿、幽默或留白保留。

## 完本返修

```text
completion.revise
  -> scope
  -> assess from prose evidence
  -> plan minimal repair
  -> writer/editor candidate
  -> holistic reread
  -> next affected act
  -> whole-book reread
  -> complete
```

分流语义（IGNORE/EDIT/REGENERATE）见 `skills/cold-read-discipline.md`。完本模式的特有路由：

- `EDIT` 交 completion-editor 输出 task 候选；不得重建核心因果、跨章事实或 Prompt。
- `REGENERATE`：Prompt 已经成立时，使用原 Prompt 与返修焦点交新 writer；Prompt 设计不足时，先在所在幕或批次中修复受影响 Prompt；规划冲突返回拥有对应产物的 planner。

普通编辑模式 表达问题仍交 anti-AI；只有显式 `completion.revise` 且问题卡边界清楚时，才交 completion-editor。连续性问题若涉及跨章事实或核心因果，必须升级为 `REGENERATE`，不能由局部编辑器处理。
completion-editor 与 anti-AI 的共同禁止边界以 `skills/edit-boundary.md` 为唯一权威源，本文件只定义完本分流。

返修只处理正文已经证明的问题。候选收齐后，completion-reviewer 重新顺序阅读整个受影响范围，重新判断人物、因果、节奏和阅读体验；不能只核对原问题卡。全部返修后再做一次全书承接复读，发现新问题回到最早受影响位置。

## 提交边界

只提交 Reader 整体复读明确接受的纯正文候选。提交前必须同时确认：候选没有混入说明且正文完整；没有未解决的 HARD FIX；最终整体复读已经通过；目标路径不存在，或已存在内容与候选一致。文件预检只检查来源、目标和覆盖冲突，不评价文学质量。任一条件不满足就在写入前停止；成功后清理当前 task，失败时保留现场。
