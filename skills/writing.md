# 写作模式（Writing Mode）与编辑模式（Editing Mode）

<!-- changed_in: 0.3.0 -->

写作模式 与编辑模式共用同一套单章 writer 派发机制，都运行在**顺序链路**（`draft.write` 阶段）中：Prompt 跟随正文顺序逐章创建，一章验收/提交后才进入下一章。差别在于草稿完成后是否进入 Reader、返修和提交：

- **写作模式**（`write.draft`）：只产出未经验收的草稿到 `drafts/`，全部目标章完成于 `drafts.ready`。工作目标是"把 Prompt 写成人物的行动过程"。
- **编辑模式**（`edit.write` → 幕末 `edit.review` → `edit.anti-ai` → `edit.synthesize` → `edit.repair` → `edit.commit`）：逐章写作、幕末批量审读，产出经文学验收的正文到 `texts/`。工作目标是"把草稿编辑到作者可接受、可发布的完成度"。

完整模式定义（工作目标/流程/调度）见 `SKILL.md` 的「写作模式」与「编辑模式」节。调度时序以本模块的各 Flow 节为准；writer 构造以 `skills/writer-construction.md` 为准，不另设派发规则。

## 执行入口（先读这一节）

顶层派发顺序链路前，按下列链路逐行执行；每行的「读/写」是精确文件接口，「判定」是完成条件。

### 顺序链路执行入口（逐章循环）

| 步骤 | operation | 角色 | 读 | 写 | 判定 → 下一跳 |
|---|---|---|---|---|---|
| 0 | —（建包） | 顶层 | 本幕稳定资料（context-pack、writing-style、幕纲、handoff、出场角色稳定事实、台账结构） | `.agent/cache/vol-N-act-K-act-pack.md`（manifest + 语义摘要） | 幕首章 `prompt.create` 前执行；包已存在且 hash 有效 → 跳过 |
| 1 | `prompt.create` | prompt-crafter ×1 | 幕级复用资料包 `act-pack`（先核 source hash）、**本章章纲**、**上一章真实验收稿/已提交正文（必读）**、上一章 chapter-delta（若有）、出场角色档案 `state_history` 最新块（跨幕首章另读上一幕幕总结）；包失效时回退完整读取 | `prompts/vol-N-ch-M.md`（`prompt_contract: 4`，frontmatter 记录 `preceding_source`） | lint 无错误、语义自检无缺口、顶层读过 → 步骤 2 |
| 2 | —（轻量审查） | 顶层 | lint 结果、目标 Prompt、语义自检表、上一章正文（承接核对） | 无（疑点写入当前 task） | 无明确问题 → 步骤 3；发现明确问题或作者要求 → `prompt.review`（步骤 2'）；机械问题 → micro-fix 后重跑 lint；`STOP` 级 → 顶层交规划层 |
| 2' | `prompt.review`（按需） | prompt-reviewer ×1 | lint 结果、目标 Prompt、顶层指出的疑点 + `preceding_source` 对应正文 + 幕纲 + 章纲 + 角色状态 | 语义审计短报告（当前 task） | `PASS` → 步骤 3；机械问题 → micro-fix 后重跑 lint；`FIX` → 回步骤 1；`STOP` → 顶层交规划层 |
| 3 | `write.draft` / `edit.write` | writer ×1 | 单章动态任务 + 可选稳定 writer-profile + 目标 Prompt | `drafts/vol-N-ch-M.md` | 先检查文件产物；完整 → 写作模式步骤 4 / 编辑模式步骤 3'；缺失或截断 → 同上下文自动重试至多一次 |
| 4 | —（顶层阅读） | 顶层 | 实际草稿 | — | 阅读信号清单：接受 / 同一 Prompt 重派 / 回退 | `state.update`、重派（回步骤 3）或 `prompt.create`（回步骤 1，必要时回规划层） |
| 5 | `state.update` | continuity-updater ×1 | 草稿或最终定稿、章纲/幕纲「设定变更通知」、既有 settings | `phase: delta` 返回 chapter-delta 由顶层写 task；`phase: commit` 从最终 `texts/` 更新 settings | delta 捕获后可进下一章；正式提交后 commit 幂等完成 |

首章（卷首或每幕首章）的步骤 1 前情来源：幕纲 `start_state` 与上一幕最后一章真实正文（若已存在）。编辑模式在第 3 步后先执行轻量 `state.update phase: delta`，再进入下一章；幕内草稿逐章形成后，在**幕末统一进入批量审读**（`edit.review` Reader 按幕冷读 → `edit.anti-ai` 同幕全量扫描 → `edit.synthesize` 整体裁决 → `edit.repair` 分流返修 → Reader 复读 → `edit.commit` 逐章提交 → `state.update phase: commit` 逐章正式回流）。完整编辑闭环见 `skills/review-archive.md`「阅读闭环步骤（六步执行表）」。

