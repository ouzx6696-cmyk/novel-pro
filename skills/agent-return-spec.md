# Agent 文件规范与返回规范

本文件是 `agents/` 下所有 agent 文件结构与返回描述的统一权威源。它回答三个问题：**agent 文件应该长什么样、agent 应该怎么知道自己这步做什么、agent 返回时应该带什么**。所有 agent 文件（含新建）按本规范组织；SKILL.md 路由表、dispatch.md 派发卡与本文件互相引用，不另建平行表述。

## 一、agent 文件五要素结构

每个 agent 文件按以下小节组织（按需合并，但五要素必须齐备、可索引）：

| 小节 | 回答的问题 | 必须包含 |
|---|---|---|
| `## 身份与边界` | 我是谁？我能做什么、绝不越界做什么？ | 角色定位、所有权边界（只写什么、绝不写什么） |
| `## 本步任务` | 我这次 operation 要完成什么？范围多大？ | 触发条件、任务范围（一幕/一卷/一批/一章/全书）、产出物 |
| `## 本步重点` | 这一步的质量核心判断是什么？ | 本步最关键的 2-4 条判断标准（不是流程复述，是"做得好"的标准） |
| `## 调用与输入` | 我读什么？挂载什么知识？ | 输入文件清单（settings/幕纲/章纲/Prompt/报告/知识）、前置条件（如 author_confirmed） |
| `## 完成判定与返回` | 我怎么知道做完了？返回什么？ | 完成判定标准、返回四要素（见下节） |

frontmatter 规范：

- `name` / `description`（含可执行定位，如"一次负责一卷"）/ `agent_created: true` / `role` / `react: true` 必须有。
- `changed_in`：记录该文件最近一次被修改的发行号（如 `"0.2.3"`）。
- `skills` / `knowledge`：挂载本角色需要加载的模块与知识索引；**设计例外**——`writer`（零知识隔离，上下文由 base + Prompt 组成）、`reader` 与 `completion-reviewer`（冷读保护，首读不预挂知识）不挂 `skills`/`knowledge`，其诊断所需的模块（如 `skills/review-archive.md`、`skills/cold-read-discipline.md`）由 dispatch 在创建时按派发卡注入，agent 正文写明"首读后才加载"。

## 二、返回四要素

所有 agent 的返回（`## 完成判定与返回` 节）必须覆盖四要素，确保 novel-agent 在收到返回后能做出一致的路由判断：

1. **写入产物**：实际写入了哪些文件或报告。格式：文件路径，或"不写产物，仅返回报告"。
2. **返回摘要**：novel-agent 判断完成与否所需的关键信息。规划角色：文件路径 + 关键事实摘要；writer：正文是否完整；reader/reviewer：verdict + 建议处理角色。
3. **下一跳信号**：返回结果决定下一 operation 的选择时，明确写出判断依据。例如 Reader 的"建议处理角色"决定 `edit.repair` 的分流（writer / prompt-crafter / planner / anti-ai）；prompt-crafter 的自检结论表决定顶层抽查范围。
4. **失败/冲突证据**：无法完成时的具体缺口描述（缺失前提事实、规划冲突位置、Prompt 无法执行的根因、需上游处理的问题）。

## 三、引用与一致性

- agent 正文引用模块/知识/模板时使用仓库源码路径（`skills/`、`knowledge/`、`templates/runtime/`）；部署后的项目内使用 `.claude/` 部署路径。
- agent 的「本步任务」与 dispatch.md 派发卡的「创建角色/角色输入/允许写入/返回顶层」必须一致；「调用与输入」与派发卡「角色输入」一致。
- 新增或修改 agent 时，同步核对：dispatch.md 对应派发卡、SKILL.md 路由表与角色地图、docs/interface-reference.md 角色说明。
