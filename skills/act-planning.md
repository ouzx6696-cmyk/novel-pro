# Act Planning

幕是卷内自然形成的叙事阶段，也是章纲规划和编辑模式阅读的基本范围。幕边界由人物、关系、信息和局势的阶段变化决定，不按固定章数切分。长期状态写作 `outline.acts`；整卷地图使用 `outline.act-map`，详细幕纲使用 `outline.act`。

## 幕规划执行入口（先读这一节）

| 步骤 | operation | 角色 | 读 | 写 | 判定 → 下一跳 |
|---|---|---|---|---|---|
| 1 | `outline.act-map` | act-planner ×1 | 已确认卷纲（驱动引擎：冲突阶梯/信息差弧线）、必要设定、`foreshadowing.md`、`timeline.md`、`knowledge/plot/act-decomposition.md` | `acts/volume-N-acts.md`（幕地图） | 幕地图覆盖整卷、幕边界落在真实状态变化处、与卷纲无冲突 → `outline.act` |
| 2 | `outline.act` | act-planner ×1 | 卷纲、幕地图、项目事实、相邻幕接口、已接受正文入口 | `acts/vol-N-act-K.md`（11 字段：dramatic_task/start_state/conflict_development/character_arcs/information/emotional_curve/promises/setting_constraints/continuity_contract/chapter_roles/end_state） | start_state 承接上一幕、end_state 可被下一幕直接承接、幕间连续性检查通过 → `outline.chapters` |

**知识调用**：拆幕方法论权威 = `knowledge/plot/act-decomposition.md`（第零步卷内分幕操作原则、六步工作流、边界判定信号、题材差异、验证清单、反模式；幕间承接五条件：事实/动机/代价/信息差/承诺，见其「承接条件」节）——建立幕地图前必读；长篇连续性通用方法（按幕拆章、状态继承）见 `knowledge/plot/continuity.md`；题材幕形态差异按 `genre_id` 从 `knowledge/genre/index.md` 叠加。方法名不写进幕纲，只写人物选择、事件因果和读者期待。

## 整卷幕地图

act-planner 先读取已确认卷纲、本卷必要设定、`foreshadowing.md`、`timeline.md`、相关人物设定、已接受正文和真正相关的创作知识，建立 `acts/volume-N-acts.md`。拆幕的方法论依据见 `knowledge/plot/act-decomposition.md`（第零步卷内分幕操作原则、六步工作流、边界判定信号、题材差异、验证清单和反模式）——它是通用写作底座（plot 方法）的一部分，act-planner 应在建立幕地图前完成对该文档的阅读；题材差异再按 `genre_id` 从题材画像叠加。这些输入只提供已确认或已发生的事实，不替代幕内正文。

幕地图确定：

- 各幕的阶段顺序和叙事功能。
- 每幕的起点、终点与主要冲突。
- 人物弧线和承诺在各幕的推进位置。
- 相邻幕之间需要传递的状态。

幕数量服从卷内冲突的自然发展。`chapter_roles` 只标记幕内章节功能，不代替详细章纲。

## 单幕规划

顶层按叙事顺序创建 act-planner，一次负责一个 `acts/vol-N-act-K.md`。act-planner 只写当前幕产物，不修改卷纲、设定或 `.agent`。详细幕纲包含：

- `dramatic_task`：本幕必须完成的阶段变化。
- `start_state`：人物、关系、信息、资源和局势的真实起点。
- `conflict_development`：冲突如何建立、加压、转向并形成结果。
- `character_arcs`、`information`、`emotional_curve` 和 `promises`。
- `setting_constraints`：世界、能力、时间、空间和资源边界。
- `continuity_contract`：事实主体、有效阶段、唯一事件归属和退出交接。
- `chapter_roles`：幕内各章的功能和状态变化。
- `end_state`：下一幕能够直接承接的具体状态。
- 可选：`## 设定变更通知` 块——本幕规划确认会改变项目事实（新角色、关系/能力/世界变化、时间线或伏笔新条目）时追加（规范见 `templates/acts/vol-N-act-K.md`「设定变更通知」节）。通知不是事实，只有正文兑现并验收后由 `state.update` 消费并写入 `settings/`，同时从源文件移除。

## 幕间承接

幕规划按叙事顺序检查上一幕终点、当前幕起点和下一幕入口。当前幕拥有自己的修改权；相邻幕的问题返回顶层交给对应 act-planner。

已接受正文提供已经发生的事实。正文终点与后续入口一致时直接推进；真实偏差只调整尚未执行的幕纲、章纲和 Prompt。幕纲返回顶层后，由顶层读过并更新 order，不能自行推进长期 cursor。
