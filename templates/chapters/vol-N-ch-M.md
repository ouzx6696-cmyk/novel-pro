---
chapter_contract: 2
volume: {N}
act: {K}
chapter: {M}
template_version: "0.3.0"
required_fields: [goal, reader_effect, conflict, characters, info_gap, scenes, must_hold, chapter_end_state, ends_with]
---

# 第 {N} 卷第 {K} 幕第 {M} 章

> 本模板字段与 `skills/planning.md` 的章纲 schema（9 必填字段 + 可选引导）一致，由 chapter-planner 在 `outline.chapters` operation 中按幕顺序填写。字段说明的权威源是 `skills/planning.md`「章纲」节。

## goal

本章必须完成的故事、关系或认知变化。

## reader_effect

本章回应、加深或转移的读者期待。

## conflict

关键人物各自的目标、筹码、阻力与不能退让的理由。

## characters

人物的已知、未知、误判、关系位置和章末变化。只列本章出场并在本场实际作用的人物。

## info_gap（信息差轨迹，必填）

**填写说明**：逐角色列 知道/不知道 清单 + 信息差关系（谁 vs 谁）+ 信息差变化（开场→结尾）。这是 Prompt「前情上下文」「角色初始状态」「人物动机与情绪」中已知/未知/误判与施压点的上游依据，也是 state.update 核对正文信息变化的参照。缺少时必须从幕纲 `start_state`/`end_state` 与 `scenes` 的对抗结构反推补齐，不允许留空。

```markdown
- {角色A}：知道 {清单}；不知道 {清单}；误判 {什么}
- 信息差关系：{谁知道什么 ↦ 谁不知道什么}（开场）
- 信息差变化：开场 {A知道↦B不知} → 中段 {如何缩小/扩大} → 结尾 {新信息差，驱动下一章}
```

## scenes

每场的入场状态、行动目标、对方目标或真实阻力、策略、反制、转折、选择、结果与下一步触发；关键场景再补充 POV 人物当下注意的空间/物件、没有说出口的意图和选择留下的余波。建议每场标注主导性质（对峙/试探/日常/追逐/独处/转场），供 prompt-crafter 判断「本场怎么写」的技法落点。

## must_hold

本章承接的事实、动机、POV、关系、信息差和幕级约束。

## chapter_end_state（章末状态快照，必填）

**填写说明**：本章结束后每个出场角色的状态快照，供 state.update 核对并从正文回流事实。写"从什么变成什么"的可检验状态：

- {角色A}：{位置/身体状态/已知信息/关系阶段/能力或资源变化}
- {角色B}：{同上}
- 新增事实：{本章确立的会影响后续承接的新事实（若有）}

**注意**：这是规划承诺。正文实际写作与快照不符时，以正文为准，由 state.update 按正文修正并回告顶层；未进入正文的事件不写入。

## ends_with

最终动作或画面，以及下一章需要承接的状态。

---

## 设定变更通知（可选，有需要时追加）

**填写说明**：本章规划确认了会改变项目事实的变更时，追加此块；由 `state.update` 在验收/提交后消费并**从源文件中移除**，防止重复消费。块内容不进入 Prompt。

```markdown
## 设定变更通知
- **目标：** settings/character-setting/{id}.md 或 settings/{world-setting|timeline|foreshadowing}.md
- **类型：** 状态更新 / 新角色 / 世界观更新 / 时间线 / 伏笔
- **原因：** {为什么需要这个变更}
- **详情：** {具体变更描述，写清从什么变成什么}
```

---

## 可选引导（兼容旧文件，缺失不强制）

### key_points（可选）
段落级引导，与 `scenes` 的场景级粒度互补。每条 2-3 句笔记体，覆盖**感官/动作/判断**三个锚点（人物看见什么、做什么、判断出什么）；条数按目标字数倒推（目标字数 ÷ 500）；对白密集章用 场景/对话/权力 变体（现场、谁在说、谁在试探或施压）。key_points 是展开引导不是正文预写，不锁定对白原文。

### must_hold 三清单（可选）
拆为 `must_resolve`（本章必须闭合）/ `must_hold`（本章承接不变）/ `partial_advance`（部分推进、留待后章）；允许空 `[]`。旧版平铺文本仍被接受。

---

## 填写指引

### 何时填写
- 由 chapter-planner 在 `outline.chapters` operation 中按幕顺序形成
- 在整卷幕地图与当前幕纲（`acts/vol-N-act-K.md`）完成后
- 一次处理一幕，顺序复读整幕章纲确认承接

### 与其他文件关系
- **幕纲**（acts/vol-N-act-K.md）：本章的 `must_hold` 承接幕纲 `continuity_contract`；幕内 `chapter_roles` 提供本章功能
- **幕级承接快照**（chapters/vol-N-act-K-handoff.md）：chapter-planner 从本幕全部章纲提炼的派生摘要，专供 prompt-crafter 使用
- **正文入口**：顺序链路下，上一章验收草稿（`drafts/`）或已提交正文（`texts/`）提供本章起点事实；`info_gap` 与 `chapter_end_state` 必须与上一章实际结尾一致
- **Prompt**（prompts/vol-N-ch-M.md）：prompt-crafter 按四步转化法把本章章纲转成单章自包含 Prompt

### 常见问题

**Q: goal 与 reader_effect 的区别？**
A: goal 是本章必须完成的变化（故事/关系/认知）；reader_effect 是读者视角的期待管理（回应/加深/转移）。

**Q: conflict 与 scenes 的关系？**
A: conflict 定人物间不可退让的张力，scenes 把张力落到每场的行动-反制-选择过程。

**Q: info_gap 与 characters 的关系？**
A: characters 写人物的动机、误判与关系位置；info_gap 是信息差的可检验清单（谁知道什么、谁不知道、开场到结尾怎么变），两者互为参照，都是 Prompt「角色初始状态」与施压点的上游。

**Q: chapter_end_state 与 ends_with 的关系？**
A: ends_with 是本章最后一帧画面（正文停在哪）；chapter_end_state 是本章结束后的事实状态快照（人物/关系/信息/能力变成什么），供 state.update 核对回流。

**Q: 什么时候用设定变更通知？**
A: 本章正文会产生新角色、明确的关系/能力/世界变化，或需要时间线/伏笔新条目时。变更进入正文并验收后由 state.update 消费；规划层的通知不是事实，正文没有兑现就不能写入 settings。
