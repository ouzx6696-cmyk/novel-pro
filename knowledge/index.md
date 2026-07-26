# Pro 创作知识索引

知识库只帮助 Agent 做创作判断，不定义流程字段或质量门禁。先判断当前任务，再读取最小的相关入口；不要为了证明“使用过知识”而把术语写进产物。

| 任务 | 入口 | 使用者 |
|---|---|---|
| 连载交付、章节最低交付、钩点与节奏 | `webnovel/index.md` | volume-planner、act-planner、chapter-planner、prompt-crafter（首任务建包，后续读 pack）；Reader、completion-reviewer 冷读后按需 |
| 题材定位、读者期待、节奏差异 | `genre/index.md` | volume-planner、act-planner、chapter-planner、prompt-crafter；completion-reviewer 冷读后按需 |
| 项目文风尚未确定、作者要求选择表达方向 | `style/index.md` | volume-planner（形成阶段） |
| 冲突、钩子、情绪、反转、幕结构、幕拆解 | `plot/index.md` | volume-planner、act-planner、chapter-planner、prompt-crafter；completion-reviewer 冷读后按需 |
| 对话、对抗、转场等具体写法、自包含提示词方法 | `scene/index.md` | prompt-crafter；Reader、completion-reviewer 冷读后按需 |
| 角色决策、人物弧线、反派 | `character/index.md` | volume-planner、act-planner、chapter-planner、prompt-crafter；completion-reviewer 冷读后按需 |
| 真实表达问题的按需处理 | `anti-ai/index.md` | 只有 Full Reader 点名后由 anti-AI 编辑加载 |

使用顺序是：识别剧情任务，识别场景主导冲突，读取题材差异；项目文风形成阶段由 volume-planner 从 `style/index.md` 选择一个主原型和至多一个辅原型，再把它们改写成项目自己的样章和边界。作者确认后，所有下游角色只使用已经确认的项目文风。writer 不读取本索引，而是执行已经自包含的 Prompt。

预生成知识只提供叙事功能、因果条件和复读方向，不提供可直接套用的剧情菜单。文风样章与声线锚点来自项目级 `settings/writing-style.md`（由 volume-planner 与作者形成、prompt-crafter 提取为 Prompt「本章质感」、writer 执行），不在此通用知识库预生成；坏句与 AI 腔字面清单由 `knowledge/anti-ai/` 在 Reader 点名后按需提供，不进入规划与 Prompt 创建阶段。Prompt 创建/修复者和独立审核者不加载 anti-AI 工作规则；anti-AI 只比对 Reader 点名的实际正文，不把诊断措辞写进候选。

volume-planner、act-planner、chapter-planner 和 prompt-crafter 在角色 frontmatter 中挂载各自索引。Reader 与 completion-reviewer 为保护冷读不预挂知识，只有发现问题后按对应 skill 追查原因。顶层不得把知识正文复制进 subagent 提示，也不得用角色扮演跳过角色文件与索引加载。`settings/context-pack.md` 是 prompt-crafter 的正式知识消费形态：本卷首个 `prompt.create` 任务完成索引加载与下钻并沉淀为 pack 后，后续任务读包即视为完成知识加载，不构成"跳过角色文件与索引加载"。
