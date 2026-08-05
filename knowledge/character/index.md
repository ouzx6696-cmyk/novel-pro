# 角色知识索引

- 角色为何会这样选择、如何保持一致又发生变化：`decision-engine.md`。
- 对手如何形成自洽压力，而非推动剧情的工具：`antagonist.md`。
- 多幕人物弧线、关系和认知怎样连续：`arc-continuity.md`（含认知6层可变性规则与状态变更记录方法）。
- 人物"截至当前章"的状态与知识存量来自 `settings/character-setting/` 档案的 `state_history` 节（`state.update` 按章追加维护），倒读重建：`arc-continuity.md`「状态变更记录方法」。

角色知识用于规划人物选择，也帮助 prompt-crafter 把当前章的人物状态落实为行动，
不用于生成完整心理档案。只保留会改变正文的动机、能力边界、认知盲区、关系、当前
压力和已经付出的不可逆代价。每章 Prompt 的「角色初始状态」块是本章所需的裁剪产物，
不是完整档案的搬运。
