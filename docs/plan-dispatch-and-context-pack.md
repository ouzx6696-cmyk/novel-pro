# 派发整合与 Context Pack 预制包方案

日期：2026-07-26 ｜ 针对版本：`0.2.2-pro` ｜ 状态：待评审

本方案解决两个痛点：

1. **写作流程的派发不够明确**——同一套派发规则散写在四份文档里，顶层每次派发都要自行拼合。
2. **Prompt 创建反复读取固定文件**——prompt-crafter 每个任务重复读取同一批跨项目不变的知识文件。

约束（作者指定）：不增加门禁脚本、不新增角色、不改变长期状态机；本方案只做**文档契约整合**与**一份项目级预制产物**，工具脚本仅做发行清单登记（各加一行，非逻辑改动）。

---

## 一、现状诊断

### 痛点 1：派发规则碎片化，四处重复且缺少"触发→模块"映射

同一套 Fast/Full / Prompt 创建流程目前写在四个位置，内容相互重叠：

| 位置 | 内容 | 问题 |
|---|---|---|
| `SKILL.md` | "创作主线""Prompt 创建""Writer Base""Fast""Full"五节 + 按主题索引的"路由"节 | 路由按**主题**（卷纲/幕规划/Prompt/状态）索引，不是按 `order.operation` 索引；顶层要自己把 operation 翻译成主题再查表 |
| `skills/dispatch.md` | cursor 表（10 行）、order.operation 表（15 行）、所有权大表（13 行）、创作循环、恢复 | 所有权大表有"读取/写入/返回/下一跳/恢复"，但**没有"触发条件"和"加载模块"两列**；"何时创建哪个角色"要回 novel-agent.md 找散文 |
| `skills/writing.md` | Fast/Full 的 writer 派发机制 | 与 dispatch.md"创作循环"节、SKILL.md Fast/Full 节是同一流程的第三次、第四次表述 |
| `agents/novel-agent.md` | "项目启动""Prompt 创建""创建 Writer""Fast""Full"五节散文 | 再次复述上述流程，且触发条件（如"用户明确提出审核提示词时才创建 prompt-reviewer"）只存在于这里的散文中 |

后果：

- 顶层每次派发要同时核对 3–4 份文档才能拼出一个操作的完整派发决策（触发条件在 agent 文件、权限在 dispatch 大表、流程细节在模块、路由在 SKILL.md）。
- 边界情形靠推理而非查表：例如 `prompt.review` 是否改变 cursor、`alignment` 能否创建 writer，答案分别藏在不同文件的散文里，恢复场景下容易作出不一致决定。
- 重复表述埋下漂移风险：改一处忘改其余三处（历史上 `prompts.ready` 的完成语义在 SKILL.md 与 dispatch.md 的措辞已不完全一致）。

### 痛点 2：Prompt 创建每任务重复读取 8–18 个固定知识文件

prompt-crafter 每个任务（一幕或一个连续批次）的读取面：

