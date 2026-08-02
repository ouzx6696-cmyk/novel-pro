# 场景知识索引

本索引有两种按需用途。创建或修复 Prompt 时，prompt-crafter 先判断场景的主导任务，再读取相关文件，把方法转化为当前人物的动作、感知和冲突指令。Reader 首读不预加载本索引；只有正文已经暴露真实的场景执行或表达问题后，Reader 才能按证据读取最小相关入口用于追因，不把条目变成预设检查清单。

一个场景可以涉及多种元素，但只保留能改变当前判断或写法的指导。

| 场景任务 | 读取 |
|---|---|
| 单章篇幅配比、轻重安排和写足判定 | `chapter-structure.md` |
| 场景像流程、人物行为缺少现场摩擦或选择余波 | `scene-truth.md` |
| 所有场景的句子、细节和信息密度 | `prose.md` |
| 有限视角、感知顺序、视角切换 | `pov.md` |
| 试探、谈判、争执、隐瞒 | `dialogue.md` |
| 战斗、追逐、竞赛、行动博弈 | `confrontation.md` |
| 空间、氛围、线索环境 | `environment.md` |
| 决策前的思考与情绪承受 | `inner-thought.md` |
| 新人物登场和外貌辨识 | `appearance.md` |
| 多人物同场 | `group-scene.md` |
| 时间、地点或情绪过渡 | `transition.md` |
| 人物死亡或永久离场 | `death-scene.md` |
| 仙侠/玄幻战斗、法宝、阵法和突破 | `xianxia-action.md`，并结合题材画像 |
| 悬疑调查、现场、证词和证据链 | `investigation.md`，并结合题材画像 |
| Prompt 不自包含：writer 拿到 Prompt 后仍需外部上下文才能写作 | `self-contained-prompt.md` |
| 返修时如何判断类型、形成焦点、执行和验证 | `repair-methods.md` |

prompt-crafter 读取后把方法改写成当前人物的动作、感知和冲突指令，不把知识库示范正文整段抄进 Prompt，不写文件名或方法标签（样句锚点只从项目 `writing-style.md` 基准样章选取或按其声线原创）。Reader 读取后只用来解释正文中已经出现的问题和复读方向，不据此虚构缺陷或直接改文。
