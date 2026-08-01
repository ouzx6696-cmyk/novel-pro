# Writer Construction

<!-- changed_in: 0.2.3 -->

本模块描述 novel-agent 如何从 `templates/runtime/novel-base.md` 模板构造单章 writer base，被 `write.draft` 和 `edit.write` 的派发流程加载。

## 构造单章 Writer

主代理在创建每个 writer 子代理前读取 `templates/runtime/novel-base.md`，再根据当前章节写成单章 writer base。base 模板分两部分：**第一部分是主代理构造指南**（base 是什么、何时构造、怎么构造、纪律），**第二部分是参考模板**（标准结构）。构造时先读第一部分获得方法，再按第二部分模板填充。

实例化使用当前任务已经确定的信息：

- 章节标识和任务模式。
- 目标 Prompt 路径。
- 草稿或候选输出路径。
- 内容返修时 Reader 已确认的返修焦点。

**质感核对（不写入 base）**：构造时阅读目标 Prompt 的「本章质感」小节，确认它是可执行的具体声线材料（含声线特征、节奏型、禁用表达、样句），不是抽象形容词或占位符。核对本身即一次 Prompt 检查：若质感空泛或文风未确认，按 `skills/prompt.md` 的缺口规则返回顶层，不构造 base、不补成通用文风。**质感不复制进 base**——writer 同时收到 base 与 Prompt，本章声线以 Prompt「本章质感」为唯一指令源，base 只提供通用写作框架与项目级硬规则（标点、禁用句式、章末纪律）。

单章 base 作为子代理的初始化提示词。目标 Prompt 作为该章的故事与表达输入。两者共同交给一个全新的 writer；每章拥有独立 base、独立 Prompt、独立上下文和独立输出。

base 的职责是建立 writer 身份和创作边界（通用框架），Prompt 的职责是提供本章内容与声线。主代理在派发时自然组合这两部分，不生成额外 manifest、质量字段或脚本校验，不复制 Prompt 内容进 base。