构造 Writer 上下文时，先核对可选 `.agent/cache/writer-profile.md` 的来源 hash：有效则复用其中不含剧情的通用框架与项目级硬规则，只填写本章动态任务；缺失或失效则按 `templates/runtime/novel-base.md` 完整构造。每章仍创建全新 writer，叙述示范与声线落点不写入 profile 或 base，本章声线只由目标 Prompt 承载。

## 真实展开

Prompt 的字段是脚手架，不是正文分镜。writer 可以调整场景顺序、停顿和措辞，只要不改变已经确认的事实、POV、人物选择和收束。优先让读者经历过程，再让读者理解结果：

- 让人物在具体空间里行动，记住距离、身体状态、物件、时间和谁在场；不要让人物漂浮在对白和解释里。
- 让人物带着自己的面子、恐惧、习惯和误判做选择。人物可以不理性、说错话、保护自己或暂时失败，但选择必须从当下压力中长出来。
- 让对白回应当下关系和筹码。人物不为作者递信息而完整发言，答非所问、停顿、改口和动作都可以保留，只要读者仍能跟上变化。
- 情绪通过注意力、动作、身体反应和选择变化显现；不要把每一种感受都命名，也不要让每一句话都承担主题。
- 重要选择之后留下具体余波：关系变了、某个退路关了、某件物品被留下、下一步变得更难或更急。不要用总结代替余波。

这些原则不是逐项检查表。若一个朴素句子最像人物此刻会说的话，就保留朴素；若场景需要笨拙、沉默或不完整，不要为了"好看"把它修成漂亮台词。

篇幅服从场景权重：Prompt 标注的**核心场景**展开最充分，承担本章主要变化；**低权重转场**（若有）控制篇幅，约 1 句环境 + 1 句动作 + 1 句氛围即可，不为凑字数展开。篇幅不服从字段数量或目标字数，服从人物选择、读者理解和场景余波。

## 写作模式

### 写作模式流程

```text
outline.chapters（章纲完成）
→ 顶层建幕级复用资料包 act-pack（幕首章 prompt.create 前）
→ 第 M 章：
   prompt.create（读 act-pack + 本章动态资料；上一章真实正文 → 前情三件套；state_history 最新块 → 角色初始状态）
   → 顶层轻量审查（lint + 阅读；无明确问题直接进写作，有明确问题 → prompt.review 细节审查）
   → write.draft：构造 writer base，writer 写 drafts/vol-N-ch-M.md
   → 顶层阅读并三向判定（接受 / 重派 / 回退）
   → 接受后 state.update phase: delta（生成 working-state/chapter-delta，不写 settings）
→ 全部目标章完成 → drafts.ready
```

写作模式仍由顶层阅读实际草稿，但不进入编辑模式 Reader、表达编辑和 `texts/` 提交。正文执行不足时沿用同一 Prompt 重派 writer；自动重试只处理文件缺失/截断且最多一次，文学执行不足仍由顶层阅读后明确重派。Prompt 不足时回到 `prompt.create`，不靠字数或字段补齐。

### 写作模式调度

写作模式从 `outline.chapters` 完成后进入：按叙事顺序逐章推进（order 的 `current_chapter`），每章一个小循环，**一章验收后才创建下一章 Prompt**——第 N+1 章 Prompt 的前情上下文直接取自第 N 章真实验收稿，角色初始状态由既有 settings 加上当前 task 的 working-state/chapter-delta 补齐。缓存或 delta 缺失时回退到完整正文与既有状态文件。已有草稿保留，重派不覆盖。

顶层阅读草稿后，根据正文实际阅读体验选择下一步：读者能够跟上人物正在做什么、为什么这么做，并感到选择带来的变化时接受草稿；正文把行动、反制、选择或后果压成提要，或人物反应与压力脱节时，使用同一 Prompt 创建新的 writer；Prompt 本身缺少可展开内容时，把对应章节交回 Prompt 创建阶段。文件存在、字段齐全和字数达到参考值都不能替代这次阅读。

### 写作模式阅读信号清单

顶层阅读草稿时按以下信号判断；信号是阅读指引，最终判断仍来自对实际文字的阅读体验。

**接受信号**（满足即接受）：
- 读者能跟上人物正在做什么、为什么这么做。
- 正文开头与 Prompt「前情上下文」的收束画面自然衔接：人物位置、身体状态、信息持有、时间与空间与上一章真实结尾连续，全文无与已接受事实矛盾的内容。
- 选择有可见后果，正文停在 Prompt 指定收束，无旁白总结。

