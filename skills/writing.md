# 写作模式（Writing Mode）与编辑模式（Editing Mode）

<!-- changed_in: 0.2.3 -->

写作模式 与编辑模式共用同一套单章 writer 派发机制。两种模式都从 `prompts.ready` 开始；差别在于草稿完成后是否进入 Reader、返修和提交：

- **写作模式**（`write.draft`）：只产出未经验收的草稿到 `drafts/`，完成于 `drafts.ready`。工作目标是"把 Prompt 写成人物的行动过程"。
- **编辑模式**（`edit.write` → `edit.review` → `edit.anti-ai` → `edit.synthesize` → `edit.repair` → `edit.commit`）：产出经文学验收的正文到 `texts/`。工作目标是"把草稿编辑到作者可接受、可发布的完成度"。

完整模式定义（工作目标/流程/调度）见 `SKILL.md` 的「写作模式」与「编辑模式」节。调度时序以本模块的各 Flow 节为准；writer 构造以 `skills/writer-construction.md` 为准，不另设派发规则。

## 执行入口（先读这一节）

顶层派发任一模式前，按下列链路逐行执行；每行的「读/写」是精确文件接口，「判定」是完成条件。

### 写作模式执行链路（write.draft）

| 步骤 | operation | 角色 | 读 | 写 | 判定 | 下一跳 |
|---|---|---|---|---|---|---|
| 1 | `write.draft` | writer ×N（每章独立） | 单章 base（顶层构造）+ 目标 Prompt | `drafts/vol-N-ch-M.md` | writer 窗口完成 | 步骤 2 |
| 2 | —（顶层阅读） | 顶层 | 全部 `drafts/` | — | 阅读信号清单：接受 / 同一 Prompt 重派 / 回退 | `drafts.ready`、重派或 `prompt.create` |

构造单章 base 的步骤（每章一次，在创建 writer 之前）：读 `templates/runtime/novel-base.md` 第一部分获得构造方法 → 核对目标 Prompt「本章质感」是可执行的声线材料（空泛或文风未确认则按 `skills/prompt.md` 缺口规则返回，不构造 base）→ 按第二部分模板填「当前任务」节（mode/chapter/prompt/output/repair_focus）→ 其余通用节按模板原样保留 → base 与 Prompt 共同交付 writer。**质感不写入 base**，本章声线以 Prompt「本章质感」为唯一指令源。

### 编辑模式执行链路（edit.write → edit.commit）

编辑模式六步的每步读/写/判定以 `skills/review-archive.md` 的「阅读闭环步骤（六步执行表）」为权威，本模块只负责其中第 1 步 `edit.write`（与写作模式相同的 base 构造与 writer 派发）。顶层从 `prompts.ready` 进入编辑模式后：`edit.write` → `edit.review`（Reader 冷读）→ `edit.anti-ai`（全量扫描）→ `edit.synthesize`（分级裁决）→ `edit.repair`（分流返修）→ Reader 复读 → `edit.commit`（写入 `texts/`）。完整链路见 `skills/review-archive.md`，冷读与复读纪律见 `skills/cold-read-discipline.md`。

## 真实展开

Prompt 的字段是脚手架，不是正文分镜。writer 可以调整场景顺序、停顿和措辞，只要不改变已经确认的事实、POV、人物选择和收束。优先让读者经历过程，再让读者理解结果：

- 让人物在具体空间里行动，记住距离、身体状态、物件、时间和谁在场；不要让人物漂浮在对白和解释里。
- 让人物带着自己的面子、恐惧、习惯和误判做选择。人物可以不理性、说错话、保护自己或暂时失败，但选择必须从当下压力中长出来。
- 让对白回应当下关系和筹码。人物不为作者递信息而完整发言，答非所问、停顿、改口和动作都可以保留，只要读者仍能跟上变化。
- 情绪通过注意力、动作、身体反应和选择变化显现；不要把每一种感受都命名，也不要让每一句话都承担主题。
- 重要选择之后留下具体余波：关系变了、某个退路关了、某件物品被留下、下一步变得更难或更急。不要用总结代替余波。

这些原则不是逐项检查表。若一个朴素句子最像人物此刻会说的话，就保留朴素；若场景需要笨拙、沉默或不完整，不要为了“好看”把它修成漂亮台词。

篇幅服从场景权重：Prompt 标注的**核心场景**展开最充分，承担本章主要变化；**低权重转场**（若有）控制篇幅，约 1 句环境 + 1 句动作 + 1 句氛围即可，不为凑字数展开。篇幅不服从字段数量或目标字数，服从人物选择、读者理解和场景余波。

