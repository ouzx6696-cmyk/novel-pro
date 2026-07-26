# Writer Construction

<!-- changed_in: 0.2.3 -->

本模块描述 novel-agent 如何从 `templates/runtime/novel-base.md` 模板构造单章 writer base，被 `fast.write` 和 `full.write` 的派发流程加载。

## 构造单章 Writer

主代理在创建每个 writer 子代理前读取 `templates/runtime/novel-base.md`，再根据当前章节写成单章 writer base。

实例化使用当前任务已经确定的信息：

- 章节标识和任务模式。
- 目标 Prompt 路径。
- 草稿或候选输出路径。
- 内容返修时 Reader 已确认的返修焦点。

单章 base 作为子代理的初始化提示词。目标 Prompt 作为该章的故事与表达输入。两者共同交给一个全新的 writer；每章拥有独立 base、独立 Prompt、独立上下文和独立输出。

base 的职责是建立 writer 身份和创作边界，Prompt 的职责是提供本章内容。主代理在派发时自然组合这两部分，不生成额外 manifest、质量字段或脚本校验。