**重派信号**（任一出现即用同一 Prompt 重派 writer）：
- 关键场景被压成行动/反制/选择的提要或事后复盘，人物没有在场经历过程。
- 人物反应与压力脱节：该犹豫处无波澜，该付出代价的选择无后果。
- 正文与 Prompt「前情上下文」或「角色初始状态」冲突：人物位置、信息持有、关系阶段对不上上一章真实结尾，或开场自说自话没有承接。
- 正文混入说明、分析或脱离 POV 的总结段。

**回退信号**（出现即交回 `prompt.create`）：
- Prompt 本身缺少可展开的人物行动、场景因果或承接事实，writer 无从展开。
- 同一 Prompt 的不同章反复出现同类执行问题，指向 Prompt 设计而非执行。

写作模式完成于 `drafts.ready`。它交付未经 Reader 文学验收的草稿：顶层仍须阅读实际文字，决定接受、重派 writer 或返回 Prompt 创建，但写作模式不进入编辑模式 Reader、表达编辑和 `texts/` 提交链。

## 编辑模式

编辑模式在顺序链路中**逐章写作、幕末批量审读**：每章 `prompt.create` → 顶层轻量审查（按需 `prompt.review`）→ `edit.write`（writer ×1 写草稿）→ `state.update phase: delta`，幕内全部草稿形成后统一进入审读链（`edit.review` Reader 按幕冷读 → `edit.anti-ai` 同幕全量扫描 → `edit.synthesize` 整体裁决 → `edit.repair` 分流返修 → Reader 复读 → `edit.commit` 逐章提交 → `state.update phase: commit` 逐章正式回流）→ 下一幕。`edit.write` 使用与写作模式相同的单章 writer 创建方式；幕内草稿形成阶段顶层不逐章验收，验收随幕末审读进行。

幕末审读时，Reader 按幕顺序冷读本幕全部草稿（上下文含前幕已提交正文）；`edit.anti-ai` 随后对同幕章节全量扫描表达问题；`edit.synthesize` 综合两份报告给出整体返修意见，顶层据此选择返修路径：

- Prompt 已经提供完整人物行动和场景因果，但 draft 没有展开时，使用原 Prompt 与 Reader 已指明的返修焦点构造新的 writer base。新 writer 从 Prompt 重新创作完整章节。
- Prompt 本身遗漏关键行动、承接或事实边界时，prompt-crafter 只修复受影响 Prompt，随后顶层用修复后的 Prompt 创建新 writer。
- 幕纲或章纲无法共同成立时，返回拥有该产物的 planner，尚不创建 writer。
- 表达问题由 anti-ai 在 edit.repair 阶段按 `edit.synthesize` 整体返修意见执行。
- **前情刷新**：某章被 REGENERATE 重写并改变既定事实时，从被重写章的后一章开始重做 `prompt.create`（前情取自重写后的真实正文）与 `edit.write`；不重做已经成立的章。

原 draft 和候选保留在 task 中供 Reader 复读比较，不作为内容 writer 的创作输入。候选完成后，Reader 重新顺序阅读受影响范围。

`edit.commit` 把 Reader 明确接受的纯正文逐章写入 `texts/`；随后 `state.update` 逐章从定稿回流状态（同锚点旧块覆盖刷新），幕末章生成幕总结；下一幕首章 Prompt 读取最新状态与前幕幕总结。

## 恢复

order 保存当前章（`current_chapter`）、任务模式、Prompt 路径、草稿路径、`state_delta`、可选 context/session/retry 和 subtask 状态。中断后，顶层读取 status/order 并按该章产物状态定位恢复步骤：

- Prompt 缺失，或 `preceding_source` 已变（上一章正文被返修重写）→ 从 `prompt.create` 重做。
- Prompt 在但未轻量审查 → 先执行顶层轻量审查；有明确问题且未细节审查 → 从 `prompt.review` 继续。
- Writer 返回为空/取消/异常 → 先检查目标文件；完整则进入顶层阅读，缺失或截断才用相同 Prompt/profile 自动重试一次，第二次失败保留现场并停止盲目重派。
- 草稿缺失 → 为未完成章节构造动态任务并复用有效 profile（失效时完整重建），按上述一次重试规则执行。
- 草稿在但未验收/未提交 → 顶层阅读当前文件后决定接受、重派或回退。
- 草稿已完成但 `state_delta.captured: false` → 从 `state.update phase: delta` 继续。
- 正文已提交但 `state_delta.committed: false` → 从 `state.update phase: commit` 继续（同 hash 已提交章节不重复同步）。

writer-profile、chapter-context 和 chapter-delta 都是可失效、可重建的派生上下文，不增加长期状态。恢复是否继续某一章节由顶层阅读当前文件、来源 hash 和任务现场后决定。
