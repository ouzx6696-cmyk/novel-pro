# Context Pack（预制包）

本模块规定 `settings/context-pack.md` 的建包、用包、补包与重建规则。它是 prompt-crafter 在 Prompt 创建阶段的正式知识消费形态：把知识库的**通用写作底座**（连载基线、剧情/场景/人物方法）与本卷**类型风格知识**（题材画像）按题材裁剪压缩为一包，避免每个 Prompt 任务重复下钻 8–18 个知识文件。

本模块只做契约整合与一份项目级预制产物，不新增角色、不增加门禁或评分脚本；pack 的有效性由阅读判断（顶层、prompt-reviewer、alignment）保证。

## 形成者与本卷唯一性

- **形成者**：本卷**第一个** `prompt.create` 任务的 prompt-crafter。它 frontmatter 已挂载底座与类型索引（webnovel/genre/scene/plot/character），自建自用，不新增角色、不改所有权表的角色清单。
- **消费者**：本卷后续所有 `prompt.create` 任务（含返修时的 Prompt 修复）；prompt-reviewer 可选核对。
- **每卷一包**：换卷重建；包内只装方法与题材执行要点，不写卷纲剧情内容（那是幕纲/章纲职责）。
- **不需要作者确认**：pack 是 skill 知识的项目化压缩，不是创作决策，区别于 `settings/writing-style.md`（后者是作者确认物）。pack 头部记录来源清单，供顶层与 prompt-reviewer 阅读核对。

## 建包（本卷首个 prompt.create 任务）

建包按知识库两层结构进行：**通用写作底座必选 + 类型风格知识按题材叠加**。

1. **底座层（必选，跨题材）**：读取 `knowledge/webnovel/index.md`（连载基线，含 `fanqie-baseline.md`）、`knowledge/scene/index.md`（含自包含提示词方法 `self-contained-prompt.md`）、`knowledge/plot/index.md`（冲突/钩子/节奏/伏笔等本卷用得到的剧情方法；**不含幕拆解方法 `act-decomposition.md`**——那是 act-planner 的拆幕方法，prompt-crafter 不拆幕，不进包）、`knowledge/character/index.md`；按本卷叙事重心从 scene/plot/character 选择子文件（见下方「建包子文件选择清单」）。
2. **类型层（叠加，按题材）**：读取 `knowledge/genre/index.md`（+父题材速写）与 `settings/genre-setting.md` 的已确认题材期待，叠加当前 `genre_id` 的题材画像。
3. 把底座方法与题材差异裁剪压缩为 8 节（读者与节奏基线、题材执行要点、冲突钩点节奏、场景写法工具箱[含自包含提示词方法]、人物决策与对手压力、文风提取接口、禁用与边界、使用纪律）。
4. 写入 `settings/context-pack.md`，头部 frontmatter 记录 `pack_contract`、`volume`、`genre_id`、`parent_genre`、`formed_by`、`sources`、`style_pointer`。
5. 继续完成本任务范围的章级 Prompt（同一任务内，不新增 operation）。

## 建包子文件选择清单

**底座层子文件**按本卷叙事重心选择；**每类至少选 1 个、至多 3 个**，不追求读全。清单是阅读选择依据，不是门禁；重心不明或另有需要时按任务裁量，并记录在返回摘要中供顶层核对。

| 本卷叙事重心 | scene 必选（按需 1-2） | plot 必选（按需 1-2） | character 必选（按需 1） |
|---|---|---|---|
| 冲突/对抗主导（战斗、追逐、审讯、比赛） | `scene/confrontation.md`、`scene/scene-truth.md` | `plot/conflict.md`、`plot/pacing.md` | `character/decision-engine.md` |
| 人物/关系主导（日常、感情、家庭、代际） | `scene/dialogue.md`、`scene/scene-truth.md` | `plot/emotional-pull.md`、`plot/foreshadowing.md` | `character/arc-continuity.md` |
| 事件/转折主导（悬念、反转、新阶段开启） | `scene/transition.md`、`scene/inner-thought.md` | `plot/hooks.md`、`plot/reversals.md` | `character/antagonist.md` |
| 卷首/幕首开篇 | `scene/chapter-structure.md`、`scene/pov.md` | `plot/opening.md`、`plot/hooks.md` | `character/decision-engine.md` |

低频场景（死亡场景、群戏、调查、环境、体术动作、破案）不列入清单，出现时按 `补包` 规则单点补读对应 `scene/<file>.md`。建包返回摘要必须列出实际选用的底座子文件，顶层据此核对是否与卷重心一致。

**类型层不进入清单选择**：按 `genre_id` 读对应题材画像（含父题材速写），题材差异直接进包第 2 节「题材执行要点」与第 7 节「禁用与边界」。

## 用包（后续每个 prompt.create 任务）

- 读 `settings/context-pack.md`（1 个文件）替代 `knowledge/` 下钻（8–18 个文件）。
- `settings` 事实文件、幕纲、章纲、承接入口照常按章筛读。
- `settings/writing-style.md` 仍每任务读（它是项目确认物、本章质感源头，保留；pack 第 6 节固化的是"怎么提取"，省去的是推理成本而非这次读取）。
- 每章 Prompt 只取本章所需，不把包整段搬进 Prompt；不把方法名、来源名、术语写进 Prompt 或正文产物。

## 补包（pack 未覆盖的场景/方法）

- 当次任务单点补读对应知识文件，返回时向顶层说明。
- 顶层决定补入 pack 对应小节（由下一个 `prompt.create` 任务顺手完成）。

## 重建

换卷 / `genre-setting` 或 `writing-style` 经作者重新确认 / `alignment` 发现漂移时：

- 下一个 `prompt.create` 任务先重建包再创建 Prompt。
- 无脚本校验：pack 头部 `sources` 与 `volume` 字段供阅读核对；漂移靠顶层阅读、prompt-reviewer 审查、alignment 任务三道人工判断发现。

## 与既有契约的关系

- **不破坏知识加载契约**：`knowledge/index.md` 已声明 `settings/context-pack.md` 是 prompt-crafter 的正式知识消费形态；本卷首个 `prompt.create` 任务完成索引加载与下钻并沉淀为 pack 后，后续任务读包即视为完成知识加载，不构成"跳过角色文件与索引加载"。
- **Reader 冷读保护不动**：reader、completion-reviewer 不读 pack，首读纪律、按需追因路径一字不改。pack 只服务 Prompt 创建侧。
- **writer 边界不动**：writer 仍只收单章 base + 单章 Prompt，不读 pack。
- **anti-ai 隔离不动**：`knowledge/anti-ai/` 不进 pack；它仍在编辑模式中按需加载（edit.anti-ai 全量扫描 / edit.repair编辑模式）。
- **迁移**：pack 是派生产物，迁移不搬运；新项目在本卷首个 `prompt.create` 任务按新 runtime 知识库重建。
- **alignment**：整卷对齐任务增加一项检查——pack 与已确认的 `genre-setting` / `writing-style` 是否漂移，漂移则列入重建清单（只重建包，不动已接受正文）。
