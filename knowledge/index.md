# Pro 创作知识索引

知识库只帮助 Agent 做创作判断，不定义流程字段或质量门禁。先判断当前任务，再读取最小的相关入口；不要为了证明“使用过知识”而把术语写进产物。

知识库按 **两层结构** 组织：

- **通用写作底座**（跨题材、跨卷不变，回答“怎么写”）：连载语法、场景方法、剧情方法、人物方法、文风原型。任何项目都要消费，不因题材变化。
- **类型风格知识**（题材专属，回答“这个题材的读者期待与禁忌”）：题材画像、题材表达规则。按 `genre_id` 叠加在底座之上，只提供差异化。

消费顺序：**底座先行、类型叠加**。规划角色先按任务读底座方法，再按题材读类型画像；prompt-crafter 首任务把两者按 `skills/context-pack.md` 压缩进预制包；anti-AI 只在编辑模式中按需加载类型表达规则。

## 通用写作底座（跨题材）

| 任务 | 入口 | 使用者 |
|---|---|---|
| 连载交付、章节最低交付、钩点与节奏 | `webnovel/index.md` | 所有规划角色、prompt-crafter（首任务建包，后续读 pack）；Reader、completion-reviewer 冷读后按需 |
| 冲突、钩子、情绪、反转、幕结构、幕拆解 | `plot/index.md` | volume-planner、act-planner、chapter-planner、prompt-crafter；completion-reviewer 冷读后按需 |
| 对话、对抗、转场等具体写法、自包含提示词方法 | `scene/index.md` | prompt-crafter；Reader、completion-reviewer 冷读后按需 |
| 角色决策、人物弧线、反派 | `character/index.md` | volume-planner、act-planner、chapter-planner、prompt-crafter；completion-reviewer 冷读后按需 |
| 项目文风尚未确定、作者要求选择表达方向 | `style/index.md` | volume-planner（形成阶段） |

## 类型风格知识（题材专属，叠加辅助）

| 任务 | 入口 | 使用者 |
|---|---|---|
| 题材定位、读者期待、节奏差异、题材失败模式 | `genre/index.md` | volume-planner、act-planner、chapter-planner、prompt-crafter（建包时按 `genre_id` 叠加）；completion-reviewer 冷读后按需 |
| 题材专属的表达删改/保留规则 | `anti-ai/index.md` | 编辑模式中由 anti-AI 加载：edit.anti-ai 全量扫描、edit.repair编辑模式|

使用顺序是：先按任务读通用底座方法（识别剧情任务、识别场景主导冲突），再按 `genre_id` 读题材画像叠加差异；项目文风形成阶段由 volume-planner 从 `style/index.md` 选择一个主原型和至多一个辅原型，再把它们改写成项目自己的样章和边界。作者确认后，所有下游角色只使用已经确认的项目文风。writer 不读取本索引，而是执行已经自包含的 Prompt。

预生成知识只提供叙事功能、因果条件和复读方向，不提供可直接套用的剧情菜单。文风样章与声线锚点来自项目级 `settings/writing-style.md`（由 volume-planner 与作者形成、prompt-crafter 提取为 Prompt「本章质感」、writer 执行），不在此通用知识库预生成；坏句与 AI 腔字面清单由 `knowledge/anti-ai/` 在编辑模式中按需提供（edit.anti-ai 全量扫描 / edit.repair编辑模式），不进入规划与 Prompt 创建阶段。Prompt 创建/修复者和独立审核者不加载 anti-AI 工作规则；anti-AI 只比对实际正文，不把诊断措辞写进候选。

volume-planner、act-planner、chapter-planner 和 prompt-crafter 在角色 frontmatter 中挂载各自索引。Reader 与 completion-reviewer 为保护冷读不预挂知识，只有发现问题后按对应 skill 追查原因。顶层不得把知识正文复制进 subagent 提示，也不得用角色扮演跳过角色文件与索引加载。`settings/context-pack.md` 是 prompt-crafter 的正式知识消费形态：本卷首个 `prompt.create` 任务完成索引加载与下钻并沉淀为 pack 后，后续任务读包即视为完成知识加载，不构成"跳过角色文件与索引加载"。