## 写作模式

### 写作模式流程

```text
prompts.ready
→ `write.draft`：每章构造 writer base
→ writer 写 `drafts/vol-N-ch-M.md`
→ 顶层阅读并处理缺口
→ 全部目标草稿形成
→ `drafts.ready`
```

写作模式仍由顶层阅读实际草稿，但不进入编辑模式 Reader、表达编辑和 `texts/` 提交。正文执行不足时沿用同一 Prompt 重派 writer；Prompt 不足时回到 `prompt.create`，不靠字数或字段补齐。

### 写作模式调度

写作模式从 `prompts.ready` 开始：为每章构造 writer base 并创建独立 writer，目标草稿写 `drafts/vol-N-ch-M.md`，顶层阅读后到达 `drafts.ready`。批次只安排 writer 并发；已有草稿保留，当前批次只派发尚未完成的章节。

顶层阅读草稿后，根据正文实际阅读体验选择下一步：读者能够跟上人物正在做什么、为什么这么做，并感到选择带来的变化时接受草稿；正文把行动、反制、选择或后果压成提要，或人物反应与压力脱节时，使用同一 Prompt 创建新的 writer；Prompt 本身缺少可展开内容时，把对应章节交回 Prompt 创建阶段。文件存在、字段齐全和字数达到参考值都不能替代这次阅读。

### 写作模式阅读信号清单

顶层阅读草稿时按以下信号判断；信号是阅读指引，最终判断仍来自对实际文字的阅读体验。

**接受信号**（满足即接受）：
- 读者能跟上人物正在做什么、为什么这么做。
- 选择有可见后果，正文停在 Prompt 指定收束，无旁白总结。

**重派信号**（任一出现即用同一 Prompt 重派 writer）：
- 关键场景被压成行动/反制/选择的提要或事后复盘，人物没有在场经历过程。
- 人物反应与压力脱节：该犹豫处无波澜，该付出代价的选择无后果。
- 正文混入说明、分析或脱离 POV 的总结段。

**回退信号**（出现即交回 `prompt.create`）：
- Prompt 本身缺少可展开的人物行动、场景因果或承接事实，writer 无从展开。
- 同一 Prompt 的不同章反复出现同类执行问题，指向 Prompt 设计而非执行。

写作模式完成于 `drafts.ready`。它交付未经 Reader 文学验收的草稿：顶层仍须阅读实际文字，决定接受、重派 writer 或返回 Prompt 创建，但写作模式不进入编辑模式 Reader、表达编辑和 `texts/` 提交链。

## 编辑模式

编辑模式从 `prompts.ready` 经 `edit.write` → `edit.review`（Reader 按幕冷读）→ `edit.anti-ai`（Anti-AI 全量扫描）→ `edit.synthesize`（整体返修裁决）→ `edit.repair` → `edit.commit`。`edit.write` 使用与写作模式相同的单章 writer 创建方式；已经存在的 draft 由顶层实际阅读后决定是否进入 Reader。

`edit.review` 由 Reader 按幕顺序冷读正文，`edit.anti-ai` 随后对同批章节全量扫描表达问题；`edit.synthesize` 综合两份报告给出整体返修意见，顶层据此选择返修路径：

- Prompt 已经提供完整人物行动和场景因果，但 draft 没有展开时，使用原 Prompt 与 Reader 已指明的返修焦点构造新的 writer base。新 writer 从 Prompt 重新创作完整章节。
- Prompt 本身遗漏关键行动、承接或事实边界时，prompt-crafter 在所在幕或连续批次的理解中只修复受影响 Prompt，随后顶层用修复后的 Prompt 创建新 writer。
- 幕纲或章纲无法共同成立时，返回拥有该产物的 planner，尚不创建 writer。
- 表达问题由 anti-ai 在 edit.repair 阶段按 `edit.synthesize` 整体返修意见执行。

原 draft 和候选保留在 task 中供 Reader 复读比较，不作为内容 writer 的创作输入。候选完成后，Reader 重新顺序阅读受影响范围。

`edit.commit` 把 Reader 明确接受的纯正文写入 `texts/`。

## 恢复

order 保存任务模式、章节范围、Prompt、输出和 subtask 状态。中断后，顶层重新读取模板并为未完成章节构造单章 base；已经完成的 draft 和候选保持原状。

单章 base 是可重新构造的派发上下文，不增加长期状态。恢复是否继续某一章节由顶层阅读当前文件和任务现场后决定。