| 类别 | 文件 | 是否随任务变化 |
|---|---|---|
| 流程模块 | `skills/prompt.md` | 固定 |
| 知识索引 | webnovel、genre、scene、plot、character 共 5 个 index | 固定 |
| 知识下钻 | `webnovel/fanqie-baseline.md`、`genre/<id>.md`（+父题材）、scene 按需 2–6 个、plot 按需 2–5 个、character 按需 1–3 个 | **同一卷内完全固定**（题材不变、方法库不变） |
| 项目事实 | `settings/` 7 个文件（style、genre、world、preferences、foreshadowing、timeline、character-setting/*） | 按章筛选，必要读取 |
| 规划产物 | 当前幕纲 + 任务范围章纲 | 必要读取 |
| 承接入口 | 上一章/幕末段 | 必要读取 |

一卷通常 4–6 个 `prompt.create` 任务（每幕一个、长幕多批次），意味着**同一批知识文件被逐字重读 4–6 次**。这些文件跨项目、跨卷、跨幕不变，是典型的可预制内容。

关键观察：项目里已有成功先例——文风库的处理就是"知识库 → 项目级沉淀 → 下游只读沉淀"的三段式：

```text
knowledge/style/index.md（原型库）
→ settings/writing-style.md（volume-planner 与作者沉淀为项目声线）
→ Prompt「本章质感」（prompt-crafter 按章提取）
```

本方案把同一个模式从文风推广到题材、连载基线、剧情、场景、人物五类知识，产物就是 **Context Pack（预制包）**。

---

## 二、方案总览

```text
痛点1 → 派发矩阵：dispatch.md 的大表升级为 15 张「操作派发卡」，
        一张卡 = 触发 → 模块 → 角色 → 输入 → 写入 → 返回 → 完成判定 → 下一跳 → 恢复。
        SKILL.md 路由节改为 operation 索引；novel-agent.md 删除重复散文，只留指针。

痛点2 → Context Pack：每卷第一个 prompt.create 任务由 prompt-crafter 先「建包」，
        把题材画像 + 连载基线 + 剧情/场景/人物方法按本项目题材裁剪压缩为
        settings/context-pack.md；后续 prompt.create 任务读包替代知识库下钻。
```

两个方案互相咬合：派发卡的 `prompt.create` 卡把"输入"明确写成"pack + 幕纲 + 章纲范围 + settings 事实按需 + 承接入口"，派发明确性和读取收敛在同一张卡上落地。

---

## 三、方案 A：派发矩阵（操作派发卡）

### 3.1 卡片格式

把 `skills/dispatch.md` 现有"文件接口与所有权"大表重构为按 `order.operation` 组织的派发卡，每个 operation 一张卡，固定九个字段：

```markdown
### prompt.create
- 触发：cursor 在 `outline.chapters` 且目标范围章纲全部形成；order 为 idle 或上一批次已完成
- 加载模块：`skills/prompt.md`；本卷首个任务追加 `skills/context-pack.md`
- 创建角色：prompt-crafter ×1（范围 = 一幕或一个连续批次）
- 角色输入：context-pack（首任务为知识库原文）、当前幕纲、范围内章纲、settings 事实按需、承接入口
- 允许写入：`prompts/vol-N-ch-M.md`；首任务另写 `settings/context-pack.md`
- 返回顶层：Prompt 路径、每章承接摘要、事实缺口或上游冲突
- 完成判定：范围内每章 Prompt 落盘且顶层逐一读过（存在 ≠ 通过）
- 下一跳：下一批次 `prompt.create`，或范围齐后 cursor 进 `prompts.ready`
- 恢复入口：只重做缺失或被正文证据点名的 Prompt；pack 未漂移不重建
```

### 3.2 十五张卡清单

对 `order.operation` 全量建卡，与现有 dispatch.md 两张表一一对应、不新增任何 operation：

| operation | 角色 | 模块 | 长期 cursor 影响 |
|---|---|---|---|
| `outline.volume` | volume-planner | `skills/planning.md` | → `outline.volume` |
| `outline.act-map` | act-planner | `skills/act-planning.md` | `outline.acts` 内临时操作 |
| `outline.act` | act-planner | `skills/act-planning.md` | `outline.acts` 内临时操作 |
| `outline.chapters` | chapter-planner | `skills/planning.md` | → `outline.chapters` |
| `prompt.create` | prompt-crafter | `skills/prompt.md`（+首任务 `skills/context-pack.md`） | 完成后 → `prompts.ready` |
| `prompt.review` | prompt-reviewer | `skills/prompt.md` 末节 | 旁路，不变 |
| `fast.write` | writer×N | `skills/writing.md` | → `draft.write` → `drafts.ready` |
| `full.write` | writer×N | `skills/writing.md` | → `draft.write` → `review` |
| `full.review` | reader | `skills/review-archive.md` + `skills/cold-read-discipline.md` | `review` |
| `full.repair` | writer / prompt-crafter / planner / anti-ai | `skills/review-archive.md`（+anti-ai 时 `skills/edit-boundary.md`） | `review` |
| `full.commit` | novel-agent 自身 | `skills/review-archive.md` | → `volume.complete` 或下一目标 |
| `completion.inspect` | completion-reviewer | `skills/completion-quality.md` + `skills/cold-read-discipline.md` | 旁路，不变 |
| `completion.revise` | completion-editor 等 | `skills/completion-quality.md` + `skills/edit-boundary.md` | 旁路，不变 |
| `alignment` | 各产物拥有者 | `skills/volume-alignment.md` | 旁路，不变 |
| `migration.review` | novel-agent 自身 | `skills/migration.md` | `migration.review` |

> 说明：`full.repair` 一张卡内列四个分流去向（正文执行→新 writer、Prompt→prompt-crafter、规划→planner、表达→anti-ai），与 dispatch.md 现有分流语义完全一致，只是从散文搬进卡里。

### 3.3 文档收敛（去重）

派发卡成为唯一权威后，其余三处收敛为指针，**删除重复流程散文，不删任何规则**：

- `agents/novel-agent.md`：保留控制面所有权、版本门禁入口、writer 构造机制一句话 + 指向 `skills/writing.md`；"项目启动 / Prompt 创建 / Fast / Full"四节散文压缩为"按 dispatch.md 派发卡执行"。文件从 68 行收敛到约 40 行。
- `SKILL.md`："路由"节改为按 operation 索引（直接复用 3.2 表的 operation → 模块两列）；"Fast""Full"两节删除流程图，各留一句定义 + 指向 dispatch.md。创作主线图保留（它是阶段概览，不是派发规则）。
- `skills/writing.md`：保留 writer base 构造与正文阅读判断的**细节**（这是模块职责），删除与 dispatch.md 重复的流程图，开头声明"调度时序以 dispatch.md 派发卡为准，本模块只规定 writer 怎么造、草稿怎么读"。
- `templates/CLAUDE.md` 第 5 行已经是正确模式（"先读取 dispatch，再按当前 operation 加载一个对应阶段模块"），不用改。

---

## 四、方案 B：Context Pack 预制包

### 4.1 产物定义

- **位置**：`settings/context-pack.md`（与 genre-setting、writing-style 同层，属于 dispatch.md"项目事实的承接"表定义的"由规划/创建阶段形成、下游按需消费的事实来源"）。
- **形成者**：本卷**第一个** `prompt.create` 任务的 prompt-crafter。它 frontmatter 已挂载 5 个知识索引，自建自用，不新增角色、不改所有权表的角色清单。
- **消费者**：本卷后续所有 `prompt.create` 任务（含返修时的 Prompt 修复）；prompt-reviewer 可选核对。
- **不需要作者确认**：pack 是 skill 知识的项目化压缩，不是创作决策，区别于 writing-style.md（后者是作者确认物）。pack 头部记录来源清单，供顶层与 prompt-reviewer 阅读核对。
- **每卷一包**：换卷重建；包内不写卷纲剧情内容（那是幕纲/章纲的职责），只装方法与题材执行要点。

### 4.2 包内容结构（模板 `templates/settings/context-pack.md`）

```markdown
---
pack_contract: 1
volume: {N}
genre_id: {题材编号}
parent_genre: {父题材或空}
formed_by: prompt.create 首任务（vol-N-act-K）
sources: [genre/<id>.md, genre/<parent>.md, webnovel/fanqie-baseline.md,
          plot/{实际选用的文件}, scene/{实际选用的文件}, character/{实际选用的文件}]
style_pointer: settings/writing-style.md
---

## 1. 读者与节奏基线
{连载基线 × 题材期待的合并压缩：本章最低交付、钩点节奏、空章/毒点禁忌，
 只留会改变章级决策的条目，不抄来源名}

## 2. 题材执行要点
{本题材的世界逻辑、成立条件、典型失败模式、表达要求的项目化压缩；
 与 settings/genre-setting.md 的作者确认内容对齐，不重复抄写，冲突以 genre-setting 为准}

## 3. 冲突、钩点与节奏方法
{plot 知识压缩：本卷幕结构下真正用得到的冲突成立条件、钩点布置、强弱交替、伏笔纪律}

## 4. 场景写法工具箱
{scene 知识压缩：按本卷高频场景类型（对白/对抗/调查/战斗/群像等）裁剪后的方法要点；
 低频类型不留全文，只留一行"出现时补读 scene/<file>.md"}

## 5. 人物决策与对手压力
{character 知识压缩：决策发动机、反派自洽压力、跨幕弧线连续的最小要点}

## 6. 文风提取接口
{指向 writing-style.md 的固定小节清单（声线定位/节奏配比/声线禁区/基准样章）
 +「本章质感」提取规则：每章取少量声线特征、一个节奏型、相关禁区、一句样句锚点}

## 7. 禁用与边界
{题材禁忌 + 作者边界（引自 genre-setting）+ 声线禁区指针；不新增规则，只做汇集}

## 8. 使用纪律
- 每章 Prompt 只取本章所需，不把包整段搬进 Prompt
- 不把方法名、来源名、术语写进 Prompt 或正文产物
- 包未覆盖的场景类型：允许单点补读一个知识文件，并在返回中说明，由顶层决定是否补入包
- 上游事实缺口或冲突：返回顶层，不自行补写
```

### 4.3 生命周期

```text
建包：本卷首个 prompt.create 任务
      → prompt-crafter 读取 5 个知识索引并下钻（唯一一次全量读取）
      → 结合 genre_id 裁剪压缩，写 settings/context-pack.md
      → 继续完成本任务范围的章级 Prompt（同一任务内，不新增 operation）

用包：后续每个 prompt.create 任务
      → 读 pack（1 个文件）替代 knowledge/ 下钻（8–18 个文件）
      → settings 事实文件、幕纲、章纲、承接入口照常按章筛读
      → writing-style.md 仍每任务读（它是项目确认物、本章质感源头，保留；
        pack 第 6 节固化的是"怎么提取"，省去的是推理成本而非这次读取）

补包：出现 pack 未覆盖的场景/方法需求
      → 当次任务单点补读对应知识文件，返回时向顶层说明
      → 顶层决定补入 pack 对应小节（由下一个 prompt.create 任务顺手完成）

重建：换卷 / genre-setting 或 writing-style 经作者重新确认 / alignment 发现漂移
      → 下一个 prompt.create 任务先重建包再创建 Prompt
      → 无脚本校验：pack 头部 sources 与 volume 字段供阅读核对，漂移靠
        顶层阅读、prompt-reviewer 审查、alignment 任务三道人工判断发现
```

### 4.4 与既有契约的关系（必须同步修订的文档规则）

1. **`knowledge/index.md` 第 19 行规则**——现行"顶层不得把知识正文复制进 subagent 提示，也不得用角色扮演跳过角色文件与索引加载"需要追加一句正式声明：`settings/context-pack.md` 是 prompt-crafter 的正式知识消费形态；本卷首个 prompt.create 任务完成索引加载与下钻并沉淀为 pack 后，后续任务读包即视为完成知识加载，不构成"跳过"。这是整合的合法性来源，必须显式写入。
2. **Reader 冷读保护不动**——reader、completion-reviewer 不读 pack，首读纪律、按需追因路径一字不改。pack 只服务 Prompt 创建侧。
3. **writer 边界不动**——writer 仍只收单章 base + 单章 Prompt，不读 pack。pack 的价值是让 Prompt 更自包含，writer 侧反而更干净。
4. **anti-ai 隔离不动**——`knowledge/anti-ai/`（含 genre/ 下同名的表达编辑文件）不进 pack；它仍是 Reader 点名后的按需内容，与规划侧的 genre 画像各司其职（genre/index.md 末节已声明两侧关系，保持不变）。
5. **迁移语义**——pack 是派生产物，`tools/migrate.py` 不搬运；迁移目标项目在本卷首个 prompt.create 任务按新 runtime 知识库重建（知识库版本可能已变化，重建比搬运更正确）。在 `skills/migration.md` 的未映射/派生产物说明中加一行。
6. **`alignment` 操作**——整卷对齐任务增加一项检查：pack 与已确认的 genre-setting / writing-style 是否漂移，漂移则列入重建清单（只重建包，不动已接受正文）。

### 4.5 收益量化

以一卷 5 个 prompt.create 任务、每次知识下钻 12 个文件估算：

| | 现状 | 建包后 |
|---|---|---|
| 知识文件读取总量 | 5 × 12 = 60 次 | 12（首任务）+ 4 × 1（包）= 16 次 |
| 每任务固定读取 | 12–18 个文件 | 1 个 pack + 必要的项目事实 |
| "读哪些知识"的即时判断 | 每任务重做一次 | 建包时做一次，写入 pack 第 4 节裁剪清单 |

---

## 五、文件级改动清单

### 新增（3 个）

| 文件 | 内容 |
|---|---|
| `skills/context-pack.md` | 新模块：建包触发、读取范围、压缩纪律、用包/补包/重建规则、与 anti-ai 和 Reader 的隔离声明（约 60–80 行，风格对齐现有 skills/*.md） |
| `templates/settings/context-pack.md` | 包模板，即 4.2 节骨架（占位符风格对齐现有 settings 模板） |
| `docs/plan-dispatch-and-context-pack.md` | 本方案文档 |

### 修改（契约整合，均为文档）

| 文件 | 改动 |
|---|---|
| `skills/dispatch.md` | "文件接口与所有权"大表重构为 15 张操作派发卡（补"触发""加载模块"两字段）；"项目事实的承接"表增加 `settings/context-pack.md` 一行（形成者：prompt.create 首任务；消费者：后续 prompt-crafter）；恢复节加"pack 未漂移不重建" |
| `skills/prompt.md` | "创作上下文"节：默认输入从"5 个知识索引下钻"改为"读 context-pack；本卷首任务先按 `skills/context-pack.md` 建包"；保留 author_confirmed 前置、单章 Prompt 结构、批次语义不变 |
| `agents/prompt-crafter.md` | frontmatter 的 knowledge 挂载保留（首任务建包仍需要），描述改为"本卷首任务建包时读取"；"所有权与输入"节：输入清单首项改为 context-pack，允许写入增加"首任务另写 settings/context-pack.md" |
| `agents/novel-agent.md` | 删除与 dispatch.md 重复的流程散文（项目启动/Prompt 创建/Fast/Full 四节压缩为指针）；保留控制面所有权、版本门禁、writer 构造指针 |
| `SKILL.md` | "路由"节改为 operation → 模块索引（含 `skills/context-pack.md` 一行）；"Prompt 创建"节加一句 pack 定位；Fast/Full 节去重 |
| `knowledge/index.md` | 第 19 行附近追加 pack 合法性声明（见 4.4-1）；表格中 prompt-crafter 行的读取方式注明"首任务建包，后续读包" |
| `skills/migration.md` | 派生产物说明加一行：context-pack 不搬运，新项目首任务重建 |
| `skills/volume-alignment.md` | 检查清单加一项：pack 漂移核对 |
| `README.md` | "Prompt 创建"附近加一句 pack 简介（保持与 SKILL.md 一致，一句话即可） |

### 工具（发行清单登记，各一行，非门禁逻辑）

| 文件 | 改动 |
|---|---|
| `tools/runtime_manifest.py` | `SKILL_FILES` 列表增加 `"context-pack.md"`（决定新模块部署到项目 `.claude/skill-resources/skills/`） |
| `tools/init.py` | `REQUIRED_SOURCE_FILES` 增加 `templates/settings/context-pack.md`；settings 拷贝段增加一行 `copy_if_missing(... context-pack.md ...)` |

> 这两处是"新文件纳入发行与部署"的登记动作，与门禁、评分、字数校验无关，符合"不增加门禁脚本"的约束。

---

## 六、明确不做什么

- 不新增任何角色（建包由 prompt-crafter 兼任）。
- 不改变长期 cursor 与 order.operation 集合（建包不新增 operation，挂在首个 prompt.create 任务内）。
- 不增加门禁、评分、关键词、字数类脚本；pack 的有效性由阅读判断（顶层、prompt-reviewer、alignment）保证，与项目"脚本不做文学判断"的立场一致。
- 不动 Reader/completion-reviewer 的冷读保护、writer 的自包含边界、anti-ai 的按需加载。
- 不动版本门禁与迁移判定条件（`skills/dispatch.md`"版本与迁移边界"原样保留）。
- 不改变单章 Prompt 的结构契约（`prompt_contract: 2` 不变；pack 只改变创建者的输入，不改变产物格式）。

---

## 七、执行顺序

1. **阶段一（派发矩阵）**：改 `skills/dispatch.md` 派发卡 → 收敛 `agents/novel-agent.md`、`SKILL.md`、`skills/writing.md` 重复散文。此阶段独立可交付，不影响任何在途项目。
2. **阶段二（pack 契约）**：新增 `skills/context-pack.md` + `templates/settings/context-pack.md` → 改 `skills/prompt.md`、`agents/prompt-crafter.md`、`knowledge/index.md`。
3. **阶段三（边缘同步）**：`skills/migration.md`、`skills/volume-alignment.md`、`README.md`、`SKILL.md` 路由行、两个 tools 文件登记。
4. **阶段四（走查）**：按下节清单人工走查；用一个测试项目跑"初始化 → 卷纲 → 幕纲 → 章纲 → 首任务建包 → 二批用包"全链路。

阶段一与阶段二/三无依赖，可并行；建议按顺序提交，便于评审。

## 八、验证方式（人工走查清单）

- [ ] 15 个 operation 每个都能在 dispatch.md 找到唯一派发卡，且与 cursor 表、order 表无矛盾。
- [ ] 全局检索：Fast/Full 流程图只存在于 dispatch.md"创作循环"一处，其余位置均为指针。
- [ ] 模拟顶层恢复场景（中断于 prompt.create 第二批）：只读 dispatch.md 即可回答"加载哪个模块、创建谁、输入是什么、从哪恢复"，无需翻 agent 文件。
- [ ] 测试项目首任务建包：pack 落盘、头部 sources 与实际读取一致、不含方法名/来源名直抄。
- [ ] 第二个 prompt.create 任务全程未打开 `knowledge/` 下任何文件（除 pack 明确声明的补读例外）。
- [ ] Prompt 产物结构与质量不变：抽查 `prompts/vol-N-ch-M.md` 仍满足 `prompt_contract: 2` 全字段，「本章质感」仍从 writing-style.md 提取。
- [ ] Reader 冷读路径全文未出现 pack；anti-ai 文件未进 pack。
- [ ] `python tools/init.py` 新项目骨架含 `settings/context-pack.md` 模板；`sync_runtime.py` 后 `.claude/skill-resources/skills/context-pack.md` 存在。
- [ ] 迁移项目：`.migration/report.md` 不列 pack 为缺失；新项目首任务重建 pack。
