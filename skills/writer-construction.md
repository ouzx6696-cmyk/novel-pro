# Writer Construction

<!-- changed_in: 0.3.0 -->

本模块描述 novel-agent 如何从 `templates/runtime/novel-base.md` 模板构造单章 writer base，被 `write.draft` 和 `edit.write` 的派发流程加载。

## 构造单章 Writer

主代理在创建每个 writer 子代理前读取 `templates/runtime/novel-base.md`，再根据当前章节写成单章 writer base。base 模板分两部分：**第一部分是主代理构造指南**（base 是什么、何时构造、怎么构造、纪律），**第二部分是参考模板**（标准结构）。构造时先读第一部分获得方法，再按第二部分模板填充。

实例化使用当前任务已经确定的信息：

- 章节标识和任务模式。
- 目标 Prompt 路径。
- 草稿或候选输出路径。
- 内容返修时 Reader 已确认的返修焦点。

**声线核对（不写入 base）**：构造时阅读目标 Prompt，确认「本章故事」叙述能示范项目声线，且各场「本场声线」是可执行的具体落点（句长倾向/对白配比/感官密度/留白/样句），不是抽象形容词或占位符。核对本身即一次 Prompt 检查：若声线空泛或文风未确认，按 `skills/prompt.md` 的缺口规则返回顶层，不构造 base、不补成通用文风。**叙述示范与声线落点不复制进 base**——writer 同时收到 base 与 Prompt，本章声线以 Prompt 内承载的声线材料（叙述示范 + 各场声线落点；旧版 contract-2 Prompt 以「本章质感」小节为准）为唯一指令源，base 只提供通用写作框架与项目级硬规则（标点、禁用句式、章末纪律）。

单章 base 由两部分组成：可选的稳定 `writer-profile`（通用框架与项目级硬规则）和本章动态任务头（chapter/mode/prompt/output/repair_focus）。目标 Prompt 作为该章的故事与表达输入。两者共同交给一个全新的 writer；writer 仍每章新建、每章独立 Prompt、独立创作上下文和独立输出。`writer-profile` 只是派生缓存，不包含剧情或章节声线，hash 失效或缺失时按 `templates/runtime/novel-base.md` 完整重建。

base 的职责是建立 writer 身份和创作边界（通用框架），Prompt 的职责是提供本章内容与声线。主代理在派发时自然组合这两部分；profile/hash、usage 和产物检查属于顶层运行时记录，不复制 Prompt 内容进 base。

## Writer Profile 缓存与重试

- profile 来源至少包含 `templates/runtime/novel-base.md`，可记录项目级硬规则来源；不得包含本章事实、上一章正文或 Prompt 摘要。
- profile 带源文件 SHA-256；缺失或失效时回退到完整模板构造，不阻断旧项目。
- Writer 空返回/取消时先检查指定输出文件。文件完整则进入顶层阅读；缺失或截断才用同一 profile、同一 Prompt、同一输出语义自动重派一次。
- 自动重派不修改 Prompt，不扩大任务范围；第二次失败保留现场，由顶层决定恢复。
- 普通 `write.draft` / `edit.write` 首稿使用项目配置的稳定推理档位；只有已经被 Reader/裁决明确分流为 `REGENERATE` 的内容返修才允许升级资源。资源升级不能替代 Prompt 或规划回退。
