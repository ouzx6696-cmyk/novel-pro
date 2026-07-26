# Writing

<!-- changed_in: 0.2.3 -->

Fast 与 Full 共用同一套单章 writer 派发机制。两种模式都从 `prompts.ready` 开始；差别在于草稿完成后是否进入 Reader、返修和提交。

调度时序以本模块的各 Flow 节为准；writer 构造以 `skills/writer-construction.md` 为准，不另设派发规则。

## 真实展开

Prompt 的字段是脚手架，不是正文分镜。writer 可以调整场景顺序、停顿和措辞，只要不改变已经确认的事实、POV、人物选择和收束。优先让读者经历过程，再让读者理解结果：

- 让人物在具体空间里行动，记住距离、身体状态、物件、时间和谁在场；不要让人物漂浮在对白和解释里。
- 让人物带着自己的面子、恐惧、习惯和误判做选择。人物可以不理性、说错话、保护自己或暂时失败，但选择必须从当下压力中长出来。
- 让对白回应当下关系和筹码。人物不为作者递信息而完整发言，答非所问、停顿、改口和动作都可以保留，只要读者仍能跟上变化。
- 情绪通过注意力、动作、身体反应和选择变化显现；不要把每一种感受都命名，也不要让每一句话都承担主题。
- 重要选择之后留下具体余波：关系变了、某个退路关了、某件物品被留下、下一步变得更难或更急。不要用总结代替余波。

这些原则不是逐项检查表。若一个朴素句子最像人物此刻会说的话，就保留朴素；若场景需要笨拙、沉默或不完整，不要为了“好看”把它修成漂亮台词。

## Fast

### Fast 流程

```text
prompts.ready
→ `fast.write`：每章构造 writer base
→ writer 写 `drafts/vol-N-ch-M.md`
→ 顶层阅读并处理缺口
→ 全部目标草稿形成
→ `drafts.ready`
```

Fast 仍由顶层阅读实际草稿，但不进入 Full Reader、表达编辑和 `texts/` 提交。正文执行不足时沿用同一 Prompt 重派 writer；Prompt 不足时回到 `prompt.create`，不靠字数或字段补齐。

### Fast 调度

Fast 从 `prompts.ready` 开始：为每章构造 writer base 并创建独立 writer，目标草稿写 `drafts/vol-N-ch-M.md`，顶层阅读后到达 `drafts.ready`。批次只安排 writer 并发；已有草稿保留，当前批次只派发尚未完成的章节。

顶层阅读草稿后，根据正文实际阅读体验选择下一步：读者能够跟上人物正在做什么、为什么这么做，并感到选择带来的变化时接受草稿；正文把行动、反制、选择或后果压成提要，或人物反应与压力脱节时，使用同一 Prompt 创建新的 writer；Prompt 本身缺少可展开内容时，把对应章节交回 Prompt 创建阶段。文件存在、字段齐全和字数达到参考值都不能替代这次阅读。

Fast 完成于 `drafts.ready`。它交付未经 Reader 文学验收的草稿：顶层仍须阅读实际文字，决定接受、重派 writer 或返回 Prompt 创建，但 Fast 不进入 Full Reader、表达编辑和 `texts/` 提交链。

## Full

Full 从 `prompts.ready` 经 `full.write` → `full.review` → `full.repair` → `full.commit`。`full.write` 使用与 Fast 相同的单章 writer 创建方式；已经存在的 draft 由顶层实际阅读后决定是否进入 Reader。

`full.review` 由 Reader 按幕顺序冷读正文。Reader 的证据同时指出问题表现和最可能根因，顶层据此选择返修路径：

- Prompt 已经提供完整人物行动和场景因果，但 draft 没有展开时，使用原 Prompt 与 Reader 已指明的返修焦点构造新的 writer base。新 writer 从 Prompt 重新创作完整章节。
- Prompt 本身遗漏关键行动、承接或事实边界时，prompt-crafter 在所在幕或连续批次的理解中只修复受影响 Prompt，随后顶层用修复后的 Prompt 创建新 writer。
- 幕纲或章纲无法共同成立时，返回拥有该产物的 planner，尚不创建 writer。
- 表达问题由 Reader 点名后交 anti-AI。

原 draft 和候选保留在 task 中供 Reader 复读比较，不作为内容 writer 的创作输入。候选完成后，Reader 重新顺序阅读受影响范围。

`full.commit` 把 Reader 明确接受的纯正文写入 `texts/`。

## 恢复

order 保存任务模式、章节范围、Prompt、输出和 subtask 状态。中断后，顶层重新读取模板并为未完成章节构造单章 base；已经完成的 draft 和候选保持原状。

单章 base 是可重新构造的派发上下文，不增加长期状态。恢复是否继续某一章节由顶层阅读当前文件和任务现场后决定。
