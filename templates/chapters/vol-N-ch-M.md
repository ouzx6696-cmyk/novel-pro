---
chapter_contract: 1
volume: {N}
act: {K}
chapter: {M}
template_version: "0.2.3"
required_fields: [goal, reader_effect, conflict, characters, scenes, must_hold, ends_with]
---

# 第 {N} 卷第 {K} 幕第 {M} 章

> 本模板字段与 `skills/planning.md` 的章纲 schema（7 字段 + 可选引导）一致，由 chapter-planner 在 `outline.chapters` operation 中按幕顺序填写。字段说明的权威源是 `skills/planning.md`「章纲」节。

## goal

本章必须完成的故事、关系或认知变化。

## reader_effect

本章回应、加深或转移的读者期待。

## conflict

关键人物各自的目标、筹码、阻力与不能退让的理由。

## characters

人物的已知、未知、误判、关系位置和章末变化。

## scenes

每场的入场状态、行动目标、对方目标或真实阻力、策略、反制、转折、选择、结果与下一步触发；关键场景再补充 POV 人物当下注意的空间/物件、没有说出口的意图和选择留下的余波。建议每场标注主导性质（对峙/试探/日常/追逐/独处/转场），供 prompt-crafter 判断「本场怎么写」的技法落点。

## must_hold

本章承接的事实、动机、POV、关系、信息差和幕级约束。

## ends_with

最终动作或画面，以及下一章需要承接的状态。

---

## 可选引导（兼容旧文件，缺失不强制）

### key_points（可选）
段落级引导，与 `scenes` 的场景级粒度互补。每条 2-3 句笔记体，覆盖**感官/动作/判断**三个锚点（人物看见什么、做什么、判断出什么）；条数按目标字数倒推（目标字数 ÷ 500）；对白密集章用 场景/对话/权力 变体（现场、谁在说、谁在试探或施压）。key_points 是展开引导不是正文预写，不锁定对白原文。

### must_hold 三清单（可选）
拆为 `must_resolve`（本章必须闭合）/ `must_hold`（本章承接不变）/ `partial_advance`（部分推进、留待后章）；允许空 `[]`。旧版平铺文本仍被接受。

### characters 信息差轨迹（可选）
逐角色列 知道/不知道 清单 + 信息差关系（谁 vs 谁）+ 信息差变化（开场→结尾）。这是 Prompt 人物动机与情绪中「已知/未知/误判」与施压点的上游依据。

---

## 填写指引

### 何时填写
- 由 chapter-planner 在 `outline.chapters` operation 中按幕顺序形成
- 在整卷幕地图与当前幕纲（`acts/vol-N-act-K.md`）完成后
- 一次处理一幕，顺序复读整幕章纲确认承接

### 与其他文件关系
- **幕纲**（acts/vol-N-act-K.md）：本章的 `must_hold` 承接幕纲 `continuity_contract`；幕内 `chapter_roles` 提供本章功能
- **幕级承接快照**（chapters/vol-N-act-K-handoff.md）：chapter-planner 从本幕全部章纲提炼的派生摘要，专供 prompt-crafter 使用
- **Prompt**（prompts/vol-N-ch-M.md）：prompt-crafter 按四步转化法把本章章纲转成单章自包含 Prompt

### 常见问题

**Q: goal 与 reader_effect 的区别？**
A: goal 是本章必须完成的变化（故事/关系/认知）；reader_effect 是读者视角的期待管理（回应/加深/转移）。

**Q: conflict 与 scenes 的关系？**
A: conflict 定人物间不可退让的张力，scenes 把张力落到每场的行动-反制-选择过程。

**Q: 可选引导什么时候用？**
A: 需要更强段落引导时用 key_points；需要显式闭合/承接/部分推进时用 must_hold 三清单；信息差是本章施压点时用 characters 信息差轨迹。缺失不强制。
